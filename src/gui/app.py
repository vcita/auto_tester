"""
FastAPI application for the vcita Test Runner GUI.

Provides REST API endpoints and Server-Sent Events for real-time test updates.
"""

import asyncio
import json
import re
import threading
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from queue import Queue, Empty

from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.discovery import TestDiscovery
from src.runner import TestRunner
from src.runner.runner import build_execution_plan
from src.runner.events import RunnerEvent
from src.runner.storage import RunStorage


# Global state
_runner: Optional[TestRunner] = None
_is_running: bool = False
_run_lock = threading.Lock()
_event_queues: List[Queue] = []
_event_queues_lock = threading.Lock()


def create_app(tests_root: Path, snapshots_dir: Path, heal_requests_dir: Path) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        tests_root: Path to the tests/ directory
        snapshots_dir: Path to the snapshots/ directory
        heal_requests_dir: Path to the .cursor/heal_requests/ directory
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="vcita Test Runner",
        description="Web GUI for running and managing tests",
        version="1.0.0"
    )
    
    # Store paths in app state (project_root = parent of tests_root for config.yaml)
    app.state.tests_root = tests_root
    app.state.project_root = tests_root.parent
    app.state.snapshots_dir = snapshots_dir
    app.state.heal_requests_dir = heal_requests_dir
    
    # Mount static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Mount snapshots for serving screenshots and videos
    if snapshots_dir.exists():
        app.mount("/snapshots", StaticFiles(directory=snapshots_dir), name="snapshots")
    
    # ==================== HTML Routes ====================
    
    @app.get("/", response_class=HTMLResponse)
    async def root():
        """Serve the main HTML page with cache-busting for static assets."""
        index_path = static_dir / "index.html"
        if not index_path.exists():
            return HTMLResponse(content="<h1>GUI not found</h1>", status_code=404)
        html = index_path.read_text(encoding="utf-8")
        # Cache-bust static assets so browser always gets latest after server restart
        for name in ("style.css", "app.js"):
            asset = static_dir / name
            if asset.exists():
                v = str(int(asset.stat().st_mtime))
                if name == "style.css":
                    html = html.replace('href="/static/style.css"', f'href="/static/style.css?v={v}"')
                else:
                    html = re.sub(r'src="/static/app\.js(?:\?v=\d+)?"', f'src="/static/app.js?v={v}"', html)
        return HTMLResponse(
            content=html,
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )
    
    # ==================== API Routes ====================
    
    @app.get("/api/categories")
    async def get_categories():
        """Get all categories and their tests (run order from execution_order in _category.yaml)."""
        discovery = TestDiscovery(app.state.tests_root)
        categories = discovery.scan()
        
        result = []
        for cat in categories:
            # Use path.name as the id since Category doesn't have an id attribute
            cat_id = cat.path.name if cat.path else cat.name.lower().replace(" ", "_")
            cat_data = {
                "id": cat_id,
                "name": cat.name,
                "description": cat.description or "",
                "has_setup": cat.setup is not None,
                "has_teardown": cat.teardown is not None,
                "tests": [],
                "subcategories": [],
                "execution_items": []  # Exact run order: setup, tests/subcats interleaved, teardown
            }
            # Build execution_items in exact run order (setup -> plan -> teardown)
            if cat_data["has_setup"]:
                cat_data["execution_items"].append({"type": "setup", "id": "_setup", "name": "_setup"})
            plan = build_execution_plan(cat)
            for item in plan:
                if hasattr(item, "id") and hasattr(item, "path"):
                    # Test
                    test_desc = getattr(item, "description", "") or ""
                    cat_data["execution_items"].append({
                        "type": "test",
                        "id": item.id,
                        "name": item.name,
                        "status": item.status.value if hasattr(item.status, "value") else str(item.status),
                        "description": test_desc,
                        "path": str(item.path.relative_to(app.state.tests_root)) if item.path else ""
                    })
                else:
                    # Subcategory
                    subcat = item
                    subcat_id = subcat.path.name if subcat.path else subcat.name.lower().replace(" ", "_")
                    subcat_tests = []
                    for test in subcat.tests or []:
                        test_desc = getattr(test, "description", "") or ""
                        subcat_tests.append({
                            "id": test.id,
                            "name": test.name,
                            "status": test.status.value if hasattr(test.status, "value") else str(test.status),
                            "description": test_desc,
                            "path": str(test.path.relative_to(app.state.tests_root)) if test.path else ""
                        })
                    cat_data["execution_items"].append({
                        "type": "subcategory",
                        "id": subcat_id,
                        "name": subcat.name,
                        "description": subcat.description or "",
                        "tests": subcat_tests,
                        "has_setup": subcat.setup is not None,
                        "has_teardown": subcat.teardown is not None,
                    })
            if cat_data["has_teardown"]:
                cat_data["execution_items"].append({"type": "teardown", "id": "_teardown", "name": "_teardown"})
            # Keep tests and subcategories for backward compatibility
            for test in cat.tests:
                test_desc = getattr(test, "description", "") or ""
                cat_data["tests"].append({
                    "id": test.id,
                    "name": test.name,
                    "status": test.status.value if hasattr(test.status, "value") else str(test.status),
                    "description": test_desc,
                    "path": str(test.path.relative_to(app.state.tests_root)) if test.path else ""
                })
            for subcat in cat.subcategories:
                subcat_id = subcat.path.name if subcat.path else subcat.name.lower().replace(" ", "_")
                subcat_data = {
                    "id": subcat_id,
                    "name": subcat.name,
                    "description": subcat.description or "",
                    "tests": [],
                    "has_setup": subcat.setup is not None,
                    "has_teardown": subcat.teardown is not None,
                }
                for test in subcat.tests:
                    test_desc = getattr(test, "description", "") or ""
                    subcat_data["tests"].append({
                        "id": test.id,
                        "name": test.name,
                        "status": test.status.value if hasattr(test.status, "value") else str(test.status),
                        "description": test_desc,
                        "path": str(test.path.relative_to(app.state.tests_root)) if test.path else ""
                    })
                cat_data["subcategories"].append(subcat_data)
            result.append(cat_data)
        
        return JSONResponse(
            content={"categories": result},
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )
    
    @app.get("/api/test/{category}/{test_path:path}")
    async def get_test_details(category: str, test_path: str):
        """Get test details including steps, script, and code."""
        # Build the test path
        test_dir = app.state.tests_root / category / test_path
        
        if not test_dir.exists():
            raise HTTPException(status_code=404, detail=f"Test not found: {category}/{test_path}")
        
        result = {
            "category": category,
            "test_path": test_path,
            "steps": None,
            "script": None,
            "code": None
        }
        
        # Read steps.md
        steps_file = test_dir / "steps.md"
        if steps_file.exists():
            result["steps"] = steps_file.read_text(encoding="utf-8")
        
        # Read script.md
        script_file = test_dir / "script.md"
        if script_file.exists():
            result["script"] = script_file.read_text(encoding="utf-8")
        
        # Read test.py
        code_file = test_dir / "test.py"
        if code_file.exists():
            result["code"] = code_file.read_text(encoding="utf-8")
        
        return result
    
    @app.get("/api/heal-requests")
    async def get_heal_requests():
        """List all heal requests with parsed details (date, test_name, category, status)."""
        heal_dir = app.state.heal_requests_dir
        
        if not heal_dir.exists():
            return {"heal_requests": []}
        
        requests = []
        for file in sorted(heal_dir.glob("*.md"), reverse=True, key=lambda p: p.stat().st_mtime):
            if file.name == ".gitkeep":
                continue
            entry = {
                "id": file.stem,
                "filename": file.name,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                "test_name": None,
                "category": None,
                "status": "open",
            }
            try:
                text = file.read_text(encoding="utf-8")
                for line in text.splitlines()[:20]:
                    line = line.strip()
                    if line.startswith("# Heal Request: "):
                        part = line.replace("# Heal Request: ", "").strip()
                        if "/" in part:
                            parts = part.split("/")
                            entry["test_name"] = parts[-1]  # test name only e.g. "Add Note", "Create Service"
                            # Category = full path (e.g. Clients/Notes, Scheduling/Services); use first two path segments
                            entry["category"] = "/".join(p.title() for p in parts[:2]) if len(parts) >= 2 else parts[0].title()
                        else:
                            entry["test_name"] = part
                    elif line.startswith("**Status**:") or ("**Status**:" in line and "`" in line):
                        # Parse value from backticks, e.g. **Status**: `expired`
                        m = re.search(r"`([^`]+)`", line)
                        if m:
                            entry["status"] = m.group(1).strip().lower()
                        elif "resolved" in line.lower() or "fixed" in line.lower():
                            entry["status"] = "fixed"
                        elif "open" in line.lower():
                            entry["status"] = "open"
                        elif "expired" in line.lower():
                            entry["status"] = "expired"
                        elif "reported" in line.lower():
                            entry["status"] = "reported"
                        break
            except (IOError, OSError):
                pass
            if entry["test_name"] is None:
                entry["test_name"] = file.stem.rsplit("_", 2)[0].replace("-", "/") if "_" in file.stem else file.stem
            requests.append(entry)
        
        return JSONResponse(
            content={"heal_requests": requests},
            headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
        )
    
    @app.get("/api/heal-request/{request_id}")
    async def get_heal_request(request_id: str):
        """Get a specific heal request content."""
        heal_file = app.state.heal_requests_dir / f"{request_id}.md"
        
        if not heal_file.exists():
            raise HTTPException(status_code=404, detail=f"Heal request not found: {request_id}")
        
        return {
            "id": request_id,
            "content": heal_file.read_text(encoding="utf-8")
        }

    @app.get("/api/setup")
    async def get_setup():
        """Get current target config for Switch setup (password masked)."""
        config_path = app.state.project_root / "config.yaml"
        if not config_path.exists():
            return {"base_url": "", "username": "", "password_masked": True}
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        target = config.get("target") or {}
        auth = target.get("auth") or {}
        return {
            "base_url": target.get("base_url") or "",
            "username": auth.get("username") or "",
            "password_masked": True,
        }

    @app.post("/api/setup")
    async def post_setup(body: Dict[str, Any] = Body(default=None)):
        """Update config.yaml target (merge provided keys; omit to keep current)."""
        config_path = app.state.project_root / "config.yaml"
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="config.yaml not found")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        if "target" not in config:
            config["target"] = {}
        if "auth" not in config["target"]:
            config["target"]["auth"] = {}
        target = config["target"]
        auth = target["auth"]
        body = body or {}
        if body.get("base_url") is not None:
            target["base_url"] = body["base_url"]
        target.pop("login_url", None)  # Login URL = base_url + "/login"
        if body.get("username") is not None:
            auth["username"] = body["username"]
        if body.get("password") is not None and body.get("password") != "":
            auth["password"] = body["password"]
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return await get_setup()
    
    @app.get("/api/screenshots")
    async def get_screenshots():
        """List all screenshots from run history."""
        screenshots = []
        
        # Scan all category _runs folders for screenshots
        for category_dir in app.state.tests_root.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            runs_dir = category_dir / "_runs"
            if not runs_dir.exists():
                continue
            
            for run_dir in runs_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                tests_dir = run_dir / "tests"
                if not tests_dir.exists():
                    continue
                
                for test_dir in tests_dir.iterdir():
                    screenshot = test_dir / "screenshot.png"
                    if screenshot.exists():
                        screenshots.append({
                            "filename": screenshot.name,
                            "url": f"/api/runs/{category_dir.name}/{run_dir.name}/tests/{test_dir.name}/screenshot",
                            "category": category_dir.name,
                            "run_id": run_dir.name,
                            "test_name": test_dir.name,
                            "modified": datetime.fromtimestamp(screenshot.stat().st_mtime).isoformat(),
                            "size": screenshot.stat().st_size
                        })
        
        # Sort by modified time, newest first
        screenshots.sort(key=lambda x: x["modified"], reverse=True)
        return {"screenshots": screenshots}
    
    @app.get("/api/videos")
    async def get_videos():
        """List all videos from run history."""
        videos = []
        
        # Scan all category _runs folders for videos
        for category_dir in app.state.tests_root.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith("_"):
                continue
            runs_dir = category_dir / "_runs"
            if not runs_dir.exists():
                continue
            
            for run_dir in runs_dir.iterdir():
                if not run_dir.is_dir():
                    continue
                video = run_dir / "video.webm"
                if video.exists():
                    videos.append({
                        "filename": video.name,
                        "url": f"/api/runs/{category_dir.name}/{run_dir.name}/video",
                        "category": category_dir.name,
                        "run_id": run_dir.name,
                        "modified": datetime.fromtimestamp(video.stat().st_mtime).isoformat(),
                        "size": video.stat().st_size
                    })
        
        # Sort by modified time, newest first
        videos.sort(key=lambda x: x["modified"], reverse=True)
        return {"videos": videos}
    
    @app.get("/api/status")
    async def get_status():
        """Get current runner status."""
        return {
            "is_running": _is_running,
            "tests_root": str(app.state.tests_root)
        }

    @app.get("/api/last-results")
    async def get_last_results():
        """
        Get the last run result (passed/failed/skipped) for each test.
        Keys are path identifiers matching the tree: category_id/test_id or category_id/subcat_id/test_id or category_id/_setup.
        """
        storage = RunStorage(app.state.tests_root)
        raw = storage.get_all_last_results()
        discovery = TestDiscovery(app.state.tests_root)
        categories = discovery.scan()
        # Build (category_path, test_name) -> path_key so we can map storage entries to frontend keys
        name_to_key: Dict[tuple, str] = {}
        for cat in categories:
            cat_id = cat.path.name if cat.path else cat.name.lower().replace(" ", "_")
            try:
                cat_path_str = str(cat.path.relative_to(app.state.tests_root)).replace("\\", "/")
            except (ValueError, AttributeError):
                cat_path_str = cat_id
            if cat.setup is not None:
                name_to_key[(cat_path_str, "_setup")] = f"{cat_id}/_setup"
            if cat.teardown is not None:
                name_to_key[(cat_path_str, "_teardown")] = f"{cat_id}/_teardown"
            for test in cat.tests or []:
                test_name = getattr(test, "name", None) or (test.path.name if test.path else "")
                name_to_key[(cat_path_str, test_name)] = f"{cat_id}/{test.path.name}" if test.path else f"{cat_id}/{getattr(test, 'id', test_name)}"
            for subcat in cat.subcategories or []:
                subcat_id = subcat.path.name if subcat.path else subcat.name.lower().replace(" ", "_")
                subcat_path_str = f"{cat_path_str}/{subcat_id}"
                if subcat.setup is not None:
                    name_to_key[(subcat_path_str, "_setup")] = f"{cat_id}/{subcat_id}/_setup"
                    name_to_key[(subcat_path_str, f"{subcat.name}/_setup")] = f"{cat_id}/{subcat_id}/_setup"
                if subcat.teardown is not None:
                    name_to_key[(subcat_path_str, "_teardown")] = f"{cat_id}/{subcat_id}/_teardown"
                    name_to_key[(subcat_path_str, f"{subcat.name}/_teardown")] = f"{cat_id}/{subcat_id}/_teardown"
                for test in subcat.tests or []:
                    test_name = getattr(test, "name", None) or (test.path.name if test.path else "")
                    path_key = f"{cat_id}/{subcat_id}/{test.path.name}" if test.path else f"{cat_id}/{subcat_id}/{getattr(test, 'id', test_name)}"
                    name_to_key[(subcat_path_str, test_name)] = path_key
                    name_to_key[(subcat_path_str, f"{subcat.name}/{test_name}")] = path_key
        result_map: Dict[str, str] = {}
        for item in raw:
            key = (item["category_path"], item["test_name"])
            path_key = name_to_key.get(key)
            if path_key and path_key not in result_map:
                result_map[path_key] = item["status"]
        return {"last_results": result_map}
    
    @app.get("/api/active-run")
    async def get_active_run():
        """Check if there's an active run and return its info."""
        # First check if GUI knows about a running test
        if _is_running and _runner:
            return {
                "is_active": True,
                "run_id": None,  # We don't track run_id in GUI state
                "started_via_gui": True
            }
        
        # Check for recent run directories that might be active
        # A run is considered potentially active if:
        # 1. It was created in the last 30 minutes
        # 2. It doesn't have a completed status in the index
        
        storage = RunStorage(app.state.tests_root)
        from datetime import timedelta
        
        # Check runs_index for the most recent run
        if storage.index_dir.exists():
            index_files = sorted(
                [f for f in storage.index_dir.glob("*.json") if f.is_file()],
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )
            
            if index_files:
                # Check the most recent index file
                most_recent = index_files[0]
                try:
                    index_data = json.loads(most_recent.read_text(encoding="utf-8"))
                    run_id = index_data.get("run_id")
                    completed_at = index_data.get("completed_at")
                    started_at = index_data.get("started_at")
                    
                    # If not completed and started recently (within 30 min), consider it active
                    if not completed_at and started_at:
                        try:
                            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                            if start_time.tzinfo is None:
                                # Assume local time if no timezone
                                start_time = datetime.fromisoformat(started_at)
                            age = datetime.now() - start_time.replace(tzinfo=None) if start_time.tzinfo else datetime.now() - start_time
                            
                            if age < timedelta(minutes=30):
                                return {
                                    "is_active": True,
                                    "run_id": run_id,
                                    "started_via_gui": False,
                                    "started_at": started_at,
                                    "categories": index_data.get("categories", [])
                                }
                        except (ValueError, AttributeError):
                            pass
                except (json.JSONDecodeError, KeyError):
                    pass
        
        return {
            "is_active": False,
            "run_id": None,
            "started_via_gui": False
        }
    
    # ==================== Run History Endpoints ====================
    
    @app.get("/api/runs")
    async def get_all_runs():
        """List all runs from the index."""
        storage = RunStorage(app.state.tests_root)
        runs = storage.list_all_runs()
        return {"runs": runs}
    
    @app.get("/api/runs/{category}")
    async def get_category_runs(category: str):
        """List all runs for a specific category."""
        storage = RunStorage(app.state.tests_root)
        runs = storage.list_category_runs(category)
        return {"category": category, "runs": runs}
    
    @app.get("/api/runs/{category}/test/{test_name:path}")
    async def get_test_runs(category: str, test_name: str):
        """List all runs that contain a specific test."""
        print(f"[DEBUG] API call: category={category}, test_name={test_name}, tests_root={app.state.tests_root}")
        storage = RunStorage(app.state.tests_root)
        runs = storage.list_test_runs(category, test_name)
        print(f"[DEBUG] Found {len(runs)} runs for {category}/{test_name}")
        if runs:
            print(f"[DEBUG] Run IDs: {[r.get('run_id') for r in runs]}")
        return {"category": category, "test_name": test_name, "runs": runs}
    
    @app.get("/api/runs/{category}/{run_id}")
    async def get_run_details(category: str, run_id: str):
        """Get detailed run data for a specific category and run."""
        storage = RunStorage(app.state.tests_root)
        details = storage.get_run_details(category, run_id)
        
        if not details:
            raise HTTPException(status_code=404, detail=f"Run not found: {category}/{run_id}")
        
        return details
    
    @app.get("/api/runs/{category}/{run_id}/video")
    async def get_run_video(category: str, run_id: str):
        """Get the video file for a specific run."""
        run_dir = app.state.tests_root / category / "_runs" / run_id
        video_path = run_dir / "video.webm"
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail=f"Video not found for run: {category}/{run_id}")
        
        return FileResponse(
            video_path,
            media_type="video/webm",
            filename=f"{category}_{run_id}.webm"
        )
    
    @app.get("/api/runs/{category}/{run_id}/tests/{test_name}/screenshot")
    async def get_test_screenshot(category: str, run_id: str, test_name: str):
        """Get the screenshot for a specific test in a run."""
        screenshot_path = app.state.tests_root / category / "_runs" / run_id / "tests" / test_name / "screenshot.png"
        
        if not screenshot_path.exists():
            raise HTTPException(status_code=404, detail=f"Screenshot not found: {category}/{run_id}/{test_name}")
        
        return FileResponse(
            screenshot_path,
            media_type="image/png",
            filename=f"{test_name}_screenshot.png"
        )
    
    @app.get("/api/runs/{category}/{run_id}/tests/{test_name}/heal_request")
    async def get_test_heal_request(category: str, run_id: str, test_name: str):
        """Get the heal request for a specific test in a run."""
        heal_path = app.state.tests_root / category / "_runs" / run_id / "tests" / test_name / "heal_request.md"
        
        if not heal_path.exists():
            raise HTTPException(status_code=404, detail=f"Heal request not found: {category}/{run_id}/{test_name}")
        
        return {
            "category": category,
            "run_id": run_id,
            "test_name": test_name,
            "content": heal_path.read_text(encoding="utf-8")
        }
    
    # ==================== Run Endpoints ====================
    
    def _broadcast_event(event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected SSE clients."""
        with _event_queues_lock:
            for queue in _event_queues:
                try:
                    queue.put_nowait({
                        "event": event_type,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    pass  # Queue full, skip
    
    def _run_tests_thread(category: Optional[str], tests_root: Path, run_all_selection: Optional[List[str]] = None):
        """Run tests in a background thread. When category is set, run that category; when run_all_selection is set, run only those paths via run_all(selection)."""
        global _is_running, _runner
        
        # Load config so runner injects target.base_url and target.auth into context (same account as config.yaml)
        config = {}
        config_path = app.state.project_root / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        
        try:
            _runner = TestRunner(tests_root, headless=False, config=config)
            
            # Subscribe to events
            def on_event(event: RunnerEvent):
                def handler(data: Dict[str, Any]):
                    # Convert non-serializable objects
                    serializable_data = {}
                    for key, value in data.items():
                        if hasattr(value, '__dict__'):
                            serializable_data[key] = str(value)
                        elif isinstance(value, Path):
                            serializable_data[key] = str(value)
                        else:
                            try:
                                json.dumps(value)
                                serializable_data[key] = value
                            except:
                                serializable_data[key] = str(value)
                    
                    _broadcast_event(event.value, serializable_data)
                return handler
            
            for event in RunnerEvent:
                _runner.events.on(event, on_event(event))
            
            # Run tests
            _broadcast_event("run_starting", {"category": category, "selection": run_all_selection})
            
            if category:
                result = _runner.run_category(category)
            elif run_all_selection is not None:
                result = _runner.run_all(selection=run_all_selection)
            else:
                result = _runner.run_all()
            
            # Send completion (RunResult has total_*, CategoryResult has passed/failed/skipped)
            passed = getattr(result, 'total_passed', None) or getattr(result, 'passed', 0) or 0
            failed = getattr(result, 'total_failed', None) or getattr(result, 'failed', 0) or 0
            skipped = getattr(result, 'total_skipped', None) or getattr(result, 'skipped', 0) or 0
            _broadcast_event("run_complete", {
                "category": category,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
            })
            
        except Exception as e:
            _broadcast_event("run_error", {"error": str(e)})
        finally:
            _is_running = False
            _runner = None
    
    @app.post("/api/run/category/{category:path}")
    async def run_category(category: str, background_tasks: BackgroundTasks):
        """Run tests in a specific category or subcategory (e.g. scheduling or scheduling/services)."""
        global _is_running
        
        with _run_lock:
            if _is_running:
                raise HTTPException(status_code=409, detail="Tests are already running")
            _is_running = True
        
        # Start in background thread
        thread = threading.Thread(
            target=_run_tests_thread,
            args=(category, app.state.tests_root),
            daemon=True
        )
        thread.start()
        
        return {"status": "started", "category": category}
    
    @app.post("/api/run/all")
    async def run_all(body: Dict[str, Any] = Body(default=None)):
        """Run all tests, or only selected category paths when body.selection is provided (list of paths, e.g. ["clients", "scheduling/events"])."""
        global _is_running
        
        selection = (body or {}).get("selection")
        if selection is not None and not isinstance(selection, list):
            selection = None
        
        with _run_lock:
            if _is_running:
                raise HTTPException(status_code=409, detail="Tests are already running")
            _is_running = True
        
        # Start in background thread
        thread = threading.Thread(
            target=_run_tests_thread,
            args=(None, app.state.tests_root),
            kwargs={"run_all_selection": selection},
            daemon=True
        )
        thread.start()
        
        return {"status": "started", "category": "all", "selection": selection}
    
    # ==================== SSE Endpoint ====================
    
    @app.get("/api/events")
    async def events():
        """Server-Sent Events endpoint for real-time updates."""
        queue = Queue()
        
        with _event_queues_lock:
            _event_queues.append(queue)
        
        async def event_generator():
            try:
                # Send initial connection event
                yield {
                    "event": "connected",
                    "data": json.dumps({"status": "connected", "is_running": _is_running})
                }
                
                heartbeat_counter = 0
                while True:
                    try:
                        # Non-blocking check for events
                        try:
                            event_data = queue.get_nowait()
                            yield {
                                "event": event_data["event"],
                                "data": json.dumps(event_data["data"])
                            }
                            heartbeat_counter = 0  # Reset counter when we have real events
                        except Empty:
                            # No event available, increment counter
                            heartbeat_counter += 1
                            # Send heartbeat every 60 iterations (~60 seconds)
                            if heartbeat_counter >= 60:
                                yield {
                                    "event": "heartbeat",
                                    "data": json.dumps({"time": datetime.now().isoformat()})
                                }
                                heartbeat_counter = 0
                    except GeneratorExit:
                        break
                    except asyncio.CancelledError:
                        break
                    except Exception:
                        # Ignore other exceptions and continue
                        pass
                    
                    await asyncio.sleep(1.0)
            finally:
                with _event_queues_lock:
                    if queue in _event_queues:
                        _event_queues.remove(queue)
        
        return EventSourceResponse(event_generator())
    
    return app


def run_server(
    tests_root: Path,
    snapshots_dir: Path,
    heal_requests_dir: Path,
    host: str = "127.0.0.1",
    port: int = 8080
):
    """
    Run the GUI server.
    
    Args:
        tests_root: Path to tests/ directory
        snapshots_dir: Path to snapshots/ directory
        heal_requests_dir: Path to .cursor/heal_requests/ directory
        host: Host to bind to
        port: Port to listen on
    """
    import uvicorn
    
    app = create_app(tests_root, snapshots_dir, heal_requests_dir)
    
    print(f"\n  vcita Test Runner GUI")
    print(f"  ----------------------")
    print(f"  Open in browser: http://{host}:{port}")
    print(f"  Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=host, port=port, log_level="warning")

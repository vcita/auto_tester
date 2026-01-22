"""
FastAPI application for the vcita Test Runner GUI.

Provides REST API endpoints and Server-Sent Events for real-time test updates.
"""

import asyncio
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from queue import Queue, Empty

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.discovery import TestDiscovery
from src.runner import TestRunner
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
    
    # Store paths in app state
    app.state.tests_root = tests_root
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
        """Serve the main HTML page."""
        index_path = static_dir / "index.html"
        if index_path.exists():
            return HTMLResponse(content=index_path.read_text())
        return HTMLResponse(content="<h1>GUI not found</h1>", status_code=404)
    
    # ==================== API Routes ====================
    
    @app.get("/api/categories")
    async def get_categories():
        """Get all categories and their tests."""
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
                "subcategories": []
            }
            
            # Add direct tests
            for test in cat.tests:
                test_desc = ""
                if hasattr(test, 'description') and test.description:
                    test_desc = test.description
                cat_data["tests"].append({
                    "id": test.id,
                    "name": test.name,
                    "status": test.status.value if hasattr(test.status, 'value') else str(test.status),
                    "description": test_desc,
                    "path": str(test.path.relative_to(app.state.tests_root)) if test.path else ""
                })
            
            # Add subcategories
            for subcat in cat.subcategories:
                subcat_id = subcat.path.name if subcat.path else subcat.name.lower().replace(" ", "_")
                subcat_data = {
                    "id": subcat_id,
                    "name": subcat.name,
                    "description": subcat.description or "",
                    "tests": []
                }
                for test in subcat.tests:
                    test_desc = ""
                    if hasattr(test, 'description') and test.description:
                        test_desc = test.description
                    subcat_data["tests"].append({
                        "id": test.id,
                        "name": test.name,
                        "status": test.status.value if hasattr(test.status, 'value') else str(test.status),
                        "description": test_desc,
                        "path": str(test.path.relative_to(app.state.tests_root)) if test.path else ""
                    })
                cat_data["subcategories"].append(subcat_data)
            
            result.append(cat_data)
        
        return {"categories": result}
    
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
        """List all heal requests."""
        heal_dir = app.state.heal_requests_dir
        
        if not heal_dir.exists():
            return {"heal_requests": []}
        
        requests = []
        for file in sorted(heal_dir.glob("*.md"), reverse=True):
            if file.name == ".gitkeep":
                continue
            requests.append({
                "id": file.stem,
                "filename": file.name,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        
        return {"heal_requests": requests}
    
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
    
    def _run_tests_thread(category: Optional[str], tests_root: Path):
        """Run tests in a background thread."""
        global _is_running, _runner
        
        try:
            _runner = TestRunner(tests_root, headless=False)
            
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
            _broadcast_event("run_starting", {"category": category})
            
            if category:
                result = _runner.run_category(category)
            else:
                result = _runner.run_all()
            
            # Send completion
            _broadcast_event("run_complete", {
                "category": category,
                "passed": result.passed if hasattr(result, 'passed') else 0,
                "failed": result.failed if hasattr(result, 'failed') else 0,
                "skipped": result.skipped if hasattr(result, 'skipped') else 0
            })
            
        except Exception as e:
            _broadcast_event("run_error", {"error": str(e)})
        finally:
            _is_running = False
            _runner = None
    
    @app.post("/api/run/category/{category}")
    async def run_category(category: str, background_tasks: BackgroundTasks):
        """Run tests in a specific category."""
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
    async def run_all(background_tasks: BackgroundTasks):
        """Run all tests."""
        global _is_running
        
        with _run_lock:
            if _is_running:
                raise HTTPException(status_code=409, detail="Tests are already running")
            _is_running = True
        
        # Start in background thread
        thread = threading.Thread(
            target=_run_tests_thread,
            args=(None, app.state.tests_root),
            daemon=True
        )
        thread.start()
        
        return {"status": "started", "category": "all"}
    
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

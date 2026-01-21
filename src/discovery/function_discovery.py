"""
Function Discovery Module

Scans the tests/_functions/ folder to find and validate reusable functions.
Reads the _functions.yaml registry for metadata.
"""

import yaml
from pathlib import Path
from typing import Optional

from src.models import Function, FunctionParameter, FunctionReturn


class FunctionDiscovery:
    """Discovers and loads reusable functions from the filesystem."""
    
    FUNCTIONS_FOLDER = "_functions"
    REGISTRY_FILE = "_functions.yaml"
    STEPS_FILE = "steps.md"
    
    def __init__(self, tests_root: str | Path):
        """
        Initialize function discovery.
        
        Args:
            tests_root: Path to the tests/ directory
        """
        self.tests_root = Path(tests_root)
        self.functions_path = self.tests_root / self.FUNCTIONS_FOLDER
    
    @property
    def has_functions_folder(self) -> bool:
        """Check if _functions folder exists."""
        return self.functions_path.exists() and self.functions_path.is_dir()
    
    def scan(self) -> list[Function]:
        """
        Scan the _functions directory and return all functions.
        
        Returns:
            List of Function objects
            
        Raises:
            ValueError: If a function is invalid (missing files)
        """
        if not self.has_functions_folder:
            return []
        
        # Load registry for metadata
        registry = self._load_registry()
        registry_functions = {f["id"]: f for f in registry.get("functions", [])}
        
        functions = []
        errors = []
        
        for item in sorted(self.functions_path.iterdir()):
            # Skip non-directories and special files
            if not item.is_dir() or item.name.startswith("_") or item.name.startswith("."):
                continue
            
            # Check if it looks like a function (has steps.md)
            if not (item / self.STEPS_FILE).exists():
                continue
            
            # Create function with metadata from registry
            func = self._create_function(item, registry_functions.get(item.name, {}))
            
            # Validate (strict mode)
            if not func.validate():
                errors.append(f"Function '{func.id}' is invalid:\n  " + 
                            "\n  ".join(func.validation_errors))
            else:
                functions.append(func)
        
        # Raise error if any functions are invalid
        if errors:
            raise ValueError("Invalid functions found:\n" + "\n".join(errors))
        
        return functions
    
    def _load_registry(self) -> dict:
        """Load and parse _functions.yaml registry file."""
        registry_path = self.functions_path / self.REGISTRY_FILE
        
        if not registry_path.exists():
            return {}
        
        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            print(f"Warning: Failed to parse {registry_path}: {e}")
            return {}
    
    def _create_function(self, path: Path, yaml_data: dict) -> Function:
        """
        Create a Function object from a folder.
        
        Args:
            path: Path to the function folder
            yaml_data: Metadata from _functions.yaml (may be empty)
            
        Returns:
            Function object
        """
        func_id = path.name
        
        # Parse parameters
        parameters = []
        for param_data in yaml_data.get("parameters", []):
            parameters.append(FunctionParameter(
                name=param_data.get("name", ""),
                type=param_data.get("type", "string"),
                required=param_data.get("required", True),
                description=param_data.get("description"),
            ))
        
        # Parse returns
        returns = []
        for ret_data in yaml_data.get("returns", []):
            returns.append(FunctionReturn(
                name=ret_data.get("name", ""),
                description=ret_data.get("description"),
            ))
        
        return Function(
            id=func_id,
            name=yaml_data.get("name", func_id.replace("_", " ").title()),
            path=path,
            description=yaml_data.get("description"),
            parameters=parameters,
            returns=returns,
        )
    
    def find_function(self, func_id: str) -> Optional[Function]:
        """
        Find a function by its ID.
        
        Args:
            func_id: Function ID (folder name)
            
        Returns:
            Function object or None
        """
        try:
            functions = self.scan()
            for func in functions:
                if func.id == func_id:
                    return func
        except ValueError:
            # Some functions are invalid, but we might still find the one we want
            pass
        
        return None
    
    def get_function_ids(self) -> list[str]:
        """Get list of all function IDs."""
        try:
            return [f.id for f in self.scan()]
        except ValueError:
            return []
    
    def create_registry_entry(self, func: Function) -> dict:
        """
        Create a registry entry for a function (for adding to _functions.yaml).
        
        Args:
            func: Function object
            
        Returns:
            Dictionary suitable for YAML serialization
        """
        entry = {
            "id": func.id,
            "name": func.name,
        }
        
        if func.description:
            entry["description"] = func.description
        
        if func.parameters:
            entry["parameters"] = [
                {
                    "name": p.name,
                    "type": p.type,
                    "required": p.required,
                    **({"description": p.description} if p.description else {}),
                }
                for p in func.parameters
            ]
        
        if func.returns:
            entry["returns"] = [
                {
                    "name": r.name,
                    **({"description": r.description} if r.description else {}),
                }
                for r in func.returns
            ]
        
        return entry


def print_functions_list(functions: list[Function]) -> None:
    """
    Print a formatted list of functions.
    
    Args:
        functions: List of functions to print
    """
    if not functions:
        print("No functions found.")
        return
    
    print(f"\nAvailable Functions ({len(functions)}):\n")
    
    for func in functions:
        status = "[OK]" if func.is_valid else "[INVALID]"
        print(f"  {status} {func.id}")
        print(f"       {func.name}")
        
        if func.description:
            print(f"       {func.description}")
        
        if func.parameters:
            params = ", ".join(
                f"{p.name}{'*' if p.required else ''}" 
                for p in func.parameters
            )
            print(f"       Parameters: {params}")
        
        if func.returns:
            rets = ", ".join(r.name for r in func.returns)
            print(f"       Returns: {rets}")
        
        print()

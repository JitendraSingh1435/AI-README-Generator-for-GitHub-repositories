import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Set
import git

# Directories to ignore during scanning
IGNORE_DIRS: Set[str] = {
    ".git", ".github", "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__", "build", "dist", "out", "target", ".idea", ".vscode",
    ".pytest_cache", ".cache", "bin", "obj", "eggs", "htmlcov", "bower_components"
}

# File extensions to ignore (binary or bulky)
IGNORE_EXTS: Set[str] = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp", ".bmp", ".tiff",
    # Compiled / Binary
    ".pyc", ".pyo", ".pyd", ".class", ".o", ".obj", ".dll", ".exe", ".so", ".dylib", ".bin",
    # Archives
    ".zip", ".tar", ".gz", ".rar", ".7z", ".tgz",
    # Documents / Audio / Video
    ".pdf", ".docx", ".xlsx", ".pptx", ".mp3", ".mp4", ".wav", ".avi", ".mov",
    # Fonts
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    # Databases
    ".db", ".sqlite", ".sqlite3", ".sql",
    # Lock files
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "poetry.lock"
}

# Key configuration files that give rich metadata about technology and libraries used
CONFIG_FILES: Set[str] = {
    "package.json", "requirements.txt", "pyproject.toml", "setup.py",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Makefile",
    "Dockerfile", "docker-compose.yml", "webpack.config.js", "vite.config.ts"
}

def clone_repository(repo_url: str, dest_dir: str) -> str:
    """
    Clones a public Git repository to the specified destination directory.
    Returns the path to the cloned repository directory.
    """
    # Create absolute destination path
    dest_path = Path(dest_dir).resolve()
    
    # If the folder already exists, delete it first to ensure clean state
    if dest_path.exists():
        shutil.rmtree(dest_path, ignore_errors=True)
        
    dest_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Cloning repository {repo_url} to {dest_path}...")
    git.Repo.clone_from(repo_url, str(dest_path), depth=1)
    print("Cloning complete!")
    return str(dest_path)

def generate_dir_tree(dir_path: str, max_depth: int = 4) -> str:
    """
    Generates a beautiful visual ASCII representation of the directory structure.
    """
    base_path = Path(dir_path)
    tree_lines = []

    def _build_tree(path: Path, prefix: str = "", depth: int = 1):
        if depth > max_depth:
            return
            
        try:
            # Sort directories first, then files
            entries = sorted(
                list(path.iterdir()),
                key=lambda e: (not e.is_dir(), e.name.lower())
            )
        except OSError:
            return

        # Filter out ignored dirs
        entries = [e for e in entries if e.name not in IGNORE_DIRS]

        count = len(entries)
        for i, entry in enumerate(entries):
            is_last = (i == count - 1)
            connector = "└── " if is_last else "├── "
            
            # Print directory name or file name
            if entry.is_dir():
                tree_lines.append(f"{prefix}{connector}{entry.name}/")
                new_prefix = prefix + ("    " if is_last else "│   ")
                _build_tree(entry, new_prefix, depth + 1)
            else:
                # Filter out files with ignored extensions
                if entry.suffix.lower() not in IGNORE_EXTS:
                    tree_lines.append(f"{prefix}{connector}{entry.name}")

    tree_lines.append(f"{base_path.name}/")
    _build_tree(base_path)
    return "\n".join(tree_lines)

def extract_project_context(repo_path: str, max_chars_per_file: int = 3000, total_budget: int = 40000) -> Dict[str, str]:
    """
    Scans the repository and extracts the contents of configuration files and major entry files.
    Ensures total character budget is respected to prevent context window bloat.
    """
    base_path = Path(repo_path)
    context_data = {
        "config_files": {},
        "entry_files": {},
        "summary": ""
    }
    
    current_chars = 0

    # 1. Walk first for config files (high priority)
    for root, dirs, files in os.walk(base_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in CONFIG_FILES:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(base_path)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(max_chars_per_file)
                        context_data["config_files"][str(rel_path)] = content
                        current_chars += len(content)
                except Exception as e:
                    pass

    # 2. Look for primary entry points or main code files
    entry_point_keywords = ["main", "app", "index", "server", "run", "cli", "bootstrap"]
    
    for root, dirs, files in os.walk(base_path):
        if current_chars >= total_budget:
            break
            
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            file_path = Path(root) / file
            suffix = file_path.suffix.lower()
            
            # Skip ignored files or configs we already parsed
            if suffix in IGNORE_EXTS or file in CONFIG_FILES:
                continue
                
            rel_path = file_path.relative_to(base_path)
            
            # Check if this file seems like a primary file or a key module
            is_key_file = any(kw in file_path.stem.lower() for kw in entry_point_keywords)
            # Or if it is a major code file in the root or small subdirectories
            is_root_code = len(rel_path.parts) <= 2 and suffix in {".py", ".js", ".ts", ".go", ".rs", ".rb", ".java", ".cpp", ".cs"}
            
            if is_key_file or is_root_code:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(max_chars_per_file)
                        context_data["entry_files"][str(rel_path)] = content
                        current_chars += len(content)
                        
                        if current_chars >= total_budget:
                            break
                except Exception as e:
                    pass

    # Add quick metadata about total files
    all_files_count = 0
    languages = set()
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            suffix = Path(file).suffix.lower()
            if suffix not in IGNORE_EXTS:
                all_files_count += 1
                if suffix:
                    languages.add(suffix)

    context_data["summary"] = f"Total Scanned Files: {all_files_count}\nDetected Languages/Extensions: {', '.join(languages)}"
    
    return context_data

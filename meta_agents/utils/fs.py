"""Filesystem utilities for meta-agentic SDK."""

from pathlib import Path
import shutil


def ensure_dir(path: Path) -> Path:
 """Ensure a directory exists, creating it if necessary.
 
 Args:
 path: Path to the directory
 
 Returns:
 The path object
 """
 path.mkdir(parents=True, exist_ok=True)
 return path


def copy_tree(src: Path, dst: Path) -> None:
 """Copy a directory tree.
 
 Args:
 src: Source directory
 dst: Destination directory
 """
 shutil.copytree(src, dst, dirs_exist_ok=True)


def safe_write(path: Path, content: str) -> None:
 """Safely write content to a file, creating parent directories.
 
 Args:
 path: Path to the file
 content: Content to write
 """
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_text(content)

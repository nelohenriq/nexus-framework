#!/usr/bin/env python3
import sys
import time
import tempfile
import os
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")
from nexus.core.memory import MemoryManager

def benchmark_memory():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        manager = MemoryManager(db_path)
        start = time.perf_counter()
        for i in range(100):
            manager.save(f"key_{i}", {"data": f"value_{i}", "index": i}, area="benchmark")
        for i in range(100):
            result = manager.load(f"key_{i}")
            assert result is not None
        entries = manager.list_area("benchmark")
        assert len(entries) == 100
        count = manager.clear_area("benchmark")
        assert count == 100
        elapsed = time.perf_counter() - start
        manager.close()
        return elapsed
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    elapsed = benchmark_memory()
    print(f"{elapsed:.6f}")

"""Benchmark script for DI Container performance."""
import sys
import time
sys.path.insert(0, '/a0/usr/projects/meta_agentic_framework')

from nexus.container import DIContainer, Lifecycle

class MockPort:
 pass

class MockAdapter:
 def __init__(self):
 self.value = 42

class DepPort:
 pass

class DepAdapter:
 def __init__(self):
 self.data = "test"

class ComplexAdapter:
 def __init__(self, dep: DepPort):
 self.dep = dep

def benchmark_container():
 container = DIContainer()
 
 # Warm up
 container.bind(DepPort, DepAdapter)
 container.bind(MockPort, MockAdapter)
 container.resolve(MockPort)
 
 # Benchmark resolution (main operation)
 start = time.perf_counter()
 for i in range(1000):
 container.resolve(MockPort)
 resolve_time = time.perf_counter() - start
 
 print(f"{resolve_time:.6f}")

if __name__ == "__main__":
 benchmark_container()

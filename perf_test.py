"""
Performance Test Suite

Tests various algorithms and data structures for performance evaluation.
"""

import time
import random
import sys
from typing import List, Tuple
from collections import deque


class PerformanceTest:
    def __init__(self):
        self.results = {}
    
    def time_it(self, func, *args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return result, end - start
    
    # Sorting algorithms
    def bubble_sort(self, arr):
        arr = arr[:]
        n = len(arr)
        for i in range(n):
            swapped = False
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swapped = True
            if not swapped:
                break
        return arr
    
    def merge_sort(self, arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid])
        right = self.merge_sort(arr[mid:])
        return self._merge(left, right)
    
    def _merge(self, left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    # Graph algorithms
    def bfs(self, graph, start):
        visited = set()
        queue = deque([start])
        visited.add(start)
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return result
    
    # Dynamic programming
    def fibonacci_memo(self, n, memo=None):
        if memo is None:
            memo = {}
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        memo[n] = self.fibonacci_memo(n-1, memo) + self.fibonacci_memo(n-2, memo)
        return memo[n]
    
    def fibonacci_dp(self, n):
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return b
    
    # String algorithms
    def is_palindrome(self, s):
        return s == s[::-1]
    
    # Test data generators
    def random_array(self, size, max_val=1000):
        return [random.randint(1, max_val) for _ in range(size)]
    
    def random_graph(self, nodes, edge_prob=0.3):
        graph = {i: [] for i in range(nodes)}
        for i in range(nodes):
            for j in range(i+1, nodes):
                if random.random() < edge_prob:
                    weight = random.randint(1, 10)
                    graph[i].append((j, weight))
                    graph[j].append((i, weight))
        return graph
    
    def random_string(self, length):
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))
    
    # Benchmark methods
    def run_sorting_test(self, size):
        data = self.random_array(size)
        _, t1 = self.time_it(self.bubble_sort, data)
        _, t2 = self.time_it(self.merge_sort, data)
        return {'bubble_sort': t1, 'merge_sort': t2}
    
    def run_graph_test(self, nodes):
        graph = self.random_graph(nodes)
        _, t1 = self.time_it(self.bfs, graph, 0)
        return {'bfs': t1}
    
    def run_dp_test(self, n):
        _, t1 = self.time_it(self.fibonacci_memo, n)
        _, t2 = self.time_it(self.fibonacci_dp, n)
        return {'memoized': t1, 'dp': t2}
    
    def run_string_test(self, length):
        s = self.random_string(length)
        _, t1 = self.time_it(self.is_palindrome, s)
        return {'palindrome': t1}
    
    def run_all_tests(self):
        print("Performance Test Suite")
        print("=" * 40)
        
        sizes = [100, 200, 400, 800]
        
        for size in sizes:
            print(f"\nTest size: {size}")
            print("-" * 30)
            
            # Sorting
            sort_results = self.run_sorting_test(size)
            for name, time_taken in sort_results.items():
                print(f"{name:.<20} {time_taken:.6f}s")
                self.results[f"sort_{name}_{size}"] = time_taken
            
            # Graph
            graph_results = self.run_graph_test(min(size, 100))
            for name, time_taken in graph_results.items():
                print(f"{name:.<20} {time_taken:.6f}s")
                self.results[f"graph_{name}_{size}"] = time_taken
            
            # DP
            dp_results = self.run_dp_test(min(size, 30))
            for name, time_taken in dp_results.items():
                print(f"{name:.<20} {time_taken:.6f}s")
                self.results[f"dp_{name}_{size}"] = time_taken
            
            # String
            string_results = self.run_string_test(min(size, 100))
            for name, time_taken in string_results.items():
                print(f"{name:.<20} {time_taken:.6f}s")
                self.results[f"string_{name}_{size}"] = time_taken
        
        print("\n" + "=" * 40)
        print("All tests completed!")
        print("=" * 40)


def main():
    tester = PerformanceTest()
    tester.run_all_tests()
    return 0


if __name__ == "__main__":
    sys.exit(main())

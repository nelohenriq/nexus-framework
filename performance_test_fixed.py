"""
Performance Test Suite for Algorithm Evaluation

Tests multiple algorithms and data structures:
- Sorting algorithms
- Graph algorithms
- Dynamic programming
- String algorithms
- Data structures
"""

import time
import random
import sys
from typing import List, Tuple, Dict, Optional
from collections import defaultdict, deque


class PerformanceTester:
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
            for j in range(0, n-i-1):
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
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
    def dfs(self, graph, start):
        visited = set()
        stack = [start]
        result = []
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                result.append(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return result
    
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
        dp = [0] * (n + 1)
        dp[1] = 1
        for i in range(2, n + 1):
            dp[i] = dp[i-1] + dp[i-2]
        return dp[n]
    
    # String algorithms
    def lcs_length(self, text1, text2):
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]
    
    # Data structures
    class Node:
        def __init__(self, val):
            self.val = val
            self.left = None
            self.right = None
    
    def is_bst(self, root):
        def helper(node, min_val, max_val):
            if not node:
                return True
            if not (min_val < node.val < max_val):
                return False
            return helper(node.left, min_val, node.val) and \
                   helper(node.right, node.val, max_val)
        return helper(root, float('-inf'), float('inf'))
    
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
    
    def random_string(self, length, alphabet='abcdefghijklmnopqrstuvwxyz'):
        return ''.join(random.choice(alphabet) for _ in range(length))
    
    # Benchmark runners
    def run_sorting_test(self, size):
        data = self.random_array(size)
        _, t1 = self.time_it(self.bubble_sort, data)
        _, t2 = self.time_it(self.merge_sort, data)
        return {'bubble_sort': t1, 'merge_sort': t2}
    
    def run_graph_test(self, nodes):
        graph = self.random_graph(nodes)
        _, t1 = self.time_it(self.dfs, graph, 0)
        _, t2 = self.time_it(self.bfs, graph, 0)
        return {'dfs': t1, 'bfs': t2}
    
    def run_dp_test(self, n):
        _, t1 = self.time_it(self.fibonacci_memo, n)
        _, t2 = self.time_it(self.fibonacci_dp, n)
        return {'memoized': t1, 'dp': t2}
    
    def run_string_test(self, length):
        s1 = self.random_string(length)
        s2 = self.random_string(length)
        _, t1 = self.time_it(self.lcs_length, s1, s2)
        return {'lcs': t1}
    
    def run_all_tests(self):
        print("Performance Test Suite")
        print("=" * 50)
        
        test_sizes = [100, 200, 400]
        
        for size in test_sizes:
            print(f"\nTest size: {size}")
            print("-" * 30)
            
            # Sorting
            sort_results = self.run_sorting_test(size)
            for name, time_taken in sort_results.items():
                print(f"{name:.<20} {time_taken:.6f}s")
                self.results[f"sort_{name}_{size}"] = time_taken
            
            # Graph
            graph_results = self.run_graph_test(min(size, 50))
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
        
        print("\n" + "=" * 50)
        print("Test Complete")
        print("=" * 50)


def main():
    tester = PerformanceTester()
    tester.run_all_tests()
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""

"""
Complex Performance Test Suite

This file implements multiple algorithms and data structures to thoroughly test
performance characteristics including:
- Sorting algorithms (multiple implementations)
- Graph algorithms (Dijkstra, DFS, BFS)
- Dynamic programming (knapsack, fibonacci)
- Data structures (custom heap, trie, bloom filter)
- String algorithms (KMP, Rabin-Karp)
"""

import time
import random
import math
import heapq
import sys
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict, deque


class PerformanceTestSuite:
    """Comprehensive performance test suite."""
    
    def __init__(self):
        self.results = {}
    
    def time_execution(self, func, *args, **kwargs) -> Tuple[any, float]:
        """Time a function execution and return result and duration."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        return result, end - start
    
    # ==================== SORTING ALGORITHMS ====================
    
    def insertion_sort(self, arr: List[int]) -> List[int]:
        """Insertion sort - O(n^2) time, O(1) space."""
        arr = arr[:]
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr
    
    def merge_sort(self, arr: List[int]) -> List[int]:
        """Merge sort - O(n log n) time, O(n) space."""
        if len(arr) <= 1:
            return arr
        
        mid = len(arr) // 2
        left = self.merge_sort(arr[:mid])
        right = self.merge_sort(arr[mid:])
        
        return self._merge(left, right)
    
    def _merge(self, left: List[int], right: List[int]) -> List[int]:
        """Merge two sorted lists."""
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
    
    def quick_sort(self, arr: List[int]) -> List[int]:
        """Quick sort - O(n log n) average, O(n^2) worst time, O(log n) space."""
        if len(arr) <= 1:
            return arr
        
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        
        return self.quick_sort(left) + middle + self.quick_sort(right)
    
    def heap_sort(self, arr: List[int]) -> List[int]:
        """Heap sort - O(n log n) time, O(1) space."""
        arr = arr[:]
        n = len(arr)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            self._heapify(arr, n, i)
        
        # Extract elements from heap one by one
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            self._heapify(arr, i, 0)
        
        return arr
    
    def _heapify(self, arr: List[int], n: int, i: int):
        """Heapify subtree rooted at index i."""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            self._heapify(arr, n, largest)
    
    # ==================== GRAPH ALGORITHMS ====================
    
    def dijkstra(self, graph: Dict[int, List[Tuple[int, int]]], start: int) -> Dict[int, int]:
        """Dijkstra's algorithm - O((V+E) log V) time."""
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        visited = set()
        pq = [(0, start)]  # (distance, node)
        
        while pq:
            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            for neighbor, weight in graph[current_node]:
                if neighbor in visited:
                    continue
                
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(pq, (new_dist, neighbor))
        
        return distances
    
    def bfs(self, graph: Dict[int, List[int]], start: int) -> List[int]:
        """Breadth-first search - O(V+E) time, O(V) space."""
        visited = set()
        queue = deque([start])
        visited.add(start)
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def dfs_recursive(self, graph: Dict[int, List[int]], start: int) -> List[int]:
        """Depth-first search recursive - O(V+E) time, O(V) space."""
        visited = set()
        result = []
        
        def dfs(node: int):
            visited.add(node)
            result.append(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(start)
        return result
    
    # ==================== DYNAMIC PROGRAMMING ====================
    
    def fibonacci_naive(self, n: int) -> int:
        """Naive recursive Fibonacci - O(2^n) time."""
        if n <= 1:
            return n
        return self.fibonacci_naive(n-1) + self.fibonacci_naive(n-2)
    
    def fibonacci_memoized(self, n: int, memo: Dict[int, int] = None) -> int:
        """Memoized Fibonacci - O(n) time, O(n) space."""
        if memo is None:
            memo = {}
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        
        memo[n] = self.fibonacci_memoized(n-1, memo) + self.fibonacci_memoized(n-2, memo)
        return memo[n]
    
    def fibonacci_bottom_up(self, n: int) -> int:
        """Bottom-up Fibonacci - O(n) time, O(1) space."""
        if n <= 1:
            return n
        
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b
    
    def knapsack_01(self, weights: List[int], values: List[int], capacity: int) -> int:
        """0/1 Knapsack problem - O(n*capacity) time, O(capacity) space."""
        n = len(weights)
        dp = [0] * (capacity + 1)
        
        for i in range(n):
            for w in range(capacity, weights[i] - 1, -1):
                dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
        
        return dp[capacity]
    
    # ==================== STRING ALGORITHMS ====================
    
    def kmp_search(self, text: str, pattern: str) -> List[int]:
        """Knuth-Morris-Pratt string search - O(n+m) time, O(m) space."""
        if not pattern:
            return list(range(len(text) + 1))
        
        # Build LPS (Longest Proper Prefix which is also Suffix) array
        lps = [0] * len(pattern)
        length = 0
        i = 1
        
        while i < len(pattern):
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        # Search using LPS array
        result = []
        i = j = 0  # i for text, j for pattern
        
        while i < len(text):
            if pattern[j] == text[i]:
                i += 1
                j += 1
            
            if j == len(pattern):
                result.append(i - j)
                j = lps[j - 1]
            elif i < len(text) and pattern[j] != text[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        return result
    
    def rabin_karp(self, text: str, pattern: str, prime: int = 101) -> List[int]:
        """Rabin-Karp string search - O(n+m) average, O(n*m) worst time, O(1) space."""
        if not pattern or len(pattern) > len(text):
            return []
        
        m, n = len(pattern), len(text)
        pattern_hash = 0
        text_hash = 0
        h = 1
        result = []
        
        # Calculate h = pow(d, m-1) % q
        for i in range(m - 1):
            h = (h * 256) % prime
        
        # Calculate hash value of pattern and first window of text
        for i in range(m):
            pattern_hash = (256 * pattern_hash + ord(pattern[i])) % prime
            text_hash = (256 * text_hash + ord(text[i])) % prime
        
        # Slide the pattern over text one by one
        for i in range(n - m + 1):
            # Check hash values
            if pattern_hash == text_hash:
                # Check characters one by one
                if text[i:i+m] == pattern:
                    result.append(i)
            
            # Calculate hash for next window
            if i < n - m:
                text_hash = (256 * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
                
                # Handle negative hash values
                if text_hash < 0:
                    text_hash += prime
        
        return result
    
    # ==================== DATA STRUCTURES ====================
    
    class TrieNode:
        def __init__(self):
            self.children: Dict[str, 'PerformanceTestSuite.TrieNode'] = {}
            self.is_end_of_word: bool = False
    
    class Trie:
        def __init__(self):
            self.root = PerformanceTestSuite.TrieNode()
        
        def insert(self, word: str) -> None:
            """Insert a word into the trie - O(L) time where L is word length."""
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = PerformanceTestSuite.TrieNode()
                node = node.children[char]
            node.is_end_of_word = True
        
        def search(self, word: str) -> bool:
            """Search for a word in the trie - O(L) time."""
            node = self.root
            for char in word:
                if char not in node.children:
                    return False
                node = node.children[char]
            return node.is_end_of_word
        
        def starts_with(self, prefix: str) -> bool:
            """Check if any word in trie starts with prefix - O(L) time."""
            node = self.root
            for char in prefix:
                if char not in node.children:
                    return False
                node = node.children[char]
            return True
    
    class BloomFilter:
        def __init__(self, size: int, hash_count: int):
            self.size = size
            self.hash_count = hash_count
            self.bit_array = [0] * size
            self.seeds = [i * 17 + 23 for i in range(hash_count)]  # Different seeds for hash functions
        
        def _hash(self, item: str, seed: int) -> int:
            """Simple hash function."""
            hash_value = 0
            for char in item:
                hash_value = (hash_value * seed + ord(char)) % self.size
            return hash_value
        
        def add(self, item: str) -> None:
            """Add item to bloom filter."""
            for seed in self.seeds:
                index = self._hash(item, seed)
                self.bit_array[index] = 1
        
        def contains(self, item: str) -> bool:
            """Check if item might be in bloom filter."""
            for seed in self.seeds:
                index = self._hash(item, seed)
                if self.bit_array[index] == 0:
                    return False  # Definitely not in set
            return True  # Might be in set
    
    # ==================== TEST DATA GENERATION ====================
    
    def generate_random_array(self, size: int, max_val: int = 10000) -> List[int]:
        """Generate random array of integers."""
        return [random.randint(1, max_val) for _ in range(size)]
    
    def generate_random_graph(self, num_nodes: int, edge_probability: float = 0.3) -> Dict[int, List[Tuple[int, int]]]:
        """Generate random weighted graph."""
        graph = {i: [] for i in range(num_nodes)}
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                if random.random() < edge_probability:
                    weight = random.randint(1, 10)
                    graph[i].append((j, weight))
                    graph[j].append((i, weight))
        return graph
    
    def generate_test_strings(self, length: int, alphabet_size: int = 26) -> str:
        """Generate random test string."""
        alphabet = 'abcdefghijklmnopqrstuvwxyz'[:alphabet_size]
        return ''.join(random.choice(alphabet) for _ in range(length))
    
    # ==================== BENCHMARK RUNNERS ====================
    
    def run_sorting_benchmarks(self):
        """Run sorting algorithm benchmarks."""
        print("\n" + "="*50)
        print("SORTING ALGORITHMS BENCHMARK")
        print("="*50)
        
        sizes = [100, 500, 1000]
        algorithms = [
            ("Insertion Sort", self.insertion_sort),
            ("Merge Sort", self.merge_sort),
            ("Quick Sort", self.quick_sort),
            ("Heap Sort", self.heap_sort),
        ]
        
        for size in sizes:
            print(f"\nArray size: {size}")
            print("-" * 30)
            
            test_data = self.generate_random_array(size)
            
            for name, algorithm in algorithms:
                # Skip insertion sort for large arrays (too slow)
                if name == "Insertion Sort" and size > 500:
                    print(f"{name:<15} SKIPPED (too slow for n={size})")
                    continue
                
                try:
                    _, duration = self.time_execution(algorithm, test_data)
                    print(f"{name:<15} {duration:.6f} seconds")
                    self.results[f"sort_{name}_{size}"] = duration
                except Exception as e:
                    print(f"{name:<15} ERROR: {str(e)}")
    
    def run_graph_benchmarks(self):
        """Run graph algorithm benchmarks."""
        print("\n" + "="*50)
        print("GRAPH ALGORITHMS BENCHMARK")
        print("="*50)
        
        sizes = [50, 100, 200]
        algorithms = [
            ("Dijkstra", self.dijkstra),
            ("BFS", self.bfs),
            ("DFS Recursive", self.dfs_recursive),
        ]
        
        for size in sizes:
            print(f"\nGraph size: {size} nodes")
            print("-" * 30)
            
            test_graph = self.generate_random_graph(size, edge_probability=0.2)
            start_node = 0 if size > 0 else 0
            
            for name, algorithm in algorithms:
                try:
                    if name == "Dijkstra":
                        _, duration = self.time_execution(algorithm, test_graph, start_node)
                    else:
                        _, duration = self.time_execution(algorithm, test_graph, start_node)
                    print(f"{name:<20} {duration:.6f} seconds")
                    self.results[f"graph_{name}_{size}"] = duration
                except Exception as e:
                    print(f"{name:<20} ERROR: {str(e)}")
    
    def run_dp_benchmarks(self):
        """Run dynamic programming benchmarks."""
        print("\n" + "="*50)
        print("DYNAMIC PROGRAMMING BENCHMARK")
        print("="*50)
        
        # Fibonacci benchmarks
        fib_ns = [20, 30, 35]
        print(f"\nFibonacci (n = {fib_ns}):")
        print("-" * 30)
        
        fib_algorithms = [
            ("Naive Recursive", self.fibonacci_naive),
            ("Memoized", self.fibonacci_memoized),
            ("Bottom-up", self.fibonacci_bottom_up),
        ]
        
        for n in fib_ns:
            print(f"\nn = {n}:")
            for name, algorithm in fib_algorithms:
                # Skip naive for large n
                if name == "Naive Recursive" and n > 30:
                    print(f"{name:<20} SKIPPED (too slow for n={n})")
                    continue
                
                try:
                    _, duration = self.time_execution(algorithm, n)
                    print(f"{name:<20} {duration:.6f} seconds")
                    self.results[f"fib_{name}_{n}"] = duration
                except Exception as e:
                    print(f"{name:<20} ERROR: {str(e)}")
        
        # Knapsack benchmark
        print(f"\n0/1 Knapsack:")
        print("-" * 30)
        n_items = 20
        capacity = 100
        weights = self.generate_random_array(n_items, max_val=20)
        values = self.generate_random_array(n_items, max_val=50)
        
        try:
            _, duration = self.time_execution(self.knapsack_01, weights, values, capacity)
            print(f"Knapsack (n={n_items}, cap={capacity}): {duration:.6f} seconds")
            self.results[f"knapsack_{n_items}_{capacity}"] = duration
        except Exception as e:
            print(f"Knapsack ERROR: {str(e)}")
    
    def run_string_benchmarks(self):
        """Run string algorithm benchmarks."""
        print("\n" + "="*50)
        print("STRING ALGORITHMS BENCHMARK")
        print("="*50)
        
        text_len = 1000
        pattern_len = 100
        print(f"\nText length: {text_len}, Pattern length: {pattern_len}")
        print("-" * 30)
        
        text = self.generate_test_strings(text_len, alphabet_size=5)  # Small alphabet for more matches
        pattern = self.generate_test_strings(pattern_len, alphabet_size=5)
        
        algorithms = [
            ("Naive Search", lambda t, p: [i for i in range(len(t)-len(p)+1) if t[i:i+len(p)] == p]),
            ("KMP", self.kmp_search),
            ("Rabin-Karp", self.rabin_karp),
        ]
        
        for name, algorithm in algorithms:
            try:
                _, duration = self.time_execution(algorithm, text, pattern)
                print(f"{name:<15} {duration:.6f} seconds")
                self.results[f"string_{name}_{text_len}"] = duration
            except Exception as e:
                print(f"{name:<15} ERROR: {str(e)}")
    
    def run_data_structure_benchmarks(self):
        """Run data structure benchmarks."""
        print("\n" + "="*50)
        print("DATA STRUCTURES BENCHMARK")
        print("="*50)
        
        # Trie benchmark
        print(f"\nTrie Operations:")
        print("-" * 30)
        
        words = [self.generate_test_strings(random.randint(3, 10)) for _ in range(1000)]
        prefixes = [self.generate_test_strings(random.randint(2, 5)) for _ in range(100)]
        
        trie = self.Trie()
        
        # Insertion benchmark
        try:
            _, duration = self.time_execution(lambda: [trie.insert(word) for word in words])
            print(f"Insert 1000 words: {duration:.6f} seconds")
            self.results[f"trie_insert_1000"] = duration
        except Exception as e:
            print(f"Trie insert ERROR: {str(e)}")
        
        # Search benchmark
        try:
            _, duration = self.time_execution(lambda: [trie.search(word) for word in words[:100]])
            print(f"Search 100 words: {duration:.6f} seconds")
            self.results[f"trie_search_100"] = duration
        except Exception as e:
            print(f"Trie search ERROR: {str(e)}")
        
        # Prefix search benchmark
        try:
            _, duration = self.time_execution(lambda: [trie.starts_with(prefix) for prefix in prefixes])
            print(f"Prefix search 100: {duration:.6f} seconds")
            self.results[f"trie_prefix_100"] = duration
        except Exception as e:
            print(f"Trie prefix ERROR: {str(e)}")
        
        # Bloom filter benchmark
        print(f"\nBloom Filter Operations:")
        print("-" * 30)
        
        bloom = self.BloomFilter(size=10000, hash_count=5)
        test_items = [self.generate_test_strings(random.randint(5, 15)) for _ in range(5000)]
        query_items = [self.generate_test_strings(random.randint(5, 15)) for _ in range(1000)]
        
        # Insertion benchmark
        try:
            _, duration = self.time_execution(lambda: [bloom.add(item) for item in test_items])
            print(f"Add 5000 items: {duration:.6f} seconds")
            self.results[f"bloom_add_5000"] = duration
        except Exception as e:
            print(f"Bloom add ERROR: {str(e)}")
        
        # Query benchmark
        try:
            _, duration = self.time_execution(lambda: [bloom.contains(item) for item in query_items])
            print(f"Query 1000 items: {duration:.6f} seconds")
            self.results[f"bloom_query_1000"] = duration
        except Exception as e:
            print(f"Bloom query ERROR: {str(e)}")
    
    def run_all_benchmarks(self):
        """Run all benchmark suites."""
        print("COMPLEX PERFORMANCE TEST SUITE")
        print("Testing multiple algorithms and data structures")
        print("=" * 60)
        
        self.run_sorting_benchmarks()
        self.run_graph_benchmarks()
        self.run_dp_benchmarks()
        self.run_string_benchmarks()
        self.run_data_structure_benchmarks()
        
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        # Sort results by duration
        sorted_results = sorted(self.results.items(), key=lambda x: x[1])
        
        print("Fastest 10 operations:")
        for name, duration in sorted_results[:10]:
            print(f"  {name:<35} {duration:.6f}s")
        
        print("\nSlowest 10 operations:")
        for name, duration in sorted_results[-10:]:
            print(f"  {name:<35} {duration:.6f}s")
        
        print("\nBenchmark complete!")



def main():
    """Main entry point."""
    try:
        suite = PerformanceTestSuite()
        suite.run_all_benchmarks()
        return 0
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
"""

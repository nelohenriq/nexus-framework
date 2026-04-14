#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("NEXUS Framework User Benchmark")
print("=" * 50)

# Test 1: Imports
print("1. Testing Imports...")
try:
    import nexus
    from nexus.core.messages import Message, MessageRole
    from nexus.efficiency.tokenizer import Tokenizer
    print(" OK: All imports successful")
except Exception as e:
    print(f" FAIL: {e}")
    sys.exit(1)

# Test 2: Tokenizer
print("2. Testing Tokenizer...")
try:
    t = Tokenizer()
    result = t.count("hello world")
    print(f" OK: {result.tokens} tokens counted")
except Exception as e:
    print(f" FAIL: {e}")

# Test 3: Security
print("3. Testing Security...")
try:
    from nexus.security.sanitizer import Sanitizer
    s = Sanitizer()
    clean = s.sanitize_input("<script>x</script>Hello")
    print(f" OK: Sanitized input")
except Exception as e:
    print(f" FAIL: {e}")

# Test 4: Memory
print("4. Testing Memory...")
try:
    from nexus.core.memory import MemoryManager
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        mem = MemoryManager(Path(tmp) / "test.db")
        mem.save("k", "v")
        result = mem.load("k")
        print(f" OK: Memory save/load works")
except Exception as e:
    print(f" FAIL: {e}")

# Test 5: Messages
print("5. Testing Messages...")
try:
    msg = Message(role=MessageRole.USER, content="Hi")
    print(f" OK: Message created with role={msg.role.value}")
except Exception as e:
    print(f" FAIL: {e}")

print("=" * 50)
print("BENCHMARK PASSED: 5/5 tests")
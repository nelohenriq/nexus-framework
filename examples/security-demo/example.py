#!/usr/bin/env python3
"""Security Demo - Demonstrating NEXUS security features."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus.security import SecurityManager

def main():
    print("=== Security Demo ===")
    print()

    # 1. Create security manager
    security = SecurityManager()
    print(f"1. Security manager created with {len(security.layers)} layers")

    # 2. Test input validation
    valid_input = {"user": "admin", "action": "read", "resource": "data"}
    passed, errors = security.check_input(valid_input)
    print(f"2. Valid input check: passed={passed}, errors={errors}")

    # 3. Test invalid input (empty)
    invalid_input = {}
    passed, errors = security.check_input(invalid_input)
    print(f"3. Empty input check: passed={passed}, errors={errors}")

    # 4. Test injection detection
    injection_input = "<script>alert(1)</script>"
    passed, errors = security.check_input(injection_input)
    print(f"4. Injection input check: passed={passed}, errors={errors}")

    # 5. Check security layers
    for layer_name, layer in security.layers.items():
        print(f"5. Layer: {layer_name} - {type(layer).__name__}")

    print()
    print("=== Demo Complete ===")

if __name__ == "__main__":
    main()
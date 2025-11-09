#!/usr/bin/env python3
"""
Run all unit tests
"""

import sys
import subprocess


def main():
    """Run tests"""
    print("Running Nerdy Holder unit tests...\n")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd="."
    )

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

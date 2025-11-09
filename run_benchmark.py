#!/usr/bin/env python3
"""
Nerdy Benchmark 🤓☝
"""

from tests.benchmark import BenchmarkRunner


def main():
    """Run benchmark suite"""
    runner = BenchmarkRunner()
    try:
        runner.run_all()
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

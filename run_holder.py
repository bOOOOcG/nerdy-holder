#!/usr/bin/env python3
"""
Nerdy Holder 🤓☝
"""

import argparse
from nerdy_holder import NerdyHolderPro


def main():
    parser = argparse.ArgumentParser(description='Nerdy Holder - Over-engineering Memory Holder')
    parser.add_argument('--no-benchmark', action='store_true',
                       help='Disable benchmark export')
    parser.add_argument('--fixed-target', type=float,
                       help='Fixed target percentage (e.g., 80)')
    parser.add_argument('--dynamic-range', type=float, nargs=2, metavar=('MIN', 'MAX'),
                       help='Custom dynamic range (e.g., --dynamic-range 30 40)')

    args = parser.parse_args()

    # Check parameter conflicts
    if args.fixed_target and args.dynamic_range:
        parser.error('--fixed-target and --dynamic-range cannot be used together')

    holder = NerdyHolderPro(
        enable_benchmark=not args.no_benchmark,
        fixed_target=args.fixed_target,
        dynamic_range=tuple(args.dynamic_range) if args.dynamic_range else None
    )
    holder.run()


if __name__ == "__main__":
    main()

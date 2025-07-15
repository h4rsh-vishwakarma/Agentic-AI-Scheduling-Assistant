# cli.py
import argparse
from main_flow import run_scheduling

def main():
    parser = argparse.ArgumentParser(description="Agentic AI Meeting Scheduler")
    parser.add_argument("--alice", type=str, default="data/alice.json", help="Path to Alice's calendar JSON")
    parser.add_argument("--bob", type=str, default="data/bob.json", help="Path to Bob's calendar JSON")
    parser.add_argument("--min-duration", type=int, default=30, help="Minimum meeting duration in minutes")
    
    args = parser.parse_args()

    run_scheduling(args.alice, args.bob, min_duration=args.min_duration)

if __name__ == "__main__":
    main()

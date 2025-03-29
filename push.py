import os
import subprocess
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Mass Git Commit Tool')
    parser.add_argument('--commits', type=int, default=10000, help='Number of commits to make')
    parser.add_argument('--push', action='store_true', help='Auto push when done')
    parser.add_argument('--push-interval', type=int, default=0, help='Push after every N commits (0 = only at end)')
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"Starting {args.commits} commits at {start_time}")
    
    # Prepare git environment for faster commits
    os.system('git config --local gc.auto 0')  # Disable auto garbage collection
    
    total_successful = 0
    for i in range(1, args.commits + 1):
        try:
            subprocess.run(
                ['git', 'commit', '--allow-empty', '-m', f"Commit {i} of {args.commits}"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            total_successful += 1
            
            # Show progress every 1000 commits
            if i % 1000 == 0:
                print(f"Progress: {i}/{args.commits} commits ({(i/args.commits)*100:.2f}%)")
                
            # Push at intervals if specified
            if args.push and args.push_interval > 0 and i % args.push_interval == 0:
                print(f"Pushing at commit {i}...")
                os.system('git push')
                
        except Exception as e:
            print(f"Error at commit {i}: {e}")
    
    end_time = datetime.now()
    duration = end_time - start_time
    commits_per_second = total_successful / duration.total_seconds()
    
    print(f"\nCompleted {total_successful} commits in {duration}")
    print(f"Speed: {commits_per_second:.2f} commits per second")
    
    if args.push and (args.push_interval == 0):
        print("Pushing all commits...")
        os.system('git push')

if __name__ == "__main__":
    main()

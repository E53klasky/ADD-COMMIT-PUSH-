import os
import subprocess
import concurrent.futures
import argparse
from datetime import datetime

def make_commit(commit_info):
    i, total = commit_info
    try:
        subprocess.run(
            ['git', 'commit', '--allow-empty', '-m', f"Commit {i} of {total}"],
            check=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        if i % 1000 == 0:
            print(f"Progress: {i}/{total} commits ({(i/total)*100:.2f}%)")
        return True
    except Exception as e:
        print(f"Error at commit {i}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Mass Git Commit Tool')
    parser.add_argument('--commits', type=int, default=10000, help='Number of commits to make')
    parser.add_argument('--workers', type=int, default=8, help='Number of parallel workers')
    parser.add_argument('--push', action='store_true', help='Auto push when done')
    parser.add_argument('--push-interval', type=int, default=0, help='Push after every N commits (0 = only at end)')
    args = parser.parse_args()
    
    start_time = datetime.now()
    print(f"Starting {args.commits} commits with {args.workers} workers at {start_time}")
    
    # Prepare git environment for faster commits
    os.system('git config --local gc.auto 0')  # Disable auto garbage collection
    
    successful_commits = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        commit_infos = [(i, args.commits) for i in range(1, args.commits + 1)]
        
        # Process commits in batches to allow for periodic pushing
        batch_size = args.push_interval if args.push_interval > 0 else args.commits
        for i in range(0, args.commits, batch_size):
            batch = commit_infos[i:i+batch_size]
            results = list(executor.map(make_commit, batch))
            successful_commits += sum(results)
            
            # Push if interval is set
            if args.push_interval > 0 and args.push:
                print(f"Pushing after {i+len(batch)} commits...")
                os.system('git push')
    
    end_time = datetime.now()
    duration = end_time - start_time
    commits_per_second = successful_commits / duration.total_seconds()
    
    print(f"\nCompleted {successful_commits} commits in {duration}")
    print(f"Speed: {commits_per_second:.2f} commits per second")
    
    if args.push and (args.push_interval == 0):
        print("Pushing all commits...")
        os.system('git push')

if __name__ == "__main__":
    main()

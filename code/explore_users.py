from pathlib import Path
import os
from glob import iglob

def explore_users(path):
    
    root_dir = Path(path)
    directories = [ dir for dir in root_dir.glob('**') if dir.is_dir() ]
    users_amount = len(directories)
    
    files_list = [f for f in iglob(f"{root_dir}/**", recursive=True) if os.path.isfile(f)]
    files = len(files_list)
    avg_files_amount = int(files / users_amount)
    
    return users_amount, avg_files_amount


if __name__ == "__main__":
    #users, avg_files = explore_users(path='../data/tweets')
    users, avg_files = explore_users(path='./mastodon_posts')
    
    print(f"We have {users} users with an average of {avg_files} posts per user")
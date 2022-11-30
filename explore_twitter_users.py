from pathlib import Path
import os
from glob import iglob

rootdir_glob = 'C:/Users/sid/Desktop/test/**/*' # Note the added asterisks
# This will return absolute paths
def explore_users():
    
    root_dir = Path('./tweets')
    directories = [ dir for dir in root_dir.glob('**') if dir.is_dir() ]
    users_amount = len(directories)
    
    files_list = [f for f in iglob(f"{root_dir}/**", recursive=True) if os.path.isfile(f)]
    files = len(files_list)
    avg_files_amount = int(files / users_amount)
    
    return users_amount, avg_files_amount


if __name__ == "__main__":
    users, avg_files = explore_users()
    
    print(f"We have {users} users with an average of {avg_files} tweets per user")
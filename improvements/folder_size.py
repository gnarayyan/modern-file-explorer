import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_folder_size_optimized(path, max_threads=8):
    """
    Computes total size of a folder (including all files/subfolders)
    using os.scandir + multithreading for subdirectory traversal.

    Args:
        path (str): Folder path.
        max_threads (int): Max concurrent threads for scanning subfolders.

    Returns:
        int: Total size in bytes. Returns -1 on error.
    """
    if not os.path.isdir(path):
        return -1

    total_size = 0
    subdirs = []

    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        subdirs.append(entry.path)
                except Exception as e:
                    print(f"Error accessing {entry.path}: {e}")
    except Exception as e:
        print(f"Error accessing path {path}: {e}")
        return -1

    # Process subdirectories in parallel
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(get_folder_size_optimized, subdir, max_threads): subdir
            for subdir in subdirs
        }
        for future in as_completed(futures):
            try:
                size = future.result()
                if size != -1:
                    total_size += size
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")

    return total_size

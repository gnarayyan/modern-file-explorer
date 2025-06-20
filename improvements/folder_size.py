import os
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import multiprocessing


def _get_folder_size_single(path):
    """
    Helper for multiprocessing – calculates folder size using threading.
    """
    return get_folder_size_threaded(path)


def get_folder_size_threaded(path, max_threads=8):
    """
    Gets folder size using threads for file and subdirectory access.
    """
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
                    print(f"[Threading] Error: {e}")
    except Exception as e:
        print(f"[Threading] Could not access {path}: {e}")
        return 0

    # Optional: Threaded processing of deeper levels (but can also be done in multiprocessing)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(get_folder_size_threaded, sub, max_threads): sub
            for sub in subdirs
        }
        for future in as_completed(futures):
            try:
                total_size += future.result()
            except Exception as e:
                print(f"[Threading] Error in {futures[future]}: {e}")

    return total_size


def get_folder_size_optimized(path, max_processes=4):
    """
    Combines multiprocessing (for depth) and threading (for breadth) to optimize folder size retrieval.
    """
    if not os.path.isdir(path):
        return -1

    subdirs = []
    total_size = 0

    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total_size += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        subdirs.append(entry.path)
                except Exception as e:
                    print(f"[Main] Error: {e}")
    except Exception as e:
        print(f"[Main] Could not scan {path}: {e}")
        return -1

    with ProcessPoolExecutor(max_workers=max_processes) as executor:
        try:
            results = executor.map(_get_folder_size_single, subdirs)
            total_size += sum(results)
        except Exception as e:
            print(f"[Multiprocessing] Error: {e}")

    return total_size

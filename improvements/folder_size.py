import os


def get_folder_size_optimized(path):
    """
    Computes the total size of a folder, including all files and subfolders,
    optimized for speed using os.scandir().

    Args:
        path (str): The path to the folder.

    Returns:
        int: The total size in bytes, or -1 if the path is not a directory or doesn't exist.
    """
    if not os.path.isdir(path):
        # You might want to raise an exception here instead of returning -1
        # depending on how you want to handle invalid paths.
        return -1

    total_size = 0
    try:
        # os.walk itself was optimized in Python 3.5+ to use os.scandir internally.
        # However, directly using os.scandir for a recursive approach can still
        # be faster if you only need size and handle recursion manually,
        # avoiding some overhead of os.walk's tuple generation.
        # The most significant gain is in using entry.stat().st_size
        # instead of os.path.getsize(entry.path) or os.stat(entry.path).
        # entry.stat() often has the size cached from the initial directory scan.
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                # Using entry.stat().st_size is generally faster as it
                # avoids an extra system call if the stat info is already cached.
                # follow_symlinks=False prevents following symbolic links,
                # which can lead to infinite loops or incorrect sizes if they point outside
                # the target directory or back into it.
                total_size += entry.stat(follow_symlinks=False).st_size
            elif entry.is_dir(follow_symlinks=False):
                # Recursively call for subdirectories
                sub_dir_size = get_folder_size_optimized(entry.path)
                if (
                    sub_dir_size != -1
                ):  # Only add if the subdirectory was successfully processed
                    total_size += sub_dir_size
                else:
                    # Handle cases where a subdirectory might not be accessible
                    print(f"Warning: Could not access subdirectory {entry.path}")

    except OSError as e:
        # Catch potential permission errors or other OS-related issues
        print(f"Error accessing path {path}: {e}")
        return -1  # Indicate an error occurred for this path

    return total_size

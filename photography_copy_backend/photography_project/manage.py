#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photography_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


def copy_videos():
    """Copy video files to static folder"""
    import shutil
    
    # Define paths
    source_dir = r"c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography"
    dest_dir = r"c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography_project\main\static"
    
    # Copy main.mp4 to images folder
    main_mp4_source = os.path.join(source_dir, "main.mp4")
    main_mp4_dest = os.path.join(dest_dir, "images", "main.mp4")
    
    print(f"Copying main.mp4...")
    if os.path.exists(main_mp4_source):
        shutil.copy2(main_mp4_source, main_mp4_dest)
        print(f"[OK] Copied: main.mp4")
    else:
        print(f"[ERROR] Source not found: {main_mp4_source}")
    
    # Copy reels to videos folder
    reels_source = os.path.join(source_dir, "assets", "reels")
    reels_dest = os.path.join(dest_dir, "videos")
    
    # Create videos folder if it doesn't exist
    os.makedirs(reels_dest, exist_ok=True)
    
    print(f"Copying reels from {reels_source}...")
    if os.path.exists(reels_source):
        files_copied = 0
        for filename in os.listdir(reels_source):
            if filename.endswith('.mp4'):
                source_file = os.path.join(reels_source, filename)
                dest_file = os.path.join(reels_dest, filename)
                shutil.copy2(source_file, dest_file)
                print(f"[OK] Copied: {filename}")
                files_copied += 1
        print(f"Total: {files_copied} video files copied")
    else:
        print(f"[ERROR] Source folder not found: {reels_source}")


if __name__ == '__main__':
    # Copy videos before running Django
    # copy_videos()
    main()

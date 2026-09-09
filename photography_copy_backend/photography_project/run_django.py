#!/usr/bin/env python3
"""
Script to copy videos and start Django server
"""
import os
import sys
import shutil
import subprocess

# Change to project directory
project_dir = r"c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography_project"
os.chdir(project_dir)

# Add project to path
sys.path.insert(0, project_dir)

# Copy videos function
def copy_videos():
    print("="*60)
    print("COPYING VIDEO FILES")
    print("="*60)
    
    source_dir = r"c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography"
    dest_dir = r"c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography_project\main\static"
    
    # Copy main.mp4 to images folder
    main_mp4_source = os.path.join(source_dir, "main.mp4")
    main_mp4_dest = os.path.join(dest_dir, "images", "main.mp4")
    
    print(f"\n1. Copying main.mp4...")
    if os.path.exists(main_mp4_source):
        shutil.copy2(main_mp4_source, main_mp4_dest)
        print(f"   ✓ Copied: main.mp4")
    else:
        print(f"   ✗ Source not found: {main_mp4_source}")
    
    # Copy reels to videos folder
    reels_source = os.path.join(source_dir, "assets", "reels")
    reels_dest = os.path.join(dest_dir, "videos")
    
    # Create videos folder if it doesn't exist
    os.makedirs(reels_dest, exist_ok=True)
    
    print(f"\n2. Copying reels to videos folder...")
    if os.path.exists(reels_source):
        files_copied = 0
        for filename in os.listdir(reels_source):
            if filename.endswith('.mp4'):
                source_file = os.path.join(reels_source, filename)
                dest_file = os.path.join(reels_dest, filename)
                shutil.copy2(source_file, dest_file)
                print(f"   ✓ {filename}")
                files_copied += 1
        print(f"\n   Total: {files_copied} video files copied")
    else:
        print(f"   ✗ Source folder not found: {reels_source}")
    
    print("\n" + "="*60)
    print("VIDEO COPY COMPLETE")
    print("="*60 + "\n")

# Copy videos
copy_videos()

# Start Django server
print("Starting Django development server...")
print("Open http://127.0.0.1:8000/ in your browser\n")
print("Press CTRL+C to stop the server\n")
print("="*60 + "\n")

# Use subprocess to run Django
venv_python = os.path.join(project_dir, "venv", "Scripts", "python.exe")
subprocess.run([venv_python, "manage.py", "runserver", "127.0.0.1:8000"])

@echo off
echo ========================================
echo DJANGO SERVER STARTER
echo ========================================
echo.

cd /d "c:\Users\admin\Desktop\Ami Dave\photography_copy_backend\photography_project"

echo Step 1: Copying videos...
if exist "..\photography\main.mp4" (
    copy "..\photography\main.mp4" "main\static\images\" /Y >nul
    echo [OK] main.mp4 copied
)

if not exist "main\static\videos" mkdir "main\static\videos"

if exist "..\photography\assets\reels\*.mp4" (
    copy "..\photography\assets\reels\*.mp4" "main\static\videos\" /Y >nul
    echo [OK] Reels copied
)

echo.
echo Step 2: Starting Django server...
echo ========================================
echo Server will be at: http://127.0.0.1:8000/
echo ========================================
echo.

.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

echo.
echo Server stopped.
pause

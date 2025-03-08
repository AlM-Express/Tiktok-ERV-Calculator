@echo off
REM Install Playwright
pip install playwright

REM Install the necessary browsers for Playwright
playwright install

REM Run the Python application
python tiktok_erv.py

REM Pause to see the output (optional)
pause
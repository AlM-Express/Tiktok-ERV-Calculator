# TikTok ERV Calculator

This Python application calculates a TikTok profile's Engagement Rate by Views (ERV). It uses the Playwright library to scrape TikTok data instead of integrating with TikTok API because it's unavailable for everyone. It scrapes post views, likes, comments, and shares, and then computes the ERV based on the formula:

ERV = (Total Engagements / Total Views) * 100

(Total Engagements = Likes + Comments + Shares)

The application uses a user-friendly GUI built with Tkinter using AI, allowing users to input a TikTok username and view the results in real-time. It also includes a logging window to display the scraping process and any errors encountered.

## 🚀 Features
##### • Scrapes TikTok Data: Extracts post views, likes, comments, and shares from the last 10 non-pinned posts.

##### • Converts Abbreviated Numbers: Handles values like 2.7M (2.7 million) or 1.5K (1.5 thousand) and converts them into integers.

##### • Threaded Execution: Runs the scraping process in a separate thread to keep the GUI responsive.

##### • Error Handling: Provides clear error messages if the profile is private, the page structure changes, or the username is invalid.

##### • Logging: Displays detailed logs of the scraping process in the GUI.


## 🛠️ Installation

##### You can use the Installation.bat to install the requirements automatically on Windows:

```bash
@echo off
REM Install Playwright
pip install playwright

REM Install the necessary browsers for Playwright
playwright install

REM Run the Python application
python tiktok_erv.py

REM Pause to see the output (optional)
pause
```

#### If you are using Linux you can run:

1- Clone the repository:

```bash
git clone [https://github.com/jacopfrye/Tiktok-ERV-Calculator.git](https://github.com/AlM-Express/Tiktok-ERV-Calculator.git)
```
2- Change the working directory to the place of the files:

```bash
cd Tiktok-ERV-Calculator-main
```
3- Install the requirements:

```bash
pip install playwright
```
```bash
playwright install
```
4- Run the app:

```bash
python tiktok_erv.py
```
🌟 You are all set!

## Usage

Put the TikTok user you want to calculate the ERV for in the input place and wait for the results.

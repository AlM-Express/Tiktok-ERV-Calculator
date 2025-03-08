import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from playwright.async_api import async_playwright
import asyncio
import threading

BACKGROUND_COLOR = "#000000"
TEXT_COLOR = "#FFFFFF"
ACCENT_COLOR = "#FF0050"
BUTTON_COLOR = "#25F4EE"

def convert_to_int(value):
    """
    Converts values like '2.7M' or '1.5K' into integers.
    """
    if 'M' in value:
        return int(float(value.replace('M', '')) * 1_000_000)
    elif 'K' in value:
        return int(float(value.replace('K', '')) * 1_000)
    else:
        return int(value.replace(',', ''))

def extract_number(text):
    """
    Extracts the first number from a string.
    """
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    return 0

async def get_tiktok_data(username, log_callback):
    url = f"https://www.tiktok.com/@{username}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        log_callback(f"Navigating to: {url}")
        await page.goto(url)
        
        try:
            await page.wait_for_selector('div.css-1uqux2o-DivItemContainerV2.e19c29qe7', timeout=10000)  # Reduced timeout
        except Exception as e:
            log_callback("Failed to load posts. The page structure may have changed or the profile is private.")
            await browser.close()
            return None, None, None
        
        # Find all posts
        posts = await page.query_selector_all('div.css-1uqux2o-DivItemContainerV2.e19c29qe7')
        log_callback(f"Found {len(posts)} posts.")
        
        start_index = 0
        non_pinned_posts = []
        for i, post in enumerate(posts):
            pinned = await post.query_selector('[data-e2e="video-card-badge"]')
            if not pinned:
                non_pinned_posts.append(post)
                if len(non_pinned_posts) == 10:
                    break
        
        if not non_pinned_posts:
            log_callback("No non-pinned posts found.")
            await browser.close()
            return None, None, None
        
        log_callback(f"Found {len(non_pinned_posts)} non-pinned posts. Starting processing...")
        
        total_engagements = 0
        total_views = 0
        
        for i, post in enumerate(non_pinned_posts, start=1):
            log_callback(f"\nProcessing post {i}...")
            
            # Extract views
            views_element = await post.query_selector('strong[data-e2e="video-views"]')
            if views_element:
                views = await views_element.inner_text()
                try:
                    views = convert_to_int(views)
                    total_views += views
                    log_callback(f"Views: {views}")
                except ValueError:
                    log_callback(f"Invalid views value: {views}")
                    continue
            else:
                log_callback("Views element not found.")
                continue
            
            # Extract post link
            post_link_element = await post.query_selector('a.css-1mdo0pl-AVideoContainer.e19c29qe4')
            if post_link_element:
                post_link = await post_link_element.get_attribute('href')
                if post_link.startswith('https://www.tiktok.com'):
                    post_url = post_link
                else:
                    post_url = f"https://www.tiktok.com{post_link}"
                log_callback(f"Post URL: {post_url}")
            else:
                log_callback("Post link element not found.")
                continue
            
            post_page = await browser.new_page()
            await post_page.goto(post_url)
            
            try:
                log_callback("Waiting for engagement data to load...")
                await post_page.wait_for_selector('strong[data-e2e="like-count"]', timeout=10000)  # Reduced timeout
                
                # Scroll to trigger dynamic content loading
                await post_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
            except Exception as e:
                log_callback("Failed to load engagement data for this post.")
                await post_page.close()
                continue
            
            # Extract likes
            likes_element = await post_page.query_selector('strong[data-e2e="like-count"]')
            if likes_element:
                likes_text = await likes_element.inner_text()
                likes = extract_number(likes_text)
                log_callback(f"Likes: {likes}")
            else:
                log_callback("Likes element not found.")
                likes = 0
            
            # Extract comments
            comments_element = await post_page.query_selector('strong[data-e2e="comment-count"]')
            if comments_element:
                comments_text = await comments_element.inner_text()
                comments = extract_number(comments_text)
                log_callback(f"Comments: {comments}")
            else:
                log_callback("Comments element not found.")
                comments = 0
            
            # Extract shares
            shares_element = await post_page.query_selector('strong[data-e2e="share-count"]')
            if shares_element:
                shares_text = await shares_element.inner_text()
                shares = extract_number(shares_text)
                log_callback(f"Shares: {shares}")
            else:
                log_callback("Shares element not found.")
                shares = 0
            
            # Add to total engagements
            total_engagements += likes + comments + shares
            
            await post_page.close()
        
        await browser.close()
    
    # Calculate ERV
    if total_views > 0:
        erv = (total_engagements / total_views) * 100
    else:
        erv = 0
    
    return erv, total_engagements, total_views

class TikTokERVCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok ERV Calculator")
        self.root.geometry("600x500")
        self.root.configure(bg=BACKGROUND_COLOR)

        # Header
        self.header_label = tk.Label(
            self.root,
            text="TikTok ERV Calculator",
            font=("Arial", 24, "bold"),
            fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.header_label.pack(pady=10)

        self.credit_label = tk.Label(
            self.root,
            text="Made by Ali Mohamed",
            font=("Arial", 10),
            fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.credit_label.pack(pady=5)

        # Username input
        self.username_label = tk.Label(
            self.root,
            text="Enter TikTok username:",
            font=("Arial", 12),
            fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(
            self.root,
            width=30,
            font=("Arial", 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR
        )
        self.username_entry.pack(pady=5)

        # Calculate button
        self.calculate_button = tk.Button(
            self.root,
            text="Calculate ERV",
            font=("Arial", 12, "bold"),
            bg=BUTTON_COLOR,
            fg=BACKGROUND_COLOR,
            command=self.start_calculation
        )
        self.calculate_button.pack(pady=10)

        # Result label
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12),
            fg=TEXT_COLOR,
            bg=BACKGROUND_COLOR
        )
        self.result_label.pack(pady=10)

        # Log window
        self.log_window = scrolledtext.ScrolledText(
            self.root,
            width=70,
            height=10,
            font=("Arial", 10),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR
        )
        self.log_window.pack(pady=10)

    def log(self, message):
        """
        Logs messages to the log window.
        """
        self.log_window.insert(tk.END, message + "\n")
        self.log_window.yview(tk.END)

    def start_calculation(self):
        """
        Starts the ERV calculation in a separate thread.
        """
        username = self.username_entry.get()
        if not username:
            messagebox.showerror("Error", "Please enter a TikTok username.")
            return
        
        self.log_window.delete(1.0, tk.END)
        self.result_label.config(text="")
        
        self.calculate_button.config(state=tk.DISABLED)
        
        threading.Thread(target=self.run_calculation, args=(username,), daemon=True).start()

    def run_calculation(self, username):
        """
        Runs the ERV calculation in a separate thread.
        """
        # Run the async function in a new event loop
        async def run_async():
            erv, total_engagements, total_views = await get_tiktok_data(username, self.log)
            
            # Update the result label
            if erv is not None:
                result_text = (
                    f"Total Engagements: {total_engagements}\n"
                    f"Total Views: {total_views}\n"
                    f"Engagement Rate by Views (ERV): {erv:.2f}%"
                )
                self.result_label.config(text=result_text)
            else:
                messagebox.showerror("Error", "Failed to calculate ERV. Please check the username or try again later.")
            
            # Re-enable the button
            self.calculate_button.config(state=tk.NORMAL)
        
        # Run the async function
        asyncio.run(run_async())

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokERVCalculator(root)
    root.mainloop()

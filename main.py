import tkinter as tk
from tkinter import messagebox, PhotoImage
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
import time
import os

def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching " + url + ": " + str(e))
        return None
# ========================================================================================
def extract_headings(soup):
    headings = []  
    for i in range(1, 7):
        tag_name = 'h' + str(i) 
        for h in soup.find_all(tag_name):
            headings.append(h.text.strip())
    return headings
# =========================================================================================
def extract_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs
# =========================================================================================
def extract_lists(soup):
    lists = []
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            lists.append(li.text.strip())
    return lists
# ========================================================================================
def extract_links(soup):
    links = []
    for a in soup.find_all('a'):
        link = a.get('href')
        if link: 
            links.append(link)
    return links
# ========================================================================================
def extract_images(soup):
    images = []
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if img_url:  # To avoid appending None if 'src' is missing
            images.append(img_url)
    return images
# =======================================================================================
def extract_content(soup):
    return {
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }
# =======================================================================================
# Save data to JSON (no CSV)

def save_data(data, url):
    # Categorize the page based on the URL
    parsed_url = urlparse(url)
    page_name = parsed_url.path.strip('/').replace('/', '_') or "home"  # Default to "home" if empty path
    
    # Generate JSON file name based on the URL
    netloc = parsed_url.netloc.replace('.', '_')  # Replace dots in domain with underscores
    json_file_name = netloc + ".json"  # Concatenate strings to create the filename
    
    # Store the data in a dictionary with categories as keys
    structured_data = {
        page_name: data
    }

    # Save to JSON file
    if os.path.exists(json_file_name):
        # Load existing JSON data and append new data
        with open(json_file_name, 'r') as json_file:
            existing_data = json.load(json_file)
        existing_data.update(structured_data)
        with open(json_file_name, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
    else:
        # Create a new JSON file
        with open(json_file_name, 'w') as json_file:
            json.dump(structured_data, json_file, indent=4)

# ======================================================================================
# Scraping logic
def scrape_page(url):
    html_content = fetch_webpage(url)
    if html_content is None:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    data = extract_content(soup)
    # Save the extracted content with the specific URL
    save_data(data, url)
    return extract_links(soup)
# =========================================================================================
def scrape_website(urls, num_urls):
    visited = set()
    to_visit = urls[:num_urls]
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        print("Scraping " + current_url + "...")
        new_links = scrape_page(current_url)
        if new_links:
            for link in new_links:
                full_url = urljoin(current_url, link)
                if full_url not in visited:
                    to_visit.append(full_url)
        visited.add(current_url)
        time.sleep(1)
    print("Scraping completed! Total pages scraped: " + str(len(visited)))
# =========================================================================================
# GUI functions
def start_scraping():
    url_input = url_text.get("1.0", "end").strip()
    if not url_input:
        messagebox.showwarning("Input Error", "Please enter at least one URL!")
        return
    urls = [url.strip() for url in url_input.split(",")]
    try:
        num_to_scrape = int(num_choice.get())
    except ValueError:
        messagebox.showerror("Selection Error", "Please select a valid number of URLs to scrape.")
        return
    if num_to_scrape > len(urls):
        messagebox.showerror("Input Error", "You cannot scrape more URLs than you have entered.")
        return
    scrape_website(urls, num_to_scrape)
    messagebox.showinfo("Scraping Complete", "Scraped " + str(num_to_scrape) + " URLs successfully!")
# ========================================================================================
# GUI setup
window = tk.Tk()
window.title("Web Scraper")
window.geometry("500x400")

# Background setup
if os.path.exists("bg.png"):
    bg_image = PhotoImage(file="bg.png")
    background_label = tk.Label(window, image=bg_image)
    background_label.place(relwidth=1, relheight=1)
else:
    window.configure(bg="#f0f0f0")  # Light gray background if image not found

# Frame for content
frame = tk.Frame(window, bg="#ffffff", bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=350)

# Title
title_label = tk.Label(frame, text="Web Scraper Tool", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#333333")
title_label.pack(pady=10)

# URL input
tk.Label(frame, text="Enter URLs (comma-separated):", bg="#ffffff", fg="#555555").pack(pady=5)
url_text = tk.Text(frame, height=5, width=40)
url_text.pack(pady=5)

# Dropdown for number of URLs
tk.Label(frame, text="Number of URLs to scrape:", bg="#ffffff", fg="#555555").pack(pady=5)
num_choice = tk.StringVar(value="1")
num_dropdown = tk.OptionMenu(frame, num_choice, *[str(i) for i in range(1, 11)])
num_dropdown.pack(pady=5)

# Scrape button
scrape_button = tk.Button(frame, text="Start Scraping", bg="#0078D7", fg="white", font=("Helvetica", 12, "bold"), command=start_scraping)
scrape_button.pack(pady=20)

window.mainloop()

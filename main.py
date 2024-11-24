import tkinter as tk
from tkinter import messagebox, PhotoImage
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
import time
import os
import shutil

def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print("Error fetching " + url + ": " + str(e))
        return None
# =====================================================================
def extract_headings(soup):
    headings = []
# Loop through heading tags from h1 to h6
    for i in range(1, 7):
        headings_in_level = soup.find_all('h' + str(i))
        for h in headings_in_level:
           headings.append(h.text.strip())
    return headings
# ======================================================================
def extract_paragraphs(soup):
    paragraphs = []
    for p in soup.find_all('p'):
        paragraphs.append(p.text.strip())
    return paragraphs
# =======================================================================
def extract_lists(soup):
    list_items = []
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            list_items.append(li.text.strip())
    return list_items
# ======================================================================
def extract_links(soup):
    links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href:  # Check if href exists
            links.append(href)
    return links
# ======================================================================
def extract_images(soup):
    image_sources = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:  # Check if src exists
            image_sources.append(src)
    return image_sources
# =========================================================================
def extract_content(soup):
    return {
        "Headings": extract_headings(soup),
        "Paragraphs": extract_paragraphs(soup),
        "Lists": extract_lists(soup),
        "Links": extract_links(soup),
        "Images": extract_images(soup),
    }
# ============================================================================
def filedailon(filepath):
    """Check if a file exists before attempting to overwrite or access it."""
    return os.path.exists(filepath)
# ========================================================================
def save_data(data, url, destination):
    """Save the extracted data to a JSON file in the specified destination."""
    # Create destination folder if it doesn't exist
    if not os.path.exists(destination):
        os.makedirs(destination)
    parsed_url = urlparse(url)
    page_name = parsed_url.path.strip('/').replace('/', '_') or "home"
    netloc = parsed_url.netloc.replace('.', '_')
    json_file_name = netloc + ".json"
    json_path = os.path.join(destination, json_file_name)
    structured_data = {page_name: data}
    if filedailon(json_path):
        with open(json_path, 'r') as json_file:
            existing_data = json.load(json_file)
        existing_data.update(structured_data)
        with open(json_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)
    else:
        with open(json_path, 'w') as json_file:
            json.dump(structured_data, json_file, indent=4)
    print("Data saved to " + json_path)
# =====================================================================
def move_file(file_path, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    try:
        shutil.move(file_path, target_dir)
        print("Moved " + file_path + " to " + target_dir)
    except Exception as e:
        print("Error moving file " + file_path + ": " + str(e))
# =====================================================================
def scrape_page(url, destination):
    html_content = fetch_webpage(url)
    if html_content is None:
        return None
    soup = BeautifulSoup(html_content, 'html.parser')
    data = extract_content(soup)
    save_data(data, url, destination)
    return extract_links(soup)
# =====================================================================
def scrape_website(urls, num_urls, destination):
    visited = set()
    to_visit = urls[:num_urls]
    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        print("Scraping " + current_url + "...")
        new_links = scrape_page(current_url, destination)
        if new_links:
            for link in new_links:
                full_url = urljoin(current_url, link)
                if full_url not in visited:
                    to_visit.append(full_url)
        visited.add(current_url)
        time.sleep(1)
    print("Scraping completed! Total pages scraped: " + str(len(visited)))
# ==============================================================================
# GUI functions
def start_scraping():
    url_input = url_text.get("1.0", "end").strip()
    destination = destination_entry.get().strip()
    if not url_input:
        messagebox.showwarning("Input Error", "Please enter at least one URL!")
        return
    if not destination:
        messagebox.showwarning("Input Error", "Please enter a valid destination folder!")
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
    scrape_website(urls, num_to_scrape, destination)
    messagebox.showinfo("Scraping Complete", "Scraped " + str(num_to_scrape) + " URLs successfully!")
# ====================================================================================================
# GUI setup
window = tk.Tk()
window.title("Web Scraper")
window.geometry("500x450")

# Background setup
if os.path.exists("bg.png"):
    bg_image = PhotoImage(file="bg.png")
    background_label = tk.Label(window, image=bg_image)
    background_label.place(relwidth=1, relheight=1)
else:
    window.configure(bg="#f0f0f0")
frame = tk.Frame(window, bg="#ffffff", bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=400)
title_label = tk.Label(frame, text="Web Scraper Tool", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#333333")
title_label.pack(pady=10)
tk.Label(frame, text="Enter URLs (comma-separated):", bg="#ffffff", fg="#555555").pack(pady=5)
url_text = tk.Text(frame, height=5, width=40)
url_text.pack(pady=5)
tk.Label(frame, text="Number of URLs to scrape:", bg="#ffffff", fg="#555555").pack(pady=5)
num_choice = tk.StringVar(value="1")
num_dropdown = tk.OptionMenu(frame, num_choice, *[str(i) for i in range(1, 11)])
num_dropdown.pack(pady=5)
tk.Label(frame, text="Destination Folder:", bg="#ffffff", fg="#555555").pack(pady=5)
destination_entry = tk.Entry(frame, width=40)
destination_entry.pack(pady=5)
scrape_button = tk.Button(frame, text="Start Scraping", bg="#0078D7", fg="white", font=("Helvetica", 12, "bold"), command=start_scraping)
scrape_button.pack(pady=20)
window.mainloop()

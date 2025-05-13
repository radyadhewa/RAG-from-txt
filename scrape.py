from playwright.sync_api import sync_playwright
import time

def scrape_dynamic_site(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # Or False to see the browser
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000) # Wait for network to be idle

            # Give some time for JS to load, if necessary (adjust as needed)
            # time.sleep(5) # Or use page.wait_for_selector for specific elements

            # Example: Extracting a title that might be set by JavaScript
            title = page.title()
            print(f"Page Title: {title}")

            # Extract all links from "a href" tags and visit each link
            # Extract all links from "a href" tags before navigating
            links = list(set([a.get_attribute("href") for a in page.query_selector_all("a")]))
            with open("scraped_texts.txt", "a", encoding="utf-8") as file:
                for href in links:
                    if href and href.startswith("http") and "telkomuniversity.ac.id" in href and href != url:
                        print(f"Visiting Link: {href}")
                        try:
                            page.goto(href, timeout=30000)  # Navigate to the link
                            # Extract text from all "p" tags on the new page
                            p_elements = page.query_selector_all("p")
                            for p in p_elements:
                                text = p.text_content()
                                print(f"P Tag Text: {text}")
                                file.write(text + "\n")  # Append text to the file
                            # Go back to the original page
                            page.go_back(timeout=30000)
                        except Exception as e:
                            print(f"Error visiting {href}: {e}")

        except Exception as e:
            print(f"Error scraping {url}: {e}")
        finally:
            browser.close()

# Before running for the first time:
# 1. pip install playwright
# 2. python -m playwright install
scrape_dynamic_site("https://bis.telkomuniversity.ac.id/")
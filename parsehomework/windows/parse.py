from selenium import webdriver
from bs4 import BeautifulSoup
import json
import os
import time

COOKIES_FILE = "cookies.json"

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filename}.")

def load_cookies_from_file(driver, filename):
    """Load cookies into a Selenium browser instance."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print("No cookies file found.")

def login_via_browser(url, cookies_file):
    """Open a browser for manual login and save cookies."""
    driver = webdriver.Chrome()  # Adjust for your browser driver if not using Chrome
    driver.get(url)

    print("Please log in manually. The browser will close automatically after login.")
    input("Press Enter after logging in to save cookies...")
    cookies = driver.get_cookies()
    save_cookies_to_file(cookies, cookies_file)
    driver.quit()

def fetch_homework_section(url, cookies_file):
    """Fetch the specific section of the homework page using Selenium."""
    driver = webdriver.Chrome()
    
    # Load cookies and navigate to the page
    driver.get(url)
    load_cookies_from_file(driver, cookies_file)
    driver.get(url)
    time.sleep(5)  # Allow the page to load completely

    # Get the HTML content of the page
    html_content = driver.page_source
    driver.quit()
    return html_content

def parse_specific_section(html_content):
    """Extract and parse the specific section from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the section with the specified class
    section = soup.find("section", class_="diary-emotion-cache-zqw19v-wrapper")
    
    if section:
        # Find elements with the multiple specific classes inside the section
        elements = section.find_all(
            class_=[
                "DSXOGdoSiFGKohRuaDDx", 
                "ZEXs1Ejbk9QHxzmfogz2", 
                "w9NS8yBPMfd3dthmeaq7", 
                "_ELGiVRWaoZZRQLlT7eO", 
                "E8taxZlPjqlq_tc1djmu"
            ]
        )
        
        # Define the unwanted class combination to skip
        unwanted_classes = "DSXOGdoSiFGKohRuaDDx ZmmVltuRq_1DuwAx9seL gLNmyfBdelwfEPxsTJQs E8taxZlPjqlq_tc1djmu diary-emotion-cache-1igpks4-time"
        unwanted_classes2 = "DSXOGdoSiFGKohRuaDDx LqxH9tRjFX8eUgojIkc1 KgrW3dFKJEe1g6YA5Hmq _ELGiVRWaoZZRQLlT7eO E8taxZlPjqlq_tc1djmu diary-emotion-cache-or1xsw-headerTitle"
        unwanted_classes3 = "DSXOGdoSiFGKohRuaDDx ebIBbAN3ZomwnCMWP167 _ELGiVRWaoZZRQLlT7eO ZEXs1Ejbk9QHxzmfogz2 E8taxZlPjqlq_tc1djmu diary-emotion-cache-cnttxm-text"
        unwanted_classes4 = "DSXOGdoSiFGKohRuaDDx yXVdBhUh4InVs1L3OfeG gLNmyfBdelwfEPxsTJQs LqxH9tRjFX8eUgojIkc1 d2QqQ_5NlRBBwapENeu8 E8taxZlPjqlq_tc1djmu eGGprM7fvltBKXuek4lO"
        
        # Extract the text from the matched elements and print each on a new line
        for element in elements:
            # Skip the element if its class matches the unwanted combination
            if unwanted_classes in " ".join(element.get("class", [])):
                continue

            if unwanted_classes2 in " ".join(element.get("class", [])):
                continue

            if unwanted_classes3 in " ".join(element.get("class", [])):
                continue
            
            if unwanted_classes4 in " ".join(element.get("class", [])):
                continue

            # Special case: Check if the element matches the class "DSXOGdoSiFGKohRuaDDx ebIBbAN3ZomwnCMWP167 _ELGiVRWaoZZRQLlT7eO E8taxZlPjqlq_tc1djmu"
            if "DSXOGdoSiFGKohRuaDDx ebIBbAN3ZomwnCMWP167 _ELGiVRWaoZZRQLlT7eO LqxH9tRjFX8eUgojIkc1 E8taxZlPjqlq_tc1djmu" in element.get("class", []):
                # Print each class on a new line (i.e., divide)
                for cls in element.get("class", []):
                    print(cls)
                print("-" * 80)  # Prints a line separator after each element
            elif "ZEXs1Ejbk9QHxzmfogz2" in element.get("class", []):
                # Print without dividing (i.e., no line separator)
                print(element.get_text(strip=True))
            else:
                # Print the normal element text without division
                print(element.get_text(strip=True))
                print("-" * 80)  # Prints a line separator after each element
                
        return elements
    else:
        print("The specified section was not found.")
        return None



def debug_html(html_content):
    """Save the HTML content for debugging."""
    with open("debug.html", "w", encoding="utf-8") as file:
        file.write(html_content)

def main():
    login_url = "https://ms-edu.tatar.ru/16/"  # Replace with actual login URL
    homework_url = "https://ms-edu.tatar.ru/diary/homeworks/homeworks/"

    # Check if cookies exist; otherwise, prompt for manual login
    if not os.path.exists(COOKIES_FILE):
        print("No saved cookies found. Opening browser for manual login.")
        login_via_browser(login_url, COOKIES_FILE)

    # Fetch the homework page's specific section
    html_content = fetch_homework_section(homework_url, COOKIES_FILE)

    # Save raw HTML for debugging
    debug_html(html_content)

    # Parse and display the specific section content
    parse_specific_section(html_content)

if __name__ == "__main__":
    main()

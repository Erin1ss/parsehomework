from bs4 import BeautifulSoup
from selenium import webdriver
import json
import os
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.ext import MessageHandler, Filters

COOKIES_FILE = "cookies.json"

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filename}.")

def login_via_browser(update: Update, context: CallbackContext):
    """Open a browser for manual login and save cookies."""
    login_url = "https://ms-edu.tatar.ru/16"  # Replace with the actual login URL

    # Open the browser and navigate to the login page
    update.message.reply_text("Ты не должен был нажимать, ну ладно. Для фикса: Пожалуйста, войдите в систему и закройте браузер, когда закончите.")
    driver = webdriver.Chrome()  # Adjust to your preferred WebDriver (e.g., Chrome, Firefox)

    try:
        driver.get(login_url)
        update.message.reply_text("После входа в систему закройте браузер, чтобы сохранить сеанс.")

        # Wait for the user to complete login
        input("Press Enter in the terminal after logging in...")
        
        # Collect cookies
        cookies = driver.get_cookies()
        save_cookies_to_file(cookies, COOKIES_FILE)
        update.message.reply_text("Вход выполнен успешно! Файлы cookie сохранены.")
    finally:
        driver.quit()

def load_cookies_from_file(driver, filename):
    """Load cookies into a Selenium browser instance."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            cookies = json.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        print("Куки не найдены")


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

    section = soup.find("section", class_="diary-emotion-cache-zqw19v-wrapper")

    if section:
        elements = section.find_all(
            class_=[
                "DSXOGdoSiFGKohRuaDDx", 
                "ZEXs1Ejbk9QHxzmfogz2", 
                "w9NS8yBPMfd3dthmeaq7", 
                "_ELGiVRWaoZZRQLlT7eO", 
                "E8taxZlPjqlq_tc1djmu"
            ]
        )
        
        unwanted_classes = [
            "DSXOGdoSiFGKohRuaDDx ZmmVltuRq_1DuwAx9seL gLNmyfBdelwfEPxsTJQs E8taxZlPjqlq_tc1djmu diary-emotion-cache-1igpks4-time",
            "DSXOGdoSiFGKohRuaDDx LqxH9tRjFX8eUgojIkc1 KgrW3dFKJEe1g6YA5Hmq _ELGiVRWaoZZRQLlT7eO E8taxZlPjqlq_tc1djmu diary-emotion-cache-or1xsw-headerTitle",
            "DSXOGdoSiFGKohRuaDDx ebIBbAN3ZomwnCMWP167 _ELGiVRWaoZZRQLlT7eO ZEXs1Ejbk9QHxzmfogz2 E8taxZlPjqlq_tc1djmu diary-emotion-cache-cnttxm-text",
            "DSXOGdoSiFGKohRuaDDx yXVdBhUh4InVs1L3OfeG gLNmyfBdelwfEPxsTJQs LqxH9tRjFX8eUgojIkc1 d2QqQ_5NlRBBwapENeu8 E8taxZlPjqlq_tc1djmu eGGprM7fvltBKXuek4lO"
        ]

        result_text = []
        for element in elements:
            element_classes = " ".join(element.get("class", []))
            if any(uc in element_classes for uc in unwanted_classes):
                continue

            if "ZEXs1Ejbk9QHxzmfogz2" in element_classes:
                result_text.append(element.get_text(strip=True))
            else:
                result_text.append(f"{element.get_text(strip=True)}\n{'-' * 80}")
        
        return "\n".join(result_text) if result_text else "No relevant elements found."
    else:
        return "Отпиши Эрику, пускай пофиксит /login"

def debug_html(html_content):
    """Save the HTML content for debugging."""
    with open("debug.html", "w", encoding="utf-8") as file:
        file.write(html_content)

def start(update: Update, context: CallbackContext):
    """Handle /start command."""
    update.message.reply_text("Привет! Напиши /homework чтобы узнать дз на неделю")

def fetch_homework(update: Update, context: CallbackContext):
    """Fetch and parse the homework content."""
    homework_url = "https://ms-edu.tatar.ru/diary/homeworks/homeworks/"
    update.message.reply_text("Ожидайте, через 20 секунд появится дз.")

    # Check if cookies exist; otherwise, prompt for manual login
    if not os.path.exists(COOKIES_FILE):
        update.message.reply_text("Отпиши Эрику, пускай пофиксит /login")
        return

    # Fetch the homework page's specific section
    html_content = fetch_homework_section(homework_url, COOKIES_FILE)

    # Save raw HTML for debugging
    debug_html(html_content)

    # Parse and display the specific section content
    parsed_content = parse_specific_section(html_content)
    update.message.reply_text(parsed_content)

def login(update: Update, context: CallbackContext):
    """Trigger browser login process."""
    response = login_via_browser("https://ms-edu.tatar.ru/16/", COOKIES_FILE)
    update.message.reply_text(response)
    

def save_cookies(update: Update, context: CallbackContext):
    """Save cookies after manual login."""
    driver = webdriver.Chrome()
    cookies = driver.get_cookies()
    save_cookies_to_file(cookies, COOKIES_FILE)
    driver.quit()
    update.message.reply_text("Куки сохранены!")

def main():
    """Start the Telegram bot."""
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True) 
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("homework", fetch_homework))
    dispatcher.add_handler(CommandHandler("login", login_via_browser))
    dispatcher.add_handler(CommandHandler("save_cookies", save_cookies_to_file))
    dispatcher.add_handler(CommandHandler("load", load_cookies_from_file))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

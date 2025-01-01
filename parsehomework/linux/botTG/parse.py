import json
import os
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from playwright.sync_api import sync_playwright

COOKIES_FILE = "cookies.json"

def save_cookies_to_file(cookies, filename):
    """Save cookies to a JSON file."""
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies saved to {filename}.")

def login_via_browser(update: Update, context: CallbackContext):
    """Open a browser for manual login and save cookies."""
    login_url = "https://ms-edu.tatar.ru/16/"  # Replace with the actual login URL

    # Open the browser and navigate to the login page
    update.message.reply_text("Ты не должен был нажимать, ну ладно. Для фикса: Пожалуйста, войдите в систему и закройте браузер, когда закончите.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto(login_url)
            update.message.reply_text("После входа в систему закройте браузер, чтобы сохранить сеанс.")

            # Wait for the user to complete login
            input("Press Enter in the terminal after logging in...")

            # Save cookies after login
            cookies = page.context.cookies()
            save_cookies_to_file(cookies, COOKIES_FILE)
            update.message.reply_text("Вход выполнен успешно! Файлы cookie сохранены.")
        finally:
            browser.close()

def load_cookies_from_file(page, filename):
    """Load cookies into a Playwright browser instance."""
    if os.path.exists(filename):
        with open(filename, "r") as file:
            cookies = json.load(file)
            page.context.add_cookies(cookies)
    else:
        print("Куки не найдены")

def fetch_homework_section(url, cookies_file):
    """Fetch the specific section of the homework page using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Load cookies
        if os.path.exists(cookies_file):
            with open(cookies_file, "r") as file:
                cookies = json.load(file)
                context.add_cookies(cookies)

        page = context.new_page()

        # Navigate to the page
        page.goto(url)
        page.wait_for_timeout(8000)  # Wait for JavaScript to load content

        # Get the rendered HTML
        html_content = page.content()
        browser.close()
        return html_content

def parse_specific_section(html_content):
    """Extract and parse the specific section from the HTML content."""
    from bs4 import BeautifulSoup
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
                result_text.append(element.get_text(strip=True) + ":")
            else:
                result_text.append(f"{element.get_text(strip=True)}\n{'-' * 80}")
        
        return "\n".join(result_text) if result_text else "Нет результатов с дневника, возможно сейчас каникулы, но если нет, отпишите Эрику, пуcть пофиксит."
    else:
        return "Отпиши Эрику, пускай пофиксит /login"

def start(update: Update, context: CallbackContext):
    """Handle /start command."""
    update.message.reply_text("Привет! Напиши /homework чтобы узнать дз на неделю")

def fetch_homework(update: Update, context: CallbackContext):
    """Fetch and parse the homework content."""
    homework_url = "https://ms-edu.tatar.ru/diary/homeworks/homeworks"
    update.message.reply_text("Ожидайте, через 20 секунд появится дз.")

    # Check if cookies exist; otherwise, prompt for manual login
    if not os.path.exists(COOKIES_FILE):
        update.message.reply_text("Отпиши Эрику, пускай пофиксит /login")
        return

    # Fetch the homework page's specific section
    html_content = fetch_homework_section(homework_url, COOKIES_FILE)

    # Parse and display the specific section content
    parsed_content = parse_specific_section(html_content)
    update.message.reply_text(parsed_content)

def login(update: Update, context: CallbackContext):
    """Trigger browser login process."""
    response = login_via_browser(update, context)
    update.message.reply_text(response)

def save_cookies(update: Update, context: CallbackContext):
    """Save cookies after manual login."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Trigger login and save cookies
        login_via_browser(update, context)
        cookies = page.context.cookies()
        save_cookies_to_file(cookies, COOKIES_FILE)
        browser.close()
        update.message.reply_text("Куки сохранены!")

def main():
    """Start the Telegram bot."""
    updater = Updater("7901658924:AAHvoH3jpA9iuAgMPq3_sHP4WS7RgQTvf50", use_context=True) 
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("homework", fetch_homework))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("save_cookies", save_cookies))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

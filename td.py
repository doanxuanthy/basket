import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Set up WebDriver options
options = webdriver.ChromeOptions()
# options.add_argument("--incognito")  # Uncomment if you want incognito mode
options.add_argument("--headless")

# Set up WebDriver using ChromeDriverManager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"

    response = requests.get(url)
    return response

def perform_actions():
    """Perform the actions needed on the webpage."""
    while True:
        try:
            logger.info("Opening website...")
            driver.get("https://www.fb88asian.com/vi-VN/Sportsbook/Sports5")

            # Maximize the browser window
            driver.maximize_window()

            # Wait for the iframe to be present and switch to it
            wait = WebDriverWait(driver, 10)
            iframe = wait.until(EC.presence_of_element_located((By.ID, 'iframe')))
            driver.switch_to.frame(iframe)

            # Wait for the element inside the iframe to be clickable
            element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[contains(text(),'Bóng rổ')]")
            ))
            element.click()

            # Wait for the input field to be clickable and interact with it
            input_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Tìm kiếm Giải đấu/Sự kiện...']")))
            input_field.click()
            input_field.send_keys('Giải IPBL Pro nữ')

            # Wait for the <div> element to be clickable and click it
            div_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='navigation_eu_fe_BetSearchItem_betSearchMainTitle']")))
            div_element.click()

            # Wait for the second <div> element to be clickable and click it
            div_element = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'components-fe_Icon_icon') and contains(@class, 'eventlist_eu_fe_EventInfo_sportIcon')]")))
            div_element.click()

            signal_flag = False

            while True:
                try:
                    # Telegram bot token and chat ID
                    TELEGRAM_TOKEN = '6735255826:AAFsAurrm95_73sWKRw0IezdE81t2WFxV1o'
                    CHAT_ID = '5559311100'

                    # Find the element using the CSS selector
                    element = driver.find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(1) td:nth-child(7)')
                    score_team_1 = int(element.text.strip())

                    # Find the element using the CSS selector
                    element = driver.find_element(By.CSS_SELECTOR, 'tbody tr:nth-child(2) td:nth-child(7)')
                    score_team_2 = int(element.text.strip())

                    # Check if the absolute difference is greater than 7
                    if abs(score_team_1 - score_team_2) > 7:
                        if signal_flag == False:
                            message = f"Score difference alert! Team 1: {score_team_1}, Team 2: {score_team_2}"
                            send_telegram_message(TELEGRAM_TOKEN, CHAT_ID, message)
                            signal_flag = True

                    # Wait for the element to be present
                    element = wait.until(EC.presence_of_element_located((By.XPATH, "//thead//span[1]")))

                    # Get the text value of the element
                    time_match = element.text
                    
                    # Extract numbers and time string
                    match = re.search(r'(\d+)\s(\d+):(\d+)', time_match)
                    if match:
                        # Extract numbers and time parts
                        quarter = match.group(1)
                        minutes = match.group(2)
                        seconds = match.group(3)

                        # Set the flag based on the comparison
                        flag = (quarter == '4' and minutes == '00' and seconds == '00')
                        logger.info("Flag is set to %s", flag)

                        if flag:
                            logger.info("Flag is True. Waiting for 5 minutes before reloading...")
                            time.sleep(300)  # Wait for 5 minutes
                            driver.refresh()  # Reload the page
                            time.sleep(5)     # Short wait before retrying
                            signal_flag = False
                            break  # Exit the inner loop to start from the top
                        else:
                            # Continue waiting in the inner loop
                            logger.info("Flag is False. Continuing to check the element.")
                            time.sleep(5)  # Short wait before rechecking

                except (TimeoutException, NoSuchElementException) as e:
                    logger.error("An error occurred: %s", e)
                    logger.info("Retrying...")
                    time.sleep(5)  # Wait before retrying

        except (TimeoutException, NoSuchElementException) as e:
            logger.error("An error occurred: %s", e)
            logger.info("Reloading page and retrying...")
            driver.refresh()
            time.sleep(5)  # Wait for a short period before retrying

try:
    perform_actions()
finally:
    logger.info("Closing browser...")
    driver.quit()

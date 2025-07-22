import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from langchain_google_genai import ChatGoogleGenerativeAI

def sanitize_for_selenium(text: str) -> str:
    return "".join(c for c in text if c <= '\uFFFF')

def run_linkedin_automation(prompt: str, image_path: str = None) -> str:
    LINKEDIN_EMAIL = os.environ.get("LINKEDIN_EMAIL", "2023pietcakrish034@poornima.org")
    LINKEDIN_PASSWORD = os.environ.get("LINKEDIN_PASSWORD", "yes567yo")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyA9KuT0uNgJC-rAvwL-FJHQ1M1QNqfvM0w")
    CHROMEDRIVER_PATH = "./chromedriver.exe"

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    full_prompt = f"""
    Generate a professional and engaging LinkedIn post based on the following topic: '{prompt}'.
    The post should have:
    1. A compelling hook to grab attention.
    2. A main body that provides value or insight.
    3. A concluding sentence or a question to encourage engagement.
    4. 3-5 relevant and popular hashtags.
    """

    response = llm.invoke(full_prompt)
    generated_post = sanitize_for_selenium(response.content)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 40)

    try:
        driver.get("https://www.linkedin.com/login")
        wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(LINKEDIN_EMAIL)
        driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()

        start_post_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start a post')]")))
        start_post_btn.click()

        post_editor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ql-editor")))
        post_editor.send_keys(generated_post)

        if image_path:
            add_media_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Add media')]")))
            add_media_button.click()

            file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
            file_input.send_keys(image_path)

            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Done']"))).click()

        post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.share-actions__primary-action")))
        post_button.click()

        time.sleep(5)
        return generated_post

    except TimeoutException:
        driver.save_screenshot("linkedin_error.png")
        raise Exception("Timeout: Element not found or slow network. Screenshot saved as linkedin_error.png")
    except Exception as e:
        driver.save_screenshot("linkedin_error.png")
        raise Exception(f"Unexpected error: {e}. Screenshot saved as linkedin_error.png")
    finally:
        driver.quit()

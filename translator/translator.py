import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def translate_word(word_to_translate, source_lang, target_lang):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    wait = WebDriverWait(driver, 10)

    url = f"https://translate.yandex.com/en/?source_lang={source_lang}&target_lang={target_lang}&text={word_to_translate}"

    driver.get(url)

    try:
        captcha_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='CheckboxCaptcha-Anchor']")))
        captcha_checkbox.click()
        time.sleep(1)
        driver.get(url)
    except Exception as e:
        print(f"Captcha checkbox was not clicked, {e}")

    translated_text_element = wait.until(
        EC.presence_of_element_located((By.XPATH, "//p[@dir='ltr']/span"))
    )

    translated_text = translated_text_element.text
    print(f"Translation [{source_lang}->{target_lang}] of '{word_to_translate}': {translated_text}")

    driver.quit()
    return translated_text

# Example usage:
if __name__ == '__main__':
    translation = translate_word("pineapple", "en", "ru")
    print(f"Translated word: {translation}")

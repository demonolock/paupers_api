import csv
import re
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from lxml import html


class ParseSozdDuma:
    def __init__(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        self.actions = ActionChains(self.driver)
        self.base_csv_file = 'duma_laws'
        self.file_counter = 1
        self.row_counter = 0
        self.current_csv_file = f"{self.base_csv_file}_{self.file_counter}.csv"
        self.initialize_csv()

    def initialize_csv(self):
        """Create CSV file with headers if it doesn't exist"""
        with open(self.current_csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Number', 'Title', 'Status', 'Date', 'Link'])  # Adjust headers as needed

    def clean_text(self, text):
        """Remove excess whitespace but preserve single spaces"""
        return re.sub(r'\s+', ' ', text.strip()) if text else ''

    def configure_table(self):
        """Configure table settings to show all columns"""
        table_view = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@class='nav_icon_2']")))
        table_view.click()

        table_settings = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@data-original-title='Дополнительные столбцы']")))
        table_settings.click()

        settings_popup_header = self.wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[contains(text(), 'Настройка дополнительных столбцов')]")))

        settings_popup_header.click()

        self.actions.send_keys(Keys.TAB).perform()
        self.actions.send_keys(Keys.ENTER).perform()

        # Select all available columns
        while True:
            try:
                available_column = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//li[@aria-selected='false']")))
                available_column.click()
                time.sleep(1)
                self.actions.send_keys(Keys.ENTER).perform()
            except:
                break

        self.actions.send_keys(Keys.ESCAPE).perform()
        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@name='table_fields_settings_type[submit]']")))
        submit_button.click()
        time.sleep(2)  # Wait for table to reload

    def parse_page(self, page_source):
        """Parse table data from page source"""
        tree = html.fromstring(page_source)
        data = []

        for row in tree.xpath('//table//tr[position()>1]'):
            row_data = [self.clean_text(td.text_content()) for td in row.xpath('.//td')]
            if row_data:  # Skip empty rows
                # Extract link if available
                link = row.xpath(".//a[@class='a_event_files ']/@href")
                if link:
                    row_data.append(link[0])
                else:
                    row_data.append("")  # Add empty string if no link
                data.append(row_data)
        return data

    def save_to_csv(self, data):
        """Append data to CSV file, creating new file every 50,000 rows"""
        rows_to_write = len(data)

        # Check if we need to create a new file
        if self.row_counter + rows_to_write >= 50000:
            remaining_space = 50000 - self.row_counter
            # Write remaining rows to current file
            with open(self.current_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(data[:remaining_space])

            # Create new file
            self.file_counter += 1
            self.current_csv_file = f"{self.base_csv_file}_{self.file_counter}.csv"
            with open(self.current_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Number', 'Title', 'Status', 'Date', 'Link'])
                writer.writerows(data[remaining_space:])

            self.row_counter = len(data[remaining_space:])
        else:
            # Write all data to current file
            with open(self.current_csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            self.row_counter += rows_to_write

    def process_page(self, chunk=1000, page=1):
        """Process a single page"""
        url = f"https://sozd.duma.gov.ru/oz/b?b%5BClassOfTheObjectLawmakingId%5D=1&count_items={chunk}&page={page}"
        self.driver.get(url)

        # Configure table on first page only
        if page == 1:
            self.configure_table()

        # Wait for table to load
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
        time.sleep(2)  # Additional wait for data to populate

        # Check for termination element
        if self.driver.find_elements(By.XPATH, "//div[@class='not_date_ic m_lupa']"):
            return False

        page_source = self.driver.page_source
        data = self.parse_page(page_source)
        self.save_to_csv(data)
        return True

    def run(self, max_pages=500):
        """Run parser through multiple pages"""
        try:
            for page in range(1, max_pages + 1):
                print(f"Processing page {page}... Current file: {self.current_csv_file}, Rows: {self.row_counter}")
                should_continue = self.process_page(page=page)
                if not should_continue:
                    print("Termination element found. Stopping.")
                    break
        finally:
            self.driver.quit()
            print(f"Processing complete. Total files created: {self.file_counter}")


if __name__ == '__main__':
    parser = ParseSozdDuma()
    parser.run(max_pages=5000)
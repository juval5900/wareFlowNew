from datetime import datetime
import os
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options



chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "C:\\Users\\juval\\Downloads\\",  # Replace with your download folder path
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})


class Hosttest(TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.live_server_url = 'http://127.0.0.1:8000/'

    def tearDown(self):
        self.driver.quit()
        
    def test_01_login_page(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.maximize_window()
        time.sleep(1)
        email=driver.find_element(By.CSS_SELECTOR,"input.input100[name='username']")
        email.send_keys("juvalkondattukunnel@gmail.com")
        password=driver.find_element(By.CSS_SELECTOR,"input.input100[type='password'][name='password']")
        password.send_keys("Juval@5900")
        time.sleep(2)
        submit=driver.find_element(By.CSS_SELECTOR,"button.login100-form-btn")
        submit.click()
        time.sleep(2)
        inventory=driver.find_element(By.CSS_SELECTOR,"a.nav-link.inventory")
        inventory.click()
        add_product=driver.find_element(By.CSS_SELECTOR,"a.btn.btn-info")
        add_product.click()
        file_path = "C:\\Users\\juval\\Downloads\\Person_icon_BLACK-01.svg.png"
        image_input = driver.find_element(By.CSS_SELECTOR, "input#productImage")
        image_input.send_keys(file_path)
        time.sleep(1)
        category=driver.find_element(By.CSS_SELECTOR,"select#category")
        category.click()
        categoryselect=driver.find_element(By.CSS_SELECTOR,"option[value='1']")
        categoryselect.click()
        time.sleep(1)
        subcategory=driver.find_element(By.ID,"subcategory")
        subcategory.click()
        subcategoryselect=driver.find_element(By.CSS_SELECTOR,"option[value='1']")
        subcategoryselect.click()
        time.sleep(1)
        productname=driver.find_element(By.CSS_SELECTOR,"input#productName")
        productname.send_keys("Iphone 14")
        time.sleep(1)
        quantity=driver.find_element(By.CSS_SELECTOR,"input#quantity")
        quantity.send_keys("870")
        time.sleep(1)
        suppliers=driver.find_element(By.CSS_SELECTOR,"button.btn.btn-secondary.dropdown-toggle")
        suppliers.click()
        checkbox = driver.find_element(By.CSS_SELECTOR,"input#supplier_1")
        # Create an ActionChains object
        actions = ActionChains(driver)
        # Perform a click action on the checkbox
        actions.click(checkbox).perform()
        time.sleep(1)
        thresholdvalue=driver.find_element(By.CSS_SELECTOR,"input#thresholdValue")
        thresholdvalue.send_keys("100")
        time.sleep(1)
        add_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'].btn.btn-primary")
        add_button.click()
        time.sleep(1)
        pdf=driver.find_element(By.CSS_SELECTOR,"a#generate-pdf-btn.btn.btn-secondary.generate-pdf")
        pdf.click()
        downloaded_file_path = "C:\\Users\\juval\\Downloads\\product_list.pdf"  # Replace with the expected file path
        if os.path.exists(downloaded_file_path):
            print("PDF file has been downloaded successfully.")
        else:
            print("PDF file download failed or not found.")
        time.sleep(5)
        

    # Add more test methods as needed

if __name__ == '__main__':
    import unittest
    unittest.main()
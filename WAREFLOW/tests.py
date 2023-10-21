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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": "C:\\Users\\juval\\Downloads\\",
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
        supplier=driver.find_element(By.CSS_SELECTOR,"span.nav-link-text.supplier")
        supplier.click()
        add_supplier=driver.find_element(By.CSS_SELECTOR,"a#showFormButton")
        add_supplier.click()
        file_path = "C:\\Users\\juval\\Downloads\\Person_icon_BLACK-01.svg.png"
        image_input = driver.find_element(By.CSS_SELECTOR, "input#supplierImage")
        image_input.send_keys(file_path)
        time.sleep(1)
        suppliername=driver.find_element(By.CSS_SELECTOR,"input#supplierName")
        suppliername.send_keys("Jomey Joseph")
        time.sleep(1)
        address=driver.find_element(By.CSS_SELECTOR,"input#supplierAddress")
        address.send_keys("kottayam")
        time.sleep(1)
        contact=driver.find_element(By.CSS_SELECTOR,"input#contactNumber")
        contact.send_keys("8734734440")
        time.sleep(1)
        contact=driver.find_element(By.CSS_SELECTOR,"input#supplieremail")
        contact.send_keys("jomeyjoseph@gmail.com")
        time.sleep(1)
        type=driver.find_element(By.CSS_SELECTOR,"select#supplierType")
        type.click()
        typeselect=driver.find_element(By.CSS_SELECTOR,"option[value='Taking returns']")
        typeselect.click()
        time.sleep(1)
        
        add_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.mb-3")
        add_button.click()
        time.sleep(1)
        pdf=driver.find_element(By.CSS_SELECTOR,"a#generate-pdf-btn.btn.btn-secondary")
        pdf.click()
        time.sleep(3)
        downloaded_file_path = "C:\\Users\\juval\\Downloads\\supplier_list.pdf"  # Replace with the expected file path
        if os.path.exists(downloaded_file_path):
            print("PDF file has been downloaded successfully.")
        else:
            print("PDF file download failed or not found.")
        time.sleep(5)
        profile=driver.find_element(By.CSS_SELECTOR,"img[alt='user profile']")
        profile.click()
        time.sleep(2)
        logout=driver.find_element(By.CSS_SELECTOR,"a.dropdown-item[href='/loggout']")
        logout.click()
        time.sleep(2)
    # Add more test methods as needed

if __name__ == '__main__':
    import unittest
    unittest.main()
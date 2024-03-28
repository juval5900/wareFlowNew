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
        self.live_server_url = 'http://127.0.0.1:8000/register.html'

    def tearDown(self):
        self.driver.quit()
        
    def test_01_login_page(self):
        driver = self.driver
        driver.get(self.live_server_url)
        driver.maximize_window()
        time.sleep(1)
        
        name=driver.find_element(By.CSS_SELECTOR,"input.signupelement[name='FirstName']")
        name.send_keys("Joseph Jomey")
        time.sleep(1)
        
        email=driver.find_element(By.CSS_SELECTOR,"input.signupelement[type='email'][name='email'][placeholder='Email']")
        email.send_keys("jomeyjoseph@gmail.com")
        time.sleep(1)
       
        passwd=driver.find_element(By.CSS_SELECTOR,"input.signupelement[type='password'][name='pass']")
        passwd.send_keys("Jomey@123")
        time.sleep(1)
        
        cpass=driver.find_element(By.CSS_SELECTOR,"input.signupelement[type='password'][name='cpass'][placeholder='Confirm Password']")
        cpass.send_keys("Jomey@123")
        time.sleep(1)
        
        submit=driver.find_element(By.CSS_SELECTOR,"button#submitButton.signupbtn[type='submit']")
        submit.click()
        time.sleep(1)
        
        mail=driver.find_element(By.CSS_SELECTOR,"input#id_username.signinelement")
        mail.send_keys("admin")
        time.sleep(1)
        
        logpass = driver.find_element(By.CSS_SELECTOR, 'input#id_password.signinelement[type="password"]')
        logpass.send_keys("admin")
        time.sleep(1)
        
        logg=driver.find_element(By.CSS_SELECTOR,"button#login_button.signinbtn")
        logg.click()
        time.sleep(1)
        
        driver.execute_script("window.scrollBy(0, 500);")  # Adjust the value 500 as per your requirement
        
        ele=driver.find_element(By.CSS_SELECTOR,"a[href='/category/electronics/']")
        ele.click()
        time.sleep(1)
        
        pro=driver.find_element(By.CSS_SELECTOR,"a[href='/product/2/']")
        pro.click()
        time.sleep(1)
        
        adcart=driver.find_element(By.CSS_SELECTOR,"button.add-to-cart-button[name='buy_now']")
        adcart.click()
        time.sleep(1)
        
        driver.execute_script("window.scrollBy(0, 500);")  # Adjust the value 500 as per your requirement
        
        chk=driver.find_element(By.CSS_SELECTOR,"a.btn.btn-primary.py-3.px-4[href='/checkout']")
        chk.click()
        time.sleep(1)
        
        adrnme = driver.find_element(By.CSS_SELECTOR, 'input#firstname.form-control[type="text"]')
        adrnme.send_keys("Jomey")
        time.sleep(1)
        
        adrlsnme = driver.find_element(By.CSS_SELECTOR, 'input#lastname.form-control[type="text"]')
        adrlsnme.send_keys("Joseph")
        time.sleep(1)
        
        strt = driver.find_element(By.CSS_SELECTOR, 'input#streetaddress.form-control[type="text"]')
        strt.send_keys("Vayalil")
        time.sleep(1)
        
        aprtnme = driver.find_element(By.CSS_SELECTOR, 'input#apartmentsuiteunit.form-control[type="text"]')
        aprtnme.send_keys("Chathenthara")
        time.sleep(1)
        
        twn = driver.find_element(By.CSS_SELECTOR, 'input#towncity.form-control[type="text"]')
        twn.send_keys("Mukkoottuthara")
        time.sleep(1)
        
        pin = driver.find_element(By.CSS_SELECTOR, 'input#postcodezip.form-control[type="text"]')
        pin.send_keys("686510")
        time.sleep(1)
        
        phn = driver.find_element(By.CSS_SELECTOR, 'input#phone.form-control[type="text"]')
        phn.send_keys("8330859255")
        time.sleep(1)
        
        milad = driver.find_element(By.CSS_SELECTOR, 'input#emailaddress.form-control[type="text"]')
        milad.send_keys("Josephjomey@gmail.com")
        time.sleep(1)
        
        driver.execute_script("window.scrollBy(0, 500);")  # Adjust the value 500 as per your requirement
        
        ordpl=driver.find_element(By.CSS_SELECTOR,"img[src='/static/admin/assets/images/profile/user-1.jpg'][alt=''][width='35'][height='35'].rounded-circle")
        ordpl.click()
        time.sleep(1)
        
        myor=driver.find_element(By.CSS_SELECTOR,"a[href='/orders/'].d-flex.align-items-center.gap-2.dropdown-item")
        myor.click()
        time.sleep(1)
        
        # rvw=driver.find_element(By.CSS_SELECTOR,"button[type='button'].btn.btn-outline")
        # rvw.click()
        # time.sleep(1)
        
        rt=driver.find_element(By.CSS_SELECTOR,"a[href='/generate_pdf/34/'][target='_blank']")
        rt.click()
        time.sleep(1)
        
        download_directory = "C:\\Users\\juval\\Downloads\\"
        
        time.sleep(5)
        
        pdf_filename = "Invoice34.pdf"  # Adjust the filename based on the expected filename
        pdf_path = os.path.join(download_directory, pdf_filename)

        if os.path.exists(pdf_path):
            print("PDF has been successfully downloaded.")
        else:
            print("PDF download failed or is still in progress.")
        
        # rview=driver.find_element(By.CSS_SELECTOR,"textarea#comment.form-control")
        # rview.send_keys("good")
        # time.sleep(1)
        
        # sub=driver.find_element(By.CSS_SELECTOR,"button[type='submit'].btn.btn-primary")
        # sub.click()
        # time.sleep(10)
        
        # pym=driver.find_element(By.CSS_SELECTOR,"button#pay-btn.btn.btn-primary.btn-block")
        # pym.click()
        # time.sleep(1)
        
        # uaddr=driver.find_element(By.CSS_SELECTOR,"#contact")
        # uaddr.send_keys("8330859255")
        # time.sleep(1)
        
        # upip=driver.find_element(By.CSS_SELECTOR,"button.instrument.slotted-option.svelte-1d17g67[data-type='method']")
        # upip.click()
        # time.sleep(1)
        
        # uadr=driver.find_element(By.CSS_SELECTOR,"input#vpa-upi.input-one-click-checkout.upi-vpa-field-one-cc.main.svelte-1lowomx[type='text'][name='vpa-upi'][required][autocomplete='off'][pattern='.+@.+']")
        # uadr.send_keys("8330859255@paytm")
        # time.sleep(1)
        
        # fin=driver.find_element(By.CSS_SELECTOR,"button#redesign-v15-cta.svelte-1milfy7")
        # fin.click()
        # time.sleep(15)
        
if __name__ == '__main__':
    import unittest
    unittest.main()
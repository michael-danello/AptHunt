from selenium.common.exceptions import NoSuchElementException

def has_captcha(driver):
    try:
        driver.find_element_by_id("px-captcha")
        return True
   
    except NoSuchElementException:
        return False

import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver_path = os.path.join(os.path.dirname(__file__),"chromedriver_linux64", "chromedriver")
driver = webdriver.Chrome(driver_path)

url = "https://www.yelp.com/biz/manas-indian-cuisine-los-angeles-2"
# url = "https://www.yelp.com/biz/l-epi-de-champrosay-draveil"
driver.get(url)
try:
    button = WebDriverWait(driver, timeout=2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/yelp-react-root/div[1]/div[4]/div/div/div[2]/div/div[1]/main/section[3]/div[2]/button")))
    button = button.click()
    amenities = driver.find_elements(By.CSS_SELECTOR,"""section[aria-label="Amenities and More"] span""")
    amenities = [amenity.text for amenity in amenities]
    print(amenities)
except TimeoutException:
    print("Timed out")
driver.quit()
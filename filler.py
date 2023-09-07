from selenium import webdriver

options = webdriver.ChromeOptions()
option.add_argument('-incognito')
# option.add_argument("--headless")
# option.add_argument("disable-gpu")

browser = webdriver.Chrome(options=option)
browser.get('browser.get("https://forms.gle/FoAoauz53Xy7A4n68")')

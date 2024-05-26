import time
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from .constants import VALID_SOURCE


def get_driver():
    """Function to create a selenium web driver for data scraping

    Returns:
        webdriver.Chrome: Selenium driver
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    options.page_load_strategy = 'normal'
    driver=webdriver.Chrome(options=options)
    return driver


def get_data_driver(url, driver, source=None):
    """_summary_

    Args:
        url (str): _description_
        driver (webdriver.Chrome): _description_
        source (str, optional): Whether it is iplt20 or cricbuzz(cb). Defaults to None.

    Raises:
        ValueError: If an invalid source is provided

    Returns:
        List: List of the HTML tags
    """
    if source is None or source not in VALID_SOURCE:
        raise ValueError("Source must be either iplt20 or cb")
    driver.implicitly_wait(20)
    driver.get(url)
    if source == 'iplt20':
        elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="cookie__accept cookie__accept_btn"]')))
        elem.click()
    time.sleep(10)
    html_schedule = driver.page_source
    soup_schedule = BeautifulSoup(html_schedule)
    if source == 'iplt20':
        tags_schedule = soup_schedule.find_all('li',class_="ng-scope")
    elif source == 'cb':
        tags_schedule = soup_schedule.find_all('div',class_="cb-col-100 cb-col cb-series-matches ng-scope")
        tags_schedule+= soup_schedule.find_all('div',class_="cb-col-100 cb-col cb-series-brdr cb-series-matches ng-scope")
    driver.close()
    return tags_schedule


def get_score_driver(driver, url, team, source=None):
    """_summary_

    Args:
        driver (webdriver.Chrome): Selenium driver
        url (str): URL to be parsed
        team (str): Name of the team whose data is to be parsed

    Returns:
        List: List of the HTML tags
    """
    if source is None or source not in VALID_SOURCE:
        raise ValueError("Source must be either iplt20 or cb")
    driver.get(url)
    if source=='iplt20':
        click_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="cookie__accept cookie__accept_btn"]')))
        click_button.click()
    elif source=='cb':
        click_button = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,"//*[contains(text(), '{} Inns')]".format(team))))
        click_button.click()
    time.sleep(30)
    if source=='iplt20':
        showmore_link = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), '{} ')]".format(team))))
        driver.execute_script("arguments[0].click()", showmore_link)
    elif source=='cb':
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(20)
    html = driver.page_source
    soup = BeautifulSoup(html)
    driver.close()
    if source=='iplt20':
        tags=soup.find_all('div', class_="ballWrapper ng-scope")
        return tags
    elif source=='cb':
        tags = soup.find_all('div',class_="cb-col cb-col-100 ng-scope")
        return tags
    

def get_results_driver(driver, url):
    """_summary_

    Args:
        driver (Selenium driver): Selenium driver
        url (str): URL to be parsed

    Returns:
        List: List of the HTML tags
    """
    driver.implicitly_wait(20)
    driver.get(url)
    elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@class="cookie__accept cookie__accept_btn"]')))
    elem.click()
    time.sleep(10)
    html_schedule = driver.page_source
    soup_schedule = BeautifulSoup(html_schedule)
    tags_schedule = soup_schedule.find_all('li',class_="ng-scope")
    driver.close()
    return tags_schedule
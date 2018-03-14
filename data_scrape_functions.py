from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, WebDriverException
from configparser import ConfigParser
import time
import os
from collections import defaultdict


config = ConfigParser()
config.read('config.ini')


def instantiate_driver():
    """
    Create a Chrome webdriver instance
    :return: driver
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")

    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver

    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

    return driver


def navigate_to_site(driver, config=config, login=True):
    """Utility function to navigate to site home page"""

    url = config.get("SiteCreds", "base_url")
    driver.get(url)
    time.sleep(1)

    welcome_screen = driver.find_element_by_class_name(config.get('SiteTags', 'site_enter'))
    if welcome_screen:
        welcome_screen.click()
        time.sleep(.5)

    # Toggle on safe search
    driver.find_element_by_class_name(config.get('SiteTags', 'safe')).click()

    if login:
        driver.get(url+'#login')
        time.sleep(1)
        login_site(driver)

    return True


def login_site(driver):
    """Utility function to enter site credentials upon login"""

    # Enter login credentials
    user_input = driver.find_element_by_class_name(config.get('SiteTags', 'email'))
    pwd_input = driver.find_element_by_class_name(config.get('SiteTags', 'pwd'))

    user_input.send_keys(config.get('SiteCreds', 'username'))
    time.sleep(2)

    pwd_input.send_keys(config.get('SiteCreds', 'password'))
    time.sleep(.5)

    pwd_input.send_keys(Keys.RETURN)
    return True


def navigate_to_city(driver, city='chicago', config=config):
    """Utility function to navigate to different city page"""

    city_id = config.get("SiteCreds", "{}".format(city))
    url = config.get("SiteCreds", "base_url") + city_id

    driver.get(url)
    return True


def make_dict(list_data):
    """Utility function to transform list of field:value strings into dictionaries"""

    keys = [i.text.split(':')[0].strip() for i in list_data if len(i.text.split(':')) > 1]
    values = [i.text.split(':')[1].strip() for i in list_data if len(i.text.split(':')) > 1]

    return dict(zip(keys, values))


def get_provider_data(driver):
    """Function to fetch provider metadata from page and return dict with basic info"""

    provider_dictionary = defaultdict()
    name_tag = config.get('SiteTags', 'name_tag')
    id_tag = config.get('SiteTags', 'id_tag')
    info_tag = config.get('SiteTags', 'info_tag')
    details_tag = config.get('SiteTags', 'details_tag')
    website_tag = config.get('SiteTags', 'site_tag')

    # Get provider name and id
    provider_name = driver.find_element_by_xpath(f'//span[@id="{name_tag}"]').text
    provider_id = driver.find_element_by_class_name(f'{id_tag}').text.split(':')[1].strip()

    # Get provider info
    info_box = driver.find_element_by_class_name(f"{info_tag}")
    info_list = info_box.find_elements_by_tag_name("li")

    # Get provider details
    details_box = driver.find_element_by_class_name(f"{details_tag}")
    details_list = details_box.find_elements_by_tag_name("li")

    try:
        website = driver.find_element_by_xpath(f'//span[@id="{website_tag}"]').text
        provider_dictionary['website'] = website
    except:
        pass

    provider_dictionary['name'] = provider_name
    provider_dictionary['id'] = provider_id
    provider_dictionary['contact'] = make_dict(info_list)
    provider_dictionary['details'] = make_dict(details_list)

    time.sleep(2.1)

    return provider_dictionary


def iterate_over_providers(driver):
    """Function to iterate over list of provider links to fetch metatdata and reviews"""

    providers_tag = config.get('SiteTags', 'providers_tag')
    divs = driver.find_elements_by_xpath(f'//div[@class="{providers_tag}"]')
    providers_list = []

    for i in range(len(divs)):

        try:
            divs[i].find_element_by_css_selector('a').send_keys(Keys.RETURN)
            time.sleep(1.5)

            # Append provider metadata and reviews
            provider_data = get_provider_data(driver)
            provider_data['reviews'] = pagenate_all_reviews(driver)
            providers_list.append(provider_data)

            driver.execute_script("window.history.go(-1)")

        except StaleElementReferenceException:

            try:
                divs = driver.find_elements_by_xpath(f'//div[@class="{providers_tag}"]')
                divs[i].find_element_by_css_selector('a').send_keys(Keys.RETURN)

                time.sleep(2)

                # Append provider metadata and reviews
                provider_data = get_provider_data(driver)
                provider_data['reviews'] = pagenate_all_reviews(driver)
                providers_list.append(provider_data)

                driver.execute_script("window.history.go(-1)")

            except NoSuchElementException:
                try:
                    attempt_relogin(driver)
                except:
                    pass

            except WebDriverException:
                print(divs[i].find_element_by_css_selector('a').text, 'is not clickable')
                pass

    return providers_list


def attempt_relogin(driver):
    """Utility function to recover when scraping interrupted for login"""
    signup_form = config.get('SiteTags', 'signup_form')

    login_page = driver.find_element_by_xpath(f'//form[@id="{signup_form}"]')
    login_page.find_element_by_css_selector('a').send_keys(Keys.RETURN)
    time.sleep(1.3)
    login_site(driver)

    print('Recovered successfully!')


def get_review_data(driver):
    """Function to fetch review from page and return dict with basic info"""
    reviews_dict = defaultdict(dict)
    review_box_tag = config.get('SiteTags', 'review_box_tag')
    user_contain_tag = config.get('SiteTags', 'user_contain_tag')

    user = driver.find_element_by_class_name(f'{user_contain_tag}').find_element_by_css_selector('a')
    user_name = user.text
    user_url = user.get_attribute('href')

    review_box = driver.find_element_by_class_name(f'{review_box_tag}')
    review_elements = review_box.find_elements_by_class_name('width_100')

    reviews_dict['user_name'] = user_name
    reviews_dict['url'] = user_url
    reviews_dict['summary'] = review_elements[0].text
    reviews_dict['details'] = review_elements[1].text

    return reviews_dict


def get_all_provider_reviews(driver, page):
    """Function to fetch all reviews for specific provider"""

    review_tag = config.get('SiteTags', 'review_tag')
    full_review = config.get('SiteTags', 'full_review_tag')
    reviews = driver.find_elements_by_class_name(f'{review_tag}')

    all_reviews_dict = defaultdict(dict)

    for i in range(len(reviews)):

        try:
            date = reviews[i].find_element_by_css_selector('span').text
            reviews[i].find_element_by_class_name(f'{full_review}').send_keys(Keys.RETURN)

            reviews_dict = get_review_data(driver)
            reviews_dict['date'] = date
            all_reviews_dict[f'review_{(page*10) + (i+1)}'] = reviews_dict

            time.sleep(1.5)

            driver.execute_script("window.history.go(-1)")

        except StaleElementReferenceException:

            try:
                reviews = driver.find_elements_by_class_name(f'{review_tag}')
                reviews[i].find_element_by_class_name(f'{full_review}').send_keys(Keys.RETURN)

                reviews_dict = get_review_data(driver)
                reviews_dict['date'] = date
                all_reviews_dict[f'review_{(page*10) + (i+1)}'] = reviews_dict

                time.sleep(2)

                driver.execute_script("window.history.go(-1)")

            except NoSuchElementException:
                print('exception here!')
                try:
                    attempt_relogin(driver)
                except:
                    pass

    return all_reviews_dict


def pagenate_all_reviews(driver):

    all_reviews_dict = defaultdict(dict)
    paginate_tag = config.get('SiteTags', 'paginate_tag')

    # Check for multiple pages of reviews but assume only one
    try:
        pagination = driver.find_element_by_class_name(f'{paginate_tag}')
        pages = pagination.find_elements_by_css_selector("li")
        max_pages = int(pages[-2].text)
        print('Max pages:', max_pages)

    except NoSuchElementException:
        max_pages = 1

    current_page = 1

    while current_page <= max_pages:
        all_reviews_dict.update(get_all_provider_reviews(driver, page=current_page-1))

        if current_page < max_pages:
            next_page = current_page + 1
            pagination = driver.find_element_by_class_name(f'{paginate_tag}')
            pagination.find_element_by_partial_link_text(f"{str(next_page)}").send_keys(Keys.RETURN)

        current_page += 1

    # Get back to first page of provider reviews
    if max_pages > 1:
        for i in range(1, max_pages):
            driver.execute_script("window.history.go(-1)")

    return all_reviews_dict


def pagenate_all_providers(driver, max_pages=None):
    """Iterate over all pages, up to the max page number if provided, and return list of data for all providers"""
    providers_list = []
    paginate_tag = config.get('SiteTags', 'paginate_tag')

    if not max_pages:

        # Find total number of pages if max page num not provided
        try:
            pagination = driver.find_element_by_class_name(f'{paginate_tag}')
            pages = pagination.find_elements_by_css_selector("li")
            max_pages = int(pages[-2].text)
            print('Max pages:', max_pages)

        except NoSuchElementException:
            max_pages = 1

    current_page = 1

    while current_page <= max_pages:
        providers_list.extend(iterate_over_providers(driver))

        if current_page < max_pages:
            next_page = current_page + 1
            pagination = driver.find_element_by_class_name( f'{paginate_tag}')
            pagination.find_element_by_partial_link_text(f"{str(next_page)}").send_keys(Keys.RETURN)

        current_page += 1

    return providers_list

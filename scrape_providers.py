from selenium.webdriver.common.keys import Keys
import data_scrape_functions as dsf
import time

# Set Parameters
city_name = 'Chicago'
start_page = 31
max_pages = 2
save_interval = 1

driver = dsf.instantiate_driver(browser=True)
dsf.navigate_to_site(driver)
time.sleep(3)

driver.find_element_by_partial_link_text(city_name).send_keys(Keys.RETURN)

if start_page > 1:
    url = driver.current_url
    new_url = url + f'-{start_page}'
    driver.get(new_url)

providers_data = dsf.pagenate_all_providers(driver,
                                            max_pages=max_pages,
                                            save_interval_pages=save_interval)


from selenium.webdriver.common.keys import Keys
import data_scrape_functions as dsf

driver = dsf.instantiate_driver()
dsf.navigate_to_site(driver)
driver.find_element_by_partial_link_text("Chicago").send_keys(Keys.RETURN)
providers_data = dsf.pagenate_all_providers(driver, max_pages=10)


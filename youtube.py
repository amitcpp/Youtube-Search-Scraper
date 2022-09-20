import csv
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common import exceptions

# Create a Browser Instance Visible (Headless False)
def create_webdriver_instance():
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

# Inputting search query and clicking search button
def search_query(driver,query):
    # Going to the URL
    driver.get('https://www.youtube.com/')
    sleep(10)
    try:
        # Inputting the query in the search input 
        driver.find_element(By.XPATH, "//input[@id='search']").send_keys(query)
        # Sending the return key or enter button to search query
        driver.find_element(By.XPATH, "//button[@id='search-icon-legacy']").send_keys(Keys.RETURN)
    except exceptions.NoSuchElementException:
        # Returning None if searching fail's
        return None
    except exceptions.StaleElementReferenceException:
        return None
    else:
        # Returning True if search success
        return True

def scroll_down_page(driver, last_position, num_seconds_to_load=5, scroll_attempt=0, max_attempts=5):
    end_of_scroll_region = False
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region

def extract_links(driver):
    video_links = []
    last_position = None
    end_of_scroll_region = False
    sleep(5)
    while not end_of_scroll_region:
        try:
            ytd_video = driver.find_elements(By.TAG_NAME, 'ytd-video-renderer')
        except exceptions.NoSuchElementException:
            video_links = None
            return video_links
        except exceptions.StaleElementReferenceException:
            return None
        else:
            for ytd in ytd_video:
                try:
                    link = ytd.find_element(By.TAG_NAME, 'a').get_attribute('href')
                except exceptions.NoSuchElementException:
                    video_links.append(None)
                except exceptions.StaleElementReferenceException:
                    continue
                else:
                    if link not in video_links:
                        video_links.append(link)
            last_position, end_of_scroll_region = scroll_down_page(driver, last_position)
        print(len(video_links))
        if len(video_links) > 40:
            break
    return video_links

def extract_data_from_video(driver,link):
    link = link.replace('shorts','watch')
    driver.get(link)
    sleep(10)
    # Pause video
    driver.find_element(By.TAG_NAME, 'body').send_keys("k")
    sleep(10)
    data = []
    # Heading
    try:
        video_title = driver.find_element(By.XPATH, "//h1[@class='style-scope ytd-watch-metadata']").text
    except exceptions.NoSuchElementException:
        video_title = None
    except exceptions.StaleElementReferenceException:
        pass
    if video_title == None:
        try:
            video_title = driver.find_element(By.XPATH, "//h1[@class='title style-scope ytd-video-primary-info-renderer']").text
        except exceptions.NoSuchElementException:
            video_title = None
        except exceptions.StaleElementReferenceException:
            pass
        else:
            data.append(video_title)
    else:
        data.append(video_title)
        
    # Description
    try:
        driver.find_element(By.XPATH, "//tp-yt-paper-button[@id='expand']").click()
        sleep(2)
    except exceptions.NoSuchElementException:
        more_flag = False 
    except exceptions.StaleElementReferenceException:
        pass
    else:
        more_flag = True

    if more_flag == False:
        try:
            driver.find_element(By.XPATH, "//tp-yt-paper-button[@id='more']").click()
            sleep(10)
        except exceptions.NoSuchElementException:
            description = None 
        except exceptions.StaleElementReferenceException:
            pass
        else:
            description = driver.find_element(By.XPATH, '(//div[@id="description"])[2]').text
            data.append(description)
    else:
        description = driver.find_element(By.XPATH, '//div[@id="description-inner"]').text
        data.append(description)
    cleaned_data = clean_data(data,link)
    return cleaned_data
    

def save_data_to_csv(datas, filepath):
    data = []
    data.append(datas[0])
    data.append(datas[1])
    data.append(datas[2])
    data.append(datas[3])
    data.append(datas[4])
    with open(filepath, 'a+', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(datas)

def clean_data(data,link):
    cleaned_data = []
    cleaned_data.append(link)
    cleaned_data.append(data[0])
    cleaned_data.append(data[1][:data[1].find('views')]) 
    if "Premiered" in data[1]:
        date = data[1][(data[1].find('Premiered'))+10:(data[1].find('Premiered'))+22]
        cleaned_data.append(date)
    else:
        date = data[1][(data[1].find('views'))+6:(data[1].find('views'))+18]
        cleaned_data.append(date)
    cleaned_data.append(''.join(data[1].splitlines()))
    return cleaned_data

def main(filepath):
    query = "Elon Musk"
    driver = create_webdriver_instance()
    # Flagging if search was successful (True) and failed (None)
    search_query_flag = search_query(driver,query)
    if search_query_flag == True:
        # Extracting links in the current view
        video_links = extract_links(driver)
        for link in video_links:
            data = extract_data_from_video(driver,link)
            save_data_to_csv(data,filepath)
    sleep(5)
    driver.close() 


if __name__ == '__main__':
    path = 'Youtube.csv'
    main(path)

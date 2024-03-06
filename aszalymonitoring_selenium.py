import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from pymongo import MongoClient
from constant import CHROME_DRIVER_PATH, WEBSITE_URL, STATIONS, WORKERS
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import threading


num_cpu_cores = multiprocessing.cpu_count()
print(f"Number of CPU cores: {num_cpu_cores}")




def without_90_days(actual_date):
    actual_date = datetime.datetime.strptime(actual_date, '%Y-%m-%d').date()
    delta = datetime.timedelta(days=90)
    today_date_without_90_days = actual_date - delta
    start_date_string = today_date_without_90_days.strftime('%Y-%m-%d')
    return start_date_string

def select_option_by_text(driver, element_id, text):
    select = Select(driver.find_element(By.ID, element_id))
    select.select_by_visible_text(text)

def get_values(driver, type, weather_data):
    parameters = Select(driver.find_element(By.ID, "drought_parameter"))
    parameters.select_by_visible_text(type) 

    driver.find_element(By.XPATH, '/html/body/div[1]/form/div[2]/input').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="drought_chart_0_container"]/h1')))

    try: 
        driver.find_element(By.XPATH, '//*[@id="drought_chart_0_container"]/h1/div').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "drought_chart_0_tbl")))

        table = driver.find_element(By.ID, "drought_chart_0_tbl")
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")    

            date = cells[0].text
            if date not in weather_data:
                weather_data[date] = {}

            if cells[2].text != "-" or cells[1].text != "-" :
                weather_data[date][type] = cells[2].text
    except:
        print("No data for this period : "+weather_data)
 

def send_to_mongodb(station, weather_data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.weather_data

    # Créez une collection avec le nom de la station
    weather_collection = db[station]

    with lock:
        for date, data in weather_data.items():
            document = {
                "date": date,
                "data": data
            }
            weather_collection.insert_one(document)

    client.close()


def get_station_data(driver, station):
    try:
        weather_data = {}
        print(f"Processing station: {station}")

        select_option_by_text(driver, "drought_station", station)

        today_date = datetime.date.today().strftime('%Y-%m-%d')
        
        for i in range(4):   
 
            today_date_without_90_days = without_90_days(today_date)

            start_date = driver.find_element(By.NAME, "drought_startdate")
            start_date.clear()
            start_date.send_keys(today_date_without_90_days)

            end_date = driver.find_element(By.NAME, "drought_enddate")
            end_date.clear()
            end_date.send_keys(str(today_date))

            select_option_by_text(driver, "drought_interval", "napi")  # Add 'driver' as the first argument

            operation = Select(driver.find_element(By.ID, "drought_function"))
            operation.select_by_visible_text("minimum - átlag - maximum") 

            get_values(driver, "Levegőhőmérséklet (°C)", weather_data)
            get_values(driver, "Talajhőmérséklet(10 cm) (°C)", weather_data)
            get_values(driver, "Talajnedvesség(10 cm) (V/V %)", weather_data)
            get_values(driver, "Talajhőmérséklet(20 cm) (°C)", weather_data)
            get_values(driver, "Talajnedvesség(20 cm) (V/V %)", weather_data)
            get_values(driver, "Relatív páratartalom (%)", weather_data)
            get_values(driver, "Vízhiány(35 cm) (mm)", weather_data)
            get_values(driver, "Vízhiány(80 cm) (mm)", weather_data)

            today_date = today_date_without_90_days
            print(f"Finished processing {i + 1} iteration for station: {station}")
        send_to_mongodb(station, weather_data)
        
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(f"Error occurred while processing station {station}: {str(e)}\n")




def create_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chromedriver_path = CHROME_DRIVER_PATH
    s = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=s, options=chrome_options)

url = WEBSITE_URL
stations = STATIONS
lock = threading.Lock()


def process_station(station):
    print(station)
    driver = create_chrome_driver()
    driver.get(url)
    get_station_data(driver, station)
    driver.quit()

with ThreadPoolExecutor(max_workers=WORKERS) as executor:
    executor.map(process_station, stations)

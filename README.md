# Technical Documentation for a Selenium Scraper

This technical documentation covers creating a Python scraper using Selenium to extract weather data from the website **[https://aszalymonitoring.vizugy.hu/index.php?view=customgraph](https://aszalymonitoring.vizugy.hu/index.php?view=customgraph)** and store it in a local MongoDB database.

---

## **Prerequisites**

To run this script, you will need:

- Python 3.x
- The following libraries:
    - **`selenium`**
    - **`pymongo`**
    - **`concurrent.futures`**
- The **`constant.py`** file containing the necessary constants.
- The **`chromedriver`** file compatible with your web browser.

---

## **Installation**

Install the required libraries using pip:

```jsx
pip install selenium pymongo
```

---

## **Project Structure**

The project consists of two main files:

- **`aszalymonitoring_selenium.py`**: the main script for retrieving weather data.
- **`constant.py`**: a file containing constants used in the main script.

---

## **Usage**

1. Modify the **`constant.py`** file to include the correct path to the **`chromedriver`** file (add **`.exe`** if you are on Windows) and the list of stations for which you want to retrieve data.

```python
CHROME_DRIVER_PATH = "./chromedriver"  # add .exe if you are on Windows
WEBSITE_URL = "[https://aszalymonitoring.vizugy.hu/index.php?view=customgraph](https://aszalymonitoring.vizugy.hu/index.php?view=customgraph)"
STATIONS = ["Csolnok", "Tata", "Sződ", "Bernecebaráti", "Csókakő", "Pusztaszabolcs"]
WORKERS = 6 # Number of parallel executions
```

1. Run the **`aszalymonitoring_selenium.py`** script using the following command:

```python
python aszalymonitoring_selenium.py
```

1. The script will retrieve weather data for the stations specified in the **`constant.py`** file and store it in a local MongoDB database. Each station will have its own collection named after the station's name.

---

## **Script Functionality**

The script uses the Selenium library to navigate the website and interact with page elements. It retrieves air temperature, soil temperature, and soil humidity data for each station and stores it in a **`weather_data`** dictionary. The data is then sent to a local MongoDB database.

The main functions of the script are:

- **`without_90_days(actual_date)`**: calculates the date 90 days before the given date.
- **`select_option_by_text(driver, element_id, text)`**: selects an option from a **`select`** element based on the visible text.
- **`get_values(driver, type, weather_data)`**: retrieves weather values from the table on the page and stores them in the **`weather_data`** dictionary.
- **`send_to_mongodb(station, weather_data)`**: sends weather data to the local MongoDB database.
- **`get_station_data(driver, station)`**: retrieves weather data for a given station and stores it in the **`weather_data`** dictionary.
- **`create_chrome_driver()`**: creates a Chrome WebDriver instance with the specified options.
- **`process_station(station)`**: processes a station by creating a WebDriver, retrieving weather data, and then closing the WebDriver.
- The main loop of the script uses a ThreadPoolExecutor to manage workers (threads) and calls the **`process_station()`** function for each station.

---

## **Structure des données**

## **Data Structure**

The weather data is stored in a local MongoDB database. Each station has its own collection, named after the station's name.

The documents in the collections have the following structure:

- **`date`**: The date for which the weather data is retrieved (in the format 'YYYY-MM-DD').
- **`data`**: A dictionary containing the weather data for that date. The keys in this dictionary are the types of weather data (e.g., air temperature, soil temperature, soil humidity), and the values are the corresponding measurements.

Example document:

```python
{
    "date": "2023-03-26",
    "data": {
        "Levegőhőmérséklet (°C)": "12.5",
        "Talajhőmérséklet(10 cm) (°C)": "10.2",
        "Talajhőmérséklet(20 cm) (°C)": "9.8",
        "Talajnedvesség(10 cm) (V/V %)": "22.3",
        "Talajnedvesség(20 cm) (V/V %)": "21.8",
        "Relatív páratartalom (%)": "60",
        "Vízhiány(35 cm) (mm)": "10",
        "Vízhiány(80 cm) (mm)": "15"
    }
}
```

Note that the data keys are in Hungarian. You can replace them with their English equivalents if desired:

- "Levegőhőmérséklet (°C)": "Air temperature (°C)"
- "Talajhőmérséklet(10 cm) (°C)": "Soil temperature (10 cm) (°C)"
- "Talajnedvesség(10 cm) (V/V %)": "Soil moisture (10 cm) (V/V %)"
- "Talajhőmérséklet(20 cm) (°C)": "Soil temperature (20 cm) (°C)"
- "Talajnedvesség(20 cm) (V/V %)": "Soil moisture (20 cm) (V/V %)"
- "Relatív páratartalom (%)": "Relative humidity (%)"
- "Vízhiány(35 cm) (mm)": "Water deficit (35 cm) (mm)"
- "Vízhiány(80 cm) (mm)": "Water deficit (80 cm) (mm)"
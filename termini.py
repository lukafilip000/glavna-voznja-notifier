from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
from playsound import playsound

WEBSITE_URL = "https://e-uprava.gov.si/si/javne-evidence/prosti-termini.html#eyJwYWdlIjpbMF0sImZpbHRlcnMiOnsidHlwZSI6WyIxIl0sImNhdCI6WyI2Il0sIml6cGl0bmlDZW50ZXIiOlsiMTgiXSwibG9rYWNpamEiOlsiMjIzIl0sIm9mZnNldCI6WyI5MCJdLCJzZW50aW5lbF90eXBlIjpbIm9rIl0sInNlbnRpbmVsX3N0YXR1cyI6WyJvayJdLCJpc19hamF4IjpbIjEiXX0sIm9mZnNldFBhZ2UiOm51bGx9"

SOUND_FILE_PATH = 'notification.wav'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

def fetch_exam_dates(soup):
    dates = soup.find_all('div', class_='calendarDayNum js_calendarDayNum')
    days = soup.find_all('div', class_='calendarDayWeek js_calendarDayWeek')
    times = soup.find_all('span', class_='bold')

    times = [times[i] for i in range(3, len(times), 4)]

    exams = []
    for i in range(min(len(dates), len(days), len(times))):
        exams.append({
            'date': dates[i].get_text().strip(),
            'day': days[i].get_text().strip(),
            'time': times[i].get_text().strip()
        })
    
    return exams

def display_exam_times(exams, title, display_time):
    print(f"{HEADER}{BOLD}{title} {display_time}{ENDC}\n")
    for i, exam in enumerate(exams[:3]):
        print(f"{OKCYAN}{BOLD}Termin {i+1}:{ENDC} {OKGREEN}Datum:{ENDC} {exam['date']}, {OKGREEN}Dan:{ENDC} {exam['day']}, {OKGREEN}Čas:{ENDC} {exam['time']}")
    print("\n")

def check_for_updates(driver, last_exams):
    driver.get(WEBSITE_URL)
    time.sleep(5)  # Wait for the content to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_exams = fetch_exam_dates(soup)
    
    if len(current_exams) > len(last_exams):
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{WARNING}{BOLD}Nov Prost Termin!{ENDC}")
        playsound(SOUND_FILE_PATH)
        display_exam_times(current_exams, "Datum posodobitve:", update_time)
    
    return current_exams

driver.get(WEBSITE_URL)
time.sleep(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
exams = fetch_exam_dates(soup)

initial_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
display_exam_times(exams, "Datum Posodobitve:", initial_time)

while True:
    exams = check_for_updates(driver, exams)
    time.sleep(15)

driver.quit()

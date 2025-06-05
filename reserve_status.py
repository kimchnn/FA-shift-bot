from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc
import time
from datetime import datetime
import random
import chromedriver_autoinstaller
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from Config import USERNAME, PASSWORD, NAVBLUE_URL
from gspread_formatting import (
    set_frozen,
    format_cell_range,
    ConditionalFormatRule,
    BooleanRule,
    GradientRule,
    BooleanCondition,
    CellFormat,
    TextFormat,
    Color
)

chromedriver_autoinstaller.install()

START_ID = 13403
END_ID = 13424
SKIP_IDS = [13407, 13415, 13416, 13417, 13419, 13420, 13423]


def slow_type(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def create_stealth_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver


def login_to_navblue(driver):
    try:
        driver.get(NAVBLUE_URL)
        time.sleep(random.uniform(2,4))

        print("Logging in...")
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'MasterMain_txtUserName'))
        )
        slow_type(username_field, USERNAME)
        
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'MasterMain_txtPassword'))
        )
        slow_type(password_field, PASSWORD)
        
        password_field.send_keys(Keys.RETURN)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, 'linkAbout'))
        )
        print("Successfully logged in")
        return True
    except Exception as e:
        print(f"Login failed: {str(e)}")
        return False


def extract_schedule(driver):

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.roster-day'))
    )
    days = driver.find_elements(By.CSS_SELECTOR, 'div.roster-day')
    schedule = {}

    for day in days:
        try:
            week_day = day.find_element(By.CLASS_NAME, 'week-day').text.strip()
            day_number = day.find_element(By.CLASS_NAME, 'day-number').text.strip()
            date_label = f"{week_day} {day_number}"

            # Collect all .activity-info > .details text
            activity_info_blocks = day.find_elements(By.CSS_SELECTOR, 'div.activity-info')
            activities = []

            for block in activity_info_blocks:
                details = block.find_elements(By.CSS_SELECTOR, 'div.details')
                texts = [d.text.strip() for d in details if d.text.strip()]
                if texts:
                    activity_code = " ".join(texts)  # e.g., "F8806 0950 YVR YYC"
                    activities.append(activity_code)

            if not activities:
                value = "OFF"
            else:
                value = " | ".join(activities)

            schedule[date_label] = value

        except Exception as e:
            print(f"Error parsing day block: {e}")
            continue

    return schedule


def sort_by_day_number(date_str):
    # Assumes format like "MON 1", "TUE 15", etc.
    try:
        return int(date_str.split()[1])
    except (IndexError, ValueError):
        return 0  # fallback in case format breaks


def save_schedule_to_google_sheet(data, spreadsheet_name='Reserve Schedule'):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open or create the spreadsheet
    try:
        sheet = client.open(spreadsheet_name).sheet1
    except gspread.SpreadsheetNotFound:
        sheet = client.create(spreadsheet_name).sheet1

    all_dates = sorted({date for schedule in data.values() for date in schedule}, key=sort_by_day_number)
    header = ["Employee ID", "Name"] + all_dates
    # Compute grid size
    num_rows = 1 + len(data)  # 1 header + N employee rows
    num_cols = 2 + len(all_dates)  # 2 for ID + Name, rest are date columns

    # Build data rows
    rows = []
    for full_name, schedule in sorted(data.items(), key=lambda x: int(x[0].split()[0])):
        emp_id, *name_parts = full_name.split()
        name = " ".join(name_parts)
        row = [emp_id, name] + [schedule.get(date, "") for date in all_dates]
        rows.append(row)

    # Grid size includes 1 extra row for timestamp
    num_rows = 2 + len(data)  # 1 for timestamp, 1 for header, rest for data
    num_cols = 2 + len(all_dates)
    sheet.clear()
    sheet.resize(rows=num_rows, cols=num_cols)

    # 🕒 Write the timestamp in A1
    timestamp = datetime.now().strftime("Last updated: %B %d, %Y at %I:%M %p")
    sheet.update(values=[[timestamp]], range_name="A1")

    # ⬇ Push everything down by 1 row
    sheet.update(values=[header], range_name="A2")
    sheet.update(values=rows, range_name="A3")

    # Freeze header row and name columns
    set_frozen(sheet, rows=2, cols=2)

    # Format header row (row 2 now)
    header_format = CellFormat(textFormat=TextFormat(bold=True))
    header_range = f"A2:{chr(65 + len(header) - 1)}2"
    format_cell_range(sheet, header_range, header_format)

    # Format columns A & B (IDs + Names)
    id_name_format = CellFormat(textFormat=TextFormat(bold=True))
    format_cell_range(sheet, f"A2:A{num_rows}", id_name_format)
    format_cell_range(sheet, f"B2:B{num_rows}", id_name_format)

    print("Data written to Google Sheets.")


def get_filtered_employees(driver, start_id, end_id, skip_ids):
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'human-resources-dropdown-select-tag'))
    )
    options = dropdown.find_elements(By.TAG_NAME, 'option')
    employees = []

    for option in options:
        try:
            value_json = option.get_attribute('value')
            display_text = option.text.strip()
            if not value_json or not display_text:
                continue

            emp_id_str, *name_parts = display_text.split()
            emp_id = int(emp_id_str)

            if emp_id < start_id or emp_id > end_id or emp_id in skip_ids:
                continue

            full_display = f"{emp_id_str} {' '.join(name_parts)}"
            employees.append((emp_id_str, full_display))
        except Exception as e:
            print(f"Skipping invalid option: {e}")
            continue

    employees.sort(key=lambda x: int(x[0]))
    return employees


def select_employee_from_dropdown(driver, emp_id):
    time.sleep(random.uniform(0.5, 1.2))
    try:
        
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'human-resources-dropdown-select-tag'))
        )
        dropdown.click()
        time.sleep(random.uniform(0.3, 0.6))  

        option = dropdown.find_element(By.XPATH, f".//option[starts-with(normalize-space(text()), '{emp_id} ')]")
        option.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.roster-day'))
        )
        time.sleep(random.uniform(1.2, 2.0))
        return True
    except Exception as e:
        print(f"Failed to select employee {emp_id}: {e}")
        return False
    

def run_for_selected_employees(driver):
    all_data = {}
    employees = get_filtered_employees(
        driver, 
        start_id = START_ID, 
        end_id = END_ID, 
        skip_ids = SKIP_IDS)

    random.shuffle(employees)

    for emp_id, full_name in employees:
        print(f"\n🔄 Loading schedule for {full_name}...")
        if not select_employee_from_dropdown(driver, emp_id):
            continue

        delay = random.uniform(10, 15)
        schedule = extract_schedule(driver)
        all_data[full_name] = schedule

        # Scroll to simulate human reading the schedule
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_points = sorted(random.sample(range(200, scroll_height, 200), k=min(5, scroll_height // 200)))

        for y in scroll_points:
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(random.uniform(0.4, 1.0))
        
        # Simulate mouse movement by hovering over schedule items
        if random.random() < 0.7:
            activity_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.activity-info')
            for el in random.sample(activity_blocks, min(3, len(activity_blocks))):
                try:
                    ActionChains(driver).move_to_element(el).perform()
                    time.sleep(random.uniform(0.5, 1.2))
                except:
                    continue

        driver.execute_script("window.scrollTo(0, 0);") 

        delay = random.uniform(10, 15)
        print(f"✅ Collected. Waiting {delay:.1f}s before next...")
        time.sleep(delay)

    return all_data


def main():
    driver = None
    try:
        driver = create_stealth_driver()

        if not login_to_navblue(driver):
            print("Login failed.")
            return

        all_schedules = run_for_selected_employees(driver)
        save_schedule_to_google_sheet(all_schedules)

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()

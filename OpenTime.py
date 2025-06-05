from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyshadow.main import Shadow
import time
from Utils import (get_shadow_element, wait_for_shadow_selector)

def open_open_time(driver):
    print("Opening menu...")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'linkMenu'))).click()
    print("Clicked the yellow menu button.")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'tabMasterMenu')))
    driver.execute_script("window.scrollBy(0, 300);")
    dots = driver.find_elements(By.CLASS_NAME, 'touchslider-nav-item')
    if len(dots) >= 2:
        dots[1].click()
        time.sleep(1)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "OpenTime.aspx")]'))
    ).click()
    print("Navigated to Open Time.")


def go_to_daily_OT(driver):
    try:
        # Step 1: Wait for <x-open-times>
        x_open_times_host = WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'x-open-times'))
        )
        print("✅ <x-open-times> found")

        # Step 2: x-ot-current
        x_ot_current = wait_for_shadow_selector(driver, x_open_times_host, 'x-ot-current', timeout=30)
        print("✅ <x-ot-current> found")

        # Step 3: x-open-time-page
        x_open_time_page = wait_for_shadow_selector(driver, x_ot_current, 'x-open-time-page', timeout=30)
        print("✅ <x-open-time-page> found")

        # Step 4: x-open-time-menu
        x_open_time_menu = wait_for_shadow_selector(driver, x_open_time_page, 'x-open-time-menu', timeout=30)
        print("✅ <x-open-time-menu> found")

        # Step 5: Get nav inside x-open-time-menu's shadow root
        daily_ot_button = driver.execute_script("""
            const shadow = arguments[0].shadowRoot;
            return shadow?.querySelector('nav > div[data-num="1"]');
        """, x_open_time_menu)

        if daily_ot_button:
            daily_ot_button.click()
            print("🟢 Clicked Daily OT tab.")
            time.sleep(5)  
        else:
            print("❌ Could not find Daily OT tab.")

    except Exception as e:
        print(f"❌ Error while going to Daily OT: {e}")
        driver.save_screenshot("error_going_to_daily_OT.png")
        return 0

def check_available_OT_shifts(driver):
    print("\n--- Starting check_available_shifts ---")
    try:
        # Step 1: Wait for <x-open-times>
        x_open_times_host = WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'x-open-times'))
        )
        print("✅ <x-open-times> found")

        # Step 2: x-ot-daily
        x_ot_daily = wait_for_shadow_selector(driver, x_open_times_host, 'x-ot-daily', timeout=30)
        print("✅ <x-ot-daily> found")

        # Step 3: x-open-time-page
        x_open_time_page = wait_for_shadow_selector(driver, x_ot_daily, 'x-open-time-page', timeout=30)
        print("✅ <x-open-time-page> found")

        # Step 4: slot[name="main"]
        slot_main = wait_for_shadow_selector(driver, x_open_time_page, 'slot[name="main"]', timeout=30)
        print("✅ <slot name='main'> found")

        # Step 5: Get <div slot="main"> from assignedElements()
        div_main = driver.execute_script("""
            const slot = arguments[0];
            const assigned = slot?.assignedElements?.() || [];
            return assigned.find(el => el.tagName === 'DIV' && el.getAttribute('slot') === 'main') || null;
        """, slot_main)

        if not div_main:
            raise Exception("<div slot='main'> not found via slot assignment.")
        print("✅ <div slot='main'> found via slot")

        # Step 6: Get <x-roster-open-time> inside that div
        x_roster_open_time = driver.execute_script(
            "return arguments[0].querySelector('x-roster-open-time')",
            div_main
        )
        if not x_roster_open_time:
            raise Exception("<x-roster-open-time> not found inside div[slot='main']")
        print("✅ <x-roster-open-time> found")

        shift_count = driver.execute_script("""
            const el = arguments[0];
            if (!el || !el.shadowRoot) return -1;
            return el.shadowRoot.querySelectorAll('x-ot-roster-item')?.length || 0;
        """, x_roster_open_time)

        if shift_count < 0:
            raise Exception("Unable to access shadowRoot or roster items.")
        else:
            print(f"🟢 Found {shift_count} shift(s).")
            return shift_count

    except Exception as e:
        print(f"❌ Error during shift check: {e}")
        driver.save_screenshot("error_checking_shifts.png")
        return 0

# # def check_available_shifts(driver):
#     """
#     Checks for x-ot-roster-item elements by navigating through the Shadow DOM
#     and resolving slotted <x-roster-open-time> from <slot name="content">.
#     """
#     print("\n--- Starting check_available_shifts ---")
#     try:
#         # Step 1: Wait for <x-open-times>
#         x_open_times_host = WebDriverWait(driver, 90).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, 'x-open-times'))
#         )
#         print("✅ <x-open-times> found")

#         # Step 2: x-ot-current
#         x_ot_current = wait_for_shadow_selector(driver, x_open_times_host, 'x-ot-current', timeout=30)
#         print("✅ <x-ot-current> found")

#         # Step 3: x-open-time-page
#         x_open_time_page = wait_for_shadow_selector(driver, x_ot_current, 'x-open-time-page', timeout=30)
#         print("✅ <x-open-time-page> found")

#         # Step 4: slot[name="main"]
#         slot_main = wait_for_shadow_selector(driver, x_open_time_page, 'slot[name="main"]', timeout=30)
#         print("✅ <slot name='main'> found")

#         # Step 5: Get <div slot="main"> from assignedElements()
#         div_main = driver.execute_script("""
#             const slot = arguments[0];
#             const assigned = slot?.assignedElements?.() || [];
#             return assigned.find(el => el.tagName === 'DIV' && el.getAttribute('slot') === 'main') || null;
#         """, slot_main)

#         if not div_main:
#             raise Exception("<div slot='main'> not found via slot assignment.")
#         print("✅ <div slot='main'> found via slot")

#         # Step 6: Get <x-roster-open-time> inside that div
#         x_roster_open_time = driver.execute_script(
#             "return arguments[0].querySelector('x-roster-open-time')",
#             div_main
#         )
#         if not x_roster_open_time:
#             raise Exception("<x-roster-open-time> not found inside div[slot='main']")
#         print("✅ <x-roster-open-time> found")

#         shift_count = driver.execute_script("""
#             const el = arguments[0];
#             if (!el || !el.shadowRoot) return -1;
#             return el.shadowRoot.querySelectorAll('x-ot-roster-item')?.length || 0;
#         """, x_roster_open_time)

#         if shift_count < 0:
#             raise Exception("Unable to access shadowRoot or roster items.")
#         else:
#             print(f"🟢 Found {shift_count} shift(s).")
#             return shift_count

#     except Exception as e:
#         print(f"❌ Error during shift check: {e}")
#         driver.save_screenshot("error_checking_shifts.png")
#         return 0
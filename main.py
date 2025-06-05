from Setup import create_stealth_driver, login_to_navblue
from OpenTime import (open_open_time, check_available_OT_shifts, go_to_daily_OT)
from Notification import send_discord_alert
from Config import WEBHOOK_URL
import time

# def check_current_roster_shifts(driver):
    # try:
    #     print("📋 Checking Current Roster...")
    #     shift_count = check_available_shifts(driver)
        
    #     if shift_count > 0:
    #         message = f"🚁 **Current Roster Alert!**\n\nFound {shift_count} available shifts in Current Roster!"
    #         send_discord_alert(WEBHOOK_URL)
    #         print(f"✅ Current Roster: {shift_count} shifts found - Discord alert sent!")
    #     else:
    #         print("ℹ️ Current Roster: No shifts found.")
            
    #     return shift_count
        
    # except Exception as e:
    #     print(f"❌ Error checking Current Roster: {e}")
    #     return 0
    
def check_daily_OT_shifts(driver):
    try:
        print("Checking Daily OT...")
        shift_count = check_available_OT_shifts(driver)
        
        if shift_count > 0:
            message = f"**Open Time Alert!**\n\nFound {shift_count} available shifts in Daily OT!"
            send_discord_alert(WEBHOOK_URL)
            print(f"Daily OT: {shift_count} shifts found - Discord alert sent!")
        else:
            print("Current Roster: No shifts found.")
            
        return shift_count
        
    except Exception as e:
        print(f"Error checking Current Roster: {e}")
        return 0

def main():
    driver = None
    try:
        print("Starting NavBlue shift checker...")
        driver = create_stealth_driver()
        login_to_navblue(driver)
        open_open_time(driver)
        go_to_daily_OT(driver)
        
        # total_shifts = check_current_roster_shifts(driver)
        total_shifts = check_daily_OT_shifts(driver)
        
        if total_shifts > 0:
            print(f"Total: {total_shifts} shifts found in Daily OT!")
        else:
            print("No shifts found.")
        
        print("All checks completed.")
        time.sleep(5)
        
    except Exception as e:
        error_msg = f"Script error: {str(e)}"
        print(error_msg)
        
        if driver:
            driver.save_screenshot("error.png")
        
        try:
            error_message = f"**NavBlue Script Error:**\n```{str(e)}```\n\nCheck the error.png screenshot for details."
            send_discord_alert(WEBHOOK_URL)
        except:
            print("Failed to send error notification to Discord")
            
    finally:
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
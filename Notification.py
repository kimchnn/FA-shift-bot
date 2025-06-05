import requests

def send_discord_alert(webhook_url):
    """
    Sends a notification message to a Discord webhook.

    Args:
        webhook_url (str): The full Discord webhook URL to send the message to.

    Returns:
        bool: True if the message was successfully sent, False otherwise.
    """

    message = "**Open Time Shifts Found!**\n\nCheck Navblue to pick them up."

    try:
        response = requests.post(webhook_url, json={"content": message}, timeout=10)
        if response.status_code == 204:
            print("Discord notification sent!")
            return True
        else:
            print("Discord error:", response.status_code, response.text)
            return False
    except Exception as e:
        print("Failed to send Discord alert:", e)
        return False
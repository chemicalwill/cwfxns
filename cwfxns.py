import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

import praw
import pyinputplus as pyip
from twilio.base.exceptions import TwilioRestException
import twilio.rest


def find_alt_firefox_profile(profile_name):
    """
    Returns the file path of a specific Firefox profile

        Params:
            profile_name (string): the target profile

        Returns:
            profile_path (Path): full path object of the target profile
    """
    if sys.platform.startswith("win"):
        profiles_dir = Path.home() / Path("AppData/Roaming/Mozilla/Firefox/Profiles")
    elif sys.platform.startswith("linux"):
        profiles_dir = Path.home() / Path(".mozilla/firefox/")
    for profile in os.listdir(profiles_dir):
        if profile.endswith(profile_name):
            profile_path = profiles_dir / Path(profile)
            return profile_path
    # print the available profiles if profile_name doesn't exist
    #   trim off the period, and exit the program
    print(f"Could not find profile '{profile_name}'. Available profiles:")
    for profile in os.listdir(profiles_dir):
        leading_str, profile_name = os.path.splitext(profile)
        print(f" - {profile_name[1:]}")
    press_enter_to_quit()


def get_random_reddit_post(subreddit):
    """
    Scrapes a random post from a subreddit.
    (Requires the appropriate environment variables to be configured for praw)

        Parameters:
            subreddit (string): the subreddit to scrape from

        Returns:
            random_submission (praw.Submission()): random post from subreddit

    """
    PRAW_CLIENT_ID = os.getenv("PRAW_CLIENT_ID")
    PRAW_CLIENT_SECRET = os.getenv("PRAW_CLIENT_SECRET")
    PRAW_USER_AGENT = os.getenv("PRAW_USER_AGENT")

    REDDIT = praw.Reddit(
        client_id=PRAW_CLIENT_ID,
        client_secret=PRAW_CLIENT_SECRET,
        user_agent=PRAW_USER_AGENT,
    )

    random_submission = REDDIT.subreddit(subreddit).random()
    return random_submission


def nordvpn(region=None, country=None):
    """
    Connects to a NordVPN server

        Params:
            region (string): 2-letter continent abbreviation in ('AF', 'AS', 'EU', 'NA', 'OC', 'SA')
            country (string): either name or ISO 3166-1 alpha-2 code (ex. 'Mexico' or 'mx')

        Raises:
            SyntaxError: if both 'region' and 'country' kwargs are passed, raises a SyntaxError

        Example:
            >>> nordvpn(region='NA')
            >>> nordvpn(country='mx')
            >>> nordvpn(country='Mexico')
    """
    server_dict = {
        "AF": {
            "South Africa": "za",
        },
        "AS": {
            "Cyprus": "cy",
            "Georgia": "ge",
            "Hong Kong": "hk",
            "India": "in",
            "Indonesia": "id",
            "Israel": "il",
            "Japan": "jp",
            "Malaysia": "my",
            "Singapore": "sg",
            "South Korea": "kr",
            "Taiwan": "tw",
            "Thailand": "th",
            "United Arab Emirates": "ae",
            "Vietnam": "vn",
        },
        "EU": {
            "Albania": "al",
            "Austria": "at",
            "Belgium": "be",
            "Bosnia and Herzegovina": "ba",
            "Bulgaria": "bg",
            "Croatia": "hr",
            "Czech Republic": "cz",
            "Denmark": "dk",
            "Estonia": "ee",
            "Finland": "fi",
            "France": "fr",
            "Germany": "de",
            "Greece": "gr",
            "Hungary": "hu",
            "Iceland": "is",
            "Ireland": "ie",
            "Italy": "it",
            "Latvia": "lv",
            "Lithuania": "lt",
            "Luxembourg": "lu",
            "Moldova": "md",
            "Netherlands": "nl",
            "North Macedonia": "mk",
            "Norway": "no",
            "Poland": "pl",
            "Portugal": "pt",
            "Romania": "ro",
            "Serbia": "rs",
            "Slovakia": "sk",
            "Slovenia": "si",
            "Spain": "es",
            "Sweden": "se",
            "Switzerland": "ch",
            "Turkey": "tr",
            "Ukraine": "ua",
            "United Kingdom": "gb",
        },
        "NA": {
            "Canada": "ca",
            "Costa Rica": "cr",
            "Mexico": "mx",
            "United States": "us",
        },
        "SA": {
            "Argentina": "ar",
            "Brazil": "br",
            "Chile": "cl",
        },
        "OC": {
            "Australia": "au",
            "New Zealand": "nz",
        },
    }

    if region and country:
        raise SyntaxError(f"Both 'region' and 'country' kwargs passed.")
    elif region:
        region = region.upper()
        server_dict = server_dict[region]
    elif country:
        if len(country) == 2:
            country = country.lower()
        country_dict = {}
        for ser in server_dict.values():
            country_dict.update(ser)
        server_dict = country_dict
    else:
        random_region = random.choice(tuple(server_dict.keys()))
        server_dict = server_dict[random_region]

    _OS = platform.system()
    if _OS == "Windows":
        if country:
            if country not in server_dict.keys():
                country = [
                    name for name, abbrev in server_dict.items() if country == abbrev
                ].pop()
        else:
            country = random.choice(tuple(server_dict.keys()))
        # passing the command 'nordvpn' requires being in 'C:\Program Files\NordVPN'
        #   I don't like using os.chdir() for a shell command, so I added it to Windows PATH
        #       you can either add the NordVPN folder to PATH or uncomment the next line
        # os.chdir("C:\Program Files\NordVPN")
        command = f"nordvpn -c {country}".split()

    elif _OS in ("Linux", "Darwin"):
        if country:
            if country not in server_dict.values():
                country = [
                    abbrev for name, abbrev in server_dict.items() if country == name
                ].pop()
        else:
            country = random.choice(tuple(server_dict.values()))
        command = f"nordvpn c {country}".split()

    subprocess.run(command, stdout=subprocess.DEVNULL)
    time.sleep(10)
    return


def press_enter_to_quit(command=None):
    """
    Prompts the user to press Enter/Return and exits the terminal

        Params:
            command (string): optional system command to execute prior to quitting

        Example:
            >>> press_enter_to_quit(command='nordvpn -d')

            Press ENTER to quit...
            #   and will disconnect from nordvpn on exit
    """
    input("\nPress ENTER to quit...")
    if command:
        subprocess.run(command.split(), stdout=subprocess.DEVNULL)
    sys.exit()


def select_browser():
    """
    Checks to see if geckodriver, chromedriver or both are in PATH.
    If both are present, asks the user to choose one.
    If neither are present, quits.

        Returns:
            webdriver (string): either "firefox" or "chrome"
    """
    path_dirs = os.getenv("PATH").split(os.pathsep)
    webdrivers = []
    for path_dir in path_dirs:
        geckodriver_path = Path(path_dir) / "geckodriver"
        chromedriver_path = Path(path_dir) / "chromedriver"

        if sys.platform.startswith("win"):
            geckodriver_path = geckodriver_path.parent / (
                geckodriver_path.name + ".exe"
            )
            chromedriver_path = chromedriver_path.parent / (
                chromedriver_path.name + ".exe"
            )

        if geckodriver_path.is_file():
            webdrivers.append("firefox")
        if chromedriver_path.is_file():
            webdrivers.append("chrome")

    if not webdrivers:
        print("Neither geckodriver nor chromedriver were found in PATH")
        print("Please install a web driver to PATH and try again.")
        press_enter_to_quit()

    if "firefox" in webdrivers and "chrome" in webdrivers:
        print(
            ("Multiple web drivers were found in PATH."),
            ("Which browser would you like to use?"),
        )
        choice = pyip.inputMenu(["Firefox", "Chrome"], numbered=True)
        return choice.lower()

    return webdrivers.pop()


def send_twilio_message(message=None, media_url=None, number=None):
    """
    Sends an SMS/MMS via twilio. Won't send unless either 'message' or 'media_url' is provided.
    See https://automatetheboringstuff.com/2e/chapter18/ for information on how to set up a free twilio account.
    Fails silently if environment variables are not set.

        Parameters:
            message (string): the text message body (defaults to None)
            media_url (string): the optional media/MMS url (defaults to None)
            number (string): recipient phone number, including country and area codes (ex. '+11238675309', defaults to None)

        These environment variables must be set:
            TWILIO_ACCOUNT_SID (string): twilio account SID
            TWILIO_AUTH_TOKEN (string): twilio auth token
            TWILIO_PHONE_NUMBER (string): twilio phone number, including country and area codes (ex. '+11238675309')
            MY_CELL_NUMBER (string): your cell number, including country and area codes (ex. '+11238675309')
                - if MY_CELL_NUMBER is set and no recipient is specified, param number will default to MY_CELL_NUMBER
    """

    if message or media_url:
        try:
            TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
            TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
            TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

            if not number:
                MY_CELL_NUMBER = os.getenv("MY_CELL_NUMBER")
                number = MY_CELL_NUMBER

            TWILIO_CLIENT = twilio.rest.Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            TWILIO_CLIENT.messages.create(
                body=message,
                media_url=[media_url],
                from_=TWILIO_PHONE_NUMBER,
                to=number,
            )

        except TwilioRestException:
            pass


def show_header(title_string):
    """
    Prints an uppercase header with asterisks.

        Parameters:
            title_string (string): the program's name/title

        Example:
            show_header("some title")
            **************
            * SOME TITLE *
            **************
    """
    title = f"* {title_string.upper()} *"
    bar = "*" * len(title)
    print(bar)
    print(title)
    print(bar)

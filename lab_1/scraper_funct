# Scraper functions
# PRIMARY DATA STRUCTURE: List of ArtEntry objects containing all scraped art entries and their individual data
#
# all_art_entries[] -> ArtEntry -> artwork_list[] -> Artwork -> img_src ""
#                             -> date ""                   -> img_alt ""
#                             -> source_title ""
#                             -> source_img_list[]  -> Artwork -> img_src ""
#
#                                                          -> img_alt ""

import csv
import pickle
import requests

import PySimpleGUI as sg
from bs4 import BeautifulSoup
from typing import List, Optional

from art_work import Artwork
from art_entry import ArtEntry


all_art_entries: List[ArtEntry] = []


def use_scraper() -> None:
    """
    Prompts the user to choose between using previously stored data or rescraping data.

    If the user chooses to rescrape, it calls the run_scraper function.
    """
    # Theme
    sg.theme("DarkGrey4")

    choice: Optional[str] = sg.popup_yes_no(
        "Do you want to use previously stored data?",
        "Selecting \"No\" will take several minutes to update all stored entries.",
        "",
        title="JoJo's Art Scraper and Viewer"
    )

    if choice == "No":
        run_scraper()


def format_img_list(img_list: List[str]) -> str:
    """
    Formats a list of image sources into a multi-line string for CSV formatting.

    Args:
        img_list (List[str]): List of image links or alt texts.

    Returns:
        str: A formatted string where each entry is on a new line.
    """
    formatted_str: str = ""

    for string in img_list:
        formatted_str += string + "\n"

    return formatted_str


def fetch_page(url: str) -> Optional[str]:
    """
    Fetches the content of a webpage.

    Args:
        url (str): The URL of the webpage to fetch.

    Returns:
        Optional[str]: The HTML content of the page if successful, None otherwise.
    """
    session = requests.Session()
    page = session.get(url)

    if page.status_code == 200:
        print("Successful Connection")
        return page.text
    else:
        print("Unsuccessful Connection")
        return None


def parse_art_entries(soup: BeautifulSoup) -> List[ArtEntry]:
    """
    Parses art entries from the BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML content.

    Returns:
        List[ArtEntry]: A list of ArtEntry objects parsed from the soup.
    """
    divs = soup.find("div", {"class": "phantom-blood-tabs"})
    entries = divs.find_all("table", {"class": "diamonds volume"})
    art_entries = []

    for entry in entries:
        art_entry_obj = extract_art_entry(entry)
        art_entries.append(art_entry_obj)

    return art_entries


def extract_art_entry(entry) -> ArtEntry:
    """
    Extracts an ArtEntry object from a given HTML entry.

    Args:
        entry: The HTML entry to extract data from.

    Returns:
        ArtEntry: An ArtEntry object containing extracted data.
    """
    sections = entry.find_all("td", {"class": "volume"})
    artwork_list: List[str] = []
    source_img_list: List[str] = []
    
    art_entry_obj = ArtEntry([], "", "", [])
    
    for section_counter, section in enumerate(sections, start=1):
        if section_counter in [1, 4]:
            process_image_section(section, section_counter, art_entry_obj, artwork_list, source_img_list)
        elif section_counter in [2, 3]:
            process_text_section(section, section_counter, art_entry_obj)

    return art_entry_obj

def process_image_section(section, section_counter: int, art_entry_obj: ArtEntry, artwork_list: List[str], source_img_list: List[str]) -> None:
    """
    Processes the image section of an art entry.

    Args:
        section: The HTML section containing image links.
        section_counter (int): The index of the section being processed.
        art_entry_obj (ArtEntry): The ArtEntry object to populate with image data.
        artwork_list (List[str]): List to store artwork links.
        source_img_list (List[str]): List to store source image links.
    """
    thumbnails = section.find_all("a")
    
    for thumbnail in thumbnails:
        href: Optional[str] = thumbnail.get("href")
        new_url: str = f"https://jojowiki.com{href}"
        new_page_text = fetch_page(new_url)

        if new_page_text:
            new_soup = BeautifulSoup(new_page_text, "lxml")
            media = new_soup.find("div", {"id": "file"}).find("img")
            src = media.get("src")
            alt = media.get("alt")

            if section_counter == 1:
                artwork_obj = Artwork(src, alt)
                art_entry_obj.artwork_list.append(artwork_obj)
                artwork_list.append(f"<src: {src}\nalt: {alt}>")
            elif section_counter == 4:
                src_img_obj = Artwork(src, alt)
                art_entry_obj.source_img_list.append(src_img_obj)
                source_img_list.append(f"<src: {src}\nalt: {alt}>")

def process_text_section(section, section_counter: int, art_entry_obj: ArtEntry) -> None:
    """
    Processes the text content of an HTML section and updates the ArtEntry object.

    Args:
        section: The HTML section containing text content.
        section_counter (int): The index of the section being processed.
        art_entry_obj (ArtEntry): The ArtEntry object to populate with text data.
    """
    text_content = section.find("center")
    
    for string in text_content.strings:
        if section_counter == 2:
            art_entry_obj.date += string
        elif section_counter == 3:
            art_entry_obj.source_title += string


def save_to_csv(entries: List[ArtEntry]) -> None:
    """
    Saves a list of ArtEntry objects to a CSV file.

    Args:
        entries (List[ArtEntry]): The list of ArtEntry objects to save.
    """
    with open("entries.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ARTWORK", "DATE", "SOURCE TITLE", "SOURCE IMAGE"])
        
        for entry in entries:
            writer.writerow([
                format_img_list(entry.artwork_list),
                entry.date,
                entry.source_title,
                format_img_list(entry.source_img_list)
            ])


def save_to_pickle(entries: List[ArtEntry]) -> None:
    """
    Saves a list of ArtEntry objects to a pickle file.

    Args:
        entries (List[ArtEntry]): The list of ArtEntry objects to save.
    """
    with open("artEntriesData.p", "wb") as file:
        pickle.dump(entries, file)


def run_scraper() -> None:
    """
    Runs the web scraper to fetch art gallery data, parse it, and save it to CSV and pickle files.
    """
    URL = "https://jojowiki.com/Art_Gallery#2021-2025-0"
    page_text = fetch_page(URL)
    
    if page_text:
        soup = BeautifulSoup(page_text, "lxml")
        all_art_entries = parse_art_entries(soup)
        save_to_csv(all_art_entries)
        save_to_pickle(all_art_entries)

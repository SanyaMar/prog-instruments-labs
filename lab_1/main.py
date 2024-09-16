"""
Scraping
    import lxml for html parser
    import cchardet for character reading
    import PySimpleGUI and urllib.request for GUI
    from PIL import Image and import io for GUI JPG Image processing
"""

import cchardet
import lxml
import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Any

import csv
import pickle

import PySimpleGUI as sg
import urllib.request

import io
from PIL import Image

# Class Objects
class Artwork:
    """
    Represents an artwork with its source link and alt text.

    Attributes:
        img_src (str): The URL of the artwork image.
        img_alt (str): The alt text for the artwork image.
    """

    img_src: str = ""
    img_alt: str = ""

    def __init__(self, img_src: str, img_alt: str) -> None:
        """
        Initializes the Artwork object with image source and alt text.

        Args:
            img_src (str): The URL of the artwork image.
            img_alt (str): The alt text for the artwork image.
        """
        self.img_src = img_src
        self.img_alt = img_alt


class ArtEntry:
    """
    Represents an entry of artwork including its details.

    Attributes:
        artwork_list (list): List of Artwork objects associated with this entry.
        date (str): The date associated with the artwork entry.
        source_title (str): The title of the source from which the artwork is taken.
        source_img_list (list): List of Artwork objects representing source images.
    """

    artwork_list: List[Artwork] = []
    date: str = ""
    source_title: str = ""
    source_img_list: List[Artwork] = []

    def __init__(self, artwork_list: List[Artwork], date: str, source_title: str, source_img_list: List[Artwork]) -> None:
        """
        Initializes the ArtEntry object with details of the artwork entry.

        Args:
            artwork_list (list): List of Artwork objects.
            date (str): The date associated with the entry.
            source_title (str): The title of the source.
            source_img_list (list): List of Artwork objects for source images.
        """
        self.artwork_list = artwork_list
        self.date = date
        self.source_title = source_title
        self.source_img_list = source_img_list

    def __repr__(self) -> str:
        """
        Returns a string representation of the ArtEntry object.
        """
        return f"{self.source_title}"


# Scraper functions
# PRIMARY DATA STRUCTURE: List of ArtEntry objects containing all scraped art entries and their individual data
#
# all_art_entries[] -> ArtEntry -> artwork_list[] -> Artwork -> img_src ""
#                             -> date ""                   -> img_alt ""
#                             -> source_title ""
#                             -> source_img_list[]  -> Artwork -> img_src ""
#                                                         -> img_alt ""

all_art_entries: List[ArtEntry] = []


def use_scraper() -> None:
    """
    Prompts the user to choose between using previously stored data or rescraping data.

    If the user chooses to rescrape, it calls the runScraper function.
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
        img_list: List of image links or alt texts.

    Returns:
        str: A formatted string where each entry is on a new line.
    """
    formatted_str: str = ""

    for string in img_list:
        formatted_str += string
        formatted_str += "\n"

    return formatted_str


# Scraper
def run_scraper() -> None:
    """
    Requests page content from a specified URL, scrapes art entries, 
    and stores the data in a list and a CSV file.
    """
    # GET Request
    URL: str = "https://jojowiki.com/Art_Gallery#2021-2025-0"
    requests_session = requests.Session()
    page = requests_session.get(URL)

    # Check for successful status code (200)
    print("Status Code - {}".format(page.status_code))
    if page.status_code == 200:
        print("Successful Connection")
    else:
        print("Unsuccessful Connection")

    # HTML Parser
    soup = BeautifulSoup(page.text, "lxml")
    divs = soup.find("div", {"class": "phantom-blood-tabs"})
    entries = divs.find_all("table", {"class": "diamonds volume"})

    # Initialize writer and csv file
    with open("entries.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ARTWORK", "DATE", "SOURCE TITLE", "SOURCE IMAGE"])

    # Scrapes every artwork entry on the page
    for entry in entries:
        # Initializes each subsection of an artwork entry
        sections = entry.find_all("td", {"class": "volume"})
        artwork_list: List[str] = []
        date: str = ""
        source_title: str = ""
        source_img_list: List[str] = []

        art_entry_obj = ArtEntry([], "", "", [])
        artwork_obj = Artwork("", "")
        src_img_obj = Artwork("", "")

        # Iterates through each subsection and row of csv, and writes to csv with scraped data
        section_counter: int = 1
        for section in sections:
            # If on a subsection containing images (1 and 4), scrape image content
            if (section_counter == 1 or section_counter == 4):
                thumbnails = section.find_all("a")

                # For every thumbnail image, find full-res webpage and create new
                for thumbnail in thumbnails:
                    # Grabs href for full-res image webpage from thumbnail container
                    href: Optional[str] = thumbnail.get("href")
                    new_url: str = f"https://jojowiki.com{href}"

                    # Temporary HTML parser to scrape full-res image
                    new_requests_session = requests.Session()
                    new_page = new_requests_session.get(new_url)
                    new_soup = BeautifulSoup(new_page.text, "lxml")

                    # Stores preview image, as full resolution images are too large
                    media = new_soup.find("div", {"id": "file"}).find("img")
                    src = media.get("src")
                    alt = media.get("alt")

                    if (section_counter == 1):
                        # Stores in all_art_entries list
                        artwork_obj = Artwork(src, alt)
                        art_entry_obj.artwork_list.append(artwork_obj)

                        # Stores in CSV
                        artwork_list.append(
                            "<src: " + src + "\nalt: " + alt + ">")

                    elif (section_counter == 4):
                        # Stores in all_art_entries list
                        src_img_obj = Artwork(src, alt)
                        art_entry_obj.source_img_list.append(src_img_obj)
                        source_img_list.append(
                            "<src: " + src + "\nalt: " + alt + ">")

            # If on a subsection containing text (2 and 3), scrape text content
            elif (section_counter == 2 or section_counter == 3):
                # Text content is stored within <center> tags
                text_content = section.find("center")

                for string in text_content.strings:
                    if (section_counter == 2):
                        date += string
                    elif (section_counter == 3):
                        source_title += string

            # After scraping subsection, update tracker to next
            section_counter += 1

        # Appends artEntry to list all_art_entries
        art_entry_obj.date = date
        art_entry_obj.source_title = source_title
        all_art_entries.append(art_entry_obj)

        # Writes to csv file, formatting the image lists into formatted strings
        writer.writerow([format_img_list(artwork_list), date,
                        source_title, format_img_list(source_img_list)])
        pickle.dump(all_art_entries, open("artEntriesData.p", "wb"))

    file.close()


def main() -> None:
    """ 
    Asks user to use stored data or scrape  
    """
    run_scraper()


if __name__ == "__main__":
    main()


# GUI functions
def open_url(src: str) -> Optional[urllib.response.urlopen]:
    """
    The function takes the URL of the image and opens it.
    Spoofing headers are used to bypass the 403: Forbidden error.

    Args:
        src (str): URL of the image.

    Returns:
        n object of type urllib.response.urlopen or None in case of an error.
    """
    try:
        req = urllib.request.Request(
            src, headers={"User-Agent": "Magic Browser"})
        return urllib.request.urlopen(req)
    except Exception as e:
        print(f"Error encountered in open_url() with src: '{src}': {e}")


def return_img_data(url: str) -> Optional[bytes]:
    """
    The function returns image data depending on its type (PNG or JPG).

    Args:
        url (str): URL of the image.

    Returns:
        The image data is in PNG format or None if the image failed to load.
    """
    # If img_src is a png, update window using urllib
    if ".png" in url:
        return open_url(url).read()

    # If img_src is a jpg, update window using Pillow
    elif ".jpg" in url:
        # Creates PIL img from scraped jpg data, converts into png data
        pil_img = Image.open(io.BytesIO(open_url(url).read()))
        png_bio = io.BytesIO()
        pil_img.save(png_bio, format="PNG")
        png_data = png_bio.getvalue()
        return png_data


# GUI
all_art_entries: List[str] = pickle.load(open("artEntriesData.p", "rb"))

check_boxes: List[sg.Radio] = []
check_boxes.append(sg.Radio("Arts", "faculty", key="arts",
                   enable_events=True, default=True))
check_boxes.append(sg.Radio("Commerce", "faculty",
                   key="comm", enable_events=True))

# List of Entries
entry_list_column: List[List[sg.Listbox]] = [
    [
        sg.Listbox(
            all_art_entries, enable_events=True, size=(80, 20), horizontal_scroll=True,
            key="-ENTRYLIST-"
        )
    ],
]

# Entry Viewer panel
entry_viewer_column: List[List[sg.Element]] = [
    # Instruction Text
    [sg.Text("Choose an entry from the list on the left:", key="-INSTRUCTION-", visible=True)], 

    # Image panel
    [sg.Image(key="-ENTRYIMAGE-")],

    # Next and Previous buttons, artwork_list index
    [sg.Button("Prev", key="-PREV-", visible=False), 
     sg.Text(key="-LISTINDEX-", visible=False), 
     sg.Button("Next", key="-NEXT-", visible=False)],

    # Title text
    [sg.Text(key='-TITLE-')],

    # Date text
    [sg.Text(key='-DATE-')],

    # Select viewed list
    [sg.Radio("Artworks", "checkbox", key='-ARTWORKLIST-', enable_events=True, default=True, visible=False), 
     sg.Radio("Source", "checkbox", key='-SOURCELIST-', enable_events=True, visible=False)]
]

# Layout
layout: List[List[sg.Column]] = [
    [
        sg.Column(entry_list_column),
        sg.VSeparator(), 
        sg.Column(entry_viewer_column),
    ]
]

window = sg.Window("JoJo's Art Scraper and Viewer", layout, finalize=True)

# Window variables
entry_img_index: int = 0
current_entry: ArtEntry = ArtEntry([Artwork("img", "alt")], "date", "title", [
                                   Artwork("srcimg", "srcalt")])
current_list: List[Artwork] = current_entry.artwork_list

# Window updater functions
def update_date() -> None:
    """
    Updates date text.
    """
    window["-DATE-"].update(f"{current_entry.date}")


def update_title() -> None:
    """
    Updates title text.
    """
    window["-TITLE-"].update(f"{current_entry.source_title}")


def update_img_window() -> None:
    """
    Updates image window.
    """
    window["-ENTRYIMAGE-"].update(return_img_data(
        current_list[entry_img_index].img_src))


def update_button_vis() -> None:
    """
    Updates button and artwork list index visibility if artwork list > 1.
    """
    if len(current_list) > 1:
        window["-PREV-"].update(visible=True)
        window["-LISTINDEX-"].update(
            f"{entry_img_index + 1} of {len(current_list)}", visible=True)
        window["-NEXT-"].update(visible=True)
    else:
        window["-PREV-"].update(visible=False)
        window["-LISTINDEX-"].update(visible=False)
        window["-NEXT-"].update(visible=False)


def update_checkboxes() -> None:
    """
    Defaults checkbox selection.
    """
    window["-ARTWORKLIST-"].update(True, visible=True)
    window["-SOURCELIST-"].update(False, visible=True)


def update_list_index() -> None:
    """
    Updates list index text.
    """
    window["-LISTINDEX-"].update(
        f"{entry_img_index + 1} of {len(current_list)}")


# EVENT LOOP
while True:
    event: str
    values: dict[str, Any]
    event, values = window.read()

    # On exit, quit
    if event == sg.WIN_CLOSED:
        break

    # Displays selected artEntry details
    elif event == "-ENTRYLIST-":
        for art_entry in values["-ENTRYLIST-"]:
            # Defaults index value and currentList for next artEntry
            entry_img_index = 0
            current_entry = art_entry
            current_list = current_entry.artwork_list

            # Updates Windows
            update_date()
            update_title()
            update_img_window()
            update_checkboxes()
            update_button_vis()

            # Hides instruction text once an entry has been selected
            window["-INSTRUCTION-"].update(visible=False)

    # Prev in artwork_list incrementer
    elif event == "-PREV-":
        if entry_img_index - 1 < 0:
            entry_img_index = len(current_list) - 1
        else:
            entry_img_index -= 1

        # Updates image selections and list index
        update_img_window()
        update_list_index()

    # Next in artwork_list incrementer
    elif event == "-NEXT-":
        if entry_img_index + 1 > len(current_list) - 1:
            entry_img_index = 0
        else:
            entry_img_index += 1

        # Updates image and index text
        update_img_window()
        update_list_index()

    # If Artworks list is selected, display
    elif event == "-ARTWORKLIST-":
        current_list = current_entry.artwork_list
        entry_img_index = 0

        # Updates image, index text, and button visibility
        update_img_window()
        update_list_index()
        update_button_vis()

    # If Source image list is selected, display
    elif event == "-SOURCELIST-":
        current_list = current_entry.source_img_list
        entry_img_index = 0

        # Updates image, index text, and button visibility
        update_img_window()
        update_list_index()
        update_button_vis()

window.close()

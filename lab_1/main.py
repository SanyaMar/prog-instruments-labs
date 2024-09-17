"""
import PySimpleGUI and urllib.request for GUI
from PIL import Image and import io for GUI JPG Image processing
"""


import io
import pickle
import urllib.request
import PySimpleGUI as sg

from typing import List, Optional, Any
from PIL import Image

from art_work import Artwork
from art_entry import ArtEntry
from scraper_funct import run_scraper
 

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

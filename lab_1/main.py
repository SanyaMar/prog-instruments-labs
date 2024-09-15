""" Scraping
    import lxml for html parser
    import cchardet for character reading
    import PySimpleGUI and urllib.request for GUI
    from PIL import Image and import io for  GUI JPG Image processing
"""
import cchardet
import lxml
import requests
from bs4 import BeautifulSoup 

import csv
import pickle

import PySimpleGUI as sg
import urllib.request

import io
from PIL import Image



##################################################
# --------------- Class Objects ---------------- #
##################################################


class Artwork:
    """
    Represents an artwork with its source link and alt text.

    Attributes:
        imgSrc (str): The URL of the artwork image.
        imgAlt (str): The alt text for the artwork image.
    """
    imgSrc = ""
    imgAlt = ""

    def __init__(self, imgSrc, imgAlt):
        """
        Initializes the Artwork object with image source and alt text.

        Args:
            imgSrc (str): The URL of the artwork image.
            imgAlt (str): The alt text for the artwork image.
        """
        self.imgSrc = imgSrc
        self.imgAlt = imgAlt


class ArtEntry:
    """
    Represents an entry of artwork including its details.

    Attributes:
        artworkList (list): List of Artwork objects associated with this entry.
        date (str): The date associated with the artwork entry.
        sourceTitle (str): The title of the source from which the artwork is taken.
        sourceImgList (list): List of Artwork objects representing source images.
    """
    artworkList = [] # list containing Artwork objects
    date = ""
    sourceTitle = ""
    sourceImgList = [] # list of Artwork objects (source images)
    
    def __init__(self, artworkList, date, sourceTitle, sourceImgList) :
        """
        Initializes the ArtEntry object with details of the artwork entry.

        Args:
            artworkList (list): List of Artwork objects.
            date (str): The date associated with the entry.
            sourceTitle (str): The title of the source.
            sourceImgList (list): List of Artwork objects for source images.
        """
        self.artworkList = artworkList
        self.date = date
        self.sourceTitle = sourceTitle
        self.sourceImgList = sourceImgList

    def __repr__(self):
        """
        Returns a string representation of the ArtEntry object.
        """
        return f"{self.sourceTitle}"





######################################################
# --------------- Scraper Functions ---------------- #
######################################################

# PRIMARY DATA STRUCTURE: List of ArtEntry objects containing all scraped art entries and their individual data
    #
    # allArtEntries[] -> ArtEntry -> artworkList[] -> Artwork -> imgSrc"" 
    #                             -> date""                   -> imgAlt""
    #                             -> sourceTitle""
    #                             -> srcImgList[]  -> Artwork -> imgSrc""
    #                                                         -> imgAlt""
    #
allArtEntries = []

def useScraper() :
    """
    Prompts the user to choose between using previously stored data or rescraping data.

    If the user chooses to rescrape, it calls the runScraper function.
    """
    # Theme
    sg.theme('DarkGrey4')
    
    choice = sg.popup_yes_no("Do you want to use previously stored data?", "Selecting \"No\" will take several minutes to update all stored entries.", "", title="JoJo's Art Scraper and Viewer")
    if (choice == "No") :
        runScraper()


def formatImgList(list) :
    """
    Formats a list of image sources into a multi-line string for CSV formatting.

    Args:
        list: List of image links or alt texts.

    Returns:
        str: A formatted string where each entry is on a new line.
    """
    formattedStr = ""

    for string in list :
        formattedStr += string
        formattedStr += "\n"

    return formattedStr


# --------------- Scraper ---------------- #

def runScraper() :
    """
    Requests page content from a specified URL, scrapes art entries, 
    and stores the data in a list and a CSV file.
    """
    # GET Request
    URL =  'https://jojowiki.com/Art_Gallery#2021-2025-0'
    requests_session = requests.Session()
    page = requests_session.get( URL )  

    # Check for successful status code (200)
    print("Status Code - {}".format(page.status_code))
    if(page.status_code == 200) :
        print("Successful Connection")
    else :
        print("Unsuccessful Connection")
     

    # HTML Parser
    soup = BeautifulSoup(page.text, "lxml")
    divs = soup.find("div", {"class":"phantom-blood-tabs"})
    entries = divs.find_all("table", {"class":"diamonds volume"})

    # Initialize writer and csv file
    file = open("entries.csv", "w", newline='', encoding='utf-8')
    writer = csv.writer(file)
    writer.writerow(["ARTWORK", "DATE", "SOURCE TITLE", "SOURCE IMAGE"])

    # Scrapes every artwork entry on the page
    for entry in entries :

        # Initializes each subsection of an artwork entry, containing:
            # Artwork      (artworkList)
            # Date         (date)
            # Original Use (sourceTitle)
            # Source Image (sourceImgList)
        sections = entry.find_all("td", {"class":"volume"}) # Subsections are stored in <td> tags with class:"volume"
        artworkList = []
        date = ""
        sourceTitle = ""
        sourceImgList = []

        artEntryObj = ArtEntry([], "", "", [])
        artworkObj = Artwork("", "")
        srcImgObj = Artwork("","")

        # Iterates through each subsection and row of csv, and writes to csv with scraped data
        sectionCounter = 1 # Tracks which subsection/column is being viewed (sections are referred to as "volumes" within the html)
        for section in sections :

            # If on a subsection containing images (1 and 4), scrape image content
            if(sectionCounter == 1 or sectionCounter == 4) :
                thumbnails = section.find_all("a") # href is stored within <a> tags

                # For every thumbnail image, find full-res webpage and create new 
                for thumbnail in thumbnails :

                    # Grabs href for full-res image webpage from thumbnail container
                        # href = /File:ARTORK_NAME
                    href = thumbnail.get('href') 
                    newURL = f"https://jojowiki.com{href}" # Appends href to domain to form new url

                    # Temporary HTML parser to scrape full-res image
                    newRequests_session = requests.Session()
                    newPage = newRequests_session.get( newURL )  
                    newSoup = BeautifulSoup(newPage.text, "lxml")

                    # Stores preview image, as full resolution images are too large
                    media = newSoup.find("div", {"id":"file"}).find("img")
                    src = media.get('src') # Grabs image source-link
                    alt = media.get('alt') # Grabs image alt text

                    # -- REPLACE ABOVE CODE FOR FULL-RESOLUTION IMAGES -- #
                        # WARNING: Images resolution may exceed monitor resolution and GUI will work improperly
                    #media = newSoup.find("a", {"class":"internal"})
                    #src = media.get('href') # Grabs image source-link
                    #alt = media.get('title') # Grabs image alt text


                    if(sectionCounter == 1) :
                        # Stores in allArtEntries list
                        artworkObj = Artwork(src, alt) 
                        artEntryObj.artworkList.append(artworkObj) 

                        # Stores in CSV
                        artworkList.append("<src: " + src + "\nalt: " + alt + ">") # Uses <> for separation of entries and ease of possible parsing

                    elif(sectionCounter == 4) :
                        # Stores in allArtEntries list
                        srcImgObj = Artwork(src, alt) 
                        artEntryObj.sourceImgList.append(srcImgObj) 

                        # Stores in CSV
                        sourceImgList.append("<src: " + src + "\nalt: " + alt + ">") # Uses <> for separation of entries and ease of possible parsing

            # If on a subsection containing text (2 and 3), scrape text content
            elif(sectionCounter == 2 or sectionCounter == 3) :
                textContent = section.find("center") # Text content is stored within <center> tags

                for string in textContent.strings :
                    if(sectionCounter == 2) :
                        date += string
                    elif(sectionCounter == 3) :
                        sourceTitle += string

            # After scraping subsection, update tracker to next
            sectionCounter += 1
        
        # Appends artEntry to list allArtEntries
        artEntryObj.date = date
        artEntryObj.sourceTitle = sourceTitle
        allArtEntries.append(artEntryObj)

        # Writes to csv file, formatting the image lists into formatted strings
        writer.writerow([formatImgList(artworkList), date, sourceTitle, formatImgList(sourceImgList)])
        pickle.dump(allArtEntries, open("artEntriesData.p", "wb"))

    file.close()





#########################################
# --------------- Main ---------------- #
#########################################

def main():
    """ 
    Asks user to use stored data or scrape  
    """
    useScraper()
    
if __name__ == '__main__':
    main()





##################################################
# --------------- GUI Functions ---------------- #
##################################################

def openUrl(src) :
    """
    The function takes the URL of the image and opens it.
    Spoofing headers are used to bypass the 403: Forbidden error.

    Args:
        src (str): URL of the image.

    Returns:
        n object of type urllib.response.urlopen or None in case of an error.
    """
    try:
        req = urllib.request.Request(src, headers={'User-Agent' : "Magic Browser"}) 
        return urllib.request.urlopen(req)
    except:
         print(f"Error encountered in openUrl() with src: \'{src}\'")

# Returns image value for EntryImage depending on img type (PNG or JPG)
def returnImgData(url) :
    """
    The function returns image data depending on its type (PNG or JPG).

    Args:
        url (str): URL of the image.

    Returns:
        The image data is in PNG format or None if the image failed to load.
    """            
    # If imgSrc is a png, update window using urllib
    if('.png' in url) :
        #window["-ENTRYIMAGE-"].update(openUrl(url).read())
        return openUrl(url).read()

    # If imgSrc is a jpg, update window using Pillow
    elif('.jpg' in url) :
        # Creates PIL img from scraped jpg data, converts into png data
        pil_img = Image.open(io.BytesIO(openUrl(url).read()))
        png_bio = io.BytesIO()
        pil_img.save(png_bio, format="PNG")
        png_data = png_bio.getvalue()

        #window["-ENTRYIMAGE-"].update(data=png_data)
        return png_data


# --------------- GUI ---------------- #

allArtEntries = pickle.load(open("artEntriesData.p", "rb"))

checkBoxes = []
checkBoxes.append(sg.Radio("Arts", "faculty", key='arts', enable_events=True,default=True))
checkBoxes.append(sg.Radio("Commerce", "faculty", key='comm', enable_events=True))

# List of Entries
entryList_column = [
    [
        sg.Listbox( 
            allArtEntries, enable_events=True, size=(80, 20), horizontal_scroll=True,
            key="-ENTRYLIST-"
        )
    ],
]

# Entry Viewer panel
entryViwer_column = [

    # Instruction Text
    [sg.Text("Choose an entry from the list on the left:", key="-INSTRUCTION-", visible=True)], 

    # Image panel
    [sg.Image(key="-ENTRYIMAGE-")],

    # Next and Previous buttons, artworkList index
    [sg.Button("Prev", key="-PREV-",  visible=False), sg.Text(key = "-LISTINDEX-", visible=False), sg.Button("Next", key="-NEXT-", visible=False)],

    # Title text
    [sg.Text(key='-TITLE-')],

    # Date text
    [sg.Text(key='-DATE-')],

    # Select viewed list
    [sg.Radio("Artworks", "checkbox", key='-ARTWORKLIST-', enable_events=True,default=True, visible=False), sg.Radio("Source", "checkbox", key='-SOURCELIST-', enable_events=True, visible=False)]
]

# Layout
layout = [
    [
        sg.Column(entryList_column),
        sg.VSeparator(), 
        sg.Column(entryViwer_column),
    ]
]

# Window
window = sg.Window("JoJo's Art Scraper and Viewer", layout, finalize=True)

# Window variables
entryImgindex = 0
currentEntry = ArtEntry([Artwork("img","alt")],"date","title",[Artwork("srcimg","srcalt")])
currentList = currentEntry.artworkList


# --------------- Window Updater Functions ---------------- #

def updateDate():
    """
    Updates date text
    """
    window["-DATE-"].update(f"{currentEntry.date}")

def updateTitle():
    """
    Updates title text
    """
    window["-TITLE-"].update(f"{currentEntry.sourceTitle}")

def updateImgWindow() :
    """
    Updates image window
    """
    window["-ENTRYIMAGE-"].update(returnImgData(currentList[entryImgindex].imgSrc))

# Updates button and artworkList index visibility if artworkList > 1 
def updateButtonVis():
    """
    Updates button and artworkList index visibility if artworkList > 1 
    """
    if(len(currentList) > 1) :
        window["-PREV-"].update(visible=True)
        window["-LISTINDEX-"].update(f"{entryImgindex+1} of {len(currentList)}", visible=True)
        window["-NEXT-"].update(visible=True)
    else:
        window["-PREV-"].update(visible=False)
        window["-LISTINDEX-"].update(visible=False)
        window["-NEXT-"].update(visible=False)

def updateCheckboxes():
    """
    Defaults checkbox selection
    """
    window["-ARTWORKLIST-"].update(True, visible=True)
    window["-SOURCELIST-"].update(False, visible=True)

def updateListIndex():
    """
    Updates list index text
    """
    window["-LISTINDEX-"].update(f"{entryImgindex+1} of {len(currentList)}")   


# --------------- EVENT LOOP ---------------- #

while True :
    event, values = window.read()
    
    # On exit, quit
    if event == sg.WIN_CLOSED :
        break

    # Displays selected artEntry details
    elif event == "-ENTRYLIST-"  :
        for artEntry in values['-ENTRYLIST-'] :
            # Defaults index value and currentList for next artEntry
            entryImgindex = 0
            currentEntry = artEntry
            currentList = currentEntry.artworkList

            # Updates Windows
            updateDate()
            updateTitle()
            updateImgWindow()
            updateCheckboxes()
            updateButtonVis()

            # Hides instruction text once an entry has been selected
            window["-INSTRUCTION-"].update(visible=False)

    # Prev in artworkList incrementer
    elif(event == "-PREV-") :
        if(entryImgindex - 1 < 0) :
            entryImgindex = len(currentList) - 1
        else :
            entryImgindex -= 1

        # Updates image selections and list index
        updateImgWindow()
        updateListIndex()

    # Next in artworkList incrementer
    elif(event == "-NEXT-") :
        if(entryImgindex + 1 > len(currentList) - 1) :
            entryImgindex = 0
        else :
            entryImgindex += 1

        # Updates image and index text
        updateImgWindow()
        updateListIndex()
    
    # If Artworks list is selected, display
    elif(event == "-ARTWORKLIST-"):
        currentList = currentEntry.artworkList
        entryImgindex =0

        # Updates image, index text, and button visibility
        updateImgWindow()
        updateListIndex()
        updateButtonVis()

    # If Source image list is selected, display
    elif(event == "-SOURCELIST-"):
        currentList = currentEntry.sourceImgList
        entryImgindex=0

        # Updates image, index text, and button visibility
        updateImgWindow()
        updateListIndex()
        updateButtonVis()

    #print(event, values)
window.close()









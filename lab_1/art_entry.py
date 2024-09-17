from typing import List

from art_work import Artwork


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

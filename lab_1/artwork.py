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

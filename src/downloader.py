from pytube import YouTube
from pytube.exceptions import PytubeError
from typing import List
import re

class downloader:

    """
    Downloads the mp3
    """
    @staticmethod
    def ReturnMusic(link: str) -> str:
        try:
            yt = YouTube(link)
            audio_stream = yt.streams.filter(only_audio=True).first()

            if audio_stream:
                title = yt.title.replace('/', '_')
                title = re.sub(r'[<>:"/\\|?*]', '', title)  # Make the file name valid when searching
                audio_stream.download(output_path='mp3', filename=f"{title}.mp3")
                print("Download completed!")
                
                del yt # Allow garbage collection
                return f"mp3/{title}.mp3"
            else:
                print("No audio stream found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    """
    For multiple link.
    """
    @staticmethod
    def ReturnLinkTitles(list: str) -> List[str]:
        titles = []
        for link in list:
            yt = YouTube(link)
            titles.append(yt.title) 
            del yt # Allow garbage collection

        return titles
    
    """
    For single link.
    """
    @staticmethod
    def ReturnLinkTitle(link: str) -> str:
        try:
            yt = YouTube(link)
            title = yt.title
            return title
        except PytubeError as e:
            return "TITLE NOT FOUND"  # or handle the error as needed
from pytube import YouTube
from pytube.exceptions import PytubeError
import re

class downloader:

    @staticmethod
    def ReturnMusic(link):
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

    @staticmethod
    def ReturnLinkTitles(list):
        titles = []
        for link in list:
            yt = YouTube(link)
            titles.append(yt.title) 
            del yt # Allow garbage collection

        return titles
    
    @staticmethod
    def ReturnLinkTitle(link):
        try:
            yt = YouTube(link)
            title = yt.title
            return title
        except PytubeError as e:
            return "TITLE NOT FOUND"  # or handle the error as needed
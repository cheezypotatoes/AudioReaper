from collections import defaultdict
from listener import listenerClass
from responder import respond
from downloader import downloader  # Static
import time
import threading
import queue
import copy

class App():
    def __init__(self, token, intents, botName) -> None:
        self.token = token
        self.intents = intents
        self.botName = botName # Can't find the api for getting it automatically
        self.listener = listenerClass(self.token, self.intents, self.botName)  # listener
        self.respond = respond()  # Responder
        self.listenerThread = threading.Thread(target=self.listener.startWebsocket, daemon=True)  # Handles Listener
        self.respondThread = threading.Thread(target=self.respondHandler, daemon=True)  # Handles sender
        self.downloadThread = threading.Thread(target=self.downloadHandler, daemon=True)  # Handles the download part
        self.queue = queue.Queue()  # Holds all sent messages
        self.downloadQueue = queue.Queue()  # Hold all message protocol with links in it (to download)
        # Holds all method per protocols
        self.protocolAdditionalFunctions = defaultdict(lambda: self.defaultDoesNothing, {
                                "CheckDownloadQueue": self.returnDownloadQueue,
                                "ClearDownloadQueue": self.clearDownloadQueue,
                                "CheckStatus": self.getStatus
                                })
        # Holds all method per download type
        self.downloadDictionary = {"YoutubeLink": self.DownloadAndRespond}
    
    # Protocol methods
    """
    Copies the queue and get all titles for it then returned a formatted version
    """
    def returnDownloadQueue(self, *args, **kwargs):
        copiedQueue = [item[2].split(" ", 1)[1] for item in copy.copy(self.downloadQueue.queue)]
        titles = downloader.ReturnLinkTitles(copiedQueue)
        cleaned_titles = [' '.join(title.strip().replace('\n', ' ').replace('\r', '').split()).title() for title in titles]
        formatted_list = "\n".join(f"• {title}" for title in cleaned_titles)
        return formatted_list
    """
    Basically if protocol doesn't use any method return nothing
    """
    def defaultDoesNothing(self, *args, **kwargs):
        return None
    """
    Clears the download queue
    """
    def clearDownloadQueue(self, *args, **kwargs):
        with self.downloadQueue.mutex:
            self.downloadQueue.queue.clear()
    """
    Return bot's status, just basic stuff, room for improvements
    """
    def getStatus(self, *args, **kwargs):
        return " Running"


    # HANDLERS
    """
    Handles the messages, if protocol require downloads such as "YoutubeLink" It is transferred to downloadQueue for download thread to handle
    """
    def handleMessageToProcess(self):
        if not self.queue.empty():
            messageQueued = self.queue.get()  # [Protocol, UserId, Message, ServerId]
            
            # If protocol is "YoutubeLink" then pass it to the downloadQueue for download thread to handle
            if messageQueued[0] == "YoutubeLink":
                self.downloadQueue.put(messageQueued)
                return

            # Call the protocol's method return None if doesn't exist
            additionalRespond = self.protocolAdditionalFunctions[messageQueued[0]](sender_text=messageQueued[2])

            # Respond to the user
            self.respond.sendRespond(messageQueued[0], messageQueued[1], messageQueued[3], self.token, additionalRespond if additionalRespond is not None else "",None)

    """
    Method that handles with the respond by checking if there's message to processes and handles it
    """
    def respondHandler(self):
        while True:
            self.CheckIfDataInQueue() # Check if there's people sending messages
            self.handleMessageToProcess() # Handles message
            time.sleep(0.3)  # Adjust?
    
    """
    Method that handles with messages that uses 'YoutubeLink' or "MultipleLink" protocol
    """
    def downloadHandler(self):
        while True:
            if not self.downloadQueue.empty():
                downloadMessageToProcess = self.downloadQueue.get()
                # Uses hashmap for determine the type of download
                self.downloadDictionary[downloadMessageToProcess[0]](downloadMessageToProcess)
            time.sleep(0.5)

    # Handler helper methods
    """
    Grabs message to process from the listener queue to handle
    """
    def CheckIfDataInQueue(self):
        result = self.listener.getQueue()
        if result:  # This checks if result is not None and not empty
            self.queue.put(result)
    """
    Downloads the link and respond to the user
    """
    def DownloadAndRespond(self, downloadMessageToProcess):
        # Downloads the music and return the path
        music_path = downloader.ReturnMusic(downloadMessageToProcess[2].split(' ', 1)[1])
        # Message that tells user that download is being processed
        self.respond.sendRespond("RespondBeforeDownload",
                                downloadMessageToProcess[1],
                                downloadMessageToProcess[3],
                                self.token,
                                f" {music_path.split('/', 1)[1]}",
                                None)
        # Message that sends the downloaded music
        self.respond.sendRespond(downloadMessageToProcess[0],
                                downloadMessageToProcess[1],
                                downloadMessageToProcess[3],
                                self.token,
                                "",
                                music_path)


    def StartProgram(self):
        self.listenerThread.start()  # Listener
        self.respondThread.start()  # Respond
        self.downloadThread.start()  # Download
        
        while True: # Keeps everything from running if main thread is done everything is done
            time.sleep(1)

    


if __name__ == "__main__":
    token = ""
    application = App(token, "32767", "existentialwonders")  # TOKEN, TYPE OF LISTENER, NAME
    application.StartProgram()





    
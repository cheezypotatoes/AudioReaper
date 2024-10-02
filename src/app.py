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
        self.protocolAdditionalFunctions = defaultdict(lambda: self.defaultDoesNothing, {
                                "CheckDownloadQueue": self.returnDownloadQueue,
                                })
        
    def returnDownloadQueue(self, *args, **kwargs):
        copiedQueue = list(copy.copy(self.downloadQueue.queue))
        print(copiedQueue)
        return None
    
    def defaultDoesNothing(self, *args, **kwargs):
        return None

    """
    Grabs message to process from the listener queue to handle
    """
    def CheckIfDataInQueue(self):
        result = self.listener.getQueue()
        if result:  # This checks if result is not None and not empty
            self.queue.put(result)

    def handleMessageToProcess(self):
        if not self.queue.empty():
            messageQueued = self.queue.get()  # [Protocol, UserId, Message, ServerId]
            
            # If protocol is "YoutubeLink" then pass it to the downloadQueue for download thread to handle
            if messageQueued[0] == "YoutubeLink":
                self.downloadQueue.put(messageQueued)
                return
        
            additionalRespond = self.protocolAdditionalFunctions[messageQueued[0]](sender_text=messageQueued[2])

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
    Method that handles with messages that uses 'YoutubeLink' protocol
    """
    def downloadHandler(self):
        while True:
            if not self.downloadQueue.empty():
                downloadMessageToProcess = self.downloadQueue.get()
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
            time.sleep(0.5)

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





    
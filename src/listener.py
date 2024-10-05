from collections import defaultdict
import asyncio
import websockets
import json
import re
import queue


class listenerClass:
    def __init__(self, token, intents, botName) -> None:
        self.token = token
        self.intents = intents
        self.botName = botName
        self.gateway_url = "wss://gateway.discord.gg/?v=10&encoding=json"
        self.youtubeRegex = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})$'
        self.events = {"MESSAGE_CREATE": self.handleMessage,
                       "READY": self.onReady,}
        self.MessageToProcess = queue.Queue()  # Temporarily holds the messages
        # Gives the type of protocol
        self.MessageProtocolMap = defaultdict(lambda: "Greet", {
            "!help": "Instruction",
            "!downloadQueue": "CheckDownloadQueue",
            "!status": "CheckStatus",
            "!clear": "ClearDownloadQueue",
            "!downloadMany": "MultipleLinks",
            "!credits": "ShowCredits"
        })

    async def onReady(self, *args, **kwargs) -> None:
        print("BOT IS READY")

    async def heartbeat(self, ws, interval) -> None:
        while True:
            await asyncio.sleep(interval / 1000)  # Convert milliseconds to seconds
            heartbeat_payload = {
                "op": 1,  # Opcode for Heartbeat
                "d": None  # Send last sequence number as None for now
            }
            await ws.send(json.dumps(heartbeat_payload))
            print('Sent Heartbeat')

    async def identify(self, ws) -> None:
        identify_payload = {
            "op": 2,  # Opcode for Identify
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "windows",
                    "$browser": "my_library",
                    "$device": "my_library"
                },
                "intents": self.intents  # Enables all intents
            }
        }
        await ws.send(json.dumps(identify_payload))
        print('Sent Identify Payload')

    async def sendHelloEvent(self, ws) -> None:  # Only called once
        message = await ws.recv()
        payload = json.loads(message)
        op = payload.get("op") # Might be useful hello event is op = 10
        t = payload.get("t")
        d = payload.get("d")

        global heartbeat_interval
        heartbeat_interval = d['heartbeat_interval']
        asyncio.create_task(self.heartbeat(ws, heartbeat_interval))
        await self.identify(ws)
        print("Connected to Discord Gateway")

    async def listen(self) -> None:
        """Main function to handle the WebSocket connection."""
        async with websockets.connect(self.gateway_url, max_size=None) as ws: # Fix file size error
            await self.sendHelloEvent(ws)
            while True:
                message = await ws.recv()
                payload = json.loads(message)
                t = payload.get("t")
                d = payload.get("d")

                if t in self.events:
                    await self.events[t](d, ws) # This calls the handleMessage if matched in event

    """
    Method used by responder thread in main to get the responses and move to a different thread handler
    """
    def getQueue(self):
        if not self.MessageToProcess.empty():
                return self.MessageToProcess.get()


    """
    Handles incoming messages directed to the bot.

    This function processes a message JSON object to determine if the message mentions
    the bot and if it contains a specific command. It can handle commands for downloading
    YouTube links and other protocols defined in the MessageProtocolMap.
    """
    async def handleMessage(self, messageJson, *args, **kwargs):
        if len(messageJson['mentions']) != 0 and messageJson['mentions'][0]['username'] == self.botName:
            messageSent = messageJson['content'].split(' ', 1)[1] # Get the message (removing the @bot)
            command = messageSent.split(' ', 1)[0]
            additional = messageSent.split(' ', 1)[1] if len(messageSent.split(' ', 1)) > 1 else ''  # Returns "" if there's no additional

            # If youtube Link
            if command == "!download" and re.match(self.youtubeRegex, additional):
                # Message Protocol (type), author id, author sent message, channel id
                self.MessageToProcess.put(["YoutubeLink", messageJson['author']['id'], messageSent, messageJson['channel_id']])
                return
            
            # If not then get its protocol from the MessageProtocolMap
            self.MessageToProcess.put([self.MessageProtocolMap[command], messageJson['author']['id'], messageSent, messageJson['channel_id']])
            return
           

                
    def startWebsocket(self):
        asyncio.run(self.listen())

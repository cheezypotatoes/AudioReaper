import requests


class respond:
    def __init__(self) -> None:
        # Responds for each protocol
        self.respond = {
            "Greet": "Hello There, This is an automatic reply",
            "Instruction": (
                "\n1. `!download <url>`\n     > Converts the provided YouTube link to an MP3. (Download)\n"
                "2. `!help`\n     > Displays this list of commands.\n"
                "3. `!status`\n     > Check the current status of the bot.\n"
                "4. `!downloadQueue`\n     > Shows the download queue.\n"
                "5. `!clear`\n     > Clears the current queue.\n"
                "6. `!downloadMany <url>,<url>..`\n     > Convert multiple links. (download)\n"
                "7. `!credits`\n     > The Man Behind The Bot"),
            "CheckStatus": "STATUS:",
            "CheckDownloadQueue": "\n Current download queue: \n",
            "YoutubeLink": "Processing link please wait",
            "RespondAfterDownload": "Here is your requested MP3 file!",
            "RespondBeforeDownload": "Processing your mp3 title: ",
            "ClearDownloadQueue": "Download queue cleared",
            "MultipleLinks": "Link Number:",
            "ShowCredits": (
                "\n=========================================\n"
                "                        CREDITS\n"
                "=========================================\n"
                " Created by:   cheezypotatoes (Jorge)\n\n"
                " Github:       https://github.com/cheezypotatoes\n"
                "=========================================\n"
                "    Good morning! If I don't see you,\n"
                "    good afternoon, good evening, and\n"
                "    good night!\n"
                "=========================================\n"
            )
        }

        self.downloadProtocol = {"YoutubeLink", "MultipleLinks"}      
    
    def sendRespond(self, protocol, sender_id, server_id, token, additional, music_path): # Normal Respond
        header = {'authorization': token}

        if protocol in self.downloadProtocol:
            with open(music_path, 'rb') as f:
                music = f.read()  # Read the MP3 file in binary mode

                files = {'file': (music_path.split('/')[-1], music, 'audio/mpeg')}  # Name, file, type

                payload = {'content': f"<@{sender_id}> {self.respond["RespondAfterDownload"]}",}
                requests.post(f"https://discord.com/api/v9/channels/{server_id}/messages", data=payload, headers=header, files=files)
        else:
            payload = {"content": f"<@{sender_id}> {self.respond[protocol]}{additional}"}
            requests.post(f"https://discord.com/api/v9/channels/{server_id}/messages", data=payload, headers=header)
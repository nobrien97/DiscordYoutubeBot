# DiscordYoutubeBot
Bot to stream YouTube audio to Discord voice chat

## Requirements
`Python 3.8`
`discord.py`
`youtube_dl`

To run the bot, you'll need to set up a bot application through the Discord developer portal, invite it to your server and substitute in your own token in `main.py`.
Then run `python3 ./main.py`


## Commands
            Prefix each with a !
            ytp <url>       : Wail audio from a YouTube(tm) link RIGHT NOW 4head
            ytq <url>       : Add a track to the queue
            stop            : The goat wails no more
            volume <int>    : Makes the goat wail louder
            next            : Wail the next track in the queue
            clear           : Remove all tracks from the queue
            pause           : The goat holds its breath. If it already is, it wails once more
            lq              : Have a look at what the goat holds in store

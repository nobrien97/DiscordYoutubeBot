import discord
import youtube_dl
import asyncio
from discord.ext import commands
from os import path

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLDownloader(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class YT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    YTqueue = []

    @commands.command()
    async def join(self , ctx, *, channel: discord.VoiceChannel):
        """ Join a Voice channel """
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        return await channel.connect()

    @commands.command()
    async def ytp(self, ctx, *, url):
        """ Stream audio from URL """
        async with ctx.typing():
            player = await YTDLDownloader.from_url(url, loop = self.bot.loop, stream=True)
            ctx.voice_client.play(player, after = lambda e: print('Player error: %s' % e) if e else self.next(ctx) if len(self.YTqueue) else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def ytq(self, ctx, *, url):
        """ Add track to the queue """
        data = await YTDLDownloader.from_url(url, loop = self.bot.loop, stream=True)
        self.YTqueue.append(data)
        await ctx.send('Added {} to the queue'.format(data.title))
        if (ctx.voice_client.is_playing() is False):
            await self.next(ctx)

    @commands.command()
    async def next(self, ctx):
        """Play the next track from the queue and remove it from the queue """
        if ctx.voice_client.is_playing() and len(self.YTqueue) != 0:
            ctx.voice_client.stop()

        if len(self.YTqueue) > 0:
            async with ctx.typing():
                player = self.YTqueue[0]
                self.YTqueue.pop(0)
                ctx.voice_client.play(player, after = lambda e: print('Player error: %s' % e) if e else self.next(ctx) if len(self.YTqueue) else None)
            await ctx.send('Now playing: {}'.format(player.title))
        else:
            await ctx.send("Nothing left in the queue!")

    @commands.command()
    async def lq(self, ctx):
        """List the queue"""
        if len(self.YTqueue) > 0:
            async with ctx.typing():
                itemsList = []
                for item in self.YTqueue:
                    itemsList.append(item.title)
                await ctx.send(itemsList)

    @commands.command()
    async def clear(self, ctx):
        """ Clear the queue """
        if len(self.YTqueue):
            self.YTqueue.clear()
            return await ctx.send("Queue cleared!")
        return await ctx.send("Nothing to clear!")

    @commands.command()
    async def pause(self, ctx):
        """ Pause playback """
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused wailback")
        elif ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed wailback")
        else:
            await ctx.send("Nothing playing!")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops audio, disconnects bot from voice channel"""
        await ctx.voice_client.disconnect()

    @commands.command()
    async def hlep(self, ctx):
        " Sends a nice help message"
        await ctx.send(
            """Commands:
            Prefix each with a !
            ytp <url>       : Wail audio from a YouTube(tm) link RIGHT NOW 4head
            ytq <url>       : Add a track to the queue
            stop            : The goat wails no more
            volume <int>    : Makes the goat wail louder
            next            : Wail the next track in the queue
            clear           : Remove all tracks from the queue
            pause           : The goat holds its breath. If it already is, it wails once more
            lq              : Have a look at what the goat holds in store
            """)

    @ytp.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You aren't connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
    
    @ytq.before_invoke
    @lq.before_invoke
    @pause.before_invoke
    @next.before_invoke
    async def ensure_voice_ytq(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You aren't connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")


bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"))

@bot.event
async def on_ready():
    print("Logged in as {0} ({0.id})".format(bot.user))
    print('-------')

bot.add_cog(YT(bot))
tokFile = open(path.expanduser('~/Projects/Discord/DISCORD_TOKEN_WAILING.tok'))
DISCORD_TOKEN = tokFile.read()
tokFile.close()
bot.run(DISCORD_TOKEN)        
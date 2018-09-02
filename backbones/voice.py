import discord
import logging
import asyncio
import os
import random
from mutagen.mp3 import MP3
from backbones.config import config
from backbones.loop import loop
from backbones.client import client
# Imports go here.

logger = logging.getLogger("dnetradio.backbones.voice")
# Defines the logger.

voice_clients = {}
# A dict of voice clients.

muted_voice_clients = {}
# A dict of muted voice clients.


class MockVoiceClient:
    """This is to make sure everything stays in sync."""
    def __init__(self):
        self.audio_source = None
        loop.create_task(self.mock_read())

    def get_current_player(self):
        return self.audio_source

    @staticmethod
    def is_playing():
        return False

    def play(self, audio_source):
        self.audio_source = audio_source

    async def mock_read(self):
        while True:
            if self.audio_source:
                self.audio_source.read()
            await asyncio.sleep(0.02)


class PreloadedBytesHandler(discord.AudioSource):
    """This handles preloaded bytes."""
    def __init__(self, preloaded_bytes):
        self.preloaded_bytes = preloaded_bytes
        self.reads = 0

    def get_current_player(self):
        try:
            return self.__getattribute__("_player")
        except AttributeError:
            pass

    def read(self):
        read_bytes = self.preloaded_bytes[self.reads]
        self.reads += 1
        return read_bytes


def preload_song(fp):
    """Preloads a song."""
    logger.info("Preloading {}".format(fp))
    preloaded_bytes = []
    player = discord.FFmpegPCMAudio(fp)
    while True:
        data = player.read()
        if data and str(data).count("\\x00") <= 1500:
            preloaded_bytes.append(data)
        elif not data:
            preloaded_bytes.append(data)
            break
        else:
            if not config['radio_config'].get("silence_removal"):
                preloaded_bytes.append(data)
    return preloaded_bytes


def get_random_jingle():
    """Returns a random jingle file name or none."""
    try:
        jingle_list = os.listdir("./jingles")
    except FileNotFoundError:
        return

    if len(jingle_list) == 0:
        return

    return "./jingles/{}".format(random.choice(jingle_list))


def get_random_song():
    """Returns a random song."""
    try:
        song_list = os.listdir("./songs")
    except FileNotFoundError:
        raise FileNotFoundError(
            "You need songs for DNetRadio to work. It is a radio doofus."
        )

    if len(song_list) == 0:
        return

    return "./songs/{}".format(random.choice(song_list))


class PlaylistGeneration:
    """This class is used for playlist generation."""
    def __init__(self):
        self.ready = False
        self.playlist = []
        self.songs_since_jingle = 0
        self.songs_before_jingle = config['radio_config'][
            'songs_before_jingle']
        self.songs_in_memory = config['radio_config'][
            'songs_in_memory']
        self.last_song = ""
        loop.create_task(self.playlist_generation())

    async def handle_specific_song(self):
        """Handles each specific song."""
        if self.songs_before_jingle == self.songs_since_jingle:
            # We want to play a jingle.
            self.songs_since_jingle = 0
            jingle_fp = await loop.run_in_executor(None, get_random_jingle)
            if jingle_fp:
                preload = await loop.run_in_executor(
                    None, preload_song, jingle_fp
                )
                mutagen_mp3 = await loop.run_in_executor(
                    None, MP3, jingle_fp
                )
                self.playlist.append(
                    [preload, jingle_fp[10:-4], mutagen_mp3.info.length]
                )
                return

        # We want to play a song.
        self.songs_since_jingle += 1
        while True:
            song_fp = await loop.run_in_executor(None, get_random_song)
            if song_fp != self.last_song:
                break
        self.last_song = song_fp
        preload = await loop.run_in_executor(
            None, preload_song, song_fp
        )
        mutagen_mp3 = await loop.run_in_executor(
            None, MP3, song_fp
        )
        self.playlist.append(
            [preload, song_fp[8:-4], mutagen_mp3.info.length]
        )

    async def playlist_generation(self):
        """Used to generate all/parts of the playlist."""
        while len(self.playlist) != self.songs_in_memory:
            await self.handle_specific_song()

        if not self.ready:
            self.ready = True

    def next(self):
        """Gets the next song from the playlist."""
        item = self.playlist[0]
        del self.playlist[0]
        loop.create_task(self.playlist_generation())
        return item

    async def wait_for(self):
        """Waits for the playlist to become ready."""
        while not self.ready:
            await asyncio.sleep(0.1)


async def handle_when_not_playing(voice_client, preload):
    """Waits for a voice client to not be playing if it is busy."""
    while voice_client.is_playing():
        await asyncio.sleep(0.1)
    voice_client.play(PreloadedBytesHandler(preload))


async def handle_playing_and_game(preload, file_name):
    """Handles playing the song and setting the game."""
    for voice_client in voice_clients.values():
        if voice_client.is_playing():
            loop.create_task(handle_when_not_playing(voice_client, preload))
        else:
            voice_client.play(PreloadedBytesHandler(preload))
    await client.change_presence(
        activity=discord.Game(file_name)
    )


async def radio_task():
    """The task that will infinitely supply the radio with songs."""
    playlist = PlaylistGeneration()
    await playlist.wait_for()
    while True:
        preload, file_name, length = playlist.next()
        loop.create_task(handle_playing_and_game(preload, file_name))
        await asyncio.sleep(length)

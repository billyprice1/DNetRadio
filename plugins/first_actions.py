from backbones.client import client
from backbones.models import Guild, objects
from backbones.utils import send_owners_dms
from backbones.embed import StandardisedEmbed
from backbones.voice import voice_clients, muted_voice_clients, radio_task, \
    MockVoiceClient
from backbones.loop import loop
import discord
import logging
# Imports go here.

logger = logging.getLogger("dnetradio.plugins.first_actions")
# Defines the logger.


@client.listen
async def on_shard_ready(shard_id):
    await send_owners_dms(
        StandardisedEmbed(
            client.user, "Liftoff!",
            "We are up and running on shard {}!".format(shard_id)
        )
    )
    logger.info("Shard {} is ready!".format(shard_id))
# Sent when a shard is ready.


@client.listen
async def on_ready():
    voice_clients[0] = MockVoiceClient()
    for guild in client.guilds:
        try:
            guilddb = await objects.get(Guild, Guild.guild_id == guild.id)
        except Guild.DoesNotExist:
            continue

        if not guilddb.voice_channel or not guilddb.enabled:
            continue

        channel = client.get_channel(guilddb.voice_channel)
        if not channel or not isinstance(channel, discord.VoiceChannel):
            continue

        try:
            if len(channel.members) >= 1:
                voice_clients[guilddb.voice_channel] = await channel.connect()
            else:
                muted_voice_clients[guilddb.voice_channel] =\
                    await channel.connect()
        except (AttributeError, discord.Forbidden, discord.NotFound):
            continue

    logger.info("Joined all guilds from the database.")
    loop.create_task(radio_task())
# Handles the bot being ready.

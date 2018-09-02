import logging
import discord
from backbones.client import client
from backbones.config import config
# Imports go here.

logger = logging.getLogger("dnetradio.utils")
# Defines the logger.


async def send_owners_dms(embed):
    owners = config['owner_ids']
    if owners:
        for owner in owners:
            user = client.get_user(owner)
            if not user:
                logger.error("{} not found on Discord.".format(owner))
                continue

            try:
                await user.send(embed=embed)
                logger.info("Successfully DM'd {}.".format(user))
            except (discord.NotFound, discord.Forbidden):
                logger.error("Could not DM {}.".format(user))

        return

    logger.error(
        "Owner DM sending function was called, but no owners were found in "
        "the environment variable."
    )
# Sends DM's to the owners.

from backbones.client import client
from backbones.models import Guild, objects
from backbones.voice import voice_clients, muted_voice_clients,\
    PreloadedBytesHandler
from backbones.embed import StandardisedEmbed
import discord
# Imports go here.

main_menu_messages = {}
# A dict of the main menu messages.


@client.listen
async def on_bot_tag(message):
    if not message.guild:
        try:
            return await message.channel.send(
                embed=StandardisedEmbed(
                    message.author, "I don't support DM's.", "Please use me "
                    "in a server.", False
                )
            )
        except (discord.NotFound, discord.Forbidden):
            return

    if not message.author.guild_permissions.administrator:
        try:
            em = StandardisedEmbed(
                message.author, "You don't have permission to use the GUI.",
                "To interface with me, please make sure you have "
                "administrator or if you want the invite that is below.", False
            )
            em.add_field(
                name="Bot Invite:",
                value="[The invite is here.]("
                      "https://discordapp.com/oauth2/authorize?client_id="
                      f"{client.user.id}&scope=bot&permissions=36726080)",
                inline=False
            )
            return await message.channel.send(embed=em)
        except (discord.NotFound, discord.Forbidden):
            return

    guilddb = (await objects.create_or_get(
        Guild, guild_id=message.guild.id
    ))[0]

    main_menu_embed = StandardisedEmbed(
        message.author, client.user.name,
        "This bot is based on DNetRadio which is written by "
        "JakeMakesStuff#0001."
    )

    reactions = []

    main_menu_embed.add_field(
        name="DNetRadio GitHub:",
        value="https://github.com/JakeMakesStuff/DNetRadio",
        inline=False
    )

    main_menu_embed.add_field(
        name="Bot Invite:",
        value="[The invite is here.]("
        "https://discordapp.com/oauth2/authorize?client_id="
        f"{client.user.id}&scope=bot&permissions=36726080)",
        inline=False
    )

    main_menu_embed.add_field(
        name="Active Channels (Local Instance):",
        value=f"{len(voice_clients)-1}"
    )

    main_menu_embed.add_field(
        name="Muted Channels (Local Instance):",
        value=f"{len(muted_voice_clients)}"
    )

    main_menu_embed.add_field(
        name="❌ Exit",
        value="Exits the menu.",
        inline=False
    )
    reactions.append("❌")

    if guilddb.enabled:
        main_menu_embed.add_field(
            name="👎 Disable",
            value="Disables the bot.",
            inline=False
        )
        reactions.append("👎")
    else:
        main_menu_embed.add_field(
            name="👍 Enable",
            value="Enables the bot.",
            inline=False
        )
        reactions.append("👍")

    if message.author.voice:
        main_menu_embed.add_field(
            name="🔊 Voice Channel",
            value="Joins the voice channel you are in.",
            inline=False
        )
        reactions.append("🔊")

    try:
        main_menu_message = await message.channel.send(
            embed=main_menu_embed
        )
    except (discord.NotFound, discord.Forbidden):
        return

    try:
        for reaction in reactions:
            await main_menu_message.add_reaction(reaction)
    except (discord.Forbidden, discord.NotFound):
        pass

    main_menu_messages[main_menu_message.id] = [message.author.id, guilddb]
# Creates the GUI.


@client.listen
async def on_message_delete(message):
    if message.id in main_menu_messages:
        del main_menu_messages[message.id]
# Deletes a main menu message if it is a main menu message.


emoji_boolean_map = {
    "👍": True,
    "👎": False
}
# The disable/enable emoji map.


bool_status_map = {
    True: "enabled",
    False: "disabled"
}
# Maps the boolean to a status.


@client.listen
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.id not in main_menu_messages:
        return

    user_id, guilddb = main_menu_messages[reaction.message.id]

    try:
        await reaction.message.remove_reaction(reaction.emoji, user)
    except (discord.Forbidden, discord.NotFound):
        pass

    if user_id != user.id:
        return

    reaction_emoji = str(reaction.emoji)

    if reaction_emoji == "❌":
        # Closes the menu.
        try:
            return await reaction.message.delete()
        except (discord.Forbidden, discord.NotFound):
            return

    if reaction_emoji in emoji_boolean_map:
        # This might be a enable/disable thing.
        new_value = emoji_boolean_map[reaction_emoji]
        if new_value == guilddb.enabled:
            return

        new_em = StandardisedEmbed(
            user, "Radio Toggled", "The radio is now "
            f"{bool_status_map[new_value]} in this server.", new_value
        )

        try:
            await reaction.message.clear_reactions()
        except (discord.Forbidden, discord.NotFound):
            pass

        del main_menu_messages[reaction.message.id]

        guilddb.enabled = new_value
        await objects.update(guilddb)

        if guilddb.voice_channel:
            if new_value:
                channel = client.get_channel(guilddb.voice_channel)
                if channel:
                    try:
                        voice_client = await channel.connect()
                        donor_voice_client = list(voice_clients.values())[0]
                        donor_player = donor_voice_client.get_current_player()
                        handler = PreloadedBytesHandler(
                            donor_player.preloaded_bytes
                        )
                        handler.reads = donor_player.reads
                        voice_client.play(handler)
                        voice_clients[guilddb.voice_channel] = voice_client
                    except (discord.Forbidden, discord.NotFound):
                        pass
            else:
                muted = True
                if guilddb.voice_channel in voice_clients:
                    voice_client = voice_clients[guilddb.voice_channel]
                    muted = False
                elif guilddb.voice_channel in muted_voice_clients:
                    voice_client = muted_voice_clients[guilddb.voice_channel]
                else:
                    voice_client = None

                if voice_client:
                    await voice_client.disconnect()
                    if muted:
                        del muted_voice_clients[guilddb.voice_channel]
                    else:
                        del voice_clients[guilddb.voice_channel]

        try:
            return await reaction.message.edit(embed=new_em)
        except (discord.Forbidden, discord.NotFound):
            return

    if reaction_emoji == "🔊":
        # Joins the voice channel the user is in.
        try:
            await reaction.message.clear_reactions()
        except (discord.Forbidden, discord.NotFound):
            pass

        voice_state = user.voice
        if not voice_state:
            try:
                return await reaction.message.edit(embed=StandardisedEmbed(
                    user, "Voice channel not found.", "You are not in a voice "
                    "channel.", False
                ))
            except (discord.Forbidden, discord.NotFound):
                return

        voice_channel = voice_state.channel
        if voice_channel.id in muted_voice_clients or voice_channel.id in \
                voice_clients:
            try:
                return await reaction.message.edit(embed=StandardisedEmbed(
                    user, "I am already in the voice channel you are in.",
                    "I can't do anymore than that, right?", False
                ))
            except (discord.Forbidden, discord.NotFound):
                return

        for guild_channel in reaction.message.guild.channels:
            if isinstance(guild_channel, discord.VoiceChannel):
                if guild_channel.id in muted_voice_clients or \
                        guild_channel.id in voice_clients:
                    from_muted = False
                    try:
                        voice_client = muted_voice_clients[guild_channel.id]
                        from_muted = True
                    except KeyError:
                        voice_client = voice_clients[guild_channel.id]

                    try:
                        await voice_client.move_to(voice_channel)
                    except (discord.Forbidden, discord.NotFound):
                        try:
                            return await reaction.message.edit(
                                embed=StandardisedEmbed(
                                    user, "I don't have permission.",
                                    "I don't have permission to join"
                                    "that voice channel.", False
                                )
                            )
                        except (discord.Forbidden, discord.NotFound):
                            return

                    try:
                        del muted_voice_clients[guild_channel.id]
                    except KeyError:
                        del voice_clients[guild_channel.id]

                    if from_muted:
                        donor_voice_client = list(voice_clients.values())[0]
                        donor_player = donor_voice_client.get_current_player()
                        handler = PreloadedBytesHandler(
                            donor_player.preloaded_bytes
                        )
                        handler.reads = donor_player.reads
                        voice_client.play(handler)
                        voice_clients[voice_channel.id] = voice_client

                    guilddb.voice_channel = voice_channel.id
                    await objects.update(guilddb)

                    try:
                        return await reaction.message.edit(
                            embed=StandardisedEmbed(
                                user, "I moved to your voice channel.",
                                "Yayyyyyyyy!"
                            )
                        )
                    except (discord.Forbidden, discord.NotFound):
                        return

        try:
            voice_client = await voice_channel.connect()
        except (discord.Forbidden, discord.NotFound):
            try:
                return await reaction.message.edit(
                    embed=StandardisedEmbed(
                        user, "I don't have permission.",
                        "I don't have permission to join"
                        "that voice channel.", False
                    )
                )
            except (discord.Forbidden, discord.NotFound):
                return

        donor_voice_client = list(voice_clients.values())[0]
        donor_player = donor_voice_client.get_current_player()
        handler = PreloadedBytesHandler(
            donor_player.preloaded_bytes
        )
        handler.reads = donor_player.reads
        voice_client.play(handler)
        voice_clients[voice_channel.id] = voice_client

        guilddb.voice_channel = voice_channel.id
        await objects.update(guilddb)

        try:
            await reaction.message.edit(
                embed=StandardisedEmbed(
                    user, "I moved to your voice channel.",
                    "Yayyyyyyyy!"
                )
            )
        except (discord.Forbidden, discord.NotFound):
            pass
# The handler for the reaction based menu.

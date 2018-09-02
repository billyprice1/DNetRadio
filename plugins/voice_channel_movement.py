from backbones.client import client
from backbones.voice import voice_clients, muted_voice_clients,\
    PreloadedBytesHandler
# Imports go here.


@client.listen
async def on_voice_state_update(member, before, after):
    if member.id == client.user.id:
        # Ok, this is us.
        if not before.channel:
            return

        try:
            voice_client = voice_clients[before.channel.id]
            del voice_clients[before.channel.id]
        except KeyError:
            try:
                voice_client = muted_voice_clients[before.channel.id]
                del muted_voice_clients[before.channel.id]
            except KeyError:
                return

        if after.channel:
            updated_after = client.get_channel(after.channel.id)
            members = updated_after.members
            if len(members) > 1:
                voice_clients[after.channel.id] = voice_client
                if not voice_client.is_playing():
                    donor_voice_client = list(voice_clients.values())[0]
                    donor_player = donor_voice_client.get_current_player()
                    handler = PreloadedBytesHandler(
                        donor_player.preloaded_bytes
                    )
                    handler.reads = donor_player.reads
                    voice_client.play(handler)
            else:
                muted_voice_clients[after.channel.id] = voice_client
                voice_client.stop()

        if not client.get_channel(before.channel.id):
            # Oh the channel got deleted. What a bad day in the office!
            await voice_client.disconnect()

        return

    # This is another user.

    if before.channel:
        updated_before = client.get_channel(before.channel.id)
        if updated_before:
            members = updated_before.members
            if len(members) == 1 and members[0].id == client.user.id:
                # We need to mute.
                voice_client = voice_clients[before.channel.id]
                del voice_clients[before.channel.id]
                voice_client.stop()
                muted_voice_clients[before.channel.id] = voice_client

    if after.channel and after.channel.id in muted_voice_clients:
        # Time to chuck this back in the pool of stuff playing.
        voice_client = muted_voice_clients[after.channel.id]

        donor_voice_client = list(voice_clients.values())[0]
        donor_player = donor_voice_client.get_current_player()
        handler = PreloadedBytesHandler(donor_player.preloaded_bytes)
        handler.reads = donor_player.reads
        voice_client.play(handler)

        del muted_voice_clients[after.channel.id]
        voice_clients[after.channel.id] = voice_client

from backbones.client import client
# Imports go here.


@client.listen
async def on_message(message):
    if client.user.id in [x.id for x in message.mentions]:
        client.dispatch("bot_tag", message)
# Detects when the bot was tagged.

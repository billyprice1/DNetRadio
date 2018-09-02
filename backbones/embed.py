import discord
# Imports go here.


class StandardisedEmbed(discord.Embed):
    """Woooo standardisation!"""
    def __init__(self, user, title, description, colour_or_success=True):
        if colour_or_success is True:
            colour = discord.Colour.blurple()
        elif colour_or_success is False:
            colour = discord.Colour.red()
        else:
            colour = colour_or_success

        super().__init__(title=title, description=description, colour=colour)
        self.set_author(name=user.name, icon_url=user.avatar_url)

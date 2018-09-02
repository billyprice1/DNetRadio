import discord
from backbones.loop import loop
from backbones.config import config
# Imports go here.


class EventHooker:
    def __init__(self, _client, event_name):
        self.client = _client
        self.event_name = event_name

    async def __call__(self, *args, **kwargs):
        try:
            for hook in self.client.hooks[self.event_name]:
                loop.create_task(hook(*args, **kwargs))
        except KeyError:
            pass
# The class used to hook onto events.


class QuickHookClient(discord.AutoShardedClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hooks = {}

    def listen(self, func):
        if func.__name__ in self.hooks:
            self.hooks[func.__name__].append(func)
        else:
            self.hooks[func.__name__] = [func]
            self.__setattr__(func.__name__, EventHooker(self, func.__name__))
# A client used for quick hooking.


client = QuickHookClient(
    shard_ids=config['shard_config'].get("shard_ids"),
    shard_count=config['shard_config'].get("shard_count"),
    loop=loop
)
# Defines the client.

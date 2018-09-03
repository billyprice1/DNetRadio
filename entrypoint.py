from backbones.client import client
from backbones.models import create_tables, database
from backbones.config import config
from pluginbase import PluginBase
from safeembeds import patch_discord
import logging
import pyximport
# Imports go here.

pyximport.install()
# Allows *.pyx imports.

logging.basicConfig(level=logging.INFO)
# Sets up logging.

patch_discord()
# Patches the default Discord embed class to truncate embeds.

create_tables()
# Creates any tables needed.

database.set_allow_sync(False)
# Blocks non-async stuff.

plugin_base = PluginBase("__main__.plugins")
plugin_source = plugin_base.make_plugin_source(searchpath=["./plugins"])
for plugin in plugin_source.list_plugins():
    plugin_source.load_plugin(plugin)
# Loads all of the plugins.

client.run(config['token'])
# Runs the client.

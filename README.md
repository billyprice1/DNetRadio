[![Build Status](https://travis-ci.org/JakeMakesStuff/DNetRadio.svg?branch=master)](https://travis-ci.org/JakeMakesStuff/DNetRadio)
[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

# DNetRadio

[The official bot can be invited from this link.](https://discordapp.com/oauth2/authorize?client_id=455289983725731842&scope=bot&permissions=36726080)

DNetRadio is a fast and intuitive Postgres-based and PEP8-compliant radio bot for Discord that is written fully in Python. Tagging the bot if you are a administrator pops up various options that allow the bot to be toggled or if the administrator is in a voice channel, join that channel.

It is designed to be reaction based, very fast to operate and very intuitive:

<img src="https://some-banned-discord-user.pinged-b1nzy-for.fun/5kxd1.png" height="400">

The bot also displays what is playing as the game so your users know what to expect when they join:

![game](https://some-banned-discord-user.pinged-b1nzy-for.fun/2cr19.png)

DNetRadio is also designed to be easily sharded either on the same server or over multiple servers to handle the load. We offer a lot of flexibility in  the configuration for this:
```json
"shard_config": {
  "shard_ids": [0],
  "shard_count": 1
}
```
If you are just sharding on one server, you can also completely remove `shard_ids`.

## Installation
In order to setup DNetRadio you will need the following things:
- Some banging tunes (Some jingles are nice too)!
- A server that has hopefully unlimited bandwidth and a amount of RAM adequate for the the `songs_in_memory` configuration you want. The normal config uses ~500MB RAM with a average amount of 3-4 minute songs, so I'd make the server have 1GB+ RAM.
- A Discord bot account.
- A Postgres server (either local or hosted elsewhere). **I will not help with the configuration of this server, I am not Postgres support.**
- FFMpeg installed in the PATH of the system you want to run this on (Ubuntu/Debian should be as easy as `sudo apt-get install ffmpeg`, Windows/other OS's is  far more  manual, I suggest Google'ing if you do not know how to do this).
- If you are on Linux, you'll need to install gcc.
- Python 3.6+ (I suggest 3.6.6, 3.5.x won't work and 3.7 is a bit more buggy on discord.py rewrite in my experience).
- Knowledge of the commandline trigger for Python 3.6+ (On most Linux/Mac-based systems, `py` or `python` triggers a older version of Python and you need to use `python3.6`, however for this tutorial I will be using  `py` so replace that with whatever your trigger is).

Got all that? Great, lets continue!

Firstly, we'll want to edit the sample config. Copy `config.sample.json` to `config.json` and open it up in a text editor. Firstly, add the token for your Discord bot where it says `DISCORD_TOKEN_HERE`. After that, you can add the user IDs for the owners where it says `owner_ids`. For example, this is it in my config:

```json
"owner_ids" [
  280610586159611905
]
```

Ok now that is done you will want to set your shard configuration and Postgres configuration. For the Postgres configuration, just insert the information in there from when you setup the bot. For the shard configuration follow this general rule:
- 1-20 guild(s) - You can remove the `shard_ids` attribute and keep shard count at 1.
- 20-70 guilds - You can remove the `shard_ids` attribute and change the shard count to 5.
- 100-1000 guilds - You can remove the `shard_ids` attribute and change the shard count to 10.
- 1000+ guilds - I'd span it over multiple servers, keep the shard count the same across all of the servers. You can remove the `shard_ids` attribute and change the shard count to 5.

Ok that is your configuration set after that! You can then run `py -m pip install -r requirements.txt` to install the requirements. If you are on a UNIX-based system, you can then run `py -m pip install uvloop` to install uvloop which is a slightly faster event loop.

From here, make 2 folders, one named "songs" and one named "jingles" (if you have any jingles). Put the songs/jingles in these folders in the MP3 format with the filename being what the thing you want to display as the game.

After this, success! Your bot should be fully configured. To test it, you can run `py entrypoint.py`. If it works, congratulations! If not, feel free to DM me (JakeMakesStuff#0001) on Discord. I'll be happy to help.

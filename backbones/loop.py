try:
    import uvloop
    loop = uvloop.new_event_loop()
except ImportError:
    import asyncio
    loop = asyncio.get_event_loop()
# Gets the event loop.

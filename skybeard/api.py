from skybeard.beards import Beard, SlashCommand
from skybear.server import web

@async_get('/loadedBeards')
async def loaded_beards(request):
    return web.json_response([str(x) for x in Beard.beards])

@async_get('/availableCommands')
async def available_commands(request):
    d = {}
    for beard in Beard.beards:
        cmds = []
        for cmd in beard.__commands__:
            if isinstance(cmd, SlashCommand):
                cmds.append(dict(command = cmd.cmd, hint = cmd.hlp))
        if cmds:
            d[beard.__name__] = cmds

    return web.json_response(d)
    

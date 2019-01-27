import aiohttp
import argparse
import asyncio
import discord
from discord.ext import commands
import io
import json
import logging
import logging.config
import re
import subprocess
import zipfile

# Logging setup
logging.config.fileConfig('config/logging.conf')
log = logging.getLogger('dev')

# Doom configuration initialization
with open('config/doom.json', 'r') as f:
    configDoom = json.load(f)
    log.info('Doom configuration loaded')

bot = commands.Bot(command_prefix='!')

@bot.command()
async def drown(ctx):
    await ctx.send("I can't")

@bot.command()
async def host(ctx, iwad, idgames):
    iwad = iwad.lower()
    if iwad not in configDoom['iwads']:
        await ctx.send('Invalid IWAD')
        return

    match = re.search('doomworld\\.com\\/idgames', idgames)
    if not match:
        await ctx.send('Invalid idgames url')
        return

    wads = []
    gameName = idgames.split('/')[-1]
    url = configDoom['idgamesMirror'] + idgames[match.end():] + '.zip'
    log.info('Attempting to download wad from {}'.format(url))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # This is synchronous which could potentially cause problems, but since
                # the bot only serves one server, I'm not going to worry about it now.
                with zipfile.ZipFile(io.BytesIO(await response.read()), 'r') as wadZip:
                    for name in wadZip.namelist():
                        if re.fullmatch('.*\\.wad', name):
                            wadZip.extract(name, configDoom['wadsDirectory'])
                            wads.append(configDoom['wadsDirectory'] + '/' + name)
            else:
                log.warning('Could not download wad from {0}, response status: {1}'.format(url, response.status))
                ctx.send('Could not download the wad')

    # Check that we have extracted wads before starting the server
    if len(wads) == 0:
        await ctx.send('No wads found in zip file')
        return

    # Build the command to run the server
    serverName = configDoom['serverBaseName'] + ' ({})'.format(gameName) 
    cmd = [
        configDoom['zandronum'],
        '-host',
        '-iwad',
        configDoom['iwads'][iwad],
    ]
    for wad in wads:
        cmd.append('-file')
        cmd.append(wad)
    cmd.append(configDoom['serverArguments'])
    cmd.append('+sv_hostname')
    cmd.append(serverName)
    
    # Start the server and notify the users
    log.info('Running command to start server: {}'.format(cmd))
    subprocess.Popen(cmd)
    await ctx.send('Created Zandronum server "{}", have fun!'.format(serverName))

@host.error
async def host_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.TooManyArguments):
        await ctx.send('Usage: !host <iwad> <idgames url>')
    else:
        # @Krankdud when something goes wrong
        await ctx.send('An error occurred when trying to host. <@83043150397968384>')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help='discord API token')
    args = parser.parse_args()

    log.info('Running the bot')
    bot.run(args.token)

if __name__ == '__main__':
    main()
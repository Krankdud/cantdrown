import aiohttp
import argparse
import asyncio
import discord
from discord.ext import commands
import io
import logging
import logging.config
import re
import subprocess
import zipfile

IDGAMES_MIRROR = 'http://mirrors.syringanetworks.net/idgames'
WAD_DIR = 'tmp'
IWAD_PATH = '/cygdrive/g/Games/Doom/Iwads/DOOM2.WAD'
ZANDRONUM_PATH = '/cygdrive/g/Games/Doom/Zandronum/zandronum.exe'

logging.config.fileConfig('config/logging.conf')

log = logging.getLogger('dev')
bot = commands.Bot(command_prefix='!')

@bot.command()
async def drown(ctx):
    await ctx.send("I can't")

@bot.command()
async def host(ctx, iwad, idgames):
    iwad = iwad.lower()
    if iwad != 'doom' and iwad != 'doom2' and iwad != 'tnt' and iwad != 'plutonia':
        await ctx.send('Invalid IWAD')
        return

    match = re.search('doomworld\\.com\\/idgames', idgames)
    if not match:
        await ctx.send('Invalid idgames url')
        return

    wads = []
    url = IDGAMES_MIRROR + idgames[match.end():] + '.zip'
    log.info('Attempting to download wad from {}'.format(url))
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with zipfile.ZipFile(io.BytesIO(await response.read()), 'r') as wadZip:
                    for name in wadZip.namelist():
                        if re.fullmatch('.*\\.wad', name):
                            wadZip.extract(name, WAD_DIR)
                            wads.append(WAD_DIR + '/' + name)
            else:
                log.warning('Could not download wad from {0}, response status: {1}'.format(url, response.status))
                ctx.send('Could not download the wad')

    if len(wads) == 0:
        await ctx.send('No wads found in zip file')
        return

    cmd = [
        ZANDRONUM_PATH,
        #'-host',
        '-iwad',
        IWAD_PATH,
    ]
    for wad in wads:
        cmd.append('-file')
        cmd.append(wad)
    
    log.info('Running command to start server: {}'.format(cmd))
    subprocess.Popen(cmd)
    await ctx.send('Server started, go get those frags!')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help='discord API token')
    parser.add_argument('-c', '--config', help='configuration')
    args = parser.parse_args()

    log.info('running bot')
    bot.run(args.token)

if __name__ == '__main__':
    main()
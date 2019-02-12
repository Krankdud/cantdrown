import aiohttp
import asyncio
from discord.ext import commands
import io
import json
import logging
import re
import subprocess
from urllib.parse import parse_qs, urlparse, urlunparse
import zipfile

log = logging.getLogger('dev')

class DoomCog:
    def __init__(self, bot):
        self.bot = bot

        # Doom configuration initialization
        with open('config/doom.json', 'r') as f:
            self.config = json.load(f)
            log.info('Doom configuration loaded')

    @commands.command()
    async def host(self, ctx, *args):
        if len(args) == 0:
            await self.host_help(ctx)
            return

        if len(args) == 1 and len(ctx.message.attachments) == 0:
            await self.host_help(ctx)
            return

        iwad = args[0].lower()
        if iwad not in self.config['iwads']:
            await ctx.send('Invalid IWAD')
            await self.host_help(ctx)
            return

        url = ''
        urlIsZip = False
        gameName = ''
        if len(args) == 1:
            attachment = ctx.message.attachments[0]
            url = attachment.url
            gameName = attachment.filename.split('.')[0]
        else:
            fileURL = urlparse(args[1])
            if 'doomworld' in fileURL.netloc:
                log.info('Obtaining wad from idgames mirror...')
                idgames = args[1]
                match = re.search('doomworld\\.com\\/idgames', idgames)
                if not match:
                    await ctx.send('Invalid idgames url')
                    await self.host_help(ctx)
                    return
                url = self.config['idgamesMirror'] + idgames[match.end():] + '.zip'
                gameName = idgames.split('/')[-1]
                urlIsZip = True
            elif 'dropbox.com' in fileURL.netloc:
                log.info('Obtaining wad from Dropbox...')
                url = urlunparse((fileURL.scheme, fileURL.netloc, fileURL.path, fileURL.params, 'raw=1', fileURL.fragment))
            elif 'drive.google.com' in fileURL.netloc:
                log.info('Obtaining wad from Google Drive...')
                googleDriveId = ''
                if fileURL.path == '/open':
                    qs = parse_qs(fileURL.query)
                    googleDriveId = qs['id'][0]
                elif 'file/d' in fileURL.path:
                    googleDriveId = fileURL.path.split('/')[3]
                else:
                    await ctx.send('Invalid Google Drive url')
                    await self.host_help(ctx)
                    return
                url = 'https://drive.google.com/uc?export=download&id={0}'.format(googleDriveId)

        wads = []
        log.info('Attempting to download wad from {}'.format(url))
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    filename = ''
                    # Check for Content-Disposition in the response header for obtaining the filename from
                    # Dropbox and Google Drive downloads
                    if 'Content-Disposition' in response.headers:
                        match = re.search('filename="(.*)"', response.headers['Content-Disposition'])
                        filename = match.group(1)
                        gameName = filename[:-4]
                        if filename[-4:].lower() == '.zip':
                            urlIsZip = True

                    if urlIsZip:
                        # This is synchronous which could potentially cause problems, but since
                        # the bot only serves one server, I'm not going to worry about it now.
                        with zipfile.ZipFile(io.BytesIO(await response.read()), 'r') as wadZip:
                            for name in wadZip.namelist():
                                if name[-4:].lower() == '.wad' or name[-4:].lower() == '.pk3':
                                    wadZip.extract(name, self.config['wadsDirectory'])
                                    wads.append(self.config['wadsDirectory'] + '/' + name)
                    elif filename[-4:].lower() == '.wad' or filename[-4:].lower == '.pk3':
                        path = self.config['wadsDirectory'] + '/' + filename
                        wads.append(path)
                        with open(path, mode='wb') as f:
                            f.write(await response.read())
                else:
                    log.warning('Could not download wad from {0}, response status: {1}'.format(url, response.status))
                    ctx.send('Could not download the wad')

        # Check that we have extracted wads before starting the server
        if len(wads) == 0:
            await ctx.send('No wads found in the zip file')
            return

        # Build the command to run the server
        serverName = self.config['serverBaseName'] + ' ({})'.format(gameName) 
        cmd = [
            self.config['zandronum'],
            '-host',
            '-iwad',
            self.config['iwads'][iwad],
        ]
        for wad in wads:
            cmd.append('-file')
            cmd.append(wad)
        cmd.append(self.config['serverArguments'])
        cmd.append('+sv_hostname')
        cmd.append(serverName)

        # Start the server and notify the users
        log.info('Running command to start server: {}'.format(cmd))
        subprocess.Popen(cmd)
        await ctx.send('Created Zandronum server "{}", have fun!'.format(serverName))

    @host.error
    async def host_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.TooManyArguments):
            await ctx.send('There are either too many arguments, or an argument is missing')
            await self.host_help(ctx)
        elif isinstance(error, commands.CommandInvokeError) and isinstance(error.original, zipfile.BadZipFile):
            await ctx.send('The attachment is not a zip file')
            await self.host_help(ctx)
        else:
            log.error(error)
            await ctx.send('An error occurred when trying to host.')

    async def host_help(self, ctx):
        helpMsg = '```Usage:\n'
        helpMsg += '!host <iwad> <idgames url> - Host a wad from the idgames archive\n'
        helpMsg += '!host <iwad> - Use with an attached zip file to host the contained wad\n'
        helpMsg += '\nValid iwads:'
        for iwad in self.config['iwads']:
            helpMsg += '\n{}'.format(iwad)
        helpMsg += '```'
        await ctx.send(helpMsg)

def setup(bot):
    bot.add_cog(DoomCog(bot))
    log.info('Added Doom cog')
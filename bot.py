import argparse
import asyncio
import discord
from discord.ext import commands
import logging
import logging.config

logging.config.fileConfig('config/logging.conf')

log = logging.getLogger('dev')
bot = commands.Bot(command_prefix='!')

@bot.command()
async def drown(ctx):
    await ctx.send("I can't")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help='discord API token')
    parser.add_argument('-c', '--config', help='configuration')
    args = parser.parse_args()

    log.info('running bot')
    bot.run(args.token)

if __name__ == '__main__':
    main()
import argparse
import asyncio
import discord
from discord.ext import commands
import logging
import logging.config

# Logging setup
logging.config.fileConfig('config/logging.conf')
log = logging.getLogger('dev')

bot = commands.Bot(command_prefix='!')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('token', help='discord API token')
    args = parser.parse_args()

    log.info('Loading cogs...')
    bot.load_extension('cogs.doom')
    bot.load_extension('cogs.misc')
    log.info('Running the bot...')
    bot.run(args.token)

if __name__ == '__main__':
    main()
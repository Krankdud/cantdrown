from discord.ext import commands
import logging

log = logging.getLogger('dev')

class MiscCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def drown(self, ctx):
        await ctx.send("I can't")

def setup(bot):
    bot.add_cog(MiscCog(bot))
    log.info('Added misc cog')

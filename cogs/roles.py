from discord.ext import commands
import json
import logging

log = logging.getLogger('dev')

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        with open('config/roles.json', 'r') as f:
            self.config = json.load(f)
            log.info('Roles configuration loaded')

    @commands.command()
    async def role(self, ctx, desiredRoleId):
        desiredRoleId = desiredRoleId.lower()
        if desiredRoleId not in self.config['roles']:
            await ctx.send('Invalid role')
            await self.role_help(ctx)
            return

        user = ctx.message.author
        guild = ctx.message.guild
        desiredRole = guild.get_role(int(self.config['roles'][desiredRoleId]))

        for role in user.roles:
            if role == desiredRole:
                await user.remove_roles(role)
                await ctx.send('<@{0}>: Removed from {1} role'.format(user.id, role.name))
                return

        await user.add_roles(desiredRole)
        await ctx.send('<@{0}>: Added to {1} role'.format(user.id, desiredRole.name))

    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Need to include a valid role')
        else:
            log.error(error)
            await ctx.send('An error occured when managing roles')
        await self.role_help(ctx)
    
    async def role_help(self, ctx):
        helpMsg = '```Usage\n'
        helpMsg += '!role <role> - Add yourself to a role, or remove yourself if you are already in it\n'
        helpMsg += '\nValid roles:'
        for role in self.config['roles']:
            helpMsg += '\n{}'.format(role)
        helpMsg += '```'
        await ctx.send(helpMsg)

def setup(bot):
    bot.add_cog(RolesCog(bot))
    log.info('Added roles cog')

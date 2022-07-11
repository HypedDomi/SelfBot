from datetime import datetime, timedelta
import requests
import discord
from typing import Union
from discord.ext import commands
from cogs.utils.helper import Plural, TimeParser, get_banned_user


class Moderator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> You can't kick yourself", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> You can't kick someone who has a higher role than you", mention_author=False)
        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.reply("> No permission to kick user", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User not found", mention_author=False)
        response = f"> {member.mention} got kicked"
        if reason:
            response += f"\n> Reason: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> You cannot ban yourself", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> You cannot ban someone who has a higher role than you", mention_author=False)
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            return await ctx.reply("> No authorization to ban users", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User not found", mention_author=False)
        response = f"> {member.mention} was banned"
        if reason:
            response += f"\n> Reason: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def unban(self, ctx, *, user: Union[discord.User, str]):
        if not isinstance(user, discord.User):
            user = await get_banned_user(ctx, user)
            if user == None:
                return await ctx.reply("> User not found", mention_author=False)
        user = await self.bot.fetch_user(user.id)
        try:
            await ctx.guild.unban(user)
        except discord.Forbidden:
            return await ctx.reply("> No permission to unban user", mention_author=False)
        except discord.NotFound:
            return await ctx.reply(f"> {user.mention} is not banned", mention_author=False)
        await ctx.reply(f"> {user.mention} was unbanned", mention_author=False)

    @commands.command()
    async def softban(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> You cannot ban yourself", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> You cannot ban someone who has a higher role than you", mention_author=False)
        try:
            await member.ban(reason=reason)
            await member.unban()
        except discord.Forbidden:
            return await ctx.reply("> No authorization to ban users", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User not found", mention_author=False)
        response = f"> {member.mention} was kicked and all messages were deleted"
        if reason:
            response += f"\n> Reason: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def slowmode(self, ctx, seconds: Union[int, str] = None):
        seconds = seconds or 0
        if not isinstance(seconds, int):
            return await ctx.reply("> Delay must be a number", mention_author=False)
        if seconds < 0:
            return await ctx.reply("> Delay must be a positive number", mention_author=False)
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
        except discord.Forbidden:
            return await ctx.reply("> No permission to edit the channel", mention_author=False)
        if seconds == 0:
            await ctx.reply("> Slow mode has been deactivated", mention_author=False)
        else:
            await ctx.reply(f"> The slow mode is set to {Plural(Seconds=seconds)}", mention_author=False)
    
    @commands.command()
    async def clear(self, ctx, amount: Union[int, str]):
        if not isinstance(amount, int):
            return await ctx.reply("> That doesn't look like a number", mention_author=False)
        if amount < 1:
            return await ctx.reply("> You must delete at least one message", mention_author=False)
        if amount > 100:
            return await ctx.reply("> You can delete a maximum of 100 messages", mention_author=False)
        try:
            await ctx.channel.purge(limit=amount+1)
        except discord.Forbidden:
            return await ctx.reply("> No permission to delete messages", mention_author=False)
        await ctx.send(f"> {Plural(Nachricht=amount)} {Plural(wurde=amount)} turned off", delete_after=10)
    
    @commands.command()
    async def timeout(self, ctx, member: discord.Member, time: str, *, reason = ""):
        try:
            time = TimeParser(time)
        except ValueError:
            return await ctx.reply("> Invalid time format", mention_author=False)

        if member == ctx.author:
            return await ctx.reply("> You cannot timeout yourself", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> You cannot timeout someone who has a higher role than you", mention_author=False)
        if member.guild_permissions.administrator:
            return await ctx.reply("> You cannot timeout someone who has admin rights", mention_author=False)
        
        timestamp = datetime.utcnow().timestamp() + time.seconds
        timestamp = datetime.fromtimestamp(timestamp).isoformat()
        
        url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{member.id}"
        headers = { "Authorization": self.bot.http.token, "Content-Type": "application/json", "x-audit-log-reason": reason }
        data = { "communication_disabled_until": timestamp }
        r = requests.patch(url, headers=headers, json=data)
        if r.status_code != 200:
            return await ctx.reply(f"> There was an error\n```json\n{r.json()}\n```", mention_author=False)
        response = f"> {member.mention} has been banned"
        response += f"\n> Time: `{TimeParser.human_timedelta(datetime.utcnow() - timedelta(seconds=time.seconds))}`"
        if reason:
            response += f"\n> Reason: `{reason}`"
        await ctx.reply(response, allowed_mentions=discord.AllowedMentions(users=False, replied_user=False))


def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))

import discord
from typing import Union
from discord.ext import commands
from cogs.utils.helper import Plural, get_banned_user


class Moderator(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> Du kannst dich nicht selber kicken", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> Du kannst nieman kicken, der eine höhere Rolle hat als du", mention_author=False)
        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um User zu kicken", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User nicht gefunden", mention_author=False)
        response = f"> {member.mention} wurde gekickt"
        if reason:
            response += f"\n> Grund: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> Du kannst dich nicht selber bannen", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> Du kannst nieman bannen, der eine höhere Rolle hat als du", mention_author=False)
        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um User zu bannen", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User nicht gefunden", mention_author=False)
        response = f"> {member.mention} wurde gebannt"
        if reason:
            response += f"\n> Grund: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def unban(self, ctx, *, user: Union[discord.User, str]):
        if not isinstance(user, discord.User):
            user = await get_banned_user(ctx, user)
            if user == None:
                return await ctx.reply("> User nicht gefunden", mention_author=False)
        user = await self.bot.fetch_user(user.id)
        try:
            await ctx.guild.unban(user)
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um User zu entbannen", mention_author=False)
        except discord.NotFound:
            return await ctx.reply(f"> {user.mention} ist nicht gebannt", mention_author=False)
        await ctx.reply(f"> {user.mention} wurde entbannt", mention_author=False)

    @commands.command()
    async def softban(self, ctx, member: discord.Member, *, reason=""):
        if member == ctx.author:
            return await ctx.reply("> Du kannst dich nicht selber bannen", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> Du kannst nieman bannen, der eine höhere Rolle hat als du", mention_author=False)
        try:
            await member.ban(reason=reason)
            await member.unban()
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um User zu bannen", mention_author=False)
        except discord.NotFound:
            return await ctx.reply("> User nicht gefunden", mention_author=False)
        response = f"> {member.mention} wurde gekickt und alle Nachrichten wurden gelöscht"
        if reason:
            response += f"\n> Grund: `{reason}`"
        await ctx.reply(response, mention_author=False)

    @commands.command()
    async def slowmode(self, ctx, seconds: Union[int, str] = None):
        seconds = seconds or 0
        if not isinstance(seconds, int):
            return await ctx.reply("> Delay muss eine Nummer sein", mention_author=False)
        if seconds < 0:
            return await ctx.reply("> Delay muss eine positive Nummer sein", mention_author=False)
        try:
            await ctx.channel.edit(slowmode_delay=seconds)
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um den Channel zu editieren", mention_author=False)
        if seconds == 0:
            await ctx.reply("> Slowmode wurde deaktiviert", mention_author=False)
        else:
            await ctx.reply(f"> Der Slowmode wurde auf {seconds} {Plural(Sekunde=seconds)} gesetzt", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))

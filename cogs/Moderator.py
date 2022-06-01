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
            await ctx.reply(f"> Der Slowmode wurde auf {Plural(Sekunde=seconds)} gesetzt", mention_author=False)
    
    @commands.command()
    async def clear(self, ctx, amount: Union[int, str]):
        if not isinstance(amount, int):
            return await ctx.reply("> Das sieht nicht nach einer Zahl aus", mention_author=False)
        if amount < 1:
            return await ctx.reply("> Du musst mindestens eine Nachricht löschen", mention_author=False)
        if amount > 100:
            return await ctx.reply("> Du kannst maximal 100 Nachrichten löschen", mention_author=False)
        try:
            await ctx.channel.purge(limit=amount+1)
        except discord.Forbidden:
            return await ctx.reply("> Keine Berechtigung um Nachrichten zu löschen", mention_author=False)
        await ctx.send(f"> {Plural(Nachricht=amount)} {Plural(wurde=amount)} gelöscht", delete_after=10)
    
    @commands.command()
    async def timeout(self, ctx, member: discord.Member, time: str, *, reason = ""):
        try:
            time = TimeParser(time)
        except ValueError:
            return await ctx.reply("> Ungültiges Zeitformat", mention_author=False)

        if member == ctx.author:
            return await ctx.reply("> Du kannst dich nicht selber timeouten", mention_author=False)
        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.reply("> Du kannst niemanden timeouten der eine höhere Rolle hat als du", mention_author=False)
        if member.guild_permissions.administrator:
            return await ctx.reply("> Du kannst niemanden timeouten der Adminrechte hat", mention_author=False)
        
        timestamp = datetime.utcnow().timestamp() + time.seconds
        timestamp = datetime.fromtimestamp(timestamp).isoformat()
        
        url = f"https://discord.com/api/v9/guilds/{ctx.guild.id}/members/{member.id}"
        headers = { "Authorization": self.bot.http.token, "Content-Type": "application/json" }
        data = { "communication_disabled_until": timestamp }
        r = requests.patch(url, headers=headers, json=data)
        if r.status_code != 200:
            return await ctx.reply(f"> Es trat ein Fehler auf\n```json\n{r.json()}\n```", mention_author=False)
        await ctx.reply(f"> {member.mention} wurde für {TimeParser.human_timedelta(datetime.utcnow() - timedelta(seconds=time.seconds))} gesperrt", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Moderator(bot))

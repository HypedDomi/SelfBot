import io
import os
import platform
import sys
import time
import aiohttp
import psutil
import discord
import emoji
from discord import PartialEmoji
from discord.ext import commands
from cogs.utils.helper import Plural


class Miscellaneous(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def uptime(self, ctx):
        timeUp = time.time() - self.bot.startTime
        hoursUp = int("{:.0f}".format(timeUp / 3600))
        minutesUp = int("{:.0f}".format((timeUp / 60) % 60))
        secondsUp = int("{:.0f}".format(timeUp % 60))
        await ctx.message.reply(f"> Uptime: {hoursUp} {Plural(Stunde=hoursUp)}, {minutesUp} {Plural(Minute=minutesUp)}, {secondsUp} {Plural(Sekunde=secondsUp)}", mention_author=False)

    @commands.command()
    async def snipe(self, ctx, mode=None):
        channel = ctx.channel
        if mode == "edit":
            try:
                message = self.bot.edited[channel.id]
            except KeyError:
                if str(ctx.channel.type) == "text":  # Guild
                    return await ctx.message.reply(f"> Es gibt keine kürzlich editierten Nachrichten in {channel.mention}", mention_author=False)
                elif str(ctx.channel.type) == "private":  # DM Channel
                    return await ctx.message.reply(f"> Es gibt keine kürzlich editierten Nachrichten bei {channel.recipient.mention}", allowed_mentions=discord.AllowedMentions(users=False, replied_user=False))
                elif str(ctx.channel.type) == "group":  # Group
                    return await ctx.message.reply(f"> Es gibt keine kürzlich editierten Nachrichten in {channel.name or 'der Gruppe'}", mention_author=False)
                else:
                    return await ctx.message.reply("> Es gibt keine kürzlich editierten Nachrichten", mention_author=False)
            msg = f"**{message.author}**\n {message.content}"
            await ctx.message.reply(msg.replace("\n", "\n> "), allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False))
        else:
            try:
                message = self.bot.deleted[channel.id]
            except KeyError:
                if str(ctx.channel.type) == "text":  # Guild
                    return await ctx.message.reply(f"> Es gibt keine kürzlich gelöschten Nachrichten in {channel.mention}", mention_author=False)
                elif str(ctx.channel.type) == "private":  # DM Channel
                    return await ctx.message.reply(f"> Es gibt keine kürzlich gelöschten Nachrichten bei {channel.recipient.mention}", allowed_mentions=discord.AllowedMentions(users=False, replied_user=False))
                elif str(ctx.channel.type) == "group":  # Group
                    return await ctx.message.reply(f"> Es gibt keine kürzlich gelöschten Nachrichten in {channel.name or 'der Gruppe'}", mention_author=False)
                else:
                    return await ctx.message.reply("> Es gibt keine kürzlich gelöschten Nachrichten", mention_author=False)
            msg = f"**{message.author}**\n {message.content}"
            files = []
            for attachment in message.attachments:
                async with aiohttp.ClientSession().get(attachment.url) as resp:
                    files.append(discord.File(io.BytesIO(await resp.read()), filename=attachment.filename))
            await ctx.message.reply(msg.replace("\n", "\n> "), allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=False), files=files)

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.reply(f"> Pong! {round(self.bot.latency * 1000)}ms", mention_author=False)

    @commands.command()
    async def sysinfo(self, ctx):
        cpu = '{:.2f}%'.format(psutil.cpu_percent())
        mem_usage = psutil.virtual_memory().used / 1024**2
        mem_total = psutil.virtual_memory().total / 1024**2
        memory = '{:.2f} MiB / {:.2f} MiB ({:.2f}%)'.format(
            mem_usage, mem_total, psutil.virtual_memory()[2])
        if os.name == "nt":
            system = '%s %s (%s)' % (platform.system(),
                                     platform.version(), sys.platform)
        else:
            syst = '%s %s' % (platform.linux_distribution(full_distribution_name=1)[
                              0].title(), platform.linux_distribution(full_distribution_name=1)[1])
            system = f"{platform.system()}, {', '.join(map(str, (syst, platform.release())))}"
        response = "**System Info**\n"
        response += f"> CPU: {cpu}\n"
        response += f"> Memory: {memory}\n"
        response += f"> System: {system}\n"
        await ctx.message.reply(response, mention_author=False)

    @commands.command()
    async def activity(self, ctx, game, *, title=None):
        if game == "clear":
            self.bot.activity = None
            await self.bot.change_presence(status=self.bot.status, activity=None, afk=True)
            await ctx.message.reply("> Aktivität entfernt", mention_author=False)

        elif 'play' == game or 'stream' == game or 'watch' == game or 'listening' == game or 'competing' == game or 'custom' == game:
            if not title == None:
                if game == "play":
                    self.bot.activity = discord.Activity(
                        type=discord.ActivityType.playing, name=title)
                    await self.bot.change_presence(status=self.bot.status, activity=discord.Activity(type=discord.ActivityType.playing, name=title), afk=True)
                    await ctx.message.reply("> Playing Aktivität gesetzt", mention_author=False)
                elif game == "stream":
                    profile = await (await self.bot.fetch_user(self.bot.user.id)).profile()
                    connections = profile.connected_accounts
                    for _, con in enumerate(connections):
                        if con["type"] == "twitch":
                            twitch = f"https://twitch.tv/{con['name']}"
                            break
                    if twitch == None:
                        return await ctx.message.reply("> Du hast keinen Twitch Account mit Discord verknüpft", mention_author=False)
                    self.bot.activity = discord.Streaming(
                        name=title, url=twitch)
                    await self.bot.change_presence(status=self.bot.status, activity=discord.Streaming(name=title, url=twitch), afk=True)
                    await ctx.message.reply("> Streaming Aktivität gesetzt", mention_author=False)
                elif game == "watch":
                    self.bot.activity = discord.Activity(
                        type=discord.ActivityType.watching, name=title)
                    await self.bot.change_presence(status=self.bot.status, activity=discord.Activity(type=discord.ActivityType.watching, name=title), afk=True)
                    await ctx.message.reply("> Watching Aktivität gesetzt", mention_author=False)
                elif game == "listening":
                    self.bot.activity = discord.Activity(
                        type=discord.ActivityType.listening, name=title)
                    await self.bot.change_presence(status=self.bot.status, activity=discord.Activity(type=discord.ActivityType.listening, name=title), afk=True)
                    await ctx.message.reply("> Listening Aktivität gesetzt", mention_author=False)
                elif game == "competing":
                    self.bot.activity = discord.Activity(
                        type=discord.ActivityType.competing, name=title)
                    await self.bot.change_presence(status=self.bot.status, activity=discord.Activity(type=discord.ActivityType.competing, name=title), afk=True)
                    await ctx.message.reply("> Competing Aktivität gesetzt", mention_author=False)
                elif game == "custom":
                    e = title.split()[0]
                    if not emoji.is_emoji(e):
                        emote = discord.utils.get(
                            self.bot.emojis, id=int(e.split(":")[2][:-1]))
                        if emote:
                            title = title.replace(e, "")
                            emote = PartialEmoji(
                                animated=emote.animated, name=emote.name, id=emote.id)
                    else:
                        emote = e
                        title = title.replace(e, "")
                    if title == "":
                        title = None
                    await self.bot.change_presence(status=self.bot.status, activity=discord.CustomActivity(title, emoji=emote), afk=True)
                    await ctx.message.reply("> Custom Aktivität gesetzt", mention_author=False)
        else:
            await ctx.message.reply(f"> Aktivität `{game}` existiert nicht", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Miscellaneous(bot))

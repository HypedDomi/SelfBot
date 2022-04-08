import time
import asyncio
import discord
from discord.ext import commands

replacements = {
    "shrug": "\xaf\_(\u30c4)_/\xaf",
    "timestamp": f"<t:{int(time.time())}>"
}


class EventHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if (isinstance(error, commands.CommandNotFound) or isinstance(error, discord.errors.NotFound) or isinstance(error, discord.NotFound)):
            return
        print("[ERROR]", str(error))

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.id != self.bot.user.id:
            return
        content = msg.content
        for key, value in replacements.items():
            try:
                content = content.replace("{" + {key} + "}", value)
            except TypeError:
                pass
        content = content.replace(self.bot.http.token, "🤡")
        if content == msg.content:
            return
        await msg.edit(content=content)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.id != self.bot.user.id:
            return
        content = after.content
        for key, value in replacements.items():
            try:
                content = content.replace("{" + {key} + "}", value)
            except TypeError:
                pass
        content = content.replace(self.bot.http.token, "🤡")
        if content == after.content:
            return
        await after.edit(content=content)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        self.bot.edited[before.channel.id] = before
        await asyncio.sleep(300)
        try:
            del self.bot.edited[before.channel.id]
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, msg: discord.Message) -> None:
        self.bot.deleted[msg.channel.id] = msg
        await asyncio.sleep(300)
        try:
            del self.bot.deleted[msg.channel.id]
        except KeyError:
            pass


def setup(bot: commands.Bot):
    bot.add_cog(EventHandler(bot))

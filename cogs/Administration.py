import asyncio
import os
import sys
from typing import Union
from discord.ext import commands

from cogs.utils.helper import Plural
import discord


class Administration(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def restart(self, ctx, delay: Union[int, str] = None):
        delay = delay or 5
        if not isinstance(delay, int):
            return await ctx.reply("> Delay muss eine Nummer sein", mention_author=False)
        if delay < 0:
            return await ctx.reply("> Delay muss eine positive Nummer sein", mention_author=False)
        await ctx.reply(f"> Bot startet in {delay} {Plural(Sekunde=delay)} neu", mention_author=False)
        if os.name == "nt":
            cwd = os.getcwd()
            restart = os.path.join(cwd, "restart.bat")
            with open(restart, "w") as f:
                f.write(f"@echo off\n")
                f.write(f"taskkill /PID {os.getpid()} /F\n")
                f.write(f"start {sys.executable} {sys.argv[0]}\n")
                f.write(f"del {restart}")
        await asyncio.sleep(delay)
        await self.bot.change_presence(status=discord.Status.invisible)
        if os.name == "nt":
            os.startfile(restart)
        else:
            os.popen("sudo -S %s" % ("service SelfBot restart"),
                     "w").write(self.bot.PASSWORD)


def setup(bot: commands.Bot):
    bot.add_cog(Administration(bot))

import asyncio
import os
import sys
from git import GitCommandError
from git.repo.base import Repo
from github import Github, UnknownObjectException
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
            return await ctx.reply("> Delay must be a number", mention_author=False)
        if delay < 0:
            return await ctx.reply("> Delay must be a positive number", mention_author=False)
        await ctx.reply(f"> The bot will restart in {Plural(Second=delay)}", mention_author=False)
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
            os.popen("sudo -S %s" % ("service SelfBot restart"), "w").write(self.bot.password)

    @commands.command()
    async def update(self, ctx):
        try:
            git = Github()
            repo = git.get_repo("HypedDomi/SelfBot")
            latest_commit = repo.get_commits()[0]
            if latest_commit.sha == self.bot.lastCommitSHA:
                return await ctx.reply("> You are already on the latest version", mention_author=False)
            url = f"https://github.com/HypedDomi/SelfBot"
            if os.path.exists("temp"):
                os.rmdir("temp")
            os.mkdir("temp")
            Repo.clone_from(url, "temp")
            self.bot.lastCommitSHA = latest_commit.sha
            with open("lastCommitSHA", "w") as f:
                f.write(self.bot.lastCommitSHA)
            if os.name == "nt":
                os.system("move /Y temp\\* .\\")
                for folder in os.listdir("temp"):
                    if os.path.isdir(os.path.join("temp", folder)):
                        os.system(f"move /Y temp\\{folder} .\\{folder}")
                os.system("rmdir /S /Q temp")
            else:
                os.system("cp -rf temp/* .")
                os.system("rm -rf temp")
            await ctx.reply("> Bot has been updated", mention_author=False)
            await ctx.invoke(self.restart)
        except UnknownObjectException:
            return await ctx.reply("> You do not have access to the repository", mention_author=False)
        except GitCommandError:
            return await ctx.reply("> An error occurred during the update", mention_author=False)
        except FileNotFoundError:
            return await ctx.reply("> Git is not installed", mention_author=False)

    @commands.command()
    async def version(self, ctx):
        await ctx.reply(f"> Version: `{self.bot.lastCommitSHA[:7]}`", mention_author=False)

    @commands.command()
    async def status(self, ctx, status: str):
        st = getattr(discord.Status, status.lower())
        if st is None:
            return await ctx.reply(f"> `{status}` does not exist", mention_author=False)
        await self.bot.change_presence(status=st, afk=True)
        await ctx.reply(f"> Status was set to `{status}`", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Administration(bot))

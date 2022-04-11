import asyncio
import os
import sys
from git import GitCommandError
from git.repo.base import Repo
from github import BadCredentialsException, Github, UnknownObjectException
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
                     "w").write(self.bot.password)

    @commands.command()
    async def update(self, ctx):
        try:
            git = Github(self.bot.githubToken)
            repo = git.get_repo("HypedDomi/SelfBot")
            latest_commit = repo.get_commits().reversed[0]
            if latest_commit.sha == self.bot.lastCommitSHA:
                return await ctx.reply("> Du bist bereits auf der neuesten Version", mention_author=False)
            url = f"https://{self.bot.githubToken}:x-oauth-basic@github.com/HypedDomi/SelfBot"
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
                os.system("mv temp/* ./")
                os.system("rm -rf temp")
            await ctx.reply("> Bot wurde aktualisiert", mention_author=False)
            await ctx.invoke(self.restart)
        except BadCredentialsException:
            return await ctx.reply("> Github Token ist falsch", mention_author=False)
        except UnknownObjectException:
            return await ctx.reply("> Du hast keinen Zugriff auf das Repository", mention_author=False)
        except GitCommandError:
            return await ctx.reply("> Es ist ein Fehler beim Update aufgetreten", mention_author=False)
        except FileNotFoundError:
            return await ctx.reply("> Git ist nicht installiert", mention_author=False)
    
    @commands.command()
    async def version(self, ctx):
        await ctx.reply(f"> Version: `{self.bot.lastCommitSHA}`", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Administration(bot))

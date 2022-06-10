import asyncio
import io
import platform
import sys
import textwrap
import time
import traceback
import os

from discord.ext import commands
from contextlib import redirect_stdout

from cogs.utils.helper import Plural, hastebin
import discord


class Debugger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.stream = io.StringIO()
        self.channel = None
        self._last_result = None

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')

    def getInterpreter(self, code):
        interpreter = "python"
        if code.startswith('```') and code.endswith('```'):
            interpreter = code.split('\n')[0].strip('```')
        return interpreter

    async def py_interpreter(self, env, body, ctx):
        stdout = io.StringIO()
        to_compile = 'async def func():\n{}'.format(textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send('```\n{}: {}\n```'.format(e.__class__.__name__, e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send('```\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()

            result = None
            if ret is None:
                if value:
                    result = '```\n{}\n```'.format(value)
                else:
                    try:
                        result = '```\n{}\n```'.format(repr(eval(body, env)))
                    except:
                        pass
            else:
                self._last_result = ret
                result = '```\n{}{}\n```'.format(value, ret)

            result = result.replace(self.bot.http.token, "TOKEN")
            if result:
                if len(str(result)) > 1950:
                    url = await hastebin(str(result).strip("`"))
                    result = 'Large output. Posted to Hastebin: %s' % url
                    await ctx.send(result)
                elif not result.replace("```\n\n```", "").strip() == "":
                    await ctx.send(result)
    
    async def js_interpreter(self, ctx):
        try:
            process = await asyncio.create_subprocess_exec('node', '%s/cogs/utils/temp' % os.getcwd(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except FileNotFoundError:
            return await ctx.send("```\nError: Node.js is not installed!\n```")
        stdout, stderr = await process.communicate()
        out = stdout.decode('utf-8') or stderr.decode('utf-8')
        out = out.replace(self.bot.http.token, "TOKEN")
        if out:
            if len(str(out)) > 1950:
                url = await hastebin(str(out).strip("`"))
                out = 'Large output. Posted to Hastebin: %s' % url
                await ctx.send(out)
            elif not out.replace("```\n\n```", "").strip() == "":
                await ctx.send('```\n{}\n```'.format(out))

    @commands.command()
    async def debug(self, ctx):
        response = "**Debug Infos**\n"
        if os.name == "nt":
            system = '%s %s (%s)' % (platform.system(),
                                     platform.version(), sys.platform)
        else:
            syst = '%s %s' % (platform.linux_distribution(full_distribution_name=1)[
                              0].title(), platform.linux_distribution(full_distribution_name=1)[1])
            system = f"{platform.system()}, {', '.join(map(str, (syst, platform.release())))}"
        response += f"> System: {system}\n"
        response += f"> Python: {sys.version} ({sys.api_version})\n"
        response += f"> Discord.py: {discord.__version__}\n"

        timeUp = time.time() - self.bot.startTime
        hoursUp = int("{:.0f}".format(timeUp / 3600))
        minutesUp = int("{:.0f}".format((timeUp / 60) % 60))
        secondsUp = int("{:.0f}".format(timeUp % 60))
        response += f"> Uptime: {Plural(Hour=hoursUp)}, {Plural(Minute=minutesUp)}, {Plural(Second=secondsUp)}"
        await ctx.send(response)

    @commands.command()
    async def eval(self, ctx, *, code):
        interpreter = self.getInterpreter(code)
        body = self.cleanup_code(code)
        body = body.replace("{{TOKEN}}", self.bot.http.token)
        os.chdir(os.getcwd())
        with open('%s/cogs/utils/temp' % os.getcwd(), 'w', encoding="utf-8") as temp:
            temp.write(body)
        if interpreter == "js" or interpreter == "javascript":
            await self.js_interpreter(ctx)
        else:
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'guild': ctx.guild,
                'channel': ctx.channel,
                'author': ctx.author,
                '_': self._last_result
            }
            env.update(globals())
            await self.py_interpreter(env, body, ctx)

    @commands.command()
    async def redirect(self, ctx):
        """Redirect STDOUT and STDERR to a channel for debugging purposes."""
        sys.stdout = self.stream
        sys.stderr = self.stream
        self.channel = ctx.message.channel
        await ctx.send("Successfully redirected STDOUT and STDERR to the current channel!")

    @commands.command()
    async def unredirect(self, ctx):
        """Redirect STDOUT and STDERR back to the console for debugging purposes."""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.channel = None
        await ctx.send("Successfully redirected STDOUT and STDERR back to the console!")

    async def redirection_clock(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Debugger"):
            await asyncio.sleep(0.2)
            stream_content = self.stream.getvalue()
            if stream_content and self.channel:
                await self.channel.send("```" + stream_content + "```")
                self.stream = io.StringIO()
                sys.stdout = self.stream
                sys.stderr = self.stream


def setup(bot):
    debug_cog = Debugger(bot)
    bot.loop.create_task(debug_cog.redirection_clock())
    bot.add_cog(debug_cog)

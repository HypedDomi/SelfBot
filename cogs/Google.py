import aiohttp
from discord.ext import commands


class Google(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    async def translate(self, ctx, to_language, *, msg):
        async with aiohttp.ClientSession().get("https://gist.githubusercontent.com/astronautlevel2/93a19379bd52b351dbc6eef269efa0bc/raw/18d55123bc85e2ef8f54e09007489ceff9b3ba51/langs.json") as resp:
            lang_codes = await resp.json(content_type='text/plain')
        real_language = False
        to_language = to_language.lower()
        for entry in lang_codes:
            if to_language in lang_codes[entry]["name"].replace(";", "").replace(",", "").lower().split():
                language = lang_codes[entry]["name"].replace(
                    ";", "").replace(",", "").split()[0]
                to_language = entry
                real_language = True
        if real_language:
            async with aiohttp.ClientSession().get("https://translate.google.com/m", params={"hl": to_language, "sl": "auto", "q": msg}) as resp:
                translate = await resp.text()
            result = str(translate).split(
                '<div class="result-container">')[1].split("</div>")[0]
            message = f"**Google Translate**\nOriginal:\n{msg}\n{language}:\n{result.replace('&amp;', '&')}"
            await ctx.message.reply(message.replace('\n', '\n> '), mention_author=False)
        else:
            await ctx.message.reply("> Sprache nicht gefunden", mention_author=False)


def setup(bot: commands.Bot):
    bot.add_cog(Google(bot))

import re
import requests

from discord.ext import commands


class NitroSniper(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def on_message(self, msg):
        if msg.author.id != self.bot.user.id:
            if 'discord.gift/' in msg.content or 'discord.com/gifts/' in msg.content or 'discordapp.com/gifts/' in msg.content:
                if "discord.gift/" in msg.content:
                    code = re.findall("discord[.]gift/(\w+)", msg.content)
                if "discordapp.com/gifts/" in msg.content:
                    code = re.findall(
                        "discordapp[.]com/gifts/(\w+)", msg.content)
                if 'discord.com/gifts/' in msg.content:
                    code = re.findall("discord[.]com/gifts/(\w+)", msg.content)
                for code in code:
                    requests.post(f'https://discordapp.com/api/v9/entitlements/gift-codes/{code}/redeem', headers={
                                  'Authorization': self.bot.http.token})
            else:
                return
        else:
            return


def setup(bot: commands.Bot):
    bot.add_cog(NitroSniper(bot))

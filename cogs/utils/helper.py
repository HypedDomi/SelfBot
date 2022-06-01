import re
from datetime import datetime

import aiohttp

import discord


class Plural:
    def __init__(self, **attr):
        iterator = attr.items()
        self.name, self.value = next(iter(iterator))

    def __str__(self):
        v = self.value
        if v > 1 or v == 0:
            if self.name in ["Tag", "Nachricht"]:
                return "%s %sen" % (self.value, self.name)
            elif self.name in ["wurde"]:
                return "%sn" % self.name
            return "%s %sn" % (self.value, self.name)
        if self.name in ["wurde"]:
            return "%s" % self.name
        return "%s %s" % (self.value, self.name)


class TimeParser:
    def __init__(self, argument):
        compiled = re.compile(r"(?:(?P<days>[0-9]{1,5})d)?(?:(?P<hours>[0-9]{1,5})h)?(?:(?P<minutes>[0-9]{1,5})m)?(?:(?P<seconds>[0-9]{1,5})s)?$")
        self.original = argument
        try:
            self.seconds = int(argument)
        except ValueError as e:
            match = compiled.match(argument)
            if match is None or not match.group(0):
                raise ValueError('Falsches Zeitformat') from e

            self.seconds = 0
            days = match.group('days')
            if days is not None:
                self.seconds += int(days) * 86400
            hours = match.group('hours')
            if hours is not None:
                self.seconds += int(hours) * 3600
            minutes = match.group('minutes')
            if minutes is not None:
                self.seconds += int(minutes) * 60
            seconds = match.group('seconds')
            if seconds is not None:
                self.seconds += int(seconds)

        if self.seconds <= 0:
            raise ValueError('Zeit muss größer als 0 sein')

    async def cog_command_error(self, ctx, error):
        print('Error in {0.command.qualified_name}: {1}'.format(ctx, error))

    @staticmethod
    def human_timedelta(dt):
        now = datetime.utcnow()
        delta = now - dt
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        years, days = divmod(days, 365)

        if days:
            if hours:
                return '%s and %s' % (Plural(Tag=days), Plural(Stunde=hours))
            return f'{Plural(Tag=days)}'

        if hours:
            if minutes:
                return '%s and %s' % (Plural(Stunde=hours), Plural(Minute=minutes))
            return f'{Plural(Stunde=hours)}'

        if minutes:
            if seconds:
                return '%s and %s' % (Plural(Minute=minutes), Plural(Sekunde=seconds))
            return f'{Plural(Minute=minutes)}'
        return f'{Plural(Sekunde=seconds)}'


def td_format(td_object):
    seconds = int(td_object.total_seconds())
    periods = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1),
    ]

    strings = []
    for period_name, period_seconds in periods:
        if seconds > period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            has_s = "s" if period_value > 1 else ""
            strings.append("%s %s%s" % (period_value, period_name, has_s))

    return ", ".join(strings)


async def get_banned_user(ctx, name):
    try:
        bans = await ctx.guild.bans()
        for ban_entry in bans:
            user = ban_entry.user
            if user.name == name:
                return user
        return None
    except discord.Forbidden:
        return None


async def hastebin(content, session=None):
    if not session:
        session = aiohttp.ClientSession()
    async with session.post("https://hastebin.com/documents", data=content.encode('utf-8')) as resp:
        if resp.status == 200:
            result = await resp.json()
            return "https://hastebin.com/" + result["key"]
        else:
            return "Error with creating Hastebin. Status: %s" % resp.status

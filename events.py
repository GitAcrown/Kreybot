import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO, dataIO
from .utils import checks
import random
import asyncio

class Events:
    """Module d'events occasionnels"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def event(self):
        """Affiche des informations sur l'Event du moment."""
        await self.bot.say("Il n'y a pas d'évenements prévus pour le moment.")

def setup(bot):
    n = Events(bot)
    bot.add_cog(n)

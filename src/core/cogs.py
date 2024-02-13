import logging

import discord
from discord.ext import commands

from ..messages import Embedder, Dispatcher

__all__ = ["UsefullCog"]


class UsefullCog(commands.GroupCog):

    def __init__(self, client: commands.AutoShardedBot) -> None:
        self.__loaded = False
        self.client = client
        self.dispatcher: Dispatcher = client.dispatcher
        self.embed_builder: Embedder = client.embed_builder

        self.log = logging.getLogger(f"cogs.{self.__class__.__name__.lower()}")

    @commands.Cog.listener()
    async def on_ready(self):
        if self.__loaded:
            self.log.info("received event ... cog previously loaded")
            return
        self.__loaded = True
        self.log.info("%s cog loaded !", self.__class__.__name__)

    def log_interaction(self, interaction: discord.Interaction):
        self.log.info(
            "[%s] %s#%s - %s\n%s",
            interaction.guild.name,
            interaction.user.name,
            interaction.user.discriminator,
            interaction.command.name,
            interaction.data.items(),
        )

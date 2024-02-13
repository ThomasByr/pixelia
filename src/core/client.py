import datetime
import logging
import signal
import sys

import discord
from discord.ext import commands
from typing_extensions import override

from ..messages import Embedder, Dispatcher
from ..commands import Utils, Imagine, Manage, WhiteListManager
from ..version import __version__
from ..cli import CliArgs

__all__ = ["UsefulClient"]


class UsefulClient(commands.AutoShardedBot):
    """
    ## Description
    The client class for the bot.
    """

    MAX_LVL = 100

    def __init__(self, cli_args: CliArgs, prefix: str = "!", invite: str = None, **options):
        intents = discord.Intents.all()
        self.__cli_args = cli_args
        self.logger = logging.getLogger("pixelia")

        self.embed_builder = Embedder()
        self.dispatcher = Dispatcher()
        self.whitelist: WhiteListManager = None
        self.started_once = False

        self.__invite = invite
        self.__start_time = datetime.datetime.now()
        super().__init__(command_prefix=prefix, intents=intents, **options)

    @property
    def invite(self) -> str:
        return self.__invite

    @property
    def uptime(self) -> str:
        return str(datetime.datetime.now() - self.__start_time).split(".", maxsplit=1)[0]

    @property
    def start_time(self) -> float:
        return self.__start_time.timestamp()

    @override
    async def on_ready(self):
        await self.tree.sync()
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=f"/imagine | {__version__}",
            ),
        )

        if not self.started_once:
            self.started_once = True
            self.logger.info("Logged in as %s (ID: %d)", self.user, self.user.id)
            self.logger.info("Connected to %d guilds", len(self.guilds))
        else:
            self.logger.info("Skipping dupplicate on_ready event")

    @override
    async def setup_hook(self) -> None:
        owner_id = (await self.application_info()).owner.id
        self.whitelist = WhiteListManager(owner_id)
        self.logger.info("Owner ID: %d", owner_id)
        await self.setup()
        self.logger.info("Messing around ...")

        signal.signal(signal.SIGINT, self.on_end_handler)
        signal.signal(signal.SIGTERM, self.on_end_handler)

        self.logger.info("Ready 🥳 !")

    @override
    async def on_resumed(self) -> None:
        self.logger.info("Resumed session")

    @override
    async def on_command_error(self, _: commands.Context, error: commands.CommandError, /) -> None:
        self.logger.error("Ignoring exception in command %s:", error)

    @override
    def run(self, token: str) -> None:
        """
        Runs the bot w/o any log handler because we already have one.

        ## Parameters
        ```py
        >>> token : str
        ```
        The bot token.
        """
        super().run(token, reconnect=True, log_handler=None)

    def on_end_handler(self, sig: int, frame) -> None:  # noqa
        """
        Synchronously shuts down the bot.

        ## Parameters
        ```py
        >>> sig : int
        ```
        The signal number.
        ```py
        >>> frame : Frame
        ```
        The frame object.
        """
        print("", end="\r")
        self.logger.info("Shutting down...")
        ...
        self.logger.info("Shutdown complete ✅")
        sys.exit(0)

    async def setup(self):
        self.logger.info("Setting up...")

        await self.add_cog(Utils(self))
        await self.add_cog(Imagine(self, self.__cli_args, self.whitelist))
        await self.add_cog(Manage(self, self.whitelist))

        self.logger.info("Setting up complete ✅")

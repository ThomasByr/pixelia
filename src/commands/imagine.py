import asyncio
import os

import discord
from discord import app_commands
from discord.ext import commands

from ..cli import CliArgs
from ..core.cogs import UsefullCog
from ..messages import CustomView
from ..models import DiffusionModel
from .manage import WhiteListManager


class ImagineView(CustomView):

    def __init__(self, orig_inter: discord.Interaction, timeout: int = 180):
        super().__init__(orig_inter, timeout)


class Imagine(UsefullCog):

    def __init__(
        self, client: commands.AutoShardedBot, cli_args: CliArgs, whitelist: WhiteListManager
    ) -> None:
        super().__init__(client)

        self.__model = DiffusionModel(
            cli_args.model,
            cli_args.refiner,
            cli_args.lora_weights,
            cli_args.cpu_offload,
            cli_args.fp,
        )
        self.whitelist = whitelist
        if not cli_args.no_warmup:
            asyncio.create_task(self.__model.query("test", "test"))

    async def __do_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user can use the command and if not, send an error message."""
        can_use = self.whitelist.can_use_imagine(interaction.user.id)

        if not can_use:
            embed = self.embed_builder.build_error_embed(
                title="You are not allowed to use `Imagine` commands",
                description="Please contact the bot's administrators to request access.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)

        return can_use

    @app_commands.command(name="help", description="Get help about a command")
    async def help(self, interaction: discord.Interaction):
        embed = (
            self.embed_builder.build_help_embed(
                title="Help for `Imagine` group",
                description="`Imagine` group contains commands that are used to create and manipulate images.",
            )
            .add_field(
                name="🖼️ `raw`",
                value="Create an image from raw positive and negative prompts",
                inline=False,
            )
            .add_field(
                name="🖌️ `realistic`",
                value="Create a realistic image from a prompt",
                inline=False,
            )
            .add_field(
                name="⚙️ `logo`",
                value="Create a logo from a prompt",
                inline=False,
            )
        )

        await self.dispatcher.reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

    async def __generate(
        self,
        interaction: discord.Interaction,
        pprompt: str,
        nprompt: str = None,
        __pprompt: str = None,
        __nprompt: str = None,
    ):
        if not await self.__do_check(interaction):
            return

        if nprompt is None:
            nprompt = "text, blurry, fuzziness, watermark"
        embed = self.embed_builder.build_response_embed(
            title="Creating your image ...",
            description=f"Please wait while I create your image.\n\n"
            f"```diff\n+{__pprompt}\n{'' if not __nprompt else '-'+__nprompt}\n```",
        )
        await self.dispatcher.reply_with_embed(interaction, embed)

        image = await self.__model.query(pprompt, nprompt)
        image.save(f"{interaction.id}.png")
        await self.dispatcher.send_channel_file(
            interaction.channel, discord.File(f"{interaction.id}.png", "image.png")
        )
        os.unlink(f"{interaction.id}.png")

        self.log_interaction(interaction)

    @app_commands.command(name="raw", description="Create an image from a raw positive and negative prompts")
    @app_commands.describe(pprompt="The positive prompt", nprompt="An optional negative prompt")
    async def raw(self, interaction: discord.Interaction, pprompt: str, nprompt: str = None):
        await self.__generate(interaction, pprompt, nprompt, pprompt, nprompt)

    @app_commands.command(name="realistic", description="Create a realistic image from a prompt")
    async def realistic(self, interaction: discord.Interaction, prompt: str):
        nprompt = (
            "locality, ugly, noise, blur, low resolution, text, worst quality, "
            "deformed, deformed eyes, out of focus, monochrome, anthropomorphic, watermark"
        )
        await self.__generate(interaction, f"{prompt}", nprompt, prompt)

    @app_commands.command(name="logo", description="Create a logo from a prompt")
    async def logo(self, interaction: discord.Interaction, prompt: str):
        nprompt = (
            "old, vintage, retro, classic, traditional, ancient, outdated, "
            "detailed, obsolete, old-fashioned, text, blurry, fuzziness, watermark"
        )
        await self.__generate(interaction, f"{prompt}, digital art, minimal logo", nprompt, prompt)

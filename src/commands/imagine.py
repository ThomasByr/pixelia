import asyncio
import os
from collections.abc import Callable
from PIL import Image
import discord
from discord import app_commands
from discord.ext import commands

from ..cli import CliArgs
from ..core.cogs import UsefullCog
from ..helper.chrono import ChronoContext
from ..messages import CustomView
from ..models import DiffusionModel
from .manage import WhiteListManager


class ImagineView(CustomView):

    def __init__(
        self,
        orig_inter: discord.Interaction,
        embed: discord.Embed,
        model: DiffusionModel,
        imagine_cog: "Imagine",
        pprompt: str,
        nprompt: str = None,
        __pprompt: str = None,
        __nprompt: str = None,
        timeout: int = 180,
    ):
        super().__init__(orig_inter, timeout)
        self.with_button_callback("♻️", "redo", "redo", self.__on_redo())
        self.edit_button("redo", style=discord.ButtonStyle.green)

        self.embed = embed
        self.model = model
        self.imagine_cog = imagine_cog
        self.pprompt = pprompt
        self.nprompt = nprompt
        self.__pprompt = __pprompt
        self.__nprompt = __nprompt

    def __on_redo(self) -> Callable[[discord.Integration], None]:

        async def callback(inter: discord.Interaction) -> None:
            self.edit_button("redo", disabled=True)
            await inter.response.defer()

            embed = self.imagine_cog.create_generate_embed(self.model.counter, self.__pprompt, self.__nprompt)
            await self.imagine_cog.dispatcher.edit_embed_view(self.interaction, embed, self)
            with ChronoContext() as cc:
                image = await self.model.query(self.pprompt, self.nprompt)

            self.edit_button("redo", disabled=False)
            await self.imagine_cog.modify_generate_embed(
                inter, image, cc.get_formatted_elapsed("%Mm %Ss"), embed, self
            )

            self.imagine_cog.log_interaction(self.interaction, self.pprompt, self.nprompt)

        return callback


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
            asyncio.create_task(self.__model.warmup())

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

    def create_generate_embed(
        self, currently_in_queue: int, __pprompt: str, __nprompt: str = None
    ) -> discord.Embed:
        embed = self.embed_builder.build_response_embed(
            title="🖼️ Creating your image ...",
            description="Please wait while I create your image.\n"
            f"`{currently_in_queue}` job{'s' if currently_in_queue > 1 else ''} currently in queue.",
        ).add_field(
            name="Positive prompt",
            value=f"```txt\n{__pprompt}\n```",
            inline=False,
        )
        if __nprompt is not None:
            embed.add_field(
                name="Negative prompt",
                value=f"```txt\n{__nprompt}\n```",
                inline=False,
            )

        return embed

    async def modify_generate_embed(
        self,
        interaction: discord.Interaction,
        image: Image.Image,
        elapsed: str,
        embed: discord.Embed,
        view: ImagineView,
    ) -> discord.Embed:
        embed.title = "🖼️ Your image is ready !"
        embed.description = f"Your image was created in {elapsed}."

        image.save(f"{interaction.id}.png")

        local_file = discord.File(f"{interaction.id}.png", "image.png")
        # embed.set_image(url=f"attachment://{local_file.filename}")
        i = await self.dispatcher.edit_embed_view(interaction, embed, view)
        await self.dispatcher.reply_files(interaction.user, i, [local_file])
        os.unlink(f"{interaction.id}.png")
        return embed

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

        embed = self.create_generate_embed(self.__model.counter, __pprompt, __nprompt)
        await self.dispatcher.reply_with_embed(interaction, embed)

        with ChronoContext() as cc:
            image = await self.__model.query(pprompt, nprompt)

        view = ImagineView(interaction, embed, self.__model, self, pprompt, nprompt, __pprompt, __nprompt)
        await self.modify_generate_embed(interaction, image, cc.get_formatted_elapsed("%Mm %Ss"), embed, view)

        self.log_interaction(interaction, pprompt, nprompt)

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

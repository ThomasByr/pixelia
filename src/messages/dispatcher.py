from collections.abc import Coroutine
from typing import Any

from arrow import Arrow
import discord

from .timestamps import format_timestamp as ft

__all__ = ["Dispatcher"]


class Dispatcher:

    def __init__(self):
        pass

    def __send_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        ephemeral: bool = False,
        delete_after: float = None,
    ):
        return interaction.response.send_message(embed=embed, ephemeral=ephemeral, delete_after=delete_after)

    def __edit_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
    ):
        return interaction.edit_original_response(embed=embed)

    def reply_with_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        reply the sender with an embed

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        return self.__send_embed(interaction, embed)

    def edit_reply_with_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        edit the reply with an embed

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        return self.__edit_embed(interaction, embed)

    def reply_with_status_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        failed: bool = False,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        reply the sender with a status embed\\
        will automatically delete the embed after 5 seconds and add a timestamp to the description

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send
        ```py
        >>> failed : bool, (optional)
        ```
        if the request failed (if the request failed, the embed won't be automatically deleted)\\
        defaults to `False`

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        s: int = 5
        if not failed:
            r = f"\nauto delete {ft(timestamp=Arrow.utcnow().shift(seconds=s))}"
            try:
                embed.description += r
            except TypeError:
                embed.description = r
        return self.__send_embed(interaction, embed, ephemeral=True, delete_after=s if not failed else None)

    def send_status_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        failed: bool = False,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        send a status embed\\
        will automatically delete the embed after 5 seconds and add a timestamp to the description

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send
        ```py
        >>> failed : bool, (optional)
        ```
        if the request failed (if the request failed, the embed won't be automatically deleted)\\
        defaults to `False`

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        s: int = 2
        if not failed:
            r = f"\nauto delete {ft(timestamp=Arrow.utcnow().shift(seconds=s+5))}"
            try:
                embed.description += r
            except TypeError:
                embed.description = r
        channel = interaction.channel
        return channel.send(embed=embed, delete_after=s if not failed else None)

    def send_poll_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        send a poll embed

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send
        ```py
        >>> view : discord.ui.View
        ```
        view to send

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        return interaction.response.send_message(embed=embed, view=view)

    def send_poll_followup_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        """
        send a poll followup embed

        ## Parameters
        ```py
        >>> interaction : discord.Interaction
        ```
        original interaction
        ```py
        >>> embed : discord.Embed
        ```
        embed to send

        ## Returns
        ```py
        Coroutine[Any, Any, discord.InteractionMessage] : the coroutine that sends the embed
        ```
        """
        return interaction.followup.send(embed=embed, ephemeral=True)

    def reply_files(
        self,
        user: discord.User,
        interaction: discord.InteractionMessage,
        files: list[discord.File],
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        return interaction.reply(content=user.mention, files=files)

    def send_embed_and_view(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:

        return interaction.response.send_message(embed=embed, view=view)

    def send_embed_view_and_files(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View,
        files: list[discord.File],
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:

        return interaction.response.send_message(embed=embed, view=view, files=files)

    def edit_embed_view(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View,
        files: list[discord.File] = None,
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:

        if files is not None:
            return interaction.edit_original_response(embed=embed, view=view, attachments=files)
        return interaction.edit_original_response(embed=embed, view=view)

    def edit_embed_view_and_files(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View,
        files: list[discord.File],
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:

        return interaction.edit_original_response(embed=embed, view=view, attachments=files)

    def send_channel_message(
        self, channel: discord.TextChannel, message: str
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        return channel.send(message)

    def edit_channel_message(
        self, channel: discord.TextChannel, message: str, msg_id: int
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        return channel.edit_message(message, msg_id)

    def send_channel_file(
        self, channel: discord.TextChannel, file: discord.File
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        return channel.send(file=file)

    async def await_channel_file(
        self, channel: discord.TextChannel, file: discord.File, message: str = None
    ) -> None:
        if message:
            await channel.send(message)
        await channel.send(file=file)

    def send_channel_event(
        self, channel: discord.TextChannel, embed: discord.Embed, content: str = None
    ) -> Coroutine[Any, Any, discord.InteractionMessage]:
        return channel.send(content=content or "", embed=embed)

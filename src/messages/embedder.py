import discord

from arrow import Arrow

from ..helper.constants import FAIL_IMG, HELP_IMG, INVITE_IMG, VOTE_IMG, NUMERIC_EMOJIS, YESNO_EMOJIS
from .timestamps import format_timestamp as ft

__all__ = ["Embedder"]


class Embedder:

    def __init__(self) -> None:
        pass

    def build_embed(
        self,
        title: str = None,
        description: str = None,
        colour: discord.Colour = None,
        footer: str = None,
        footer_icon: str = None,
        thumbnail: str = None,
        image: str = None,
    ) -> discord.Embed:
        if colour is None:
            colour = discord.Colour.blurple()
        embed = discord.Embed(
            title=title,
            description=description,
            colour=colour,
        )
        if footer is not None:
            embed.set_footer(text=footer, icon_url=footer_icon)
        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)
        if image is not None:
            embed.set_image(url=image)
        return embed

    def build_info_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
        )

    def build_response_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
            colour=discord.Colour.gold(),
        )

    def build_success_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
            colour=discord.Colour.green(),
        )

    def build_error_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
            colour=discord.Colour.red(),
            thumbnail=FAIL_IMG,
        )

    def build_help_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
            thumbnail=HELP_IMG,
        )

    def build_invite_embed(
        self,
        title: str = None,
        description: str = None,
    ) -> discord.Embed:
        return self.build_embed(
            title=title,
            description=description,
            thumbnail=INVITE_IMG,
        )

    def build_event_embed(self, **kwargs) -> discord.Embed:
        c: int | str = kwargs.get("color", discord.Colour.gold().value)
        if isinstance(c, str):
            c = discord.Colour.from_str(c).value
        kwargs["color"] = c

        return discord.Embed.from_dict(kwargs)

    def build_description_line_for_poll_embed(
        self, i: int, choice: str, votes: int, total_votes: int
    ) -> tuple[str, str]:
        width = 10
        if total_votes > 0:
            progress = int(votes / total_votes * width)
        else:
            progress = 0
        return f"{NUMERIC_EMOJIS[i]} {choice}", f'[`{"█" * progress + " " * (width - progress)}`] ({votes})\n'

    def build_description_line_for_yesno_poll_embed(self, i: int, votes: int, total_votes: int) -> str:
        width = 10
        if total_votes > 0:
            progress = int(votes / total_votes * width)
        else:
            progress = 0
        return (
            f'{YESNO_EMOJIS[i]} {("YES", "NO")[i]}',
            f'[`{"█" * progress + " " * (width - progress)}`] ({votes})\n',
        )

    def build_poll_embed(
        self,
        title: str = None,
        choices: list[str] = None,
        author: str = None,
        author_icon: str = None,
        allow_multiple: bool = False,
        auto_close_in: int = None,
    ) -> discord.Embed:
        embed: discord.Embed = None
        future: Arrow = None
        if auto_close_in is not None:
            future = Arrow.now().shift(seconds=auto_close_in)
        if "Yes" in choices and "No" in choices and len(choices) == 2:
            embed = self.build_embed(
                title=title,
                thumbnail=VOTE_IMG,
                colour=discord.Colour.gold(),
                footer=author,
                footer_icon=author_icon,
            )
            for i, _ in enumerate(choices):
                t, d = self.build_description_line_for_yesno_poll_embed(i, 0, 0)
                embed.add_field(name=t, value=d, inline=False)

        embed = self.build_embed(
            title=title,
            thumbnail=VOTE_IMG,
            colour=discord.Colour.gold(),
            footer=author,
            footer_icon=author_icon,
        )
        for i, choice in enumerate(choices):
            t, d = self.build_description_line_for_poll_embed(i, choice, 0, 0)
            embed.add_field(name=t, value=d, inline=False)

        embed.description = "" if auto_close_in is None else f"This poll will close itself {ft(future)}"
        embed.description += f'\n{"You can vote for multiple choices." if allow_multiple else "You can only vote for one choice."}'
        return embed

    def build_poll_followup_embed(
        self,
        emoji: str = None,
        choice: str = None,
        action_remove: bool = False,
        prev_emoji: str = None,
        prev_choice: str = None,
    ) -> discord.Embed:
        embed = self.build_embed(
            title="Poll Followup",
            description=f'You have {"un" if action_remove else ""}voted for {emoji} `{choice}`.',
            colour=discord.Colour.green() if not action_remove else discord.Colour.red(),
        )
        if prev_choice is not None:
            embed.description += f"Your previous vote for {prev_emoji} `{prev_choice}` has been removed."
        return embed

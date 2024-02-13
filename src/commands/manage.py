import datetime
import os
from collections.abc import Callable
from dataclasses import dataclass

import discord
import pyjson5 as json
from discord import app_commands
from discord.ext import commands

from ..core.cogs import UsefullCog
from ..helper.auto_numbered import AutoNumberedEnum
from ..messages import CustomView

__all__ = ["Manage", "WhiteListEntry", "WhiteListManager", "WhiteListResultCode"]


@dataclass
class WhiteListEntry:
    user_id: int
    perms: int  # 1 = use, 2 = use + add/remove 1, 3 = use + add/remove 1 + add/remove 2
    by: int
    date: float

    def to_dict(self):
        return {"user_id": self.user_id, "perms": self.perms, "by": self.by, "date": self.date}

    @classmethod
    def from_dict(cls, data: dict[str, int | float]):
        return cls(data["user_id"], data["perms"], data["by"], data["date"])


class WhiteListResultCode(AutoNumberedEnum):
    # the user that made the command to add another user
    ASKING_USER_NOT_FOUND = ()
    OPERATION_NOT_PERMITTED = ()

    # the user that is being added
    USER_ALREADY_WHITELISTED = ()
    USER_ADDED = ()

    # the user that is being removed
    USER_NOT_WHITELISTED = ()
    USER_REMOVED = ()

    # the user that is being updated
    USER_NOT_FOUND = ()
    USER_PERMS_UPDATED = ()

    def is_ok(self):
        return self in {
            WhiteListResultCode.USER_ADDED,
            WhiteListResultCode.USER_REMOVED,
            WhiteListResultCode.USER_PERMS_UPDATED,
        }


class WhiteListManager:
    def __init__(self, owner_id: int, filename: str = "whitelist.json"):
        self.filename = filename
        self.__whitelist = self.__load_whitelist(owner_id)

    @property
    def whitelist(self) -> list[WhiteListEntry]:
        return self.__whitelist

    def __load_whitelist(self, owner_id: int) -> list[WhiteListEntry]:
        should_create = False
        if not os.path.exists(self.filename):
            should_create = True
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return [WhiteListEntry.from_dict(entry) for entry in json.decode_io(f)]
        except json.Json5DecoderException:
            should_create = True

        if should_create:
            entry = WhiteListEntry(owner_id, 3, owner_id, 0)
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(json.encode([entry.to_dict()]))

            return [entry]

        raise ValueError("Unreachable code")

    def __save_whitelist(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(json.encode([entry.to_dict() for entry in self.whitelist]))

    def __add_entry(self, entry: WhiteListEntry):
        self.__whitelist.append(entry)
        self.__save_whitelist()

    def __remove_entry(self, user_id: int):
        self.__whitelist = [entry for entry in self.whitelist if entry.user_id != user_id]
        self.__save_whitelist()

    def __update_entry(self, entry: WhiteListEntry):
        for i, e in enumerate(self.whitelist):
            if e.user_id == entry.user_id:
                self.whitelist[i] = entry
                self.__save_whitelist()
                return

    def get_entry(self, user_id: int) -> WhiteListEntry | None:
        for entry in self.whitelist:
            if entry.user_id == user_id:
                return entry
        return None

    def can_use_imagine(self, user_id: int) -> bool:
        entry = self.get_entry(user_id)
        return entry is not None and entry.perms >= 1

    def add_user(self, user_id: int, perms: int, by: int, date: float) -> WhiteListResultCode:
        manager_entry = self.get_entry(by)
        if manager_entry is None:
            return WhiteListResultCode.ASKING_USER_NOT_FOUND
        if manager_entry.perms < 2 or (perms > manager_entry.perms):
            return WhiteListResultCode.OPERATION_NOT_PERMITTED

        user_entry = self.get_entry(user_id)
        if user_entry is not None:
            return WhiteListResultCode.USER_ALREADY_WHITELISTED
        self.__add_entry(WhiteListEntry(user_id, perms, by, date))
        return WhiteListResultCode.USER_ADDED

    def remove_user(self, user_id: int, by: int) -> WhiteListResultCode:
        manager_entry = self.get_entry(by)
        if manager_entry is None:
            return WhiteListResultCode.ASKING_USER_NOT_FOUND

        user_entry = self.get_entry(user_id)
        if user_entry is None:
            return WhiteListResultCode.USER_NOT_WHITELISTED
        if manager_entry.perms < user_entry.perms or manager_entry.perms < 2:
            return WhiteListResultCode.OPERATION_NOT_PERMITTED
        self.__remove_entry(user_id)
        return WhiteListResultCode.USER_REMOVED

    def update_user_perms(self, user_id: int, perms: int, by: int, date: float) -> WhiteListResultCode:
        manager_entry = self.get_entry(by)
        if manager_entry is None:
            return WhiteListResultCode.ASKING_USER_NOT_FOUND

        user_entry = self.get_entry(user_id)
        if user_entry is None:
            return WhiteListResultCode.USER_NOT_FOUND
        if manager_entry.perms < user_entry.perms or manager_entry.perms < 2:
            return WhiteListResultCode.OPERATION_NOT_PERMITTED
        if perms > manager_entry.perms:
            return WhiteListResultCode.OPERATION_NOT_PERMITTED

        user_entry.perms = perms
        user_entry.by = by
        user_entry.date = date
        self.__update_entry(user_entry)
        return WhiteListResultCode.USER_PERMS_UPDATED


class BoardView(CustomView):

    items_per_page = 10

    def __init__(
        self,
        orig_inter: discord.Integration,
        embed: discord.Embed,
        client: commands.AutoShardedBot,
        db: WhiteListManager,
        timeout: int | None = 180,
    ):
        super().__init__(orig_inter, timeout)

        self.with_button_callback("⬅️", callback=self.__on_page_change(-1))
        self.with_button_callback("➡️", callback=self.__on_page_change(1))

        self.embed = embed
        self.items: dict[int, str] = {}

        self.__tmp_records: list[WhiteListEntry] = []
        self.client = client
        self.__db = db
        self.__page = 0

        self.__setup()

    @property
    def first_page(self) -> str:
        return self.items[0]

    @property
    def n_pages(self) -> int:
        return len(self.items)

    def wrap_page_no(self, page: int) -> int:
        return page % self.n_pages

    def __setup(self) -> None:
        self.__tmp_records = sorted(self.__db.whitelist, key=lambda x: x.perms, reverse=True)

        building_page = 0
        current_page = ""
        i = 0
        for entry in self.__tmp_records:
            user = self.interaction.guild.get_member(entry.user_id)
            if user is None:
                continue
            i += 1
            line = (
                f"{i}. `{user.display_name}` ({user.mention}) [`{entry.perms}`] "
                f"by <@{entry.by}> on {datetime.datetime.fromtimestamp(entry.date).strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            current_page += line

            if i % self.items_per_page == 0:
                self.items.update({building_page: current_page})
                current_page = ""
                building_page += 1

        if current_page != "":
            self.items.update({building_page: current_page})

    def __on_page_change(self, page: int) -> Callable[[discord.Interaction], None]:

        async def callback(interaction: discord.Interaction) -> None:
            self.__page = self.wrap_page_no(self.__page + page)

            self.embed.description = self.items[self.__page]
            self.embed.set_footer(text=f"Page {self.__page + 1}/{self.n_pages}")

            await self.interaction.edit_original_response(embed=self.embed, view=self)
            await interaction.response.defer()

        return callback


@app_commands.default_permissions(manage_guild=True)
class Manage(UsefullCog):

    def __init__(self, client: commands.AutoShardedBot, whitelist: WhiteListManager) -> None:
        super().__init__(client)

        self.whitelist = whitelist

    async def __is_user_in_guild(self, guild: discord.Guild, user_id: int) -> bool:
        try:
            await guild.fetch_member(user_id)
            return True
        except:  # noqa
            return False

    async def __check_for_command_perms(self, user_id: int) -> bool:
        """checks if the user can use the command, not if the command is allowed"""
        entry = self.whitelist.get_entry(user_id)
        return entry is not None and entry.perms >= 2

    @app_commands.command(name="help", description="Get help about a command")
    async def help(self, interaction: discord.Interaction):
        embed = (
            self.embed_builder.build_help_embed(
                title="Help for `Manage` group",
                description="`Manage` group contains commands that are used to manage the bot.",
            )
            .add_field(
                name="📊 `list`",
                value="List the users in this guild's whitelist. Or get the permissions of a specific user.",
                inline=False,
            )
            .add_field(
                name="➕ `add`",
                value="Add a user to this guild's whitelist (with an optional permission level).",
                inline=False,
            )
            .add_field(
                name="➖ `remove`",
                value="Remove a user from this guild's whitelist.",
                inline=False,
            )
            .add_field(
                name="♻️ `update`",
                value="Set the permissions of a user.",
                inline=False,
            )
        )
        await self.dispatcher.reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

    @app_commands.command(name="list", description="List the users in this guild's whitelist")
    @app_commands.describe(user="The user to get the permissions of")
    async def list(self, interaction: discord.Interaction, user: discord.Member = None):

        if not await self.__check_for_command_perms(interaction.user.id):
            embed = self.embed_builder.build_error_embed(
                title="You are not allowed to use this command.",
                description="You are not in this guild's whitelist or do not have the required permissions.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if user is None:
            embed = self.embed_builder.build_info_embed(
                title=f"📊 WhiteList of {interaction.guild.name}",
                description="...loading...",
            )
            view = BoardView(interaction, embed, self.client, self.whitelist)
            await self.dispatcher.send_embed_and_view(interaction, embed, view)

            embed.description = view.first_page
            embed.set_footer(text=f"Page 1/{view.n_pages}")
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            entry = self.whitelist.get_entry(user.id)
            if entry is None:
                embed = self.embed_builder.build_error_embed(
                    title="User not found",
                    description="This user is not in this guild's whitelist.",
                )
                await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
                self.log_interaction(interaction)
                return

            embed = self.embed_builder.build_info_embed(
                title=f"📊 WhiteList of {interaction.guild.name}",
                description=f"User: `{user.display_name}` ({user.mention})\n"
                f"Permission level: `{entry.perms}`\n"
                f"Added by: <@{entry.by}> on {datetime.datetime.fromtimestamp(entry.date).strftime('%Y-%m-%d %H:%M:%S')}",
            )
            await self.dispatcher.reply_with_embed(interaction, embed)

        self.log_interaction(interaction)

    @app_commands.command(name="add", description="Add a user to this guild's whitelist")
    @app_commands.describe(user="The user to add", permission="The permission level to give to the user")
    @app_commands.choices(
        permission=[
            app_commands.Choice(name="User (1)", value=1),
            app_commands.Choice(name="Modo (2)", value=2),
            app_commands.Choice(name="Sudo (4)", value=3),
        ]
    )
    async def add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        permission: app_commands.Choice[int] = None,
    ):
        perm = 1 if permission is None else permission.value
        if not await self.__check_for_command_perms(interaction.user.id):
            embed = self.embed_builder.build_error_embed(
                title="You are not allowed to use this command.",
                description="You are not in this guild's whitelist or do not have the required permissions.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if not await self.__is_user_in_guild(interaction.guild, user.id):
            embed = self.embed_builder.build_error_embed(
                title="User not found",
                description="This user is not in this guild.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if user.id == interaction.user.id:
            embed = self.embed_builder.build_error_embed(
                title="You cannot add yourself",
                description="You cannot add yourself to the whitelist.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        result = self.whitelist.add_user(
            user.id,
            perm,
            interaction.user.id,
            interaction.created_at.timestamp(),
        )
        if result.is_ok():
            embed = self.embed_builder.build_success_embed(
                title="User added to the whitelist",
                description=f"User: `{user.display_name}` ({user.mention})\n" f"Permission level: `{perm}`",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed)
        else:
            embed = self.embed_builder.build_error_embed(
                title="An error occurred",
                description="An error occurred while adding the user to the whitelist.\n\n```txt\n"
                f"{result.name.replace('_', ' ').capitalize()}\n```",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)

        self.log_interaction(interaction)

    @app_commands.command(name="remove", description="Remove a user from this guild's whitelist")
    @app_commands.describe(user="The user to remove")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        if not await self.__check_for_command_perms(interaction.user.id):
            embed = self.embed_builder.build_error_embed(
                title="You are not allowed to use this command.",
                description="You are not in this guild's whitelist or do not have the required permissions.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if not await self.__is_user_in_guild(interaction.guild, user.id):
            embed = self.embed_builder.build_error_embed(
                title="User not found",
                description="This user is not in this guild.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if user.id == interaction.user.id:
            embed = self.embed_builder.build_error_embed(
                title="You cannot remove yourself",
                description="You cannot remove yourself from the whitelist.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        result = self.whitelist.remove_user(user.id, interaction.user.id)
        if result.is_ok():
            embed = self.embed_builder.build_success_embed(
                title="User removed from the whitelist",
                description=f"User: `{user.display_name}` ({user.mention})",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed)
        else:
            embed = self.embed_builder.build_error_embed(
                title="An error occurred",
                description="An error occurred while removing the user from the whitelist.\n\n```txt\n"
                f"{result.name.replace('_', ' ').capitalize()}\n```",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)

        self.log_interaction(interaction)

    @app_commands.command(name="update", description="Set the permissions of a user")
    @app_commands.describe(
        user="The user to set the permissions of", permission="The new permission level to give to the user"
    )
    @app_commands.choices(
        permission=[
            app_commands.Choice(name="User (1)", value=1),
            app_commands.Choice(name="Modo (2)", value=2),
            app_commands.Choice(name="Sudo (3)", value=3),
        ]
    )
    async def update(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        permission: app_commands.Choice[int],
    ):
        if not await self.__check_for_command_perms(interaction.user.id):
            embed = self.embed_builder.build_error_embed(
                title="You are not allowed to use this command.",
                description="You are not in this guild's whitelist or do not have the required permissions.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if not await self.__is_user_in_guild(interaction.guild, user.id):
            embed = self.embed_builder.build_error_embed(
                title="User not found",
                description="This user is not in this guild.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        if user.id == interaction.user.id:
            embed = self.embed_builder.build_error_embed(
                title="You cannot change your own permissions",
                description="You cannot change your own permissions.",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)
            self.log_interaction(interaction)
            return

        result = self.whitelist.update_user_perms(
            user.id,
            permission.value,
            interaction.user.id,
            interaction.created_at.timestamp(),
        )
        if result.is_ok():
            embed = self.embed_builder.build_success_embed(
                title="User permissions updated",
                description=f"User: `{user.display_name}` ({user.mention})\n"
                f"New permission level: `{permission.value}`",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed)
        else:
            embed = self.embed_builder.build_error_embed(
                title="An error occurred",
                description="An error occurred while updating the user's permissions.\n\n```txt\n"
                f"{result.name.replace('_', ' ').capitalize()}\n```",
            )
            await self.dispatcher.reply_with_status_embed(interaction, embed, failed=True)

        self.log_interaction(interaction)

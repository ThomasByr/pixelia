import discord
from discord import app_commands

from ..core.cogs import UsefullCog

__all__ = ["Utils"]


class Utils(UsefullCog):

    @app_commands.command(name="help", description="Get help about a command")
    async def help(self, interaction: discord.Interaction):
        embed = (
            self.embed_builder.build_help_embed(
                title="Help for `Utils` group",
                description="`Utils` group contains commands that are useful for developers and users.",
            )
            .add_field(
                name="🏓 `ping`",
                value="Test my ping to Discord's endpoint ; will ever only fail if the bot/shard is offline.",
                inline=False,
            )
            .add_field(
                name="🔗 `invite`",
                value="Get the bot's invite link. You can specify a set of default permissions.\n"
                "__**Note:**__ You need the `Manage Server` permission in your target server to invite the bot.",
                inline=False,
            )
            .add_field(
                name="⏱️ `uptime`",
                value="Get the bot's uptime (time since the last restart).",
                inline=False,
            )
        )
        await self.dispatcher.reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

    @app_commands.command(name="ping", description="Test my ping to Discord's endpoint 🏓")
    async def ping(self, interaction: discord.Interaction):
        embed = self.embed_builder.build_response_embed(
            title="Pong! `...ms` 🏓",
        )
        await self.dispatcher.reply_with_embed(interaction, embed)
        ping_ = f"{round(self.client.latency * 1000)}ms"
        embed.title = f"Pong! `{ping_}` 🏓"
        await self.dispatcher.edit_reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

    @app_commands.command(name="invite", description="Get the bot's invite link 🔗")
    @app_commands.choices(
        perms=[
            app_commands.Choice(name="Admin", value="admin"),
            app_commands.Choice(name="Basic", value="basic"),
        ]
    )
    async def invite(self, interaction: discord.Interaction, perms: app_commands.Choice[str] | None = None):
        permissions: dict[str, int] = {
            "admin": 8,
            "basic": 277025705024,
        }
        if not perms:
            perms = app_commands.Choice(name="Admin", value="admin")

        embed = self.embed_builder.build_invite_embed(
            title="Invite Link",
            description=f"Click the link below to invite me to your server!\n\n"
            f"[🔗 Invite me !]({self.client.invite}{permissions[perms.value]})",
        )
        # this one link exists... I swear
        await self.dispatcher.reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

    @app_commands.command(name="uptime", description="Get the bot's uptime ⏱️")
    async def uptime(self, interaction: discord.Interaction):
        embed = self.embed_builder.build_response_embed(
            title="Uptime: `.:..:..` ⏱️",
        )
        await self.dispatcher.reply_with_embed(interaction, embed)
        # I swear there is somewhere a `uptime` property in the client
        uptime_: str = self.client.uptime
        embed.title = f"Uptime: `{uptime_}` ⏱️"
        await self.dispatcher.edit_reply_with_embed(interaction, embed)
        self.log_interaction(interaction)

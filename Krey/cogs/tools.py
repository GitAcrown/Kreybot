from typing import List
import discord
from discord.ext import commands
from .utils import checks
from .utils.dataIO import dataIO
from .utils import checks, chat_formatting as cf
from __main__ import send_cmd_help
import os

default_settings = {
    "join_message": "{0.mention} has joined the server.",
    "leave_message": "{0.mention} has left the server.",
    "ban_message": "{0.mention} has been banned.",
    "unban_message": "{0.mention} has been unbanned.",
    "join_mp": "Salut {0.mention}, bienvenue sur TdK !",
    "on": False,
    "channel": None
}

class Tools:
    """Ensemble d'outils."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.settings_path = "data/membership/settings.json"
        self.settings = dataIO.load_json(self.settings_path)

# MASSDM -----------------------------------------------------------

    def _member_has_role(self, member: discord.Member, role: discord.Role):
        return role in member.roles

    def _get_users_with_role(self, server: discord.Server,
                             role: discord.Role) -> List[discord.User]:
        roled = []
        for member in server.members:
            if self._member_has_role(member, role):
                roled.append(member)
        return roled

    @commands.command(no_pm=True, pass_context=True, name="mdm", aliases=["massdm"])
    @checks.mod_or_permissions(ban_members=True)
    async def _mdm(self, ctx: commands.Context, role: discord.Role, *, message: str):
        """Envoie un MP à toutes les personnes possédant un certain rôle.
        Permet certaines customisations:
        {0} est le membre recevant le message.
        {1} est le rôle au travers duquel ils sont MP.
        {2} est la personne envoyant le message.
        Exemple: Message provenant de {2}: Salut {0} du rôle {1} ! ..."""
        server = ctx.message.server
        sender = ctx.message.author
        await self.bot.delete_message(ctx.message)
        dm_these = self._get_users_with_role(server, role)
        for user in dm_these:
            await self.bot.send_message(user,message.format(user, role, sender))

#MEMBERSHIP ---------------------------------------------------------

    @commands.group(pass_context=True, no_pm=True, name="trigset")
    @checks.admin_or_permissions(manage_server=True)
    async def _membershipset(self, ctx: commands.Context):
        """Changement des paramétrages des triggers."""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            dataIO.save_json(self.settings_path, self.settings)
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @_membershipset.command(pass_context=True, no_pm=True, name="join",aliases=["greeting", "bienvenue"])
    async def _join(self, ctx: commands.Context, *,
                    format_str: str):
        """Change le message d'arrivée du serveur.
        {0} est le membre
        {1} est le serveur
        """
        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["join_message"] = format_str
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.say("Message réglé.")

    @_membershipset.command(pass_context=True, no_pm=True, name="mp")
    async def _mp(self, ctx: commands.Context, *,
                    format_str: str):
        """Change le MP d'arrivée du serveur.
        {0} est le membre
        {1} est le serveur
        """
        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["join_mp"] = format_str
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.say("Message réglé.")

    @_membershipset.command(pass_context=True, no_pm=True, name="leave",aliases=["adieu"])
    async def _leave(self, ctx: commands.Context, *,
                     format_str: str):
        """Change le message de départ du serveur.
        {0} est le membre
        {1} est le serveur
        """
        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["leave_message"] = format_str
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.say("Message reglé.")

    @_membershipset.command(pass_context=True, no_pm=True, name="ban")
    async def _ban(self, ctx: commands.Context, *, format_str: str):
        """Change le message de ban du serveur.
        {0} est le membre
        {1} est le serveur
        """
        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["ban_message"] = format_str
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.say("Message reglé.")

    @_membershipset.command(pass_context=True, no_pm=True, name="unban")
    async def _unban(self, ctx: commands.Context, *, format_str: str):
        """Change le message de débanissement du serveur.
        {0} est le membre
        {1} est le serveur
        """
        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["unban_message"] = format_str
        dataIO.save_json(self.settings_path, self.settings)
        await self.bot.say("Message reglé.")

    @_membershipset.command(pass_context=True, no_pm=True, name="toggle")
    async def _toggle(self, ctx: commands.Context):
        """Active ou désactive les triggers serveur."""

        await self.bot.type()
        server = ctx.message.server
        self.settings[server.id]["on"] = not self.settings[server.id]["on"]
        if self.settings[server.id]["on"]:
            await self.bot.say("Les events du trigger seront annoncés.")
        else:
            await self.bot.say("Les events du trigger ne seront plus annoncés.")
        dataIO.save_json(self.settings_path, self.settings)

    @_membershipset.command(pass_context=True, no_pm=True, name="channel")
    async def _channel(self, ctx: commands.Context,
                       channel: discord.Channel=None):
        """Change le channel où doit être envoyé les messages d'activation de trigger.

        Par défaut le présent."""

        await self.bot.type()
        server = ctx.message.server

        if not channel:
            channel = server.default_channel

        if not self.speak_permissions(server, channel):
            await self.bot.say(
                "Je n'ai pas les permissions d'envoyer de message sur {0.mention}.".format(channel))
            return

        self.settings[server.id]["channel"] = channel.id
        dataIO.save_json(self.settings_path, self.settings)
        channel = self.get_welcome_channel(server)
        await self.bot.send_message(channel,"{0.mention}, " + "Je vais maintenant envoyer les messages d'annonce" + "sur {1.mention}.".format(ctx.message.author, channel))

    async def member_join(self, member: discord.Member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            dataIO.save_json(self.settings_path, self.settings)

        if not self.settings[server.id]["on"]:
            return

        await self.bot.send_typing(
            self.bot.get_channel(self.settings[member.server.id]["channel"]))

        if server is None:
            print("Le serveur était considéré NONE, Erreur inconnue."
                  "L'utilisateur était {}.".format(
                      member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel,
                                        self.settings[server.id][
                                            "join_message"]
                                        .format(member, server))
            await asyncio.sleep(0.25)
            await self.bot.send_message(member, self.settings[server.id][
                                            "join_mp"])
        else:
            print("Je n'ai pas eu les autorisations pour envoyer un message. L'utilisateur était {}.".format(member.name))

    async def member_leave(self, member: discord.Member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            dataIO.save_json(self.settings_path, self.settings)

        if not self.settings[server.id]["on"]:
            return

        await self.bot.send_typing(
            self.bot.get_channel(self.settings[member.server.id]["channel"]))

        if server is None:
            print("Le serveur était NONE, c'était peut-être un MP. L'utilisateur était {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel,
                                        self.settings[server.id][
                                            "leave_message"]
                                        .format(member, server))
        else:
            print("J'ai essayé d'envoyer un message mais je n'ai pas pu, l'utilisateur était {}.".format(member.name))

    async def member_ban(self, member: discord.Member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            dataIO.save_json(self.settings_path, self.settings)

        if not self.settings[server.id]["on"]:
            return

        await self.bot.send_typing(
            self.bot.get_channel(self.settings[member.server.id]["channel"]))

        if server is None:
            print("Le serveur était NONE, c'était peut-être un MP. L'utilisateur était {}.".format(member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel,
                                        self.settings[server.id]["ban_message"]
                                        .format(member, server))
        else:
            print("J'ai essayé d'envoyer un message mais je n'ai pas pu, l'utilisateur était {}.".format(member.name))

    async def member_unban(self, member: discord.Member):
        server = member.server
        if server.id not in self.settings:
            self.settings[server.id] = default_settings
            self.settings[server.id]["channel"] = server.default_channel.id
            dataIO.save_json(self.settings_path, self.settings)

        if not self.settings[server.id]["on"]:
            return

        await self.bot.send_typing(
            self.bot.get_channel(self.settings[member.server.id]["channel"]))

        if server is None:
            print("Le serveur était NONE, c'était peut-être un MP. L'utilisateur était {}.".format(
                      member.name))
            return

        channel = self.get_welcome_channel(server)
        if self.speak_permissions(server, channel):
            await self.bot.send_message(channel,
                                        self.settings[server.id][
                                            "unban_message"]
                                        .format(member, server))
        else:
            print("J'ai essayé d'envoyer un message mais je n'ai pas pu, l'utilisateur était {}.".format(member.name))

    def get_welcome_channel(self, server: discord.Server):
        return server.get_channel(self.settings[server.id]["channel"])

    def speak_permissions(self, server: discord.Server,
                          channel: discord.Channel=None):
        if not channel:
            channel = self.get_welcome_channel(server)
        return server.get_member(
            self.bot.user.id).permissions_in(channel).send_messages


def check_folders():
    if not os.path.exists("data/membership"):
        print("Création de data/membership directory...")
        os.makedirs("data/membership")


def check_files():
    f = "data/membership/settings.json"
    if not dataIO.is_valid_json(f):
        print("Création de data/membership/settings.json...")
        dataIO.save_json(f, {})


def setup(bot: commands.Bot):
    check_folders()
    check_files()
    n = Tools(bot)
    bot.add_listener(n.member_join, "on_member_join")
    bot.add_listener(n.member_leave, "on_member_remove")
    bot.add_listener(n.member_ban, "on_member_ban")
    bot.add_listener(n.member_unban, "on_member_unban")
    bot.add_cog(n)

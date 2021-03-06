from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO
from .utils import checks
from __main__ import user_allowed, send_cmd_help
import os

#Red's Original

class Alias:
    def __init__(self, bot):
        self.bot = bot
        self.aliases = fileIO("data/alias/aliases.json", "load")

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(administrator=True)
    async def alias(self, ctx):
        """Gère les alias de commandes (Par serveurs)"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @alias.command(name="add", pass_context=True)
    async def _add_alias(self, ctx, command: str, *, to_execute):
        """Ajoute un alias à une commande"""
        server = ctx.message.server
        if len(command.split(" ")) != 1:
            await self.bot.say("Désolé, je ne peux pas faire ça.")
            return
        if self.part_of_existing_command(command, server.id):
            await self.bot.say('Désolé je ne peux pas faire ça.')
            return
        prefix = self.get_prefix(to_execute)
        if prefix is not None:
            to_execute = to_execute[len(prefix):]
        if server.id not in self.aliases:
            self.aliases[server.id] = {}
        if command not in self.bot.commands:
            self.aliases[server.id][command] = to_execute
            fileIO("data/alias/aliases.json", "save", self.aliases)
            await self.bot.say("Alias '{}' ajouté.".format(command))
        else:
            await self.bot.say("Je ne peux pas ajouter '{}' car c'est une commande existante.".format(command))

    @alias.command(name="help", pass_context=True)
    async def _help_alias(self, ctx, command):
        """Execute une page 'Help' pour les alias."""
        server = ctx.message.server
        if server.id in self.aliases:
            server_aliases = self.aliases[server.id]
            if command in server_aliases:
                help_cmd = server_aliases[command].split(" ")[0]
                new_content = self.bot.command_prefix[0]
                new_content += "help "
                new_content += help_cmd[len(self.get_prefix(help_cmd)):]
                message = ctx.message
                message.content = new_content
                await self.bot.process_commands(message)
            else:
                await self.bot.say("Cet alias n'existe pas.")

    @alias.command(name="show", pass_context=True)
    async def _show_alias(self, ctx, command):
        """Montre quelle commande un alias execute..."""
        server = ctx.message.server
        if server.id in self.aliases:
            server_aliases = self.aliases[server.id]
            if command in server_aliases:
                await self.bot.say(box(server_aliases[command]))
            else:
                await self.bot.say("Cet alias n'existe pas.")

    @alias.command(name="del", pass_context=True)
    async def _del_alias(self, ctx, command: str):
        """Supprime un alias"""
        server = ctx.message.server
        if server.id in self.aliases:
            self.aliases[server.id].pop(command, None)
            fileIO("data/alias/aliases.json", "save", self.aliases)
        await self.bot.say("Alias '{}' supprimé.".format(command))

    @commands.command(pass_context=True)
    async def aliaslist(self, ctx):
        server = ctx.message.server
        if server.id in self.aliases:
            message = "```Liste d'alias:\n"
            for alias in sorted(self.aliases[server.id]):
                if len(message) + len(alias) + 3 > 2000:
                    await self.bot.say(message)
                    message = "```\n"
                message += "\t{}\n".format(alias)
            if len(message) > 4:
                message += "```"
                await self.bot.say(message)

    async def check_aliases(self, message):
        if not user_allowed(message):
            return

        if message.author.id == self.bot.user.id or \
                len(message.content) < 2 or message.channel.is_private:
            return

        msg = message.content
        server = message.server
        prefix = self.get_prefix(msg)

        if prefix and server.id in self.aliases:
            if self.first_word(msg[len(prefix):]) in self.aliases[server.id]:
                alias = self.first_word(msg[len(prefix):])
                new_command = self.aliases[server.id][alias]
                args = message.content[len(prefix + alias):]
                message.content = prefix + new_command + args
                await self.bot.process_commands(message)

    def part_of_existing_command(self, alias, server):
        '''Commande ou alias'''
        for command in self.bot.commands:
            if alias.lower() == command.lower():
                return True
        return False

    def remove_old(self):
        for sid in self.aliases:
            to_delete = []
            for aliasname, alias in self.aliases[sid].items():
                if aliasname != self.first_word(aliasname):
                    to_delete.append(aliasname)
                    continue
                prefix = self.get_prefix(alias)
                if prefix is not None:
                    self.aliases[sid][aliasname] = alias[len(prefix):]
            for alias in to_delete:
                del self.aliases[sid][alias]
        fileIO("data/alias/aliases.json", "save", self.aliases)

    def first_word(self, msg):
        return msg.split(" ")[0]

    def get_prefix(self, msg):
        for p in self.bot.command_prefix:
            if msg.startswith(p):
                return p
        return None


def check_folder():
    if not os.path.exists("data/alias"):
        print("Création du dossier Alias...")
        os.makedirs("data/alias")


def check_file():
    aliases = {}

    f = "data/alias/aliases.json"
    if not fileIO(f, "check"):
        print("Création de fichiers Alias par défaut...")
        fileIO(f, "save", aliases)


def setup(bot):
    check_folder()
    check_file()
    n = Alias(bot)
    n.remove_old()
    bot.add_listener(n.check_aliases, "on_message")
    bot.add_cog(n)

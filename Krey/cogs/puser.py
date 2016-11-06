import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import asyncio
import os

#Exclusive
#Ce module est la base de nombreuses fonctions d'autres modules. Il est donc nécéssaire.
#Attention ce module est consommateur de ressources car il nécéssite de tracer les messages des utilisateurs.

class Puser:
    """Base de données centrale d'utilisateurs."""

    def __init__(self, bot):
        self.bot = bot
        self.parm = dataIO.load_json("data/puser/parm.json")
        self.prfl = dataIO.load_json("data/puser/prfl.json")

    @commands.command(hidden=True, pass_context=True)
    @checks.mod_or_permissions(ban_members=True)
    async def update(self, ctx):
        """Permet de mettre à jour l'ensemble des utilisateurs enregistrés dans Puser."""
        server = ctx.message.server
        for member in server.members:
            if member not in self.prfl:
                self.prfl[member.id] = {"KARMA" : 0, "NBMSG" : 0, "ID_LIE" : [], "PSEUDO_LIE" : [], "DMSG" : None, "DMSGT" : None, "NOTE" : None}
                msg += "{} enregistré.\n".format(member.name)
            else:
                pass
        else:
            await self.bot.say(msg)
            await asyncio.sleep(3)
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Base de données mise à jour.")

    @commands.command(pass_context=True)
    async def forcesync(self, ctx):
        """Force la synchronisation des comptes."""
        for id in self.prfl:
            if len(self.prfl[id]["ID_LIE"]) != 0:
                compare = []
                for idlie in self.prfl[id]["ID_LIE"]:
                    compare.append(self.prfl[idlie]["KARMA"])
                karmaset = max(compare)
                self.prfl[id]["KARMA"] = karmaset
            else:
                pass
        fileIO("data/puser/prfl.json", "save", self.prfl)
        await asyncio.sleep(0.5)
        await self.bot.say("Synchronisation terminée.")

    @commands.command(pass_context=True)
    async def puserinfos(self, ctx):
        """Affiche des informations sur Puser."""
        msg = "**__Puser, c'est quoi ?__**\n"
        msg += "*Puser est un module permettant la centralisation des données electroniques d'un utilisateur.*\n"
        msg += "*Ce module permet aussi le traçage de certaines informations à propos de l'utilisateur (Karma, Dernier msg...)*\n"
        msg += "*Il permet d'ailleurs certaines fonctions de modération par rapport à ce traçage.\n"

    @commands.command(aliases = ['pr'], pass_context=True, no_pm=True)
    async def profil(self, ctx, user : discord.Member = None):
        """Permet de consulter le profil electronique d'un utilisateur.(Utilisateur)"""
        bank = self.bot.get_cog('Economy').bank
        if user is None:
            user = ctx.message.author
            name = "Vous"
        if bank.account_exists(user):
            banque = bank.get_balance(user)
        else:
            banque = "Non inscrit"
        name = user.name
        karma = self.prfl[user.id]["KARMA"]
        balance = banque
        message = self.prfl[user.id]["DMSG"]
        mtemps = self.prfl[user.id]["DMSGT"]
        nombre = self.prfl[user.id]["NBMSG"]
        msg = "**A propos de *{}*:**\n".format(name)
        msg += "\n**----- ECONOMIE -----**\n"
        msg += "**N° Compte** *{}*\n".format(user.id)
        msg += "**Banque** *{}§*\n".format(balance)
        msg += "\n**------ SERVEUR -----**\n"
        msg += "**Karma** *{}*\n".format(karma)
        msg += "**Dernier msg** *{}* [{}]\n".format(message, mtemps)
        msg += "**Nb de msg** *{}*".format(nombre)
        await self.bot.whisper(msg)

    @commands.command(aliases = ['prm'], pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def profilm(self, ctx, user : discord.Member = None):
        """Permet de consulter le profil electronique d'un utilisateur.(Moderation)"""
        bank = self.bot.get_cog('Economy').bank
        if user is None:
            user = ctx.message.author
            name = "Vous"
        if bank.account_exists(user):
            banque = bank.get_balance(user)
        else:
            banque = "Non inscrit"
        name = user.name
        karma = self.prfl[user.id]["KARMA"]
        balance = banque
        message = self.prfl[user.id]["DMSG"]
        mtemps = self.prfl[user.id]["DMSGT"]
        comptes = self.prfl[user.id]["PSEUDO_LIE"]
        note = self.prfl[user.id]["NOTE"]
        nombre = self.prfl[user.id]["NBMSG"]
        msg = "**A propos de *{}*:**\n".format(name)
        msg += "\n**----- ECONOMIE -----**\n"
        msg += "**N° Compte** *{}*\n".format(user.id)
        msg += "**Banque** *{}§*\n".format(balance)
        msg += "\n**------ SERVEUR -----**\n"
        msg += "**Karma** *{}*\n".format(karma)
        msg += "**Dernier msg** *{}* [{}]\n".format(message, mtemps)
        msg += "**Nb de msg** *{}*\n".format(nombre)
        msg += "**Comptes liés** *{}*\n".format(str(comptes))
        msg += "**Note de modération** *{}*".format(note)
        await self.bot.whisper(msg)

    @commands.command(aliases = ['km'], pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def karmamod(self, ctx, user : discord.Member):
        """Modère automatiquement un utilisateur en fonction de son Karma.

        1+ : Prison de 5 minutes
        3+ : Prison d'une heure
        5+ : Kick
        7+ : Softban (Neutral)
        9-10 : Ban"""
        r = discord.utils.get(ctx.message.server.roles, name= "Prison")
        kus = self.prfl[user.id]["KARMA"]
        await self.bot.say("**Detection de la punition appropriée...**")
        await asyncio.sleep(0.25)
        if kus != 0:
            if kus >= 1 and kus < 3: #PRISON 5m
                if "Prison" not in [r.name for r in user.roles]:
                    temps = 5
                    await self.bot.add_roles(user, r)
                    if self.prfl[user.id]["KARMA"] < 10:
                        self.prfl[user.id]["KARMA"] += 1
                        fileIO("data/puser/prfl.json", "save", self.prfl)
                        notif = "(+1 Karma)"
                    else:
                        notif = "(Karma maximum)"
                    await self.bot.say("Détecté : **{}** est maintenant en prison pour {} minute(s). {}".format(user.name, temps, notif))
                    await self.bot.send_message(user, "Tu es maintenant en prison pour {} minute(s). Si tu as une réclamation à faire, va sur le canal *prison* du serveur ou contacte un modérateur.".format(temps))
                    await self.bot.server_voice_state(user, mute=True)
                    # ^ Mise en prison
                    await asyncio.sleep(300)
                    # v Sortie de prison
                    if "Prison" in [r.name for r in user.roles]:
                        await self.bot.remove_roles(user, r)
                        await self.bot.server_voice_state(user, mute=False)
                        await self.bot.say("**{}** à été libéré de la prison.".format(user.name))
                        await self.bot.send_message(user, "Tu es libéré de la prison.")
                    else:
                        pass
                else:
                    await self.bot.say("L'utilisateur est déjà en prison. Utilisez &p pour le libérer.")

            elif kus >= 3 and kus < 5: #PRISON 1h
                if "Prison" not in [r.name for r in user.roles]:
                    temps = 60
                    await self.bot.add_roles(user, r)
                    if self.prfl[user.id]["KARMA"] < 10:
                        self.prfl[user.id]["KARMA"] += 1
                        fileIO("data/puser/prfl.json", "save", self.prfl)
                        notif = "(+1 Karma)"
                    else:
                        notif = "(Karma maximum)"
                    await self.bot.say("Détecté : **{}** est maintenant en prison pour {} minute(s). {}".format(user.name, temps, notif))
                    await self.bot.send_message(user, "Tu es maintenant en prison pour {} minute(s). Si tu as une réclamation à faire, va sur le canal *prison* du serveur ou contacte un modérateur.".format(temps))
                    await self.bot.server_voice_state(user, mute=True)
                    # ^ Mise en prison
                    await asyncio.sleep(3600)
                    # v Sortie de prison
                    if "Prison" in [r.name for r in user.roles]:
                        await self.bot.remove_roles(user, r)
                        await self.bot.server_voice_state(user, mute=False)
                        await self.bot.say("**{}** à été libéré de la prison.".format(user.name))
                        await self.bot.send_message(user, "Tu es libéré de la prison.")
                    else:
                        pass
                else:
                    await self.bot.say("L'utilisateur est déjà en prison. Utilisez &p pour le libérer.")
            
            elif kus >= 5 and kus < 7: #KICK
                author = ctx.message.author
                try:
                    await self.bot.kick(user)
                    logger.info("{}({}) à kické {}({})".format(
                        author.name, author.id, user.name, user.id))
                    if self.prfl[user.id]["KARMA"] < 8:
                        self.prfl[user.id]["KARMA"] += 3
                    elif self.prfl[user.id]["KARMA"] > 7:
                        self.prfl[user.id]["KARMA"] = 10
                    fileIO("data/puser/prfl.json", "save", self.prfl)
                    await self.bot.say("Détecté : Kick effectué. (+3 Karma)")
                except discord.errors.Forbidden:
                    await self.bot.say("Je ne suis pas autorisé à faire ça.")
                except Exception as e:
                    print(e)
                    
            elif kus >= 7 and kus < 9: #SOFTBAN
                server = ctx.message.server
                channel = ctx.message.channel
                can_ban = channel.permissions_for(server.me).ban_members
                author = ctx.message.author
                if can_ban:
                    try:
                        try: 
                            msg = await self.bot.send_message(user, "Tu as été neutralisé. Nous venons d'effacer tes messages, tu peux si tu veux rejoindre à nouveau le serveur.")
                        except:
                            pass
                        await self.bot.ban(user, 1)
                        logger.info("{}({}) à neutralisé {}({}) ".format(author.name, author.id, user.name,
                             user.id))
                        await self.bot.unban(server, user)
                        if self.prfl[user.id]["KARMA"] < 7:
                            self.prfl[user.id]["KARMA"] += 4
                        elif self.prfl[user.id]["KARMA"] > 6:
                            self.prfl[user.id]["KARMA"] = 10
                        fileIO("data/puser/prfl.json", "save", self.prfl)
                        await self.bot.say("Détecté : Softban effectué. (+4 Karma)")
                    except discord.errors.Forbidden:
                        await self.bot.say("Je n'ai pas le droit de faire ça.")
                        await self.bot.delete_message(msg)
                    except Exception as e:
                        print(e)
                else:
                    await self.bot.say("Je n'ai pas les autorisations pour faire ça.")
                    
            elif kus >= 9: #BAN
                days = 1
                author = ctx.message.author
                if days < 0 or days > 7:
                    await self.bot.say("Les jours doivent être compris entre 0 et 7.")
                    return
                try:
                    await self.bot.ban(user, days)
                    logger.info("{}({}) banned {}({}), deleting {} days worth of messages".format(
                        author.name, author.id, user.name, user.id, str(days)))
                    if self.prfl[user.id]["KARMA"] < 6:
                        self.prfl[user.id]["KARMA"] += 5
                    elif self.prfl[user.id]["KARMA"] > 5:
                        self.prfl[user.id]["KARMA"] = 10
                    fileIO("data/puser/prfl.json", "save", self.prfl)
                    await self.bot.say("Détecté : Ban effectué. Les messages des dernières 24h sont effacés. (+5 Karma)")
                except discord.errors.Forbidden:
                    await self.bot.say("Je ne suis pas autorisé à le faire.")
                except Exception as e:
                    print(e)
        else:
            await self.bot.say("Le karma de l'utilisateur est nul. Aucune punition à appliquer.")

    # KARMA ----------------------------------------

    @commands.group(pass_context=True)
    async def karma(self, ctx):
        """Gestion du karma."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @karma.command(pass_context=True, no_pm=True)
    async def pts(self, ctx, user : discord.Member = None):
        """Affiche les points de Karma de l'utilisateur. (Les siens si aucun utilisateur visé)"""
        if user is None:
            user = ctx.message.author
        await self.bot.say("**{}** a *{}* points de Karma sur ses comptes.".format(user.name, self.prfl[user.id]["KARMA"]))

    @karma.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def edit(self, ctx, val, user : discord.Member):
        """Permet d'éditer les points de Karma d'un utilisateur.

        Le minimum est de 0 et le maximum de 10."""
        if val >= 0 and val <= 10:
            self.prfl[user.id]["KARMA"] = val
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Le karma de **{}** est reglé à *{}*".format(user.name, val))
        else:
            await self.bot.whisper("La valeur doit être entre 0 et 10")

    @karma.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def plus(self, ctx, user : discord.Member):
        """Permet d'ajouter un point de Karma à un utilisateur."""
        if self.prfl[user.id]["KARMA"] < 10:
            self.prfl[user.id]["KARMA"] += 1
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Le karma de **{}** est augmenté de 1. ({}pts)".format(user.name, self.prfl[user.id]["KARMA"]))
        else:
            await self.bot.say("Cet utilisateur est déjà au maximum du karma (10pts) !")

    @karma.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def moins(self, ctx, user : discord.Member):
        """Permet d'enlever un point de Karma à un utilisateur."""
        if self.prfl[user.id]["KARMA"] > 0:
            self.prfl[user.id]["KARMA"] -= 1
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Le karma de **{}** est baissé de 1. ({}pts)".format(user.name, self.prfl[user.id]["KARMA"]))
        else:
            await self.bot.say("Cet utilisateur est déjà au minimum du karma (0pts) !")

    # USER ----------------------------------------

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def chain(self, ctx, principal : discord.Member, secondaire : discord.Member):
        """Permet de lier des comptes entre eux.

        Lier des comptes permet de synchroniser le karma en cas de secondaire."""
        if principal.id in self.prfl:
            if secondaire.id in self.prfl: # On vérifie qu'ils sont présents car le compte est peut-être plus ancien que le module...
                if principal.id not in self.prfl[secondaire.id]["ID_LIE"]:
                    self.prfl[principal.id]["ID_LIE"].append(str(principal.id))
                    self.prfl[principal.id]["PSEUDO_LIE"].append(str(principal.name))
                    self.prfl[secondaire.id]["ID_LIE"].append(str(principal.id))
                    self.prfl[secondaire.id]["PSEUDO_LIE"].append(str(principal.name))
                    if self.prfl[principal.id]["KARMA"] != self.prfl[secondaire.id]["KARMA"]:
                        compare = [self.prfl[principal.id]["KARMA"], self.prfl[secondaire.id]["KARMA"]]
                        karmaset = max(compare)
                        self.prfl[principal.id]["KARMA"] = karmaset
                        self.prfl[secondaire.id]["KARMA"] = karmaset
                        fileIO("data/puser/prfl.json", "save", self.prfl)
                        await self.bot.say("Les deux comptes ont été correctement liés et synchronisés. (Ils seront synchronisés de nouveau toutes les deux heures)")
                    else:
                        fileIO("data/puser/prfl.json", "save", self.prfl)
                        await self.bot.say("Les deux comptes ont été liés et synchronisés")
                else:
                    await self.bot.say("Les deux comptes ont déjà étés liés")
            else:
                await self.bot.say("Apparemment ce compte n'est pas dans les bases de données. Je vais l'ajouter...")
                self.prfl[secondaire.id] = {"KARMA" : 0, "NBMSG" : 0, "ID_LIE" : [], "PSEUDO_LIE" : [], "DMSG" : None, "DMSGT" : None, "NOTE" : None}
                await asyncio.sleep(1)
                fileIO("data/puser/prfl.json", "save", self.prfl)
                await self.bot.say("Ajouté. Vous pouvez refaire la commande.")
        else:
            await self.bot.say("Apparemment ce compte n'est pas dans les bases de données. Je vais l'ajouter...")
            self.prfl[principal.id] = {"KARMA" : 0, "NBMSG" : 0, "ID_LIE" : [], "PSEUDO_LIE" : [], "DMSG" : None, "DMSGT" : None, "NOTE" : None}
            await asyncio.sleep(1)
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Ajouté. Vous pouvez refaire la commande.")

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(ban_members=True)
    async def unchain(self, ctx, principal : discord.Member, secondaire : discord.Member):
        """Permet de délier des comptes entre eux.

        Lier des comptes permet de synchroniser le karma en cas de secondaire."""
        if principal.id in self.prfl[secondaire.id]["ID_LIE"]:
            self.prfl[principal.id]["ID_LIE"].remove(str(principal.id))
            self.prfl[principal.id]["PSEUDO_LIE"].remove(str(principal.name))
            self.prfl[secondaire.id]["ID_LIE"].remove(str(principal.id))
            self.prfl[secondaire.id]["PSEUDO_LIE"].remove(str(principal.name))
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await self.bot.say("Les deux comptes sont maintenant déliés.")
        else:
            await self.bot.say("Les deux comptes ne sont pas liés.")

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(ban_members=True)
    async def note(self, ctx, uid, *note):
        """Permet d'ajouter une note de modération sur un utilisateur (Avec son ID).

        Il est possible d'utiliser son numéro de compte comme ID (Visible avec &prm)."""
        note = " ".join(note)
        if uid in self.prfl:
            self.prfl[uid]["NOTE"] = note
            if len(self.prfl[uid]["ID_LIE"]) != 0:
                for idlie in self.prfl[uid]["ID_LIE"]:
                    self.prfl[idlie]["NOTE"] = note
            else:
                pass
            await self.bot.say("La note à été ajoutée aux différents comptes de l'utilisateur.")
            fileIO("data/puser/prfl.json", "save", self.prfl)
        else:
            await self.bot.say("ID inconnu, utilisez '&prm' sur un utilisateur et utilisez son N° de Compte comme ID")
                    
# SYSTEME ------------------------------------------------

    def karmadd(self, id, pts): #FONCTION INTER-MODULE KARMA
        if id in self.prfl:
            self.prfl[id]["KARMA"] += 1
            fileIO("data/puser/prfl.json", "save", self.prfl)
        else:
            return False

    async def karmacheck(self):
        while self == self.bot.get_cog("Puser"):
            for id in self.prfl:
                if self.prfl[id]["KARMA"] > 0:
                    self.prfl[id]["KARMA"] -= 1
                else:
                    pass
                self.prfl[id]["NBMSG"] = 0
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await asyncio.sleep(86400)  # La tâche recommence tout les 24h

    async def sync(self):
        while self == self.bot.get_cog("Puser"):
            for id in self.prfl:
                if len(self.prfl[id]["ID_LIE"]) != 0:
                    compare = []
                    for idlie in self.prfl[id]["ID_LIE"]:
                        compare.append(self.prfl[idlie]["KARMA"])
                    karmaset = max(compare)
                    self.prfl[id]["KARMA"] = karmaset
                else:
                    pass
            fileIO("data/puser/prfl.json", "save", self.prfl)
            await asyncio.sleep(7200)  # La tâche recommence tout les 2h

    async def checking(self, message):
        author = message.author
        if author.id in self.prfl:
            self.prfl[author.id]["NBMSG"] += 1
            temps = message.timestamp
            temps = "{:%c}".format(message.timestamp)
            self.prfl[author.id]["DMSGT"] = temps
            self.prfl[author.id]["DMSG"] = message.content
        else:
            self.prfl[author.id] = {"KARMA" : 0, "NBMSG" : 0, "ID_LIE" : [], "PSEUDO_LIE" : [], "DMSG" : None, "DMSGT" : None, "NOTE" : None}
            fileIO("data/puser/prfl.json", "save", self.prfl)
                    

def check_folders():
    if not os.path.exists("data/puser"):
        print("Creation du fichier centrale de profils d'utilisateur...")
        os.makedirs("data/puser")

def check_files():
    
    if not os.path.isfile("data/puser/parm.json"):
        print("Creation du fichier de paramétrage...")
        fileIO("data/puser/parm.json", "save", {})

    if not os.path.isfile("data/puser/prfl.json"):
        print("Creation du fichier de profils...")
        fileIO("data/puser/prfl.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Puser(bot)
    bot.add_listener(n.checking, "on_message")
    bot.loop.create_task(n.karmacheck())
    bot.loop.create_task(n.sync())
    bot.add_cog(n)

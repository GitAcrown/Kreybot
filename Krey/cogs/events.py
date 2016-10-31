import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import fileIO, dataIO
from __main__ import send_cmd_help, settings
from .utils import checks
import random
import asyncio
import os

dispo = ["Réglisse","Caramel","Marshmallow","Dragée","Nougat","Sucette",
         "Calisson","Guimauve","Tagada","Berlingot","Praline","Pastille","Doliprane"]

default = {"EVENTCHAN" : None, "RAMASSEUR" : None, "SPAWNED": None, "COMPTEUR" : 0, "MINIMUM" : 150, "MAXIMUM" : 350, "LIMITE" : 225}

class Events:
    """Module d'events occasionnels. (Nécéssite 'Mine' pour fonctionner)"""

    def __init__(self, bot):
        self.bot = bot
        self.system = dataIO.load_json("data/events/system.json")
        self.player = dataIO.load_json("data/events/player.json")
        self.chan = dataIO.load_json("data/mine/sys.json")

    @commands.command(pass_context=True, hidden=True)
    async def event_debug(self, ctx):
        """Debug du module Events"""
        minimum = self.system["MINIMUM"]
        maximum = self.system["MAXIMUM"]
        limite = self.system["LIMITE"]
        compteur = self.system["COMPTEUR"]
        bonbon = None
        if self.system["SPAWNED"] != None:
            bonbon = self.system["SPAWNED"][0]
            eventchan = self.system["EVENTCHAN"]
            eventchan = self.bot.get_channel(eventchan)
        ramasseur = self.system["RAMASSEUR"]
        msg = "**--DEBUG--**\n"
        msg += "Minimum : {}\n".format(minimum)
        msg += "Maximum : {}\n".format(maximum)
        msg += "Limite : {}\n".format(limite)
        msg += "Compteur : {}\n".format(compteur)
        if ramasseur is not None:
            msg += "Bonbon **{}** sur *{}*\n".format(bonbon, eventchan.name)
        else:
            msg += "Aucun ramassage en cours"
        await self.bot.say(msg)

    @commands.command(pass_context=True)
    async def now(self, ctx):
        """Affiche des informations sur l'Event du moment."""
        await self.bot.whisper("**En ce moment:** *Event Halloween !*")
        await asyncio.sleep(1)
        msg = "__*Quelques informations sur cet Event :*__\n \n"
        msg += "De la même façon que pour le module Mine, des bonbons peuvent appraitre sur des channels écrits.\n"
        msg += "Collectionnez-les, échangez-les ou mangez-les !\n"
        msg += "Le seul but ? Tous les avoir eu avant le 1er Novembre !\n"
        msg += "Vous pouvez avoir la liste des bonbons à collectionner avec [p]event infos !"
        await self.bot.whisper(msg)

    @commands.group(pass_context=True)
    async def eventset(self, ctx):
        """Commandes de réglages pour l'event du moment."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @eventset.command(aliases = ["reset"], hidden=True, pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def reset_module(self, ctx):
        """Permet de reset le module"""
        self.reset()
        await self.bot.say("Module reset.")

    @eventset.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(kick_members=True)
    async def wipedata(self, ctx):
        """Supprime tout les inventaires"""
        self.player = {}
        await self.bot.say("Voilà que c'est fait.")

    @eventset.command(aliases = ["end"], hidden=True, pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def end_event(self, ctx):
        """Permet de terminer l'évenement. (1er Novembre)"""
        server = ctx.message.server
        msgend = "**__Voici les gagnants de cet Event Halloween :__**\n"
        for userid in self.player:
            manque = set(dispo) - set(self.player[userid])
            manque = len(manque)
            user = server.get_member(userid)
            msgend += "**{}** - *{}*\n".format(user.name, manque)
        else:
            msgend += "\n"
            msgend += "C'est le nombre de bonbons manquant à chaque personne dans son palmarès !\n"
            msgend += "C'est donc la personne ayant le plus petit chiffre qui emporte l'event ! Bravo à lui !"
            await self.bot.say(msgend)
                
    @eventset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def minimum(self, ctx, val):
        """Change le minimum de messages à compter avant la génération"""
        self.system["MINIMUM"] = int(val)
        fileIO("data/events/system.json", "save", self.system)
        await self.bot.say("Le minimum est maintenant de {}".format(val))

    @eventset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def maximum(self, ctx, val):
        """Change le maximum de messages à compter avant la génération"""
        self.system["MAXIMUM"] = int(val)
        fileIO("data/events/system.json", "save", self.system)
        await self.bot.say("Le maximum est maintenant de {}".format(val))

    @eventset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def compteur(self, ctx, val):
        """Change la valeur du compteur de messages avant génération"""
        self.system["COMPTEUR"] = int(val)
        fileIO("data/events/system.json", "save", self.system)
        await self.bot.say("Le compteur est reglé à {} pour cette session.".format(val))

    #------ EVENT HALLOWEEN ------#

    @commands.group(pass_context=True)
    async def event(self, ctx):
        """Commandes de l'event du moment !"""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @event.command(pass_context=True)
    async def infos(self, ctx):
        """Affiche les bonbons pouvant apparaître."""
        msg = "**__Voici les bonbons disponibles que vous devez collectionner:**__\n"
        for item in dispo:
            msg += "{}\n".format(item)
        else:
            await self.bot.whisper(msg)

    @event.command(pass_context=True)
    async def sac(self, ctx):
        """Affiche les bonbons en votre possession."""
        author = ctx.message.author
        if author.id in self.player:
            msg = "__**Voici votre inventaire:**__\n"
            for item in self.player[author.id]:
                if self.player[author.id][item]["QT"] == 0:
                    pass
                else:
                    msg += "{} **{}**\n".format(self.player[author.id][item]["NOM"], self.player[author.id][item]["QT"])
            else:
                if msg == "__**Voici votre inventaire:**__\n":
                    msg += "**VIDE**"
                await self.bot.whisper(msg)
        else:
            self.player[author.id] = {}
            fileIO("data/events/player.json", "save", self.player)
            await self.bot.say("Vous n'avez rien ! *(Je viens juste de vous enregistrer en fait)*")

    @event.command(pass_context=True, hidden=True)
    async def don(self, ctx, user: discord.Member, item: str):
        """Permet de donner un bonbon à un membre enregistré."""
        author = ctx.message.author
        item = item.title()
        if item == "Reglisse":
            item = "Réglisse"
        if item == "Dragee":
            item = "Dragée"
        if author.id in self.player:
            if user.id in self.player:
                if item in self.player[author.id]:
                    if self.player[author.id][item]["QT"] > 0:
                        self.player[author.id][item]["QT"] -= 1
                        if item not in self.player[user.id]:
                            self.player[user.id][item] = {"NOM" : item, "QT" : 1}
                            fileIO("data/events/player.json", "save", self.player)
                            await self.bot.send_message(user, "J'ai rajouté ce bonbon à votre inventaire provenant de {}: {}.".format(author.name, item))
                        else:
                            self.player[user.id][item]["QT"] += 1
                            fileIO("data/events/player.json", "save", self.player)
                            await self.bot.send_message(user, "Nouvel exemplaire de {} provenant de {}.".format(item, author.name))

    @event.command(pass_context=True)
    async def eat(self, ctx, *item):
        """Permet de manger un bonbon. Ne l'enlève pas de votre 'palmares'."""
        item = item.title()
        if item == "Reglisse":
            item = "Réglisse"
        if item == "Pate de fruit":
            item = "Pâte de fruit"
        if item == "Dragee":
            item = "Dragée"
        author = ctx.message.author
        user = author
        if author.id in self.player:
            if item in self.player[author.id]:
                if self.player[author.id][item]["QT"] >= 1:
                    await self.bot.say("{} Vous venez de manger **{}**.".format(author.mention, item))
                    self.player[author.id][item]["QT"] -= 1
                    fileIO("data/events/player.json", "save", self.player)
                    chance = random.randint(1, 5)
                    if chance == 1:
                        if item == "Caramel":
                            r = discord.utils.get(ctx.message.server.roles, name="Nègre")
                            if "Nègre" not in [r.name for r in user.roles]:
                                await self.bot.add_roles(author, r)
                                await self.bot.say("Oh non {}, le caramel t'a rendu Nègre ! (5m)".format(author.mention))
                                await asyncio.sleep(300)
                                await self.bot.remove_roles(author, r)
                                await self.bot.whisper("Les effets du caramel se sont dissipés...")
                        if item == "Doliprane":
                            r = discord.utils.get(ctx.message.server.roles, name="Cancéreux")
                            if "Cancéreux" not in [r.name for r in user.roles]:
                                await self.bot.add_roles(author, r)
                                await self.bot.say("{} Tu as la nausée... Oh non, le doliprane t'a rendu temporairement cancéreux ! (5m)".format(author.mention))
                                await asyncio.sleep(300)
                                await self.bot.whisper("Les effets du doliprane se sont dissipés...")
                        if item == "Tagada":
                            r = discord.utils.get(ctx.message.server.roles, name="Attention Whore")
                            if "Attention Whore" not in [r.name for r in user.roles]:
                                await self.bot.add_roles(author, r)
                                await self.bot.say("{} Tu as soudainement envie de parler de ta vie de merde... Oh non, la Tagada t'a rendu Attention Whore ! (5m)".format(author.mention))
                                await asyncio.sleep(300)
                                await self.bot.remove_roles(author, r)
                                await self.bot.whisper("Les effets de la tagada se sont dissipés...")
                        if item == "Calisson":
                            r = discord.utils.get(ctx.message.server.roles, name="Jaquette")
                            if "Jaquette" not in [r.name for r in user.roles]:
                                await self.bot.add_roles(author, r)
                                await self.bot.say("{} Des arcs-en ciel apparaissent au loin... Non ce n'est pas le GHB, c'est le Calisson qui t'a rendu Jaquette ! (5m)".format(author.mention))
                                await asyncio.sleep(300)
                                await self.bot.remove_roles(author, r)
                                await self.bot.whisper("Les effets du calisson se sont dissipés...")
                        if item == "Pastille":
                            r = discord.utils.get(ctx.message.server.roles, name="Prison")
                            if "Prison" not in [r.name for r in user.roles]:
                                await self.bot.add_roles(author, r)
                                await self.bot.say("Il semble que la pastille de {} n'était pas du sucre, mais bien de la drogue illégale ! Hop, en prison ! (30s)".format(author.mention))
                                await self.bot.whisper("30 secondes de prison suffiront...")
                                await asyncio.sleep(30)
                                await self.bot.remove_roles(author, r)
                                await self.bot.whisper("Les effets de la pastille se sont dissipés...")
                        else:
                            await self.bot.say("Mh, il n'était plus très bon...")
                    else:
                        pass
                else:
                    await self.bot.say("Vous n'avez pas assez de ce bonbon !")
            else:
                await self.bot.say("Vous n'avez pas ce bonbon !")
        else:
            self.player[author.id] = {}
            fileIO("data/events/player.json", "save", self.player)
            await self.bot.say("Vous n'avez rien ! *(Je viens juste de vous enregistrer en fait)*")

    @event.command(pass_context=True)
    async def pick(self, ctx):
        """Permet de ramasser un bonbon qui vient d'apparaître sur le même channel !"""
        author = ctx.message.author
        channel = ctx.message.channel
        if author.id in self.player:
            if channel.id in self.chan["CHANNELS"]:
                if channel.id == self.system["EVENTCHAN"]:
                    if self.system["RAMASSEUR"] is None:
                        self.system["RAMASSEUR"] = author.id
                        bonbon = self.system["SPAWNED"]
                        await self.bot.say("{} Vous ramassez **{}** !".format(author.mention, bonbon))
                        await asyncio.sleep(1.5)
                        await self.bot.say("**Terminé !** *{}* a été rajouté à votre inventaire.".format(bonbon))
                        fileIO("data/events/system.json", "save", self.system)
                        if bonbon not in self.player[author.id]:
                            self.player[author.id][bonbon] = {"NOM" : bonbon, "QT" : 1}
                            fileIO("data/events/player.json", "save", self.player)
                            await self.bot.whisper("J'ai rajouté ce bonbon à votre inventaire : {}.".format(bonbon))
                        else:
                            self.player[author.id][bonbon]["QT"] += 1
                            fileIO("data/events/player.json", "save", self.player)
                            await self.bot.whisper("Nouvel exemplaire de {}.".format(bonbon))
                        self.reset()
                    else:
                        await self.bot.say("Quelqu'un ramasse le bonbon !")
                else:
                    await self.bot.say("Il n'y a rien sur ce channel.")
            else:
                await self.bot.say("Ce channel n'est pas dans ma base de donnée")
        else:
            self.player[author.id] = {}
            fileIO("data/events/player.json", "save", self.player)
            await self.bot.say("Vous n'avez pas la possibilité de faire ça ! Réessayez plus tard. *(Je viens juste de vous enregistrer en fait)*")

    def reset(self):
        self.system["RAMASSEUR"] = None
        self.system["EVENTCHAN"] = None
        self.system["SPAWNED"] = None
        minimum = self.system["MINIMUM"]
        maximum = self.system["MAXIMUM"]
        self.system["COMPTEUR"] = 0
        newcounter = random.randint(minimum, maximum)
        self.system["LIMITE"] = newcounter
        fileIO("data/events/system.json", "save", self.system)

    async def generator(self, message):
        if self.system["RAMASSEUR"] is None: #Si il n'y a pas de minage
            self.system["COMPTEUR"] += 1 #On ajoute 1 au compteur
            fileIO("data/events/system.json", "save", self.system)
            if self.system["COMPTEUR"] == self.system["LIMITE"]: #Si le compteur atteint la limite
                eventchan = random.choice(self.chan["CHANNELS"]) #On choisi un channel au hasard
                self.system["EVENTCHAN"] = eventchan #On enregistre l'ID du channel
                channel = self.bot.get_channel(eventchan) #On obtient le channel lié à l'ID 
                bonbon = random.choice(dispo) #On génère un bonbon
                self.system["SPAWNED"] = bonbon #On met le bonbon dans la mémoire
                await self.bot.send_message(channel, "==============================================\n**{}** vient d'apparaitre ! Ramassez-le avec [p]event pick ([p]evp) !\n==============================================".format(bonbon)) #On fait spawner le bonbon généré (en msg)
                fileIO("data/events/system.json", "save", self.system)
            else:
                pass
        else:
            pass

def check_folders():
    folders = ("data", "data/events/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Création fichier " + folder)
            os.makedirs(folder)

def check_files():
    if not os.path.isfile("data/events/system.json"):
        print("Création de data.json...")
        fileIO("data/events/system.json", "save", default)
        
    if not os.path.isfile("data/events/player.json"):
        print("Création de data.json...")
        fileIO("data/events/player.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Events(bot)
    bot.add_listener(n.generator, 'on_message')
    bot.add_cog(n)

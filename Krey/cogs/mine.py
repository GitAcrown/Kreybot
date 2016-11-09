import discord
from discord.ext import commands
from .utils.dataIO import fileIO, dataIO
from .utils import checks
from __main__ import send_cmd_help, settings
import random
import logging
import asyncio
import os

#Freya Exclusive
default = {"CHANNELS" : [], "MINECHAN" : None, "MINEUR" : None, "SPAWNED": None, "COMPTEUR" : 0, "MINIMUM" : 250, "MAXIMUM" : 1000, "LIMITE" : 500}

class Mine:
    """Il est temps de partir à la mine..."""

    def __init__(self, bot):
        self.bot = bot
        self.sys = dataIO.load_json("data/mine/sys.json")
        self.inv = dataIO.load_json("data/mine/inv.json")
        self.mine_commun = [["Fer", "kg de fer", 18, 3],
                            ["Charbon", "kg de charbon", 7, 2],
                            ["Sel", "kg de sel", 12, 3],
                            ["Zinc", "kg de zinc", 19, 3],
                            ["Cuivre", "kg de cuivre", 22, 3],
                            ["Plomb", "kg de plomb", 25, 3]]
        self.mine_altern = [["Argent", "g d'argent", 34, 4],
                            ["Or", "g d'or", 48, 4],
                            ["Platine", "g de platine", 60, 4],
                            ["Inox", "g d'inox", 40, 4],
                            ["Aluminium", "g d'aluminium", 45, 4]]
        self.mine_rare = [["Rubis", "mg de rubis", 68, 5],
                          ["Saphir", "mg de saphirs", 78, 5],
                          ["Iridium", "mg d'iridium", 102, 5],
                          ["Diamant", "mg de diamants", 90, 5]]
        self.mine_urare = [["Tritium", "µg de tritium", 140, 6],
                           ["Plutonium", "µg de plutonium", 196, 6],
                           ["Europium", "µg d'europium", 232, 6],
                           ["Antimatière", "µg d'antimatière", 370, 7]]
        self.mine_legend = [["Mitrhil", "ng de mithrhil", 410, 8],
                            ["Epice", "ng d'épice", 475, 8],
                            ["Orichalque", "ng d'orichalque", 534, 8],
                            ["Kryptonite", "ng de kryptonite", 592, 8],
                            ["Vibranium", "ng de vibranium", 620, 8],
                            ["Devilium", "ng de devilium", 666, 9],
                            ["Naquadah", "ng de naquadah", 714, 9]]
    
    @commands.command(pass_context=True, hidden=True)
    async def mine_debug(self, ctx):
        """Debug du module Mine"""
        minimum = self.sys["MINIMUM"]
        maximum = self.sys["MAXIMUM"]
        limite = self.sys["LIMITE"]
        compteur = self.sys["COMPTEUR"]
        minerai = None
        if self.sys["SPAWNED"] != None:
            minerai = self.sys["SPAWNED"][0]
            minechan = self.sys["MINECHAN"]
            minechan = self.bot.get_channel(minechan)
        mineur = self.sys["MINEUR"]
        msg = "**--DEBUG--**\n"
        msg += "Minimum : {}\n".format(minimum)
        msg += "Maximum : {}\n".format(maximum)
        msg += "Limite : {}\n".format(limite)
        msg += "Compteur : {}\n".format(compteur)
        if minerai is not None:
            msg += "Minerai **{}** sur *{}*\n".format(minerai, minechan.name)
        else:
            msg += "Aucun minage en cours"
        await self.bot.say(msg)

    @commands.group(pass_context=True)
    async def mineset(self, ctx):
        """Règle le module de minage."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @mineset.command(aliases = ["reset"], hidden=True, pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def reset_module(self, ctx):
        """Permet de reset le module"""
        self.reset()
        await self.bot.say("Module reset.")

    @mineset.command(aliases = ["add"], pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def addchannel(self, ctx, channelid):
        """Permet de rajouter un channel où génerer des minerais."""
        if channelid not in self.sys["CHANNELS"]:
            self.sys["CHANNELS"].append(channelid)
            fileIO("data/mine/sys.json", "save", self.sys)
            await self.bot.say("J'ai bien pris en compte le chan demandé.")
        else:
            await self.bot.say("J'ai déjà enregistré ce channel.")

    @mineset.command(aliases = ["remove"], pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def remchannel(self, ctx, channelid):
        """Permet d'enlever un channel où l'ont génere les minerais."""
        if channelid in self.sys["CHANNELS"]:
            self.sys["CHANNELS"].remove(channelid)
            fileIO("data/mine/sys.json", "save", self.sys)
            await self.bot.say("J'ai bien pris en compte la suppresion du chan demandé.")
        else:
            await self.bot.say("Ce channel n'est pas dans mes registres.")

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def minimum(self, ctx, val):
        """Change le minimum de messages à compter avant la génération"""
        self.sys["MINIMUM"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le minimum est maintenant de {}".format(val))

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def maximum(self, ctx, val):
        """Change le maximum de messages à compter avant la génération"""
        self.sys["MAXIMUM"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le maximum est maintenant de {}".format(val))

    @mineset.command(pass_context=True, no_pm=True)
    @checks.admin_or_permissions(kick_members=True)
    async def compteur(self, ctx, val):
        """Change la valeur du compteur de messages avant génération"""
        self.sys["COMPTEUR"] = int(val)
        fileIO("data/mine/sys.json", "save", self.sys)
        await self.bot.say("Le compteur est reglé à {} pour cette session".format(val))

# ------------ UTILISATEUR -------------------

    @commands.group(pass_context=True)
    async def mine(self, ctx):
        """Règle le module de minage."""
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)
            msg = "```"
            for k, v in settings.get_server(ctx.message.server).items():
                msg += str(k) + ": " + str(v) + "\n"
            msg += "```"
            await self.bot.say(msg)

    @mine.command(pass_context=True, no_pm=True)
    async def register(self, ctx):
        """Permet de s'enregistrer en avance."""
        author = ctx.message.author
        if author.id not in self.inv:
            await self.bot.say("Vous n''avez pas de pioche ! Laissez-moi vous en donner une...")
            await asyncio.sleep(1)
            self.inv[author.id] = {}
            fileIO("data/mine/inv.json", "save", self.inv)
            await self.bot.say("Voilà ! Si vous voulez miner, vous pouvez dès à présent refaire la commande.")
        else:
            await self.bot.say("Vous êtes déjà inscrit !")

    @mine.command(pass_context=True, no_pm=True)
    async def raffine(self, ctx, item : str, qual : int = 1):
        """Permet de raffiner un minerai pour en augmenter (peut-^être) sa valeur.
        Item = Groupe de minerai qui doit être raffiné
        Qual = Qualité visé parmis trois catégorie (1 = Moyen(28§/u), 2 = Bon(42§/u), 3 = Excellent(56§/u))
        Plus la qualité visée est haute moins il y a de chances que ça fonctionne et plus ça coute cher.

        ATTENTION : Cette commande raffine le groupe de minerai entier et pas seulement une unité.
        En cas de réussite, les minerais sont vendus automatiquement pour éviter l'encombrement de l'inventaire."""
        author = ctx.message.author
        if qual == 1:
            p_u = 28
            raf = "Moyen"
            await self.bot.say("**Qualité choisie :** *Moyen* (28§ par unité).")
        if qual == 2:
            p_u = 42
            raf = "Bon"
            await self.bot.say("**Qualité choisie :** *Bon* (42§ par unité).")
        if qual == 3:
            p_u = 56
            raf = "Excellent"
            await self.bot.say("**Qualité choisie :** *Excellent* (56§ par unité).")
        item = item.title()
        bank = self.bot.get_cog('Economy').bank
        if author.id in self.inv:
            if item in self.inv[author.id]:
                before = self.inv[author.id][item]["PUNITE"]
                if bank.account_exists(author):
                    quant = self.inv[author.id][item]["QUANTITE"]
                    prix = p_u * quant
                    if bank.can_spend(author, prix):
                        bank.withdraw_credits(author, prix)
                        wd = random.randint(1, 7)
                        time = qual * 2
                        await asyncio.sleep(0.5)
                        await self.bot.say("*Vous raffinez lentement votre **{}**...*".format(item))
                        await asyncio.sleep(time)
                        if wd > qual:
                            bonus = self.inv[author.id][item]["PUNITE"] / 2
                            bonus = int(bonus * qual)
                            self.inv[author.id][item]["PUNITE"] = self.inv[author.id][item]["PUNITE"] + bonus
                            fileIO("data/mine/inv.json", "save", self.inv)
                            await self.bot.say("**C'est une réussite !** La valeur de {} est augmenté de {}§ ! *Vos minerais raffinés vont être vendus automatiquement dans quelques secondes...*".format(item, bonus))
                            await asyncio.sleep(2)
                            dispo = self.inv[author.id][item]["QUANTITE"]
                            vente = self.inv[author.id][item]["PUNITE"] * dispo
                            bank.deposit_credits(author, vente)
                            await self.bot.say("Vous venez de vendre {} **{}** [Raffinage {}]. Vous obtenez donc {}§".format(quant, item, raf, vente))
                            self.inv[author.id][item]["QUANITE"] = 0
                            self.inv[author.id][item]["PUNITE"] = before
                            fileIO("data/mine/inv.json", "save", self.inv)
                        else:
                            await self.bot.say("C'est un échec ! Vos minerais vous sont donc rendus.")
                    else:
                        await self.bot.say("Vous n'avez pas assez d'argent sur votre compte.")
                else:
                    await self.bot.say("Vous n'avez pas de compte bancaire sur ce serveur.")
            else:
                await self.bot.say("Vous ne possédez pas cet item.")
        else:
            await self.bot.say("Vous n'êtes pas inscrit dans cette extension.")

    @mine.command(pass_context=True, no_pm=True)
    async def pioche(self, ctx):
        """Permet le minage de l'item apparu sur le channel où la commande est réalisée."""
        author = ctx.message.author
        channel = ctx.message.channel
        if author.id in self.inv:
            if channel.id in self.sys["CHANNELS"]:
                if channel.id == self.sys["MINECHAN"]:
                    if self.sys["MINEUR"] is None:
                        self.sys["MINEUR"] = author.id
                        minerai = self.sys["SPAWNED"]
                        await self.bot.say("{} Vous commencez à miner **{}** !".format(author.mention, minerai[0]))
                        quant = random.randint(2, 8)
                        time = int(minerai[3])
                        await asyncio.sleep(time)
                        await self.bot.say("**Terminé !** {} *{}* a été rajouté à votre inventaire.".format(quant, minerai[1]))
                        punite = int(minerai[2])
                        fileIO("data/mine/sys.json", "save", self.sys)
                        if minerai[0] not in self.inv[author.id]:
                            self.inv[author.id][minerai[0]] = {"NOM" : minerai[0], "PHRASE" : minerai[1], "QUANTITE" : quant, "PUNITE" : punite}
                            fileIO("data/mine/inv.json", "save", self.inv)
                            await self.bot.whisper("J'ai rajouté ce nouveau minerai à votre inventaire : {}.".format(minerai[0]))
                        else:
                            self.inv[author.id][minerai[0]]["QUANTITE"] += quant
                            fileIO("data/mine/inv.json", "save", self.inv)
                            await self.bot.whisper("Ajout de : {}.".format(minerai[0]))
                        self.reset()
                    else:
                        await self.bot.say("Quelqu'un est en train de miner !")
                else:
                    await self.bot.say("Il n'y a rien sur ce channel.")
            else:
                await self.bot.say("Ce channel n'est pas dans ma base de donnée")
        else:
            await self.bot.say("Vous n''avez pas de pioche ! Laissez-moi vous en donner une...")
            await asyncio.sleep(1)
            self.inv[author.id] = {}
            fileIO("data/mine/inv.json", "save", self.inv)
            await self.bot.say("Voilà ! Si vous voulez miner, vous pouvez dès à présent refaire la commande.")

    @mine.command(pass_context=True, no_pm=True)
    async def sell(self, ctx, quant : int, item : str):
        """Permet de vendre un item en fonction de sa valeur."""
        item = item.title()
        author = ctx.message.author
        bank = self.bot.get_cog('Economy').bank
        if author.id in self.inv:
            if item in self.inv[author.id]:
                if quant <= self.inv[author.id][item]["QUANTITE"]:
                    if bank.account_exists(author):
                        vente = self.inv[author.id][item]["PUNITE"] * quant
                        self.inv[author.id][item]["QUANTITE"] -= quant
                        bank.deposit_credits(author, vente)
                        await self.bot.say("Vous venez de vendre {} **{}**. Vous obtenez donc {}§".format(quant, item, vente))
                        fileIO("data/mine/inv.json", "save", self.inv)
                    else:
                        await self.bot.say("Vous n'avez pas de compte bancaire (Wtf ?)")
                else:
                    await self.bot.say("Vous n'avez pas cette quantité de cet item.")
            else:
                await self.bot.say("Vous n'avez pas cet item.")
        else:
            await self.bot.say("Votre inventaire est vide.")

    @mine.command(pass_context=True, no_pm=True)
    async def sellall(self, ctx):
        """Permet la vente de l'ensemble des items possédés."""
        author = ctx.message.author
        bank = self.bot.get_cog('Economy').bank
        msg = "__**Voici vos ventes :**__\n"
        total = 0
        if author.id in self.inv:
            if bank.account_exists(author):
                for item in self.inv[author.id]:
                    if self.inv[author.id][item]["QUANTITE"] > 0:
                        vente = self.inv[author.id][item]["PUNITE"] * self.inv[author.id][item]["QUANTITE"]
                        before = self.inv[author.id][item]["QUANTITE"]
                        self.inv[author.id][item]["QUANTITE"] = 0
                        bank.deposit_credits(author, vente)
                        msg += "Vous venez de vendre {} **{}**. Vous obtenez donc {}§\n".format(before, item, vente)
                        total += vente
                    else:
                        pass
                else:
                    msg += "*Total:* {}§".format(total)
                    fileIO("data/mine/inv.json", "save", self.inv)
                    await self.bot.say(msg)
            else:
                await self.bot.say("Vous n'avez pas de compte bancaire.")
        else:
            await self.bot.say("Vous n'êtes pas inscrit.")

    @mine.command(pass_context=True)
    async def inventaire(self, ctx):
        """Montre votre inventaire de minerais minés"""
        author = ctx.message.author
        msg = "__**Voici votre inventaire** {}:__\n".format(author.mention)
        if author.id in self.inv:
            if len(self.inv[author.id]) > 0:
                for item in self.inv[author.id]:
                    msg += "{} **{}** | *{}*§ l'unité\n".format(self.inv[author.id][item]["QUANTITE"], self.inv[author.id][item]["NOM"], self.inv[author.id][item]["PUNITE"])
                else:
                    msg += "-------------"
                    await self.bot.whisper(msg)
            else:
                await self.bot.say("Vous n'avez rien !")
        else:
            await self.bot.say("Votre inventaire est vide.")

    @mine.command(pass_context=True)
    async def infos(self, ctx):
        """Affiche des informations sur les minerais disponibles."""
        msg = "__**Minerais disponibles :**__\n" + "\n"
        msg += "**------ COMMUNS ------**\n"
        msg += "*Charbon*, 7§ l'unité\n"
        msg += "*Sel*, 12§ l'unité\n"
        msg += "*Fer*, 18§ l'unité\n"
        msg += "*Zinc*, 19§ l'unité\n"
        msg += "*Cuivre*, 22§ l'unité\n"
        msg += "*Plomb*, 25§ l'unité\n"
        msg += "\n"
        msg += "**---- PEU COMMUNS ----**\n"
        msg += "*Argent*, 34§ l'unité\n"
        msg += "*Inox*, 40§ l'unité\n"
        msg += "*Aluminium*, 45§ l'unité\n"
        msg += "*Or*, 48§ l'unité\n"
        msg += "*Platine*, 60§ l'unité\n"
        msg += "\n"
        msg += "**------- RARES -------**\n"
        msg += "*Rubis*, 68§ l'unité\n"
        msg += "*Saphire*, 78§ l'unité\n"
        msg += "*Diamant*, 90§ l'unité\n"
        msg += "*Iridium*, 120§ l'unité\n"
        msg += "\n"
        msg += "**---- TRES RARES ----**\n"
        msg += "*Tritium*, 140§ l'unité\n"
        msg += "*Plutonium*, 196§ l'unité\n"
        msg += "*Europium*, 232§ l'unité\n"
        msg += "*Antimatière*, 370§ l'unité\n"
        msg += "\n"
        msg += "**---- LEGENDAIRES ----**\n"
        msg += "*Mitrhil*, 410§ l'unité\n"
        msg += "*Epice*, 475§ l'unité\n"
        msg += "*Orichalque*, 534§ l'unité\n"
        msg += "*Kryptonite*, 592§ l'unité\n"
        msg += "*Vibranium*, 620§ l'unité\n"
        msg += "*Devilium*, 666§ l'unité\n"
        msg += "*Naquadah*, 714§ l'unité\n"
        msg += "\n"
        msg += "**Il y a environ:**\n- 45% de chance de tomber sur un commun\n- 25% de chance pour peu commun\n- 15% de chance pour rare\n- 10% de chance pour très rare\n- 5% de chance pour Légendaire"
        msg += "\nLes temps de minage varient en fonction de la rareté du minerai extrait. Plus ça met du temps, plus vous êtes chanceux !"
        await self.bot.whisper(msg)
        
    def reset(self):
        self.sys["MINEUR"] = None
        self.sys["MINECHAN"] = None
        self.sys["SPAWNED"] = None
        minimum = self.sys["MINIMUM"]
        maximum = self.sys["MAXIMUM"]
        self.sys["COMPTEUR"] = 0
        newcounter = random.randint(minimum, maximum)
        self.sys["LIMITE"] = newcounter
        fileIO("data/mine/sys.json", "save", self.sys)

    def gen_mine(self):
        aleat = random.randint(1, 100)
        if aleat < 45:
            choix = random.choice(self.mine_commun)
            return choix
        elif aleat >= 45 and aleat < 70:
            choix = random.choice(self.mine_altern)
            return choix
        elif aleat >= 70 and aleat < 85:
            choix = random.choice(self.mine_rare)
            return choix
        elif aleat >= 85 and aleat < 93:
            choix = random.choice(self.mine_urare)
            return choix
        else:
            choix = random.choice(self.mine_legend)

    async def counter(self, message):
        if self.sys["MINEUR"] is None: #Si il n'y a pas de minage
            self.sys["COMPTEUR"] += 1 #On ajoute 1 au compteur
            fileIO("data/mine/sys.json", "save", self.sys)
            if self.sys["COMPTEUR"] == self.sys["LIMITE"]: #Si le compteur atteint la limite
                randomize = random.randint(1, 10)
                if randomize != 1:
                    minechan = random.choice(self.sys["CHANNELS"]) #On choisi un channel au hasard
                    self.sys["MINECHAN"] = minechan #On enregistre l'ID du channel
                    channel = self.bot.get_channel(minechan) #On obtient le channel lié à l'ID 
                    minerai = self.gen_mine() #On génère un minerai
                    self.sys["SPAWNED"] = minerai #On met le minerai dans la mémoire
                    await self.bot.send_message(channel, "-------------------------------------\n**{}** vient d'apparaitre ! Faîtes [p]mine pioche pour miner !\n-------------------------------------".format(minerai[0])) #On fait spawner le minerai généré (en msg)
                    fileIO("data/mine/sys.json", "save", self.sys)
                else:
                    minechan = random.choice(self.sys["CHANNELS"]) #On choisi un channel au hasard
                    self.sys["MINECHAN"] = minechan #On enregistre l'ID du channel
                    channel = self.bot.get_channel(minechan) #On obtient le channel lié à l'ID
                    minerai = self.gen_mine() #On génère un minerai
                    self.sys["SPAWNED"] = minerai #On met le minerai dans la mémoire
                    await self.bot.send_message(channel, "-------------------------------------\nUn **Minerai indétectable** vient d'apparaitre. Faîtes [p]mine pioche pour miner ce mystère !\n-------------------------------------")
                    fileIO("data/mine/sys.json", "save", self.sys)
            else:
                pass
        else:
            pass

def check_folders():
    folders = ("data", "data/mine/")
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    if not os.path.isfile("data/mine/sys.json"):
        print("Creating empty data.json...")
        fileIO("data/mine/sys.json", "save", default)

    if not os.path.isfile("data/mine/inv.json"):
        print("Creating empty data.json...")
        fileIO("data/mine/inv.json", "save", {})

def setup(bot):
    check_folders()
    check_files()
    n = Mine(bot)
    bot.add_listener(n.counter, 'on_message')
    bot.add_cog(n)    

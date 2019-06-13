import discord
from discord.ext import commands
from discord import Client
from discord import Server
from datetime import datetime
from tabulate import tabulate
import configparser
import os
import urllib.request
import json
config = configparser.ConfigParser()
config.read('config.ini')

bot = commands.Bot(command_prefix='ng!')
client = discord.Client()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await client.login(config['TOKEN']['TOKEN'])

@bot.command(pass_context=True, aliases=['profile', 'player'])
async def p(ctx, input = ""):
    if input:
        player = input.replace(" ", "%20")
        print(str(player))
        try:
            request = urllib.request.Request("https://api.nethergames.org/?action=stats&player=" + str(player), headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('UTF-8'))
        except BaseException as e:
            await bot.say("Sorry, that player could not be found. Perhaps you made a typo?")

        if not data:
            await bot.say("Sorry, that player could not be found. Perhaps you made a typo?")
        else:
            embed=discord.Embed(title="Player statistics for " + str(data["name"]), url="https://account.nethergames.org/player/" + str(player))
            embed.set_author(name="NetherGames Network", url="https://nethergames.org", icon_url="https://cdn.nethergames.org/img/logo_small_trans.png")
            embed.set_thumbnail(url="https://player.nethergames.org/avatar/" + str(player))
            embed.add_field(name="Kills", value=str(data["kills"]), inline=True)
            embed.add_field(name="Deaths", value=str(data["deaths"]), inline=True)
            embed.add_field(name="K/DR", value=str(round(int(data["kills"]) / int(data["deaths"]), 2)), inline=True)
            embed.add_field(name="Wins", value=str(data["wins"]), inline=True)
            embed.add_field(name="Level", value=str(data["level"]), inline=True)
            embed.add_field(name="Credits", value=str(data["status_credits"]), inline=True)
            if not data["rank"]:
                data["rank"] = "Guest"
            embed.add_field(name="Rank", value=str(data["rank"]), inline=True)
            if not data["tier"]:
                data["tier"] = "No tier"
            embed.add_field(name="Tier", value=str(data["tier"]), inline=True)
            embed.add_field(name="First seen", value=str(data["firstJoin"]), inline=True)
            embed.add_field(name="Last seen", value=str(data["lastJoin"]), inline=True)
            if int(data["online"]) == 1:
                embed.set_footer(text="Online - playing on " + str(data["lastServer"]), icon_url="https://cdn.nethergames.org/img/green.png")
            else:
                embed.set_footer(text="Offline - last seen on " + str(data["lastServer"]), icon_url="https://cdn.nethergames.org/img/red.png")
            try:
                await bot.say(embed=embed)
            except BaseException as e:
                await bot.say("Backtrace: " + str(e))
    else:
        await bot.say("Usage: ng!p <player>")

@bot.command(pass_context=True, aliases=['r', 'ranking', 'leaderboard', 'leaderboards'])
async def l(ctx, leaderboard = "", game = ""):
    if leaderboard:
        leaderboard = str(leaderboard)
        leaderboard = leaderboard.lower()
        if game:
            game = str(game)
            game = game.upper()
        print(str(leaderboard))
        try:
            if game:
                request = urllib.request.Request("https://api.nethergames.org/?action=leaderboards&type=wins&game=" + game, headers={'User-Agent': 'Mozilla/5.0'})
            else:
                request = urllib.request.Request("https://api.nethergames.org/?action=leaderboards&type=" + leaderboard, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(request)
            data = json.loads(response.read().decode('UTF-8'))
        except BaseException as e:
            await bot.say("Sorry, that leaderboard could not be loaded.")
    
        if not data:
            await bot.say("Sorry, that leaderboard could not be loaded.")
        else:
            table_data = []
            number = 0
            for d in data:
                table_data.append([])
                table_data[number].append(number + 1)
                table_data[number].append(str(d["player"]))
                table_data[number].append(str(d["kdr"]))
                table_data[number].append(str(d["kills"]))
                table_data[number].append(str(d["deaths"]))
                table_data[number].append(str(d["wins"]))
                table_data[number].append(str(d["level"]))
                table_data[number].append(str(d["credits"]))
                number += 1
            leaderboards_data = tabulate([table_data[0], table_data[1], table_data[2], table_data[3], table_data[4]], ["#", "Name", "K/DR", "Kills", "Deaths", "Wins", "Level", "Credits"], tablefmt="grid")
            leaderboards_data2 = tabulate([table_data[5], table_data[6], table_data[7], table_data[8], table_data[9]], ["#", "Name", "K/DR", "Kills", "Deaths", "Wins", "Level", "Credits"], tablefmt="grid")
            message = "```" + leaderboards_data + "```"
            message2 = "```" + leaderboards_data2 + "```"
            try:
                await bot.say("Leaderboard for " + leaderboard)
                await bot.say(message)
                await bot.say(message2)
                await bot.say("Data fetched from API cache at " + str(datetime.now()))
            except BaseException as e:
                await bot.say("Backtrace: " + str(e))
    else:
        await bot.say("Usage: ng!l <kdr|kills|wins|xp|credits> [bb|bh|br|bw|mm|sc|sw]")
        await bot.say("Game (2nd parameter) filter only works for the wins leaderboard")
bot.run(config['TOKEN']['TOKEN'])

# Std Lib Imports
import os
import datetime

# 3rd Party Imports
import discord
import databases

# Local Imports
from utils import load_config

#intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True

#bot
bot = discord.Bot(debug_guilds=[config.guild_id], intents=intents)

#config
config = load_config()

@bot.event
async def on_ready():

    #create log file
    f = open("cronjob/logs/log.txt", "a")
    f.write(str(datetime.datetime.now()) + " - Cronjob started.\n")

    print(f"{bot.user} cronjob is running.")

    guild = bot.get_guild(config.guild_id)

    #get the vip object
    vip = discord.utils.get(guild.roles, name="VIP")

    #db connection
    database = databases.Database(config.databases.tf2maps_site)
    await database.connect()

    #print the members under that role
    for member in vip.members:
        current_user = member.id
        
        #check DB
        query = "SELECT provider_key FROM xf_user INNER JOIN xf_user_connected_account ON xf_user.user_id = xf_user_connected_account.user_id WHERE find_in_set(19, secondary_group_ids) AND provider = 'th_cap_discord' AND provider_key = :provider_key;"
        values = {"provider_key": member.id}
        result = await database.fetch_one(query=query, values=values)
        
        #if not in query remove vip role
        if not result:

            f.write(str(datetime.datetime.now()) + " - Vip expired for: " + str(member) + "\n")
            #send them a DM notifying if the expiration
            await member.send("Your VIP status has expired. Upgrade to VIP https://tf2maps.net/account/upgrades")

            #remove role
            await member.remove_roles(vip)
            print("We need to remove the VIP role for: " + str(member))

    f.write(str(datetime.datetime.now()) + " - Cronjob ended.\n")
    print("Cronjob ended.")
    f.close()
    os._exit(os.EX_OK)

bot.run(config.bot_token)

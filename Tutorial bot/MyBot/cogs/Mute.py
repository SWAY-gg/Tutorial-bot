# Imports
import discord
from discord.ext import commands, tasks

import json 
import typing 
import datetime
from datetime import datetime, timedelta

class Mute(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot     = bot
        self.mute_id = None 

        self.check.start()
    
    def cog_unload(self):
        self.check.cancel()

    @tasks.loop(seconds = 5)
    async def check(self):
        with open('./DataBase/Mute.json', 'r') as file: 
            data = json.load(file)

        guild = await self.bot.fetch_guild(861623322927038525) 

        if guild == None:
            return 

        role = guild.get_role(974083129121845309) 

        if (role == None) or (role not in guild.roles):
            return # Сегодня без роли ;-;

        for user, unmute_time in data.items():
            member = await guild.fetch_member(user) 

            if member == None:
                del data[user]

            if member in guild.members:
                if role not in member.roles:
                    try:
                        await member.add_roles(role)
                    except:
                        pass
                
            if datetime.now() > datetime.strptime(unmute_time, "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    await member.remove_roles(role)
                    
                    del data[user]
                except:
                    pass

        with open("./DataBase/Mute.json", 'w') as file: 
            json.dump(data, file)

# запуск лупа
    @check.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

# Mute
    @commands.guild_only()
    @commands.has_permissions(kick_members = True)
    @commands.command(name = "mute", aliases = ["Mute"])
    async def commadns_mut(self, ctx: commands.Context, member: typing.Optional[discord.Member] = None, duration: str = None, *, reason: str = 'Причина не указана') -> None:
        if member == None:
            return 

        if duration == None:
            return 

        if len(reason) > 401:
            return 
        
        unit = duration[-1]
        if unit not in ['s', 'm', 'h', 'd'] or not duration[:-1].isdigit():
            return
            
        try:
            if int(duration[:-1]) <= 10 and unit == 's': 
                return 
        except: 
            return 

        if unit == 's' and int(duration[:-1]) >= 61: 
            return
        elif unit == 'm' and int(duration[:-1]) >= 61: 
            return
        elif unit == 'h' and int(duration[:-1]) >= 25: 
            return
        elif unit == 'd' and int(duration[:-1]) >= 8:  
            return
        else:
            mutetime = int(duration[:-1])

        if member.id == self.bot.user.id: 
            return 
        if member == ctx.author: 
            return 
        if member.id == ctx.guild.owner.id: 
            return 
        if member.top_role >= ctx.author.top_role: 
            return 

        async def create_mute_role(guild: discord.Guild):
            try:
                role = await guild.create_role(name = "Mute") 

                for channel in guild.channels: 
                    await channel.set_permissions(role, overwrite = discord.PermissionOverwrite(send_messages = False, speak = False))

                return role
            except:
                return None

        if self.mute_id == None:
            role = await create_mute_role(ctx.guild)

            if role == None:
                return

            self.mute_id = role.id

        try:
            role = ctx.guild.get_role(self.mute_id)
        except:
            role = await create_mute_role(ctx.guild)

            if role == None:
                return

            self.mute_id = role.id

        if   unit == 's': 
            time = datetime.now() + timedelta(seconds = mutetime)
        elif unit == 'm': 
            time = datetime.now() + timedelta(minutes = mutetime)
        elif unit == 'h': 
            time = datetime.now() + timedelta(hours = mutetime)
        elif unit == 'd': 
            time = datetime.now() + timedelta(days = mutetime)

        await member.add_roles(role)

        with open("./DataBase/Mute.json", 'r') as file: 
            mute_data = json.load(file)
        
        mute_data[str(member.id)] = str(time)

        with open("./DataBase/Mute.json", 'w') as file: 
            json.dump(mute_data, file)

def setup(bot):
    bot.add_cog(Mute(bot))
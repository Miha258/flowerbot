
import discord
from discord.ext import tasks,commands
import sqlite3
import time
import asyncio
import datetime
from clock import Clock
import gifs
import random
import io
import json
import requests
from PIL import Image,ImageFont,ImageDraw
from dashboard import draw_progress
import pytz
from db import *

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '!',intents = intents)
bot.remove_command('help')
conection = sqlite3.connect('server.db')
cursor = conection.cursor()



@bot.event 
#shop system db on sqlite3
#add member to db
async def on_ready():
  print('Я готов!')
  create_tables()
  conection.commit()
  

  weekly_clear.start()
  pay.start()
  
  
  for guild in bot.guilds:
    for member in guild.members:
     if member.bot == False:
      if cursor.execute(f"SELECT id FROM serverss_db WHERE id = {member.id} ").fetchone() is None:
        cursor.execute(f'INSERT INTO serverss_db (name,id,cash,timess,when_climed,names) VALUES("{member}",{member.id},{0},{0},{0},"{member.display_name}")')
        conection.commit()
      
  for guild in bot.guilds:
    for member in guild.members:
     if member.bot == False:
      if cursor.execute(f"SELECT id FROM log WHERE id = {member.id}").fetchone() is None: 
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({member.id},'{time.asctime()}','🔵Инициализации счета')")
        conection.commit()
      
  for guild in bot.guilds:
   for member in guild.members:
    if member.bot == False:
     if cursor.execute(f"SELECT id FROM warninform WHERE id = {member.id}").fetchone() is None: 
       cursor.execute(f"INSERT INTO warninform (name,id,warns,type,reason,timess,admin) VALUES('{member}',{member.id},{0},'','','','')")
       conection.commit()
     
  for guild in bot.guilds:
   for member in guild.members:
    if member.bot == False:
     if cursor.execute(f"SELECT id FROM exp_system WHERE id = {member.id}").fetchone() is None: 
      cursor.execute(f"INSERT INTO exp_system (lvl,xp,id,when_xp) VALUES({1},{0},{member.id},{0})")
      conection.commit()
     
  
  for guild in bot.guilds:
   for member in guild.members:
    if member.bot == False:
     if cursor.execute(f"SELECT users FROM clans WHERE users = {member.id}").fetchone() is None:
      cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{member.id},{0},FALSE,0)")
      conection.commit()
     


  
  
         
@bot.event
async def on_command_error(ctx,error):
  if isinstance(error,discord.ext.commands.errors.MissingAnyRole):  
      await ctx.send(embed = discord.Embed(description = f'**⚙️У вас нет прав на использование команды {ctx.invoked_with}⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.errors.RoleNotFound):
      await ctx.send(embed = discord.Embed(description = '**⚙️Это должно быть участником а не ролью⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.CommandNotFound):
      await ctx.send(embed = discord.Embed(description = '**⚙️Команда не найдена⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.TooManyArguments):
    await ctx.send(embed = discord.Embed(description = '**⚙️В команде нет столько аргументов⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.MemberNotFound):
    await ctx.send(embed = discord.Embed(description = '**⚙️Такого участника нет на сервере⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.BadColourArgument):
    await ctx.send(embed = discord.Embed(description = '**⚙️Неправильно введен цвет⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.BotMissingPermissions):
    await ctx.send(embed = discord.Embed(description = '**⚙️У меня недостаточно прав⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.errors.MemberNotFound):
    await ctx.send(embed = discord.Embed(description = '**⚙️Участник не найден⚙️**',color = 0xff1111))
  elif isinstance(error,ValueError):
    await ctx.send(embed = discord.Embed(description = '**⚙️Неправильное значение для комды⚙️**',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.MissingRequiredArgument):
    await ctx.send(embed = discord.Embed(description = '**⚙️Вы пропустили важный параметер в команде⚙️',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.ChannelNotFound):
    await ctx.send(embed = discord.Embed(description = '⚙️Канал не найден⚙️',color = 0xff1111))
  elif isinstance(error,discord.ext.commands.MissingPermissions):
    await ctx.send(embed = discord.Embed(description = '⚙️Похоже что-то не так с моими правами⚙️',color = 0xff1111))
  





@bot.event
async def on_member_remove(member):
  cursor.execute(f'DELETE FROM serverss_db WHERE id = {member.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM log WHERE id = {member.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM warninform WHERE id = {member.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM exp_system WHERE id = {member.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM clans WHERE users = {member.id}')
  conection.commit()
  if cursor.execute(f"SELECT id FROM adminnsnff WHERE id = {member.id}").fetchone() is not None:
    cursor.execute(f'DELETE FROM adminnsnff WHERE id = {member.id}')
    conection.commit()
  log = await member.guild.audit_logs().flatten()
  if log[0].action == discord.AuditLogAction.kick:
     emb = discord.Embed(description=f'**{member}** был **кикнут**\n```fix',color =  0xab92e0)
     emb.set_footer(text = f'Выполнил(а) {log[0].user}', icon_url = log[0].user.avatar_url)
     channel = member.guild.get_channel(593822330631749646)
     await channel.send(embed = emb)
     
    
    
  
@bot.event
async def on_message(message):
  if message.author.bot is False:
    user_levl = cursor.execute(f"SELECT lvl FROM exp_system WHERE id = {message.author.id}").fetchone()[0]
    
    exp_for_levl = 0
    timely = 300
    claimed_in = cursor.execute(f"SELECT when_xp FROM exp_system WHERE id = {message.author.id}").fetchone()[0]
    now = time.time()
    has_gone = now - claimed_in
    if claimed_in == 0 or has_gone >= timely:
      if len(message.content) > 5:
        expi = random.randint(1,5)
        cursor.execute(f"UPDATE exp_system SET when_xp = {time.time()} WHERE id = {message.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE exp_system SET xp = xp + {expi} WHERE id = {message.author.id}")
        conection.commit()
        user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {message.author.id}").fetchone()[0] 
        exp_for_levl = 40 + (user_levl - 1) * 20
        if user_xp >= exp_for_levl:
          cursor.execute(f"UPDATE exp_system SET lvl = {user_levl + 1} WHERE id = {message.author.id}")
          conection.commit()
          cursor.execute(f"UPDATE exp_system SET xp = xp - {user_xp} WHERE id = {message.author.id}")
          conection.commit()
          await message.author.send(embed = discord.Embed(description = f'Вы достигли **{user_levl + 1} уровня**',color = 0xab92e0 ))
          
    await bot.process_commands(message)






@bot.event
async def on_member_ban(guild,user):
  channel = guild.get_channel(701908235627790453)
  log = await guild.audit_logs(action=discord.AuditLogAction.ban).flatten()
  embed = discord.Embed(description = f'({log[0].id}) {log[0].user.mention} забанил {log[0].target.mention}',color = 0xab92e0)
  if log[0].user.id != guild.me.id:
    if log[0].reason:
      embed.description = embed.description + f'\n``Причина:{log[0].reason}``'
  await channel.send(embed = embed)
  cursor.execute(f'DELETE FROM serverss_db WHERE id = {user.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM log WHERE id = {user.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM warninform WHERE id = {user.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM exp_system WHERE id = {user.id}')
  conection.commit()
  cursor.execute(f'DELETE FROM clans WHERE users = {user.id}')
  conection.commit()
  if cursor.execute(f"SELECT id FROM adminnsnff WHERE id = {user.id}").fetchone() != None:
    cursor.execute(f'DELETE FROM adminnsnff WHERE id = {user.id}')
    conection.commit()

@bot.event
async def on_member_unban(guild,user):
  channel = guild.get_channel(701908235627790453)
  log = await guild.audit_logs(action=discord.AuditLogAction.unban).flatten()
  if log[0].user.id != guild.me.id:
     await channel.send(embed = discord.Embed(description = f'({log[0].id}) {log[0].user.mention} разабанил {log[0].target.mention}',color = 0xab92e0))
  

@bot.event               
async def on_user_update(before, after):
  guild = discord.utils.get(bot.guilds,id = 717726165003010109)
  members = [member.id for member in guild.members]
  channel = discord.utils.get(guild.channels,id = 717726165003010109)
  if after.id in members:
    if after.avatar != before.avatar:
      embed = discord.Embed(color = 0xab92e0)
      embed.set_author(name = f'{after.name}#{after.discriminator} изменил аватар:',icon_url = after.avatar_url)
      embed.set_image(url = after.avatar_url)
      await channel.send(embed = embed)
    if after.name != before.name:
       embed = discord.Embed(color = 0xab92e0)
       embed.set_author(name = f'{before.name}#{before.discriminator} изменил ник: {after.name}',icon_url = after.avatar_url)
       await channel.send(embed = embed)

@bot.event
async def on_member_update(before,after):
  role = after.guild.get_role(701908235615076358)
  for member in before.guild.members:
    if cursor.execute(f"SELECT id FROM adminnsnff WHERE id = {member.id}").fetchone() is None:
      if role in member.roles: 
         cursor.execute(f"INSERT INTO adminnsnff (id,reports,mutes,warns,weekly_reports,weekly_mutes,weekly_warns,rating_pos,rating_neg) VALUES({member.id},{0},{0},{0},{0},{0},{0},{0},{0})")
         conection.commit()
    
  if cursor.execute(f"SELECT id FROM adminnsnff WHERE id = {member.id}").fetchone() is not None:
    if role not in member.roles:
      cursor.execute(f'DELETE FROM adminnsnff WHERE id = {member.id}')     
      conection.commit()  
  if before.nick != after.nick and after.nick:
    channel = after.guild.get_channel(717726165003010109)
    cursor.execute(f"INSERT INTO serverss_db (id,names) VALUES({member.id},'{after.nick}')")
    conection.commit()    
    embed = discord.Embed(color = 0xab92e0)
    embed.set_author(name = f'{before.name}#{before.discriminator} изменил на сервере ник: {after.name}',icon_url = after.avatar_url)
    await channel.send(embed = embed)
  if len(before.roles) < len(after.roles):
    log = await after.guild.audit_logs(action = discord.AuditLogAction.member_role_update).flatten()
    if log[0].user.id != after.guild.me.id:
      channel = after.guild.get_channel(728021862759530608)
      new_role = [role for role in after.roles if role not in before.roles]
      embed = discord.Embed(description = f'{log[0].user.mention} выдал роль {log[0].target.mention}: {new_role[0].mention}',color = 0xab92e0)
      await channel.send(embed = embed)
  if len(before.roles) > len(after.roles):
    log = await after.guild.audit_logs(action = discord.AuditLogAction.member_role_update).flatten()
    print(log[0].user.mention)
    if log[0].user.id != after.guild.me.id:
      channel = after.guild.get_channel(728021862759530608)
      new_role = [role for role in before.roles if role not in after.roles]
      embed = discord.Embed(description = f'{log[0].user.mention} убрал роль {log[0].target.mention}: {new_role[0].mention}',color = 0xab92e0)
      await channel.send(embed = embed)
  
  

@bot.event
#cash voice xp system
async def on_voice_state_update(member,before,after):
     counter = 0
     pay_time = 0
     everyone = discord.utils.get(member.guild.roles,name = '@everyone')
     private_channels = [discord.utils.get(member.guild.channels,id = x[0]) for x in cursor.execute(f"SELECT private_room FROM serverss_db")]
     channel = member.guild.get_channel(701908235627790452)  
     mute_role = discord.utils.get(member.guild.roles,name = 'MUTEHAMMERd')
     log = await member.guild.audit_logs().flatten()
     
     if not log[0].action == discord.AuditLogAction.member_update and member is not None:
       if mute_role not in member.roles and member.voice.mute:
          await member.edit(mute = False)
     
     if after.mute:
      log = await member.guild.audit_logs(action = discord.AuditLogAction.member_update).flatten()
      embed = discord.Embed(description = f'{log[0].user.mention} выключил микрофон {log[0].target.mention}',color = 0xab92e0)
      await channel.send(embed = embed)
     if not after.mute and before.mute:
      log = await member.guild.audit_logs(action = discord.AuditLogAction.member_update).flatten()
      embed = discord.Embed(description = f'{log[0].user.mention} включил микрофон {log[0].target.mention}',color = 0xab92e0)
      await channel.send(embed = embed)
     
     if after.channel is not None:
       if after.channel in private_channels:
         if len(after.channel.members) > 0:            
               await after.channel.set_permissions(everyone,view_channel = True,connect = False)
     if before.channel is not None:
       if before.channel in private_channels:
         if len(before.channel.members) == 0:
          
               await before.channel.set_permissions(everyone,view_channel = False,connect = False)
     
     while before.channel is None and after.channel is not None:
           if member.bot == False:
            user_levl = cursor.execute(f"SELECT lvl FROM exp_system WHERE id = {member.id}").fetchone()[0]
            exp_for_levl = 0
            await asyncio.sleep(1)
            counter += 1
            pay_time += 1  
           
            cursor.execute(f"UPDATE serverss_db SET timess = timess + {1} WHERE id = {member.id}")
            conection.commit()
            if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone()[0] == 1:
               clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0]
               cursor.execute(f"UPDATE clans SET voice_time = voice_time + {1} WHERE clan_id = {clan_id}")
               conection.commit()
            
            

            if pay_time > 300:
               cursor.execute(f"UPDATE exp_system SET xp = xp + {1} WHERE id = {member.id}")
               conection.commit()
               user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {member.id}").fetchone()[0] 
               
               pay_time -= 300
               exp_for_levl = 40 + (user_levl - 1) * 20



               if user_xp >= exp_for_levl:
                   cursor.execute(f"UPDATE exp_system SET lvl = {user_levl + 1} WHERE id = {member.id}")
                   conection.commit()

                   cursor.execute(f"UPDATE exp_system SET xp = xp - {user_xp} WHERE id = {member.id}")
                   conection.commit()
                   await member.send(embed = discord.Embed(description = f'Вы достигли **{user_levl + 1} уровня**',color = 0xab92e0))

            
            if counter > 120:
               counter -= 120
               cursor.execute(f"UPDATE serverss_db SET cash = cash + {1} WHERE id = {member.id}")
               conection.commit()
               
               if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone()[0] == 1: 
                clan_channel = cursor.execute(f"SELECT clan_channel_id FROM clans WHERE clan_id = {clan_id}").fetchone()[0]         
                clan_points = cursor.execute(f"SELECT clan_points FROM clans WHERE clan_id = {clan_id}").fetchone()[0] 
                clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
                points_for_lvl = 100000 + (clan_lvl - 1) * 10000
                if after.channel.id == clan_channel:
                   
                     cursor.execute(f"UPDATE clans SET clan_points = clan_points + 1 WHERE clan_id = {clan_id}")
                     conection.commit()
                     cursor.execute(f"UPDATE clans SET balance = balance + 2 WHERE users = {member.id}")
                     conection.commit()
                     
                     if clan_points >= points_for_lvl:
                      cursor.execute(f"UPDATE clans SET lvl = {clan_lvl + 1} WHERE clan_id = {clan_id}")
                      conection.commit()
                      cursor.execute(f"UPDATE clans SET clan_points = clan_points - {clan_points} WHERE clan_id = {clan_id}")
                      conection.commit()




 
#add to db when member joined to guild 
@bot.event
async def on_member_join(member):
    role = member.guild.get_role(701908235590041681)
    channel = member.guild.get_channel(703227582019272776)
    rules = member.guild.get_channel(701908236248547329)
    await member.add_roles(role)
    await channel.send(f'Добро пожаловать на сервер **{member.guild.name}**,{member.mention}.Обязательно прочитай {rules.mention}.')
    if member.bot == False:
      if cursor.execute(f"SELECT id FROM serverss_db WHERE id = {member.id} ").fetchone() is None:
          cursor.execute(f"INSERT INTO serverss_db (name,id,cash,timess,when_climed,names) VALUES('{member}',{member.id},{0},{0},{0},'{member.display_name}')")
          conection.commit()
      
    if member.bot == False:
      if cursor.execute(f"SELECT id FROM log WHERE id = {member.id}").fetchone() is None: 
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({member.id},'{time.asctime()}','🔵Инициализации счета')")
        conection.commit()
      
    if member.bot == False:
      if cursor.execute(f"SELECT id FROM warninform WHERE id = {member.id}").fetchone() is None: 
        cursor.execute(f"INSERT INTO warninform (name,id,warns,type,reason,timess,admin) VALUES('{member}',{member.id},{0},'','','','')")
        conection.commit()
      
    if member.bot == False:
      if cursor.execute(f"SELECT id FROM exp_system WHERE id = {member.id}").fetchone() is None: 
        cursor.execute(f"INSERT INTO exp_system (lvl,xp,id,when_xp) VALUES({1},{0},{member.id},{0})")
        conection.commit()
     
    if member.bot == False:
      if cursor.execute(f"SELECT users FROM clans WHERE users = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{member.id},{0},FALSE,0)")
        conection.commit()
       

@bot.event
async def on_guild_join(guild):
  def create_emoji(url):
    r = requests.get(url)
    return io.BytesIO(r.content).getvalue()
  muted_role = await guild.create_role(name = 'MUTEHAMMERd', permissions = discord.Permissions(1115136), colour = discord.Colour(0x5e5757))
  banned_role = await guild.create_role(name = 'BANHAMMERd', permissions = discord.Permissions(35840), colour = discord.Colour(0x5e5757))
  castom_role = await guild.create_role(name = '!мояроль')
  await guild.create_role(name = 'Clan leader')
  cursor.execute(f"INSERT INTO shops (guild_id,role_id,role_name,cost) VALUES ({guild.id},{castom_role.id},'!мояроль',{1000})")
  conection.commit()
  roles = [701908235615076355,701908235627790446]
  await guild.create_custom_emoji(name = 'mu', image = create_emoji('https://cdn.discordapp.com/attachments/593822330631749646/813794088792752148/765644783187394571.png',roles = [guild.get_role(role) for role in roles]))
  await guild.create_custom_emoji(name = 'un', image = create_emoji('https://cdn.discordapp.com/emojis/723865167846178857.png?v=1',roles = [guild.get_role(role) for role in roles]))
  await guild.create_custom_emoji(name = 'ban', image = create_emoji('https://cdn.discordapp.com/attachments/750791349518729236/834786482472222791/774999209862365214.png',roles = [guild.get_role(role) for role in roles]))
  await guild.create_custom_emoji(name = 'znak', image = create_emoji('https://cdn.discordapp.com/attachments/593822330631749646/776107767273488404/warned.png',roles = [guild.get_role(role) for role in roles]))
  await guild.create_custom_emoji(name = 'report', image = create_emoji('https://cdn.discordapp.com/attachments/593822330631749646/776107826375294996/699677378645065828.png',roles = [guild.get_role(role) for role in roles]))
                                                                        
  
  BANNED_CHANNEL = 701908235627790453
  if (guild.system_channel):
    channel = guild.system_channel
  else:
    channel = guild.text_channels[0]
  for i in guild.channels:
    await i.set_permissions(muted_role, add_reactions = False, speak = False, send_messages = False)
    if (i.id != BANNED_CHANNEL):
        await i.set_permissions(banned_role, add_reactions = False, read_messages = False, send_messages = False, connect = False, speak = False)
  await channel.send(embed = discord.Embed(
        description = f'**{guild.owner}**, я рад существовать на вашем сервере! Позвольте дать вам пару инструкций:\nЯ создал роли, которые нужны для мута и бана участников, поднимите её повыше в списке ролей и старайтесь не изменять их.\nПомощь по командам: !help',
        colour = 0xab92e0))
  
  
   

  for member in guild.members:
    girl_role = guild.get_role(701908235590041682)
    boy_role = guild.get_role(701908235590041681)
    if girl_role and boy_role not in member.roles:
      
      await member.add_roles(boy_role)

    
    
   
  for member in guild.members:
   if member.bot == False:
    if cursor.execute(f"SELECT id FROM serverss_db WHERE id = {member.id} ").fetchone() is None:
      cursor.execute(f"INSERT INTO serverss_db (name,id,cash,timess,when_climed,names) VALUES('{member}',{member.id},{0},{0},{0},'{member.display_name}')")
      conection.commit()
    
 
  for member in guild.members:
   if member.bot == False:
    if cursor.execute(f"SELECT id FROM log WHERE id = {member.id}").fetchone() is None: 
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({member.id},'{time.asctime()}','🔵Инициализации счета')")
      conection.commit()
 
  for member in guild.members:
   if member.bot == False:
    if cursor.execute(f"SELECT id FROM warninform WHERE id = {member.id}").fetchone() is None: 
      cursor.execute(f"INSERT INTO warninform (name,id,warns,type,reason,timess,admin) VALUES('{member}',{member.id},{0},'','','','')")
      conection.commit()

  for member in guild.members:
   if member.bot == False:
    if cursor.execute(f"SELECT id FROM exp_system WHERE id = {member.id}").fetchone() is None: 
      cursor.execute(f"INSERT INTO exp_system (lvl,xp,id,when_xp) VALUES({1},{0},{member.id},{0})")
      conection.commit()
   
  for member in guild.members:
   if member.bot == False:
    if cursor.execute(f"SELECT users FROM clans WHERE users = {member.id}").fetchone() is None:
      cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{member.id},{0},FALSE,0)")
      conection.commit()
    
   
  print('Я готов!')

@bot.event
async def on_guild_channel_create(channel):
        muted_role = discord.utils.get(channel.guild.roles,name = 'MUTEHAMMERd')
        banned_role = discord.utils.get(channel.guild.roles,name ='BANHAMMERd')
        await channel.set_permissions(banned_role, add_reactions = False, read_messages = False, send_messages = False, connect = False, speak = False)
        await channel.set_permissions(muted_role, add_reactions = False, speak = False, send_messages = False)

@tasks.loop(seconds = 1)
async def pay():
  
    for guild in bot.guilds:
      for member in guild.members:
        if cursor.execute(f"SELECT time_for_pay FROM clans WHERE clan_id = {member.id}").fetchone() is None:
          pass
        else:
         balance_user = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {member.id}").fetchone()[0]
         claimed_in = cursor.execute(f"SELECT time_for_pay FROM clans WHERE clan_id = {member.id}").fetchone()[0]
         now = int(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
         when_pay = int(claimed_in) + 2592000
        
         

         if now >= when_pay:
          cursor.execute(f"UPDATE clans SET has_payed = FALSE WHERE clan_id = {member.id}")
          conection.commit()
          
          if balance_user < 3000 and cursor.execute(f"SELECT has_payed FROM clans WHERE clan_id = {member.id}").fetchone()[0] == 0: 
          
            if cursor.execute(f"SELECT clan_cash FROM clans WHERE clan_id = {member.id}").fetchone()[0] < 3000:
              cursor.execute(f'DELETE FROM clans WHERE clan_id = {member.id}')
              conection.commit()
              cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited) VALUES(FALSE,FALSE,{member.id},{0},FALSE)")
              conection.commit()
              await member.send(embed = discord.Embed(description = f'Ваш клан удален за невыплату аренды',color = 0xff1111))
            else:
             if balance_user < 3000 and cursor.execute(f"SELECT has_payed FROM clans WHERE clan_id = {member.id}") == 0:
               cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 3000 WHERE clan_id = {member.id}")
               conection.commit()
             else:
               cursor.execute(f"UPDATE serverss_db SET cash = cash - 3000 WHERE clan_id = {member.id}")
               conection.commit()
               cursor.execute(f"UPDATE clans SET time_for_pay = time_for_pay + 2592000  WHERE clan_id = {member.id}") #2592000 
               conection.commit()
               cursor.execute(f"UPDATE clans SET str_time_for_pay = '{(datetime.datetime.today() + datetime.timedelta(days = 30)).strftime('%d.%m.%Y')}' WHERE clan_id = {member.id}")
               conection.commit()
               cursor.execute(f"UPDATE clans SET has_payed = TRUE WHERE clan_id = {member.id}")
               conection.commit()
               await member.send(embed = discord.Embed(description = f'Аренда продлена',color = 0xab92e0))

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def private_room(ctx,member:discord.Member = None,name:str = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника!',color = 0xff1111))
  elif name is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите название команаты',color = 0xff1111))
  else:
    category = discord.utils.get(ctx.guild.categories,id = 701908236453806127)
    voice = await category.create_voice_channel(name = name)
    everyone = discord.utils.get(ctx.guild.roles,name = '@everyone')
    cursor.execute(f"INSERT INTO serverss_db (id,private_room) VALUES({member.id},{voice.id})")
    conection.commit()
    await voice.set_permissions(everyone,view_channel = False,create_instant_invite = False)
    await voice.set_permissions(member,view_channel = True,create_instant_invite = True,mute_members = True,kick_members = True,connect = True)
    await ctx.send(embed = discord.Embed(description = f'Канал {voice.mention} успешно создан для {member.mention}',color = 0xab92e0))



@bot.command()
async def stats(ctx,member:discord.Member = None):
      
      await ctx.message.delete()
      member = ctx.author if not member else member
      
      async with ctx.typing():
        
        image = Image.new("RGBA", (800, 392), (0, 0, 0, 0))
        
        r = Image.open(io.BytesIO(await member.avatar_url.read())).convert('RGBA').resize((79, 79), Image.ANTIALIAS)
  
        image.paste(r, (14, 5, 93, 84))
 

        SEMIBOLD_8 = ImageFont.truetype("rankCardAssets/fonts/MONTSERRAT-SEMIBOLD.TTF", size = 45)
        SEMIBOLD_25 = ImageFont.truetype("rankCardAssets/fonts/MONTSERRAT-SEMIBOLD.TTF", size = 25)
        SEMIBOLD_15 = ImageFont.truetype("rankCardAssets/fonts/MONTSERRAT-SEMIBOLD.TTF", size = 17)
        THIN_30 = ImageFont.truetype("rankCardAssets/fonts/MONTSERRAT-THIN.TTF", size = 30)
        
        clan_name = None
        if cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0] is not None:
         if cursor.execute(f"SELECT clan_avatar_url FROM clans WHERE users = {member.id}").fetchone()[0] != ' ':
          clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0]
          clan_image_url = cursor.execute(f"SELECT clan_avatar_url FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
          clan_name = cursor.execute(f"SELECT clan_name FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
     
        # "скачивание" аватарки + ресайз
          
          if cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0] is not None: 
            clan_image = requests.get(clan_image_url,stream = True)
            clan_image = Image.open(io.BytesIO(clan_image.content)).convert('RGBA').resize((79, 79), Image.ANTIALIAS)
          
         
            image.paste(clan_image, (14,100,93,179))
        
        idraw = ImageDraw.Draw(image)
        all_voice_time = cursor.execute(f"SELECT timess FROM serverss_db WHERE id = {member.id}").fetchone()[0]
        user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {member.id}").fetchone()[0]
        user_levl = cursor.execute(f"SELECT lvl FROM exp_system WHERE id = {member.id}").fetchone()[0]
        

      
        

        exp_for_levl = 40 + (user_levl - 1) * 20
  
       
        # интерпретация данных о нахождении пользователя в войсе в вид: 00:00:00
        if all_voice_time >= 3600:
          hours = int(all_voice_time) / 3600
          d = int(hours) * 3600
          f = int(all_voice_time) - int(d)
          minutes = f / 60
          dd = int(minutes) * 60
          seconds = int(all_voice_time) - int(d) - int(dd)
        else:
          hours = 0
          minutes = int(all_voice_time) / 60
          d = int(minutes) * 60
          seconds = int(all_voice_time) - int(d)
        
        
        
        path = 'rankCardAssets/images/mainBackground.png'
        banner = Image.open(path).convert('RGBA')
        image.paste(banner, (0, 0, 800, 392), banner)
        
        
        if user_levl == 1:
          num = 75
        elif user_levl == 2:
          num = 55
        elif user_levl > 2 and user_levl < 11:
          num = 44
        elif user_levl > 11 and user_levl < 21:
            num = 42
        else:
          num = 41

        
        percent = round(2 * (user_xp/(((user_levl + num) - user_levl)* user_levl/100)))
        draw_progress(image,percent)
        
        path = 'rankCardAssets/images/progressBarBackground.png'
        progress_bar_line = Image.open(path).convert('RGBA')
        progress_bar_line.putalpha(128)
        banner.paste(progress_bar_line, (315,270)) #429,78
        
        
       
        
        # получение информации о пользователе

        name = member.name
        tag = member.discriminator
        
      
        idraw.text((110, 13), f'{name}#{tag}', font = SEMIBOLD_8)
        idraw.text((110, 110), 'Не в клане' if clan_name is None else clan_name, font = SEMIBOLD_8)
        idraw.text((33, 227), f'{user_levl}', font = SEMIBOLD_25)
        # idraw.text((159, 243), f'{rank}', font = SEMIBOLD_25)
        idraw.text((35, 301), f'{int(hours)}h {int(minutes)}m {int(seconds)}s', font = SEMIBOLD_15)
        # idraw.text((159, 315), f'{voiceRank}', font = SEMIBOLD_25)
        idraw.text((41, 357), f'{ctx.author.joined_at.strftime("%d.%m.%y %H:%M")}', font = SEMIBOLD_25)
        idraw.text((311, 241), f'{user_xp}/{exp_for_levl}', font = SEMIBOLD_25)
       

        # сохранение и отправка готовой карточки
        image.save('rankCards/rankCard.png')
        await ctx.send(file = discord.File(fp = 'rankCards/rankCard.png'))




           
          
         

@tasks.loop(hours = 168)
async def weekly_clear():
   for x in cursor.execute(f"SELECT weekly_reports,id,weekly_mutes,weekly_warns FROM adminnsnff").fetchall():
      cursor.execute("UPDATE adminnsnff SET weekly_reports = weekly_reports - {} WHERE id = {}".format(x[0],x[1]))
      conection.commit()
      cursor.execute("UPDATE adminnsnff SET weekly_mutes = weekly_mutes - {} WHERE id = {}".format(x[2],x[1]))
      conection.commit()
      cursor.execute("UPDATE adminnsnff SET weekly_warns = weekly_warns - {} WHERE id = {}".format(x[3],x[1]))
      conection.commit()

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def xp_give(ctx,member:discord.Member = None,amouth:int = None):
   await ctx.message.delete()
   if member is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
    
   elif amouth is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите суму exp',color = 0xff1111))
   else:
        user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
        user_levl = cursor.execute(f"SELECT lvl FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
        exp_for_levl = 40 + (user_levl - 1) * 20
        if user_xp + amouth > exp_for_levl:
          await ctx.send(embed = discord.Embed(description = f'Задайте меньшую сумму exp',color = 0xff1111))
        else:
          cursor.execute("UPDATE exp_system SET xp = xp + {} WHERE id = {}".format(amouth,member.id))
          conection.commit()
          if exp_for_levl == user_xp:
            cursor.execute("UPDATE exp_system SET lvl = lvl + {} WHERE id = {}".format(1,member.id))
            conection.commit()

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def xp_take(ctx,member:discord.Member = None,amouth:int = None):
   await ctx.message.delete()
   
   if member is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
    
   elif amouth is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите суму exp',color = 0xff1111))
   else:  
        user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
        if user_xp < user_xp + amouth:
          await ctx.send(embed = discord.Embed(description = f'Задайте меньшую сумму exp',color = 0xff1111))
        else:
          cursor.execute("UPDATE exp_system SET xp = xp - {} WHERE id = {}".format(amouth,member.id))
          conection.commit()

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def lvl_give(ctx,member:discord.Member = None,amouth:int = None):
      await ctx.message.delete()
      if member is None:
          await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
      else:
          user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
          cursor.execute("UPDATE exp_system SET lvl = lvl + {} WHERE id = {}".format(amouth,member.id))
          conection.commit()
          await member.send(embed = discord.Embed(description = f'Вам дали {amouth} уровней',colour = 0xab92e0))    
          cursor.execute("UPDATE exp_system SET xp = xp + {} WHERE id = {}".format(user_xp,member.id))
          conection.commit()

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def lvl_take(ctx,member:discord.Member = None,amouth:int = None):
         await ctx.message.delete()
         user_levl = cursor.execute(f"SELECT lvl FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
         if member is None:
          await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
         else:
          if user_levl == 1:
             await ctx.send(embed = discord.Embed(description = f'У **{member}** уже 1 уровень',color = 0xff1111))
          elif user_levl < amouth:
             await ctx.send(embed = discord.Embed(description = f'Укажите меньше уровней',color = 0xff1111))
          else:
            user_xp = cursor.execute(f"SELECT xp FROM exp_system WHERE id = {ctx.author.id}").fetchone()[0]
            cursor.execute("UPDATE exp_system SET lvl = lvl - {} WHERE id = {}".format(amouth,member.id))
            conection.commit()
            await member.send(embed = discord.Embed(description = f'У вас забрали {amouth} уровней',colour = 0xab92e0))
            cursor.execute("UPDATE exp_system SET xp = xp - {} WHERE id = {}".format(user_xp,member.id))
            conection.commit()

#clans
@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def create_clan(ctx,member:discord.Member = None,role_color:discord.Colour = None,*,clan_name:str = None,):
  await ctx.message.delete()
  if clan_name is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите имя клана',color = 0xff1111))
  elif member is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите лидера клана',color = 0xff1111))
  elif role_color is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите цвет клана (hex)',color = 0xff1111))
  else:
      roles = []
      roles = [roles.append(role.name) for role in ctx.guild.roles]
      if cursor.execute(f"SELECT have_clan FROM clans WHERE users = {member.id}").fetchone() == 1:
        await ctx.send(embed = discord.Embed(description = f'У **{member}** уже есть свой клан',colour = 0xff1111))
      elif clan_name in ctx.guild.roles:
        await ctx.send(embed = discord.Embed(description = f'Клан с таким именем уже существует',color = 0xff1111))
      elif cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone() == 1:
        await ctx.send(embed = discord.Embed(description = f'**{member}** уже в клане ',colour = 0xff1111))                                                                                                                                      # clan_members INT,
      else:                                                                                             
        clan_leader = discord.utils.get(ctx.guild.roles,name = 'Clan leader')
        clan_role = await ctx.guild.create_role(name = clan_name,colour = role_color)
        category_for_voice = discord.utils.get(ctx.guild.categories,id = 703258294155870219)
        category_for_text = discord.utils.get(ctx.guild.categories,id = 797068569191514112)
        clan_voice = await category_for_voice.create_voice_channel(name = clan_name)
        clan_text = await category_for_text.create_text_channel(name = clan_name)
        everyone = discord.utils.get(ctx.guild.roles,name = '@everyone')
        await clan_voice.set_permissions(member,connect = True,mute_members = True,move_members = True)
        await clan_voice.set_permissions(clan_role,connect = True)
        await clan_voice.set_permissions(everyone,connect = False)
        await clan_text.set_permissions(member,send_messages = True,manage_webhooks = True,manage_messages = True)
        await clan_text.set_permissions(clan_role,send_messages = True)
        await clan_text.set_permissions(everyone,send_messages = False)
        await member.add_roles(clan_leader,clan_role)

        balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {member.id}").fetchone()[0]
        cursor.execute(f'DELETE FROM clans WHERE users = {member.id}')
        conection.commit()
        cursor.execute(f"INSERT INTO clans (clan_name,clan_owner,clan_id,clan_members,clan_channel_id,clan_text_channel_id,str_time_for_pay,clan_role_id,clan_slots,time_for_pay,when_created,clan_img_url,clan_avatar_url,clan_description,channels,clan_points,has_payed,clan_cash,users,have_clan,in_clan,lvl,balance,voice_time) VALUES ('{clan_name}','{member}',{member.id},1,{clan_voice.id},{clan_text.id},'{(datetime.datetime.today() + datetime.timedelta(days = 30)).strftime('%d.%m.%Y')}',{clan_role.id},{6},{int((datetime.datetime.today()).strftime('%Y%m%d%H%M%S'))},'{datetime.datetime.today().strftime('%d.%m.%Y')}',' ',' ',' ',{clan_voice.id},0,FALSE,0,{member.id},TRUE,TRUE,1,{balance},0)")
        conection.commit()



@bot.command()
async def clan_invite(ctx,member:discord.Member = None):
    await ctx.message.delete()
    if member is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
    elif ctx.author.id == member.id:
      await ctx.send(embed = discord.Embed(description = 'Операция невозможна (',colour = 0xff1111)) 
    else:
      if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone()[0] == 1: 
         await ctx.send(embed = discord.Embed(description = 'Этот участник в другом клане',colour = 0xff1111))
      elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
         await ctx.send(embed = discord.Embed(description = 'Вы не обладатель клана',colour = 0xff1111))
      elif cursor.execute(f"SELECT clan_slots FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0] == cursor.execute(f"SELECT clan_members FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]:
         await ctx.send(embed = discord.Embed(description = 'В клане недостаточно места',colour = 0xff1111))
      elif cursor.execute(f"SELECT has_invited FROM clans WHERE users = {member.id}").fetchone()[0] == 1:
         await ctx.send(embed = discord.Embed(description = 'Этот участник уже приглашен',colour = 0xff1111))
      else:
        clan = cursor.execute(f"SELECT clan_name FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
        msg = await member.send(embed = discord.Embed(description=f'Вы приглашены в клан **{clan}**',color = 0xab92e0))
        await msg.add_reaction('✅')
        await msg.add_reaction('❎')
        def check(reaction, user):
            conditions = [
                str(reaction.emoji) in '✅❎',
                user != ctx.guild.me,
                reaction.me == True,
                msg.id == reaction.message.id]   
            return all(conditions)
        chosen_green = False
        cursor.execute(f"UPDATE clans SET has_invited = TRUE WHERE users = {member.id}")
        conection.commit()
        while chosen_green is False:
              try:
                rea, usr= await bot.wait_for('reaction_add',check = check,timeout = 600)
                if (str(rea.emoji) == '✅'):
                        embed = msg.embeds[0]
                        embed.colour = 0x33fd13
                        embed.description = f'Вы приняли приглашение в клан **{clan}**'
                        avatar_url = cursor.execute(f"SELECT clan_avatar_url FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
                        balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {usr.id}").fetchone()[0]
                        cursor.execute(f'DELETE FROM clans WHERE users = {usr.id}')
                        conection.commit()
                        cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,clan_id,clan_avatar_url,balance) VALUES(TRUE,FALSE,{usr.id},{0},FALSE,{ctx.author.id},'{avatar_url}',{balance})")
                        conection.commit()
                        cursor.execute(f"UPDATE clans SET clan_members = clan_members + 1 WHERE clan_id = {ctx.author.id}")
                        conection.commit()                        
                        clan_role = cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
                        
                        await member.add_roles(ctx.guild.get_role(clan_role))
                        await msg.edit(embed = embed)
                
                        chosen_green = True
                                
                elif (str(rea.emoji) == '❎'):              
                          embed = msg.embeds[0]
                          embed.colour = 0xfd3313
                          embed.description = f'Вы отклонили приглашение в клан **{clan}**'
                          await msg.edit(embed = embed)
                          break
        
              except asyncio.TimeoutError:
                embed.description = f'Приглашение не действительно'
                embed.colour = 0xfd3313
                cursor.execute(f"UPDATE clans SET has_invited = FALSE WHERE users = {member.id}")
                conection.commit()
                await msg.edit(embed = embed)
        await asyncio.sleep(60*5)
        cursor.execute(f"UPDATE clans SET has_invited = FALSE WHERE users = {member.id}")
        conection.commit()

@bot.command()
async def clan_info(ctx,member:discord.Member = None):
    await ctx.message.delete()
    member = ctx.author if not member else member
    if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone()[0] == 0:
          await ctx.send(embed = discord.Embed(description = f'**{member}** не участник клана',colour = 0xff1111)) 
    else:
        clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0]
        clan_name = cursor.execute(f"SELECT clan_name FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_owner = cursor.execute(f"SELECT clan_owner FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        members = cursor.execute(f"SELECT clan_members FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_slots = cursor.execute(f"SELECT clan_slots FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_created_at = cursor.execute(f"SELECT when_created FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        time_for_pay = cursor.execute(f"SELECT str_time_for_pay FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        avatar = cursor.execute(f"SELECT clan_avatar_url FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_description = cursor.execute(f"SELECT clan_description FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        img = cursor.execute(f"SELECT clan_img_url FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_points = cursor.execute(f"SELECT clan_points FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_balance = cursor.execute(f"SELECT clan_cash FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
        clan_role =  cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
      
        
        embed = discord.Embed(title = f':flag_black: Клан: {clan_name}',description = clan_description,color = ctx.guild.get_role(clan_role).color)
        embed.add_field(name = 'Владелец',value = f'**{clan_owner}**',inline = True)
        embed.add_field(name = 'Роль:',value = f'**{ctx.guild.get_role(clan_role).mention}**',inline = True)
        embed.add_field(name = '** **',value = f'** **',inline = False)
        embed.add_field(name = 'Уровень',value = f'```fix\n{lvl}\n```',inline = True)
        embed.add_field(name = 'Очки:',value = f'```py\n{clan_points}\n```',inline = True)
        embed.add_field(name = '** **',value = f'** **',inline = False)
        embed.add_field(name = 'Участники',value = f'**{members}/{clan_slots}**',inline = True)
        embed.add_field(name = 'Клановый баланс:',value = f'{clan_balance} :cherry_blossom:',inline = True)
        embed.add_field(name = '** **',value = f'** **',inline = False)
        embed.add_field(name = 'Дата создания:',value = f'**{clan_created_at}**',inline = True)
        embed.add_field(name = 'Продлен до:',value = f'**{time_for_pay}**',inline = True)
        
        if avatar is not None:
          embed.set_thumbnail(url = avatar) 
        if img is not None:
          embed.set_image(url = img)
        await ctx.send(embed = embed)


@bot.command()
async def set_clan_avatar(ctx,url:str = None): 
  await ctx.message.delete()
  if url is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите ссылку',color = 0xff1111))
  elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  else:
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
    if clan_lvl < 2:
      await ctx.send(embed = discord.Embed(description = 'Доступно с 2 левела клана',color = 0xff1111))
    else:
      if cursor.execute(f"SELECT clan_cash FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < 3000:
        await ctx.send(embed = discord.Embed(description = 'На клановом балансе недостаточно средств',color = 0xff1111))
      else:
        cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 3000 WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE clans SET clan_avatar_url = '{url}' WHERE clan_id = {ctx.author.id}")
        conection.commit()

@bot.command()
async def change_clan_color(ctx,color:discord.Color = None): 
  await ctx.message.delete()
  if color is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите цвет hex',color = 0xff1111))
  elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  else:
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
    if clan_lvl < 3:
      await ctx.send(embed = discord.Embed(description = 'Доступно с 3 левела клана',color = 0xff1111))
    else:
      if cursor.execute(f"SELECT clan_cash FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < 5000:
        await ctx.send(embed = discord.Embed(description = 'На клановом балансе недостаточно средств',color = 0xff1111))
      else:
        role = cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
        role = ctx.guild.get_role(role)
        cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 5000 WHERE clan_id = {ctx.author.id}")
        conection.commit()
        await role.edit(colour = color)

      
@bot.command()
async def set_clan_name(ctx,name:str = None): 
  await ctx.message.delete()
 
  roles = []
  roles = [roles.append(role.name) for role in ctx.guild.roles]
  if name is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите имя клана',color = 0xff1111))
  elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  else:
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
    if clan_lvl < 3:
      await ctx.send(embed = discord.Embed(description = 'Доступно с 3 левела клана',color = 0xff1111))
    else:
      if cursor.execute(f"SELECT clan_cash FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < 5000:
        await ctx.send(embed = discord.Embed(description = 'На клановом балансе недостаточно средств',color = 0xff1111))
      elif name in roles:
        await ctx.send(embed = discord.Embed(description = f'Клан с таким именем уже существует',color = 0xff1111))
      else:
        cursor.execute(f"UPDATE clans SET clan_name = '{name}' WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 5000 WHERE clan_id = {ctx.author.id}")
        conection.commit()
        category = discord.utils.get(ctx.guild.categories,id = 797383476411760651)
        voice_channel = ctx.guild.get_channel(cursor.execute(f"SELECT clan_channel_id FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0])
        text_channel = ctx.guild.get_channel(cursor.execute(f"SELECT clan_text_channel_id FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0])
        clan_role = ctx.guild.get_role(cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0])
        await clan_role.edit(name = name)
        await voice_channel.edit(name = name)
        await text_channel.edit(name = name)
       
        


@bot.command()
async def set_clan_banner(ctx,url:str = None): 
  await ctx.message.delete()
  if url is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите ссылку',color = 0xff1111))
  elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  else:
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
    if clan_lvl < 4:
      await ctx.send(embed = discord.Embed(description = 'Доступно с 4 левела клана',color = 0xff1111))
    else:
      if cursor.execute(f"SELECT clan_cash FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < 7000:
        await ctx.send(embed = discord.Embed(description = 'На клановом балансе недостаточно средств',color = 0xff1111))
      else:
        cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 7000 WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE clans SET clan_img_url = '{url}' WHERE clan_id = {ctx.author.id}")
        conection.commit()







@bot.command()
async def set_clan_description(ctx,*,text:str = None): 
  await ctx.message.delete()
  
  if text is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите текст',color = 0xff1111))
  elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  else:
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0]
    if clan_lvl < 2:
      await ctx.send(embed = discord.Embed(description = 'Доступно с 2 левела клана',color = 0xff1111))
    
    else:
      if cursor.execute(f"SELECT clan_cash FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < 3000:
          await ctx.send(embed = discord.Embed(description = 'На клановом балансе недостаточно средств',color = 0xff1111))
      else:
        cursor.execute(f"UPDATE clans SET clan_description = '{text}' WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - 3000 WHERE clan_id = {ctx.author.id}")
        conection.commit()


@bot.command()
async def pay_for_clan(ctx):
  balance_user = cursor.execute(f"SELECT balance FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
  await ctx.message.delete()
  if cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
    await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',colour = 0xff1111))
  elif cursor.execute(f"SELECT has_payed FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0] == 1:
    await ctx.send(embed = discord.Embed(description = 'Аренда уже оплачена',colour = 0xff1111))
  else:
    if balance_user < 3000:
      await ctx.send(embed = discord.Embed(description = 'У вас недостаточно средств на балансе',colour = 0xff1111))
    else:
        cursor.execute(f"UPDATE clans SET has_payed = TRUE WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE clans SET balance = balance - 3000 WHERE clan_id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','⚪️Оплатил аренду клана (3000 :cherry_blossom: )')")
        conection.commit()
@bot.command()
async def clan_award(ctx,amouth:int = None):
  await ctx.message.delete()
  if amouth is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
  else:
    if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Вы не в клане',color = 0xff1111))
    elif cursor.execute(f"SELECT balance FROM clans WHERE users = {ctx.author.id}").fetchone()[0] < amouth:
       await ctx.send(embed = discord.Embed(description = 'У вас нет столько денег',color = 0xff1111))
    else:
      clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
      cursor.execute(f"UPDATE clans SET balance = balance - {amouth} WHERE users = {ctx.author.id}")
      conection.commit()
      cursor.execute(f"UPDATE clans SET clan_cash = clan_cash + {amouth} WHERE clan_id = {clan_id}")
      conection.commit()
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','⚪️Пополнил клановый баланс на {amouth} :cherry_blossom: ')")
      conection.commit() 
      
      await ctx.send(embed = discord.Embed(description = 'Транзакция прошла успешно',color = 0xab92e0))

@bot.command()
async def clan_take(ctx,amouth:int = None):
  await ctx.message.delete()
  if amouth is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
  else:
    if cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',color = 0xff1111))
    elif cursor.execute(f"SELECT clan_cash FROM clans WHERE clan_id = {ctx.author.id}").fetchone()[0] < amouth:
       await ctx.send(embed = discord.Embed(description = 'В клане нет столько денег',color = 0xff1111))
    else:
      clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
      cursor.execute(f"UPDATE clans SET balance = balance + {amouth} WHERE users = {ctx.author.id}")
      conection.commit()
      cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - {amouth} WHERE clan_id = {clan_id}")
      conection.commit()
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','⚪️Снял деньги с клановой казны({amouth} :cherry_blossom: )')")
      conection.commit() 
      await ctx.send(embed = discord.Embed(description = f'Транзакция прошла успешно',color = 0xab92e0))

@bot.command()
async def clan_leave(ctx):
  await ctx.message.delete()
  
  if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Вы не в клане',color = 0xff1111))
  else:
    clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
    if cursor.execute(f"SELECT clan_members FROM clans WHERE clan_id = {clan_id}").fetchone()[0] == 1:
      for member in cursor.execute(f"SELECT users FROM clans WHERE clan_id = {clan_id}").fetchall():
        member = bot.get_user(member[0])
        await member.send(embed = discord.Embed(description = f'Ваш клан удалили',color = 0xab92e0))
        balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
        cursor.execute(f'DELETE FROM clans WHERE users = {member.id}')
        conection.commit()
        cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{member.id},{0},FALSE,{balance})")
        conection.commit()
      await ctx.send(embed = discord.Embed(description = 'Вы покинули свой клан,но теперь он удален, потому что вы были последним участником',color = 0xab92e0))
       
    else:
      balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
      cursor.execute(f'DELETE FROM clans WHERE users = {ctx.author.id}')
      conection.commit()
      cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{ctx.author.id},{0},FALSE,{balance})")
      conection.commit()
      cursor.execute(f"UPDATE clans SET clan_members = clan_members - 1 WHERE clan_id = {clan_id}")
      conection.commit()
      await ctx.author.send(embed = discord.Embed(description = 'Вы покинули свой клан',color = 0xab92e0))
@bot.command()
async def clan_kick(ctx,member:discord.Member = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))

  else:
   if member.id == ctx.author.id:
    await ctx.send(embed = discord.Embed(description = f'Вы не можете выгнать самого себя',color = 0xff1111))
   elif cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',color = 0xff1111))
   elif cursor.execute(f"SELECT in_clan FROM clans WHERE users = {member.id}").fetchone() == 0:
      await ctx.send(embed = discord.Embed(description = 'Участник не в клане',color = 0xff1111))
   elif cursor.execute(f"SELECT clan_id FROM clans WHERE users = {member.id}").fetchone()[0] != ctx.author.id:
      await ctx.send(embed = discord.Embed(description = 'Участник не в вашем клане',color = 0xff1111))
   else:
     cursor.execute(f"UPDATE clans SET in_clan = FALSE WHERE users = {member.id}")
     conection.commit()
     cursor.execute(f"UPDATE clans SET clan_id = NULL WHERE users = {member.id}")
     conection.commit()
     cursor.execute(f"UPDATE clans SET clan_members = clan_members - 1 WHERE clan_id = {ctx.author.id}")
     conection.commit()
     await ctx.send(embed = discord.Embed(description = f'Вы выгнали **{member}**',color = 0xab92e0))
     await member.send(embed = discord.Embed(description = f'Вас выгнали из клана',color = 0xab92e0))


@bot.command()
async def buy_slots(ctx,amouth:int = None):
  await ctx.message.delete()
  if amouth is None:
      await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
  else:
    cost = amouth * 2000
    clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
    if cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = 'Вы не лидер клана',color = 0xff1111))
    elif cursor.execute(f"SELECT clan_cash FROM clans WHERE clan_id = {clan_id}").fetchone()[0] < cost:
         await ctx.send(embed = discord.Embed(description = 'У вас недостаточно средств',color = 0xff1111))
    else:
      cursor.execute(f"UPDATE clans SET clan_cash = clan_cash - {cost} WHERE users = {ctx.author.id}")
      conection.commit()
      cursor.execute(f"UPDATE clans SET clan_slots = clan_slots + {amouth} WHERE clan_id = {ctx.author.id}")
      conection.commit()
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','⚪️Купил {ctx.author} слотов на **{cost}** :cherry_blossom: ')")
      conection.commit()
      await ctx.send(embed = discord.Embed(description = f'Вы купили {amouth} слотов для клана',color = 0xab92e0))


@bot.command()
async def clan_shop(ctx):
  await ctx.message.delete()
  if cursor.execute(f"SELECT in_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Вы не в клане',color = 0xff1111))
  else:
    clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE users = {ctx.author.id}").fetchone()[0]
    clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE users = {clan_id}").fetchone()[0]

    if clan_lvl < 2: 
      await ctx.send(embed = discord.Embed(description = 'Клановый магазин работает с 2 левела',color = 0xff1111))
    else:
     embed = discord.Embed(title = 'Клановый магазин',color = discord.Color.purple(),description = 'Возможности:')
     embed.insert_field_at(index = 0,name  = '** **',value = '~~🔒Купить слоты🔒\n🔒Сменить аватарку клана🔒\n🔒Описание клана🔒~~',inline = False)
     embed.insert_field_at(index = 1,name  = '** **',value = '~~🔒Изменить название клана🔒\n🔒Изменить цвет клана🔒~~',inline = False)
     embed.insert_field_at(index = 2,name  = '** **',value = '~~🔒Поставить аватарку клана🔒~~',inline = False)
  
     if clan_lvl >= 2:
       embed.remove_field(0)
       embed.insert_field_at(index = 0,name  = '** **',value = '**Купить слоты(2000 :cherry_blossom:)\nАватарку клана(3000 :cherry_blossom:)\nОписание клана(3000 :cherry_blossom:)**',inline = False)
       
     if clan_lvl >= 3:
       embed.remove_field(1)
       embed.insert_field_at(index = 1,name  = '** **',value = '**Изменить название клана(5000 :cherry_blossom:)\nИзменить цвет клана(5000 :cherry_blossom:)**',inline = False)
     
     if clan_lvl >= 4:
       embed.remove_field(2)
       embed.insert_field_at(index = 2,name  = '** **',value = '**Поставить аватарку клана(7000 :cherry_blossom:)**',inline = False)


     
     await ctx.send(embed = embed)

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def give_clan_lvl(ctx,clan_id:int = None,amouth:int = None):
    if clan_id is None:
       await ctx.send(embed = discord.Embed(description = 'Укажите айди клана',color = 0xff1111))
    elif amouth is None:
       await ctx.send(embed = discord.Embed(description = 'Укажите количество уровнейь',color = 0xff1111))
    else:
      clan_name = cursor.execute(f"SELECT clan_name FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({clan_id},'{time.asctime()}','🔘Администратор **{ctx.author}** выдал **{amouth}** уровней для клана **{clan_name}**')")
      conection.commit()
      cursor.execute(f"UPDATE clans SET lvl = lvl + 1 WHERE clan_id = {clan_id}")
      conection.commit()
      await ctx.send(embed = discord.Embed(description = f'Вы успешно выдали клановый уровень для **{clan_name}**',color = 0xff1111))


@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def take_clan_lvl(ctx,clan_id:int = None,amouth:int = None):
    if clan_id is None:
       await ctx.send(embed = discord.Embed(description = 'Укажите айди клана',color = 0xff1111))
    elif amouth is None:
       await ctx.send(embed = discord.Embed(description = 'Укажите количество уровнейь',color = 0xff1111))
    else:
      if cursor.execute(f"SELECT have_clan FROM clans WHERE users = {ctx.author.id}").fetchone()[0] == 0:
        await ctx.send(embed = discord.Embed(description = f'**{ctx.guild.get_member(clan_id).name}** не лидер клана',color = 0xff1111))
      else:
        clan_lvl = cursor.execute(f"SELECT lvl FROM clans WHERE users = {clan_id}").fetchone()[0]
        if clan_lvl == 1:
          await ctx.send(embed = discord.Embed(description = f'У этого клана уже 1 уровень',color = 0xff1111))
        elif clan_lvl < amouth:
          await ctx.send(embed = discord.Embed(description = f'Укажите меньше уровней',color = 0xff1111))   
        else:
          clan_name = cursor.execute(f"SELECT clan_name FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
          cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({clan_id},'{time.asctime()}','🔘Администратор **{ctx.author}** забрал **{amouth}** уровней у клана **{clan_name}**')")
          conection.commit()
          cursor.execute(f"UPDATE clans SET lvl = lvl + 1 WHERE clan_id = {clan_id}")
          conection.commit()
          await ctx.send(embed = discord.Embed(description = f'Вы успешно выдали клановый уровень для **{clan_name}**',color = 0xff1111))


@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def clan_member_award(ctx,member:discord.Member = None,amouth:int = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника!',color = 0xff1111))
  elif amouth is None:
      await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
  else:
    cursor.execute(f"UPDATE clans SET balance = balance + {amouth} WHERE users = {ctx.author.id}")
    conection.commit()
    cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({member.id},'{time.asctime()}','🔘Администратор **{ctx.author}** пополнил клановый баланс на **{amouth}** :cherry_blossom: ')")
    conection.commit()
    await ctx.send(embed = discord.Embed(description = f'Клановый баланс **{member}** успешно пополнен ',color = 0xab92e0))

@commands.has_any_role(701908235615076355,701908235627790446)
@bot.command()
async def clan_member_take(ctx,member:discord.Member = None,amouth:int = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника!',color = 0xff1111))
  elif amouth is None:
      await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
  else:
    if cursor.execute(f"SELECT balance FROM clans WHERE users = {member.id}").fetchone()[0] < amouth:
       await ctx.send(embed = discord.Embed(description = 'У этого участника не имеет столько денег',color = 0xff1111))
      
    else:
      cursor.execute(f"UPDATE clans SET balance = balance - {amouth} WHERE users = {ctx.author.id}")
      conection.commit()
      cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','⚫️Администратор **{ctx.author}** снял с кланового баланса **{amouth}** :cherry_blossom: ')")
      conection.commit()
      await ctx.send(embed = discord.Embed(description = f'С кланового баланса **{member}** баланса было снято **{amouth}** :cherry_blossom:',color = 0xab92e0))
    

@bot.command()
async def convert(ctx,amouth:int = None):
 await ctx.message.delete()
 if amouth is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите суму денег',color = 0xff1111))
 else:
  if cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0] < amouth:
       await ctx.send(embed = discord.Embed(description = 'У вас нет столько денег',color = 0xff1111))
  else:
    cursor.execute(f"UPDATE serverss_db SET cash = cash - {amouth} WHERE id = {ctx.author.id}")
    conection.commit()
    cursor.execute(f"UPDATE clans SET balance = balance + {amouth} WHERE users = {ctx.author.id}")
    conection.commit()
    await ctx.send(embed = discord.Embed(description = 'Баланс успешно конвертирован',color = 0xab92e0))

@bot.command(name = 'clan$')
async def clan_balance(ctx,member:discord.Member = None):
  await ctx.message.delete()
  member = ctx.author if member is None else member  
  balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {member.id}").fetchone()[0]
  await ctx.send(embed = discord.Embed(description = f'Клановый баланс **{member}** составляет **{balance} :cherry_blossom: **',color = 0xab92e0))




@bot.command()
async def names(ctx,member:discord.Member = None):
  await ctx.message.delete()
  embed = discord.Embed(title = f'Никнеймы {member}:',color = discord.Colour.purple())
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника!',color = 0xff1111))
  for name in cursor.execute(f"SELECT names FROM serverss_db WHERE id = {member.id}").fetchall():
     embed.add_field(name = name[0],value = '** **',inline = False)
  await ctx.send(embed = embed)

@commands.has_any_role(701908235615076355,701908235627790446)  
@bot.command()
async def del_clan(ctx,role:discord.Role = None):
  await ctx.message.delete()
  clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE clan_role_id = {role.id}").fetchone()[0]
  if role is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите роль',color = 0xff1111))
  else:
    if cursor.execute(f"SELECT have_clan FROM clans WHERE clan_id = {clan_id}").fetchone()[0] == 0:
      await ctx.send(embed = discord.Embed(description = 'Этот участник не лидер клана',color = 0xff1111))
    else:
      clan_id = cursor.execute(f"SELECT clan_id FROM clans WHERE clan_role_id = {role.id}").fetchone()[0]
      text_channel = cursor.execute(f"SELECT clan_text_channel_id FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
      voice_channel = cursor.execute(f"SELECT clan_channel_id FROM clans WHERE clan_id = {clan_id}").fetchone()[0]
      clan_leader_role = discord.utils.get(ctx.guild.roles,name = 'Clan leader')
      await role.delete()
      await ctx.guild.get_channel(text_channel).delete()
      await ctx.guild.get_channel(voice_channel).delete()
      leader = ctx.guild.get_member(clan_id)
      await leader.remove_roles(clan_leader_role)
      for member in cursor.execute(f"SELECT users FROM clans WHERE clan_id = {clan_id}").fetchall():
        member = bot.get_user(member[0])
        await member.send(embed = discord.Embed(description = 'Ваш клан удалили',color = 0xab92e0))
        balance = cursor.execute(f"SELECT balance FROM clans WHERE users = {member.id}").fetchone()[0]
        cursor.execute(f'DELETE FROM clans WHERE users = {member.id}')
        conection.commit()
        cursor.execute(f"INSERT INTO clans (in_clan,have_clan,users,time_for_pay,has_invited,balance) VALUES(FALSE,FALSE,{member.id},{0},FALSE,{balance})")
        conection.commit()
      await ctx.send(embed = discord.Embed(description = f'Клан **{role.name}** успешно удален',color = 0xab92e0))
         

#economy commands 
@bot.command()
@commands.has_any_role(701908235615076355)
async def take(ctx,member:discord.Member = None,amouth:int = None):
   await ctx.message.delete()
   if member is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
    
   elif amouth is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите суму денег',color = 0xff1111))
   
   else:  
     cursor.execute(f"UPDATE serverss_db SET cash = cash - {amouth} WHERE id = {member.id}")
     conection.commit()
     cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({member.id},'{time.asctime()}','🔴Снято со счета админом {ctx.author} в количестве {amouth} ☘️')")
     conection.commit()
     await ctx.send(embed = discord.Embed(description = f'Баланс успешно снят со счета **{member}**',color = 0xab92e0))

#check member log 
@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def trans(ctx,member:discord.Member = None,page:int = 1):
  await ctx.message.delete()
  if member is None: 
     await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
  else:
        balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {member.id}").fetchone()[0]
        info = cursor.execute(f"SELECT timess,resaon FROM log WHERE id = {member.id}").fetchall()
       
        if (page < 1):
            page = 1
        ELEMENTS_ON_PAGE = 6
        PAGES = len(info) // ELEMENTS_ON_PAGE
        if (len(info) % ELEMENTS_ON_PAGE != 0):
            PAGES += 1
        def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
            if (page > 1):
                START = ELEMENTS_ON_PAGE // (page - 1)
            elif (page == 1):
                START = 0
            STOP = START + ELEMENTS_ON_PAGE
            return (START, STOP)
        START, STOP = calculate_shown_goods(page)
        log_msg = await ctx.send('⠀')
        
        while True:
             emb = discord.Embed(title = f'Транзакции {member} :'
              ,description = f'Страница {page}'
              ,color = discord.Colour.purple())
             
             for row in info[START:STOP]:
                emb.add_field(name = f'Время:```{row[0]}```',value = f'**{row[1]}**   ',inline = False)
             emb.set_footer(text = f'Балнс {member} составляет: {balance}☘️\nЗапросил {ctx.author}',icon_url= ctx.author.avatar_url)
        
             await log_msg.edit(embed = emb)
             await log_msg.add_reaction('◀️')
             await log_msg.add_reaction('▶️')
             
             try:
                rea, usr = await bot.wait_for('reaction_add', check = lambda r, u: r.message.channel == ctx.channel and u == ctx.author, timeout = 60)
             except asyncio.TimeoutError:
                await log_msg.delete()
                break
             else:
                if (str(rea.emoji) == '▶️' and page < PAGES):
                    page += 1
                    START, STOP = calculate_shown_goods(page)
                elif (str(rea.emoji) == '◀️' and page > 1):
                    page -= 1
                    START, STOP = calculate_shown_goods(page)



@bot.command(name = 'timely')
async def timely_money(ctx):
      await ctx.message.delete()
      DELAY = 43200
      NOW = time.time()
      earned = random.randint(25, 50)
      claimed_in = cursor.execute("SELECT when_climed FROM serverss_db WHERE id = {}".format(ctx.author.id)).fetchone()[0]
      balance = cursor.execute("SELECT cash FROM serverss_db WHERE id = {}".format(ctx.author.id)).fetchone()[0]
      HAS_GONE = NOW - claimed_in
      if (claimed_in == 0 or HAS_GONE >= DELAY):
        cursor.execute(f"UPDATE serverss_db SET when_climed = {time.time()} WHERE id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"UPDATE serverss_db SET cash = cash + {earned} WHERE id = {ctx.author.id}")
        conection.commit()
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({ctx.author.id},'{time.asctime()}','🟢Получено {earned}🍀 в качестве бонуса')")
        conection.commit()
        await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, вы получили {earned}☘️\nВы сможете еще раз получить бонус через 12ч',colour = 0xab92e0))
      else:
            to_wait = DELAY - HAS_GONE
            hours = int(to_wait / 60 / 60)
            minutes = int(to_wait / 60) - (hours * 60)
            await ctx.author.send(embed = discord.Embed(description = f'**{ctx.author}**, вы уже получили бонус\nСледующий бонус через {hours}ч {minutes}м',colour = 0xff1111))

@bot.command(name = 'мояроль')
async def castom_role(ctx,role_name:str = None,color:discord.Color = None): 
  await ctx.message.delete()
  castom_role = discord.utils.get(ctx.guild.roles,name = '!мояроль')
  if role_name is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите имя роли!',color = 0xff1111))
  elif castom_role not in ctx.author.roles:
    await ctx.author.send(embed = discord.Embed(description = 'У вас нет роли **!мояроль**.Купить ее в магазине ролей',color = 0xff1111))
  else:
    if color is None:
      color = discord.Color.default()
    roles_in_db = cursor.execute(f'SELECT role_id FROM shops WHERE guild_id = {ctx.guild.id}').fetchall()
    costs = cursor.execute(f"SELECT cost FROM shops WHERE role_id = {castom_role.id}").fetchone()[0]
    new_role = await ctx.guild.create_role(name = role_name,colour = color,mentionable = False)
    await ctx.author.remove_roles(castom_role)
    await ctx.author.add_roles(new_role)
    cursor.execute(f"UPDATE serverss_db SET cash = cash - {costs} WHERE id = {ctx.author.id}")
    conection.commit()
    cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({ctx.author.id},'{time.asctime()}','🟡Создал кастомную роль {new_role.name} за {costs} ☘️')")
    conection.commit()
    await ctx.send(embed = discord.Embed(description = f'Вы создали свою роль **{new_role.name}**',color = 0xab92e0 ))



@bot.command()
async def online(ctx,member:discord.Member = None):
    await ctx.message.delete()
    member = ctx.author if not member else member
    hours = cursor.execute("SELECT timess FROM serverss_db WHERE id = {}".format(member.id)).fetchone()[0]
    c = Clock(int(hours)) 
    h,m,s = c.get_time()
    embed = discord.Embed(title = f'Количество время в войсе: **{h}** часов **{m}** минут **{s}** секунд ',color =  0xab92e0)
    embed.set_author(name = f'Онлайн {member.name}🏆')
    await ctx.send(embed = embed)            


@bot.command()
@commands.has_any_role(701908235615076355)
async def award(ctx,member:discord.Member = None,amouth:int = None):
   await ctx.message.delete()
   if member is None and amouth is None:  
    await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
   
   elif amouth is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите суму денег',color = 0xff1111))
      
   else:
     cursor.execute(f"UPDATE serverss_db SET cash = cash + {amouth} WHERE id = {member.id}")
     conection.commit()
     cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({member.id},'{time.asctime()}','🟢Администратор {ctx.author} наградил {member} в количестве: {amouth} ☘️')")
     conection.commit()
     await ctx.send(embed = discord.Embed(description = f'Баланс успешно пополнен',color =  0xab92e0))


@bot.command()
async def give(ctx,member:discord.Member = None,amouth:int = None):
   await ctx.message.delete()
   user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]

   if member is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
   
   elif amouth is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите суму денег',color = 0xff1111))
     
   else:
    if user_balance < amouth:
      await ctx.send(embed = discord.Embed(description = f'У вас нету столько денег',color = 0xff1111))
    elif amouth == 0:
      await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, укажите сумму больше нуля.',colour = 0xff1111))
    else:
     cursor.execute(f"UPDATE serverss_db SET cash = cash + {amouth} WHERE id = {member.id}")
     conection.commit()
     cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({member.id},'{time.asctime()}','🟢{ctx.author} наградил {member} в количестве: {amouth} ☘️')")
     conection.commit()
     cursor.execute(f"UPDATE serverss_db SET cash = cash - {amouth} WHERE id = {ctx.author.id}")
     conection.commit()
     await ctx.send(embed = discord.Embed( description = f'**{ctx.author}** наградил {amouth}☘️ пользователя {member.mention}',colour = 0xab92e0))

#check user balance
@bot.command(aliases = ['balance','$'])
async def __balance(ctx,member:discord.Member = None):
    await ctx.message.delete()
    member = ctx.author if not member else member
    emb = discord.Embed(description = f"""Баланс **{member}** составляет: **{cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {member.id}").fetchone()[0]}☘️**""",color =  0xab92e0)
    await ctx.send(embed = emb)


@bot.command(name = 'shop')
async def show_goods(ctx,page: int = 1):
        await ctx.message.delete()
        counter = 0
        goods = cursor.execute("SELECT role_name,cost FROM shops WHERE guild_id = {}".format(ctx.guild.id)).fetchall()
        if (page < 1):
            page = 1
        ELEMENTS_ON_PAGE = 9
        PAGES = len(goods) // ELEMENTS_ON_PAGE
        if (len(goods) % ELEMENTS_ON_PAGE != 0):
            PAGES += 1
        def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
            if (page > 1):
                START = ELEMENTS_ON_PAGE // (page - 1)
            elif (page == 1):
                START = 0                 
            STOP = START + ELEMENTS_ON_PAGE
            return (START, STOP)
        START, STOP = calculate_shown_goods(page)
        shop_msg = await ctx.send('⠀')
        while True:
            embed = discord.Embed(
                title = 'Магазин',colour = 0xab92e0)  
            embed.set_footer(text= f'{page}/{PAGES}') 
            for x in goods[START:STOP]:
                counter += 1
                try:
                    embed.add_field(name = f'{counter}', value = f'**{x[0]}** за {x[1]}☘️')
                except IndexError:
                    print('Index Error')
            await shop_msg.edit(embed = embed)
     
            await shop_msg.add_reaction('◀️')
            await shop_msg.add_reaction('▶️')
            try:
                rea, usr = await bot.wait_for('reaction_add', check = lambda r, u: r.message.channel == ctx.channel and u == ctx.author, timeout = 30.0)
            except asyncio.TimeoutError:
                break
            else:
                if (str(rea.emoji) == '▶️' and page < PAGES):
                  
                    page += 1
                    START, STOP = calculate_shown_goods(page)
                elif (str(rea.emoji) == '◀️' and page > 1):
                    
                    page -= 1
                    START, STOP = calculate_shown_goods(page)



@bot.command(name = 'addshop')
@commands.has_any_role(701908235615076355,701908235627790446,773125586527715329)
async def add_goods(ctx,cost:int = None,role:int = None):
   await ctx.message.delete()
   if cost is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите цену роли!',color = 0xff1111))
   elif role is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите айди роли',color = 0xff1111))
   else: 
     if ctx.guild.get_role(role) not in ctx.guild.roles:
        await ctx.send(embed = discord.Embed(description = f'Такой роли не существует',color = 0xff1111))
     elif cursor.execute("SELECT role_id FROM shops WHERE role_id = {}".format(role)).fetchone() is not None:
        await ctx.send(embed = discord.Embed(description = f'Такая роль уже есть в магазине',color = 0xff1111))
     else:
      if ctx.author.guild.get_role(role).name == 'MUTEHAMMERd' or ctx.author.guild.get_role(role).name == 'BANHAMMERd' or role == 701908235627790446 or role == 701908235615076359 or role == 701908235615076358:
        await ctx.send(embed = discord.Embed(description = 'Эту роль нельзя выставлять на продажу!',color = 0xff1111))
      else:
       cursor.execute(f"INSERT INTO shops (guild_id,role_name,role_id,cost) VALUES ({ctx.author.guild.id},'{ctx.author.guild.get_role(role).name}',{role},{cost})")
       conection.commit()
       embed = discord.Embed(title = 'Роль была добавлена в магазин',colour = 0xab92e0)
       embed.add_field(name = 'Название', value = ctx.author.guild.get_role(role).name)
       embed.add_field(name = 'Цена', value = str(cost) + '☘️')
       await ctx.send(embed = embed)



@bot.command(name = 'removeshop')
@commands.has_any_role(701908235615076355,701908235627790446,773125586527715329)
async def remove_goods(ctx,role:int = None):
   await ctx.message.delete()
   if role is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите айди роли',color = 0xff1111))
   else: 
     if ctx.guild.get_role(role) not in ctx.guild.roles:
        await ctx.send(embed = discord.Embed(description = f'Такой роли не существует',color = 0xff1111))
     else:
       try:
         cursor.execute("SELECT role_id FROM shops WHERE role_id = {}".format(role)).fetchone()[0] is None
       except TypeError:
          await ctx.send(embed = discord.Embed(description = f'Такой роли нету в магазине ролей',color = 0xff1111))
       else:
         cursor.execute(f"DELETE FROM shops WHERE role_id = {role}")
         conection.commit()
         await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, роль была успешно удалена',colour = 0xab92e0))





@bot.command(name = 'buy')
async def buy_role(ctx,index:int = None):
  await ctx.message.delete()
  roles = cursor.execute("SELECT role_id FROM shops WHERE guild_id = {}".format(ctx.guild.id)).fetchall()
  balance_user = cursor.execute("SELECT cash FROM serverss_db WHERE id = {}".format(ctx.author.id)).fetchone()[0]
  cost_role = cursor.execute(f"SELECT cost FROM shops WHERE role_id = {roles[index - 1][0]}").fetchone()[0]
  if index is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите номер роли в магазине',color = 0xff1111))
  else:
   if len(roles) < abs(index) or index == 0:
    await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**,роли под таким номером нет в магазине',colour = 0xff1111))

   elif cursor.execute(f"SELECT role_id FROM shops WHERE role_id = {roles[abs(index) - 1][0]}").fetchone() is None:
      await ctx.send(embed = discord.Embed(description = f'Такой роли нету в магазине ролей',color = 0xff1111))
   else:
     if cursor.execute("SELECT cost FROM shops WHERE role_id = {}".format(roles[abs(index) - 1][0])).fetchone()[0] >= balance_user:
       await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**,у вас недостаточно ☘️',colour = 0xff1111))
     elif ctx.guild.get_role(roles[abs(index) - 1][0]) in ctx.author.roles:
       await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, у вас уже имеется данная роль',colour = 0xff1111))
     else: 
       cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(cost_role,ctx.author.id))
       conection.commit()
       cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES ({ctx.author.id},'{time.asctime()}','🟤Купил роль {ctx.guild.get_role(roles[abs(index) - 1][0]).name}')")
       conection.commit()

       await ctx.author.add_roles(ctx.guild.get_role(roles[abs(index) - 1][0]))
       await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, вы успешно купили роль **{ctx.guild.get_role(roles[abs(index) - 1][0]).name}**',colour = 0xab92e0))

#moderation
@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359)
async def girl (ctx,member:discord.Member = None):
  await ctx.message.delete() 
  if member is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
  else:
    girl_role = ctx.guild.get_role(701908235590041682)
    boy_role = ctx.guild.get_role(701908235590041681)
    if boy_role in member.roles:
      await member.remove_roles(boy_role)
      await member.add_roles(girl_role)
    
@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def ban (ctx,member:discord.Member = None,*,reason:str = None):
  await ctx.message.delete()
  if member is None:
      await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
  elif reason is None: 
      await ctx.send(embed = discord.Embed(description = f'Укажите причину!',color = 0xff1111))
  elif ctx.author.id == member.id:
    await ctx.send(embed = discord.Embed(description = 'Операция невозможна (',colour = 0xff1111)) 
  elif member.id == ctx.guild.me.id:
      await ctx.send(embed = discord.Embed(description = f'Я не могу забанить самого себя!',color = 0xff1111))
  else:
    banned_role = discord.utils.find(lambda role: role.name == 'BANHAMMERd', ctx.guild.roles)
    emb = discord.Embed(description=f'**{member}** был **забанен**\n```fix\nПричина: {reason}\n```',color =  0xab92e0)
    emb.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
    emoji = discord.utils.get(bot.emojis, name='ban ')
    cursor.execute(f"INSERT INTO warninform (name,id,type,timess,reason,admin) VALUES('{member}',{member.id},'{emoji}','{datetime.datetime.now().strftime('%d.%m.%Y,%H:%M')}','{reason}',{ctx.author.id})")
    conection.commit()
    await ctx.send(embed = emb)
    await member.add_roles(banned_role)
    channel = ctx.guild.get_channel(701908235627790453)
    await channel.send(embed = emb)
  
    
    
    

@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def kick (ctx,member:discord.Member = None,*,reason = None):
  await ctx.message.delete()
  
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))
 
  elif reason is None:
     await ctx.send(embed = discord.Embed(description = 'Укажите причину!',color = 0xff1111))

  elif member.id == ctx.guild.me.id:
      await ctx.send(embed = discord.Embed(description = 'Я не могу кикнуть самого себя!',color = 0xff1111))
  
  elif ctx.author.id == member.id:
    await ctx.send(embed = discord.Embed(description = 'Операция невозможна (',colour = 0xff1111))
  else:
    emb = discord.Embed(description=f'**{member}** был **кикнут**\n```fix\nПричина: {reason}\n```',color =  0xab92e0)
    emb.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed = emb)
    await member.kick()
    channel = ctx.guild.get_channel(717726165003010109)
    await channel.send(embed = emb)
                                                                                          

@bot.command()  
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359)
async def unban(ctx,member:discord.Member = None):
 if member is None:
  await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
 else:
   await ctx.message.delete()
   banned_role = discord.utils.find(lambda role: role.name == 'BANHAMMERd', member.guild.roles)
   if banned_role not in member.roles:
    await ctx.send(discord.Embed(description=f'!**{member}** не найден в бан листе',color = 0xff1111))
   else:
    await member.remove_roles(banned_role)
    emb = discord.Embed(description=f'**{member}** был **разбанен**',color =  0xab92e0)
    emb.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed = emb)
    channel = ctx.guild.get_channel(701908235627790453)
    await channel.send(embed = discord.Embed(description = f'{ctx.author.mention} разбанил {member.mention}',color = 0xab92e0))
    
@bot.command()  
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def mute(ctx,member:discord.Member = None,mutex_minetes:str = None,*,reason = None):
  await ctx.message.delete()
  mute_role = discord.utils.find(lambda role: role.name == 'MUTEHAMMERd', ctx.guild.roles)
  if member is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите участника',color = 0xff1111))
  elif reason is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите причину!',color = 0xff1111))
  elif member.id == ctx.guild.me.id:
     await ctx.send(embed = discord.Embed(description =  f'Я не могу замютить самого себя!',color = 0xff1111))
  elif mute_role in member.roles:
     await ctx.send(embed = discord.Embed(description =  f'**{member}** уже замучен',color = 0xff1111))
  else:
    
    emoji = discord.utils.get(bot.emojis, name='mu')
    emoji2 = discord.utils.get(bot.emojis, name='un')

    cursor.execute(f"UPDATE adminnsnff SET weekly_mutes = weekly_mutes + {1} WHERE id = {ctx.author.id}")
    conection.commit()
  
    cursor.execute(f"UPDATE adminnsnff SET mutes = mutes + {1} WHERE id = {ctx.author.id}")
    conection.commit()
    
    cursor.execute(f"INSERT INTO warninform (name,id,type,timess,reason,admin) VALUES('{member}',{member.id},'{emoji}','{datetime.datetime.now().strftime('%d.%m.%Y,%H:%M')}','{reason}',{ctx.author.id})")
    conection.commit()
   
    

    embed = discord.Embed(
      description = f'**[{emoji}]{member} ({member.id})** был **замучен** на **{mutex_minetes}**\n```fix\nПричина: {reason}\n```',
      colour = 0xab92e0)  
    embed.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed = embed)
    await member.add_roles(mute_role, reason = reason)
    channel = ctx.guild.get_channel(701908235627790452)
    await channel.send(embed = embed)

    if member.voice:
      await member.edit(mute = True)
    
    await asyncio.sleep(int(mutex_minetes[:-1]) * 60)
    
    if mute_role in member.roles:
     if member.voice:
        await member.edit(mute = False)
        await member.remove_roles(mute_role, reason = reason)
        embed = discord.Embed(description=f'**[{emoji2}]**Вы были **размучены**.Больше не нарушайте :heart:',color = 0xab92e0 )
        await member.send(embed = embed)
        await member.remove_roles(mute_role)
  
     
    
    
@bot.command(name = 'unmute')
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def un_mute(ctx,member:discord.Member = None):        
  await ctx.message.delete()
  if member is None:
     await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))
  else:
    emoji = discord.utils.get(bot.emojis, name='un')
    role = discord.utils.find(lambda role: role.name == 'MUTEHAMMERd', ctx.guild.roles)
    if role not in member.roles: 
      await ctx.send(embed = discord.Embed(description=f'Пользователь {member} не были замучен.',color = 0xff1111 ))
    else:
      mute_role = discord.utils.find(lambda role: role.name == 'MUTEHAMMERd', ctx.guild.roles)
      if member.voice:
         await member.edit(mute = False )
      embed = discord.Embed(description=f'**[{emoji}]**Вы были **размучены**.Больше не нарушайте :heart:',color = 0xab92e0 )
      embed.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
      embed2 = discord.Embed(description=f'**[{emoji}]{member}** был **размучен**.',color = 0xab92e0 )
      embed2.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
      await member.remove_roles(mute_role)
      await member.send(embed=embed)
      await ctx.send(embed=embed2)
      channel = ctx.guild.get_channel(701908235627790452)
      await channel.send(embed = embed2)
      
        

@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def warn(ctx,member:discord.Member = None,*,reason = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))
  elif reason is None:
    await ctx.send(embed = discord.Embed(description='Укажите причину!',color = 0xff1111))
  elif member.id == ctx.guild.me.id:
      await ctx.send(embed = discord.Embed(description = 'Я не могу заварнить самого себя!',color = 0xff1111))
  else:
    emoji = discord.utils.get(bot.emojis, name='znak')
    warns = cursor.execute(f'SELECT warns FROM warninform WHERE id = {member.id}').fetchone()[0]

    cursor.execute(f"UPDATE warninform SET warns = warns + {1} WHERE id = {member.id}")
    conection.commit()
    
    cursor.execute(f"INSERT INTO warninform (name,id,warns,type,timess,reason,admin) VALUES('{member}',{member.id},{warns + 1},'{emoji}','{datetime.datetime.now().strftime('%d.%m.%Y,%H:%M')}','{reason}',{ctx.author.id})")
    conection.commit()
    
    cursor.execute(f"UPDATE adminnsnff SET weekly_warns = weekly_warns + {1} WHERE id = {ctx.author.id}")
    conection.commit()
    
    cursor.execute(f"UPDATE adminnsnff SET warns = warns + {1} WHERE id = {ctx.author.id}")
    conection.commit()
    

    embed = discord.Embed(
            description = f'**[{emoji}] {member} ({member.id})** был предупреждён\n```fix\nПричина: {reason}\n```',
            colour = 0xab92e0
        )
    
    embed.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed = embed)
    channel = ctx.guild.get_channel(717726165003010109)
    await channel.send(embed = embed)
    if (warns + 1 >= 3):
         banned_role = discord.utils.find(lambda role: role.name == 'BANHAMMERd', channel.guild.roles)
         await member.add_roles(banned_role,reason = '3/3 варнов')


   

@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359)
async def un_warn(ctx,member:discord.Member = None):
  await ctx.message.delete()
  if member is None:
    await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))
  elif member.id == ctx.guild.me.id:
      await ctx.send(embed = discord.Embed(description = 'Я не могу заварнить самого себя!',color = 0xff1111))
  else:
    warns = cursor.execute(f"SELECT warns FROM warninform WHERE id = {member.id}").fetchone()[0]
    if warns == 0:
      await ctx.send(embed = discord.Embed(description = f'В участника {member} нету варнов',color = 0xff1111))
    else:

      cursor.execute(f"UPDATE warninform SET warns = warns - {1} WHERE id = {member.id}")
      conection.commit()
      
      embed = discord.Embed(description = f'Послднее **передупреджение c {member} ({member.id})** было снято',colour = 0xab92e0)
      embed.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)

      embed2 = discord.Embed(description = f'Послднее **передупреджение** было снято.Больше не нарушайте :heart:',colour = 0xab92e0)
      embed2.set_footer(text = f'Выполнил(а) {ctx.author}', icon_url=ctx.author.avatar_url)
      await ctx.send(embed = embed)
      await member.send(embed = embed2)
      channel = ctx.guild.get_channel(717726165003010109)
      await channel.send(embed = embed)
     
@bot.command()
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def user_warns(ctx,member:discord.Member = None,page:int = 1):
 await ctx.message.delete()
 
 if member is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите участника!',color = 0xff1111))
 else:
        info = cursor.execute(f"SELECT type,reason,timess,admin FROM warninform WHERE id = {member.id}").fetchall()
        if (page < 1):
            page = 1
        ELEMENTS_ON_PAGE = 9
        PAGES = len(info) // ELEMENTS_ON_PAGE
        if (len(info) % ELEMENTS_ON_PAGE != 0):
            PAGES += 1
        def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
            
            if (page > 1):
                START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
                
            elif (page == 1):
                START = 0
            STOP = START + ELEMENTS_ON_PAGE
            return (START, STOP)
        START, STOP = calculate_shown_goods(page)
        
        
        msg = await ctx.send('⠀')
        while True:
          try:
             embed = discord.Embed(title = f'Нарушения | **{member}**'
              ,description = f'Страница {page}'
              ,color = discord.Colour.purple()) 
             a = ''
             b = ''
             for row in info[START:STOP]:
                if (bool(row[2])) is False:
                     pass
                else:
                    a += f'{row[0]}/**{row[2]}**\n'
                    b += f'**{row[1]}**/{bot.get_user(row[3]).mention}\n'
             
             embed.add_field(name = 'Тип/Дата', value = a)
             embed.add_field(name = '** **', value = '** **')
             embed.add_field(name = 'Причина/Выполнил(а)', value = b)
             
             

             await msg.edit(embed = embed)
             await msg.add_reaction('◀️')
             await msg.add_reaction('▶️')

           
          except discord.HTTPException:
               return await ctx.send(embed = discord.Embed(description = f'У **{member}** нету нарушений',color =  0xab92e0))
          else:
             try:
                rea, usr = await bot.wait_for('reaction_add', check = lambda r, u: r.message.channel == ctx.channel and u == ctx.author, timeout = 60)
             except asyncio.TimeoutError:
                await msg.delete()
                break
             else:
                if (str(rea.emoji) == '▶️' and page < PAGES):
                    page += 1
                    START, STOP = calculate_shown_goods(page)
                elif (str(rea.emoji) == '◀️' and page > 1):
                    page -= 1
                    START, STOP = calculate_shown_goods(page)

#other
@bot.command()
async def inrole(ctx,roles:int = None):
    await ctx.message.delete()
    role = ctx.guild.get_role(roles)
    if roles is None:
       await ctx.send(embed = discord.Embed(description = f'Укажите роль!',color = 0xff1111))
    else:
     goods = role.members
  
     page = 0
     if (page < 1):
        page = 1
     ELEMENTS_ON_PAGE = 10
     PAGES = len(goods) // ELEMENTS_ON_PAGE
     if len(goods) % ELEMENTS_ON_PAGE:
          PAGES += 1

     def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
              if (page > 1):
                  START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
          
              elif (page == 1):       
                  START = 0
              
              STOP = START + ELEMENTS_ON_PAGE
              return (START, STOP)

     START, STOP = calculate_shown_goods(page)
     roles_list_msg = await ctx.send('⠀')
     
     while True:
      
          try:
            embed = discord.Embed(title = f'Список пользователей с ролью: {role.name}',color = discord.Colour.purple())
            a = ''
        
            for row in goods[START:STOP]:
                a += f'{row} - {row.mention}\n'
               
 
            embed.add_field(name = '** **', value = f'{a}',inline = False)
            embed.set_footer(text= f'{page}/{PAGES}')
  
  
            await roles_list_msg.edit(embed = embed)
          except discord.errors.HTTPException:
                await ctx.send(embed = discord.Embed(description = 'Ни один участник не имеет такой роли',color = 0xab92e0))
                break
          else:
             await roles_list_msg.add_reaction('◀️')
             await roles_list_msg.add_reaction('▶️')
             
             try:
                rea, usr = await bot.wait_for('reaction_add', check = lambda r, u: r.message.channel == ctx.channel and u == ctx.author,timeout = 60)
             except asyncio.TimeoutError:
                
                break
             else:
                if (str(rea.emoji) == '▶️'and page < PAGES):
                    
                    page += 1
                    START, STOP = calculate_shown_goods(page)
                    
                elif (str(rea.emoji) == '◀️' and page > 1):
                    page -= 1
                    START, STOP = calculate_shown_goods(page)

@bot.command()
async def top_reports(ctx,page:int = 1):
    await ctx.message.delete()
    goods = cursor.execute("SELECT id, reports FROM adminnsnff ORDER BY reports DESC LIMIT 27").fetchall()
    
    if page < 1:
        page = 1
    
    ELEMENTS_ON_PAGE = 9
    PAGES = len(goods) // (ELEMENTS_ON_PAGE - 1)
    if (len(goods)) % ELEMENTS_ON_PAGE:
      PAGES += 1
    def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
        if (page > 1):
            START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
        elif (page == 1):
            START = 0
        STOP = START + ELEMENTS_ON_PAGE
        return (START, STOP)
    START, STOP = calculate_shown_goods(page)
    i = START + 1  
    embed = discord.Embed(title=f"Топ по репортам",color = discord.Color.purple())
   
    for id, reports in goods[START:STOP]:
       
        embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Кол. принятых репортов: **{reports}**', inline = True)
        i += 1
    embed.set_footer(text = f'{page}/{PAGES}')
    online = await ctx.send(embed=embed)
    await online.add_reaction('◀️')
    await online.add_reaction('▶️')
    while True:
  
      try:
          rea, usr = await bot.wait_for('reaction_add',check = lambda r, u: u == ctx.author and u != ctx.guild.me, timeout = 60)
      except asyncio.TimeoutError:
          break

      else:
        if str(rea.emoji == '▶️') and (str(rea.emoji) != '◀️' ) and page < PAGES:
          page += 1
          START,STOP = calculate_shown_goods(page)
          i = START
          embed = discord.Embed(title = 'Топ по репортам',color = discord.Color.purple())
          for id,reports in goods[START:STOP]:
    
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Кол. принятых репортов: **{reports}**', inline = True)
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)
        elif (str(rea.emoji) == '◀️' and page > 1):
          page -= 1
          START,STOP = calculate_shown_goods(page)
          i = START
          embed = discord.Embed(title = 'Топ по репортам',color = discord.Color.purple())
          if i == 0:
            i += 1
          for id,reports in goods[START:STOP]:
           
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Кол. принятых репортов: **{reports}**', inline = True)
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)


@bot.command()
async def top_online(ctx,page:int = 1):
    await ctx.message.delete()
    goods = cursor.execute("SELECT id, timess FROM serverss_db ORDER BY timess DESC LIMIT 27").fetchall()
    
    if page < 1:
        page = 1
    
    ELEMENTS_ON_PAGE = 9
    PAGES = len(goods) // (ELEMENTS_ON_PAGE - 1)
    if len(goods) % ELEMENTS_ON_PAGE:
      PAGES += 1
    
    def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
        if (page > 1):
            START = START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
        elif (page == 1):
            START = 0
        STOP = START + ELEMENTS_ON_PAGE
        return (START, STOP)
    START, STOP = calculate_shown_goods(page)
    i = START + 1  
    embed = discord.Embed(title=f"Топ по онлайну",color = discord.Color.purple())
   
    for id, timess in goods[START:STOP]:
        c = Clock(int(timess)) 
        h,m,s = c.get_time()
        
        embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'**{h}** ч. **{m}** мин. **{s}** сек.', inline = True)
        i += 1
    embed.set_footer(text = f'{page}/{PAGES}')
    online = await ctx.send(embed=embed)
    await online.add_reaction('◀️')
    await online.add_reaction('▶️')
    while True:
     
      try:
          rea, usr = await bot.wait_for('reaction_add',check = lambda r, u: u == ctx.author and u != ctx.guild.me, timeout = 60)
      except asyncio.TimeoutError:
          break

      else:
        if str(rea.emoji == '▶️') and (str(rea.emoji) != '◀️' ) and page < PAGES:
          page += 1 
          START,STOP = calculate_shown_goods(page)
    
          embed = discord.Embed(title = 'Топ по онлайну',color = discord.Color.purple())
          for id,timess in goods[START:STOP]:
    
              c = Clock(int(timess)) 
              h,m,s = c.get_time()
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}',value = f'**{h}** ч. **{m}** мин. **{s}** сек.')
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)
        elif (str(rea.emoji) == '◀️' ) and 1 < page:
          
          page -= 1
          START,STOP = calculate_shown_goods(page)
          i = START
          embed = discord.Embed(title = 'Топ по онлайну',color = discord.Color.purple())
          if i == 0:
            i += 1
          for id,timess in goods[START:STOP]:
              c = Clock(int(timess)) 
              h,m,s = c.get_time() 
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}',value = f'**{h}** ч. **{m}** мин. **{s}** сек.' )
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)

@bot.command()
async def top_clans(ctx,page:int = 1):
    await ctx.message.delete()
    
    goods = cursor.execute("SELECT clan_name,voice_time FROM clans ORDER BY voice_time DESC LIMIT 27").fetchall()
    len_goods = 0
    for x in goods:
      if x[0] is not None:
        len_goods += 1
        
    if page < 1:
        page = 1
    ELEMENTS_ON_PAGE = 9
    PAGES = len_goods // (ELEMENTS_ON_PAGE - 1)
    if len_goods % ELEMENTS_ON_PAGE:
      PAGES += 1
    
    def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
        if (page > 1):
            START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
        elif (page == 1):
            START = 0
        STOP = START + ELEMENTS_ON_PAGE
        return (START, STOP)
    START, STOP = calculate_shown_goods(page)
    i = START + 1  
    embed = discord.Embed(title=f"Топ кланов",color = discord.Color.purple())
    
    for clan, timess in goods[START:STOP]:
      if clan is not None:
        c = Clock(int(timess)) 
        h,m,s = c.get_time()
        
        embed.add_field(name = f'#{i} {clan}', value = f'**{h}** ч. **{m}** мин. **{s}** сек.', inline = True)
        i += 1
    embed.set_footer(text = f'{page}/{PAGES}')
    online = await ctx.send(embed=embed)
    await online.add_reaction('◀️')
    await online.add_reaction('▶️')
    while True:
  
      try:
          rea, usr = await bot.wait_for('reaction_add',check = lambda r, u: u == ctx.author and u != ctx.guild.me, timeout = 60)
      except asyncio.TimeoutError:
          break

      else:
        if str(rea.emoji == '▶️') and (str(rea.emoji) != '◀️' ) and page < PAGES:
          page += 1
          START,STOP = calculate_shown_goods(page)
          embed = discord.Embed(title = 'Топ кланов',color = discord.Color.purple())
          for user,timess in goods[START:STOP]:
    
              c = Clock(int(timess)) 
              h,m,s = c.get_time()
              embed.add_field(name = f'#{i} {clan}', value = f'**{h}** ч. **{m}** мин. **{s}** сек.', inline = True)
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)
        elif (str(rea.emoji) == '◀️' and page > 1):
          page -= 1

          START,STOP = calculate_shown_goods(page)
          i = START
          embed = discord.Embed(title = 'Топ кланов',color = discord.Color.purple())
          if i == 0:  
            i += 1
          for user,timess in goods[START:STOP]:
              c = Clock(int(timess)) 
              h,m,s = c.get_time() 
              embed.add_field(name = f'#{i} {clan}', value = f'**{h}** ч. **{m}** мин. **{s}** сек.', inline = True)
              i += 1
          embed.set_footer(text = f'{page}/{PAGES}')
          await online.edit(embed = embed)

@bot.command()
async def top_level(ctx,page:int = 1):
    await ctx.message.delete()
    
  
    goods = cursor.execute("SELECT id,lvl,xp FROM exp_system ORDER BY lvl,xp DESC LIMIT 27").fetchall()
    if page < 1:
        page = 1
    ELEMENTS_ON_PAGE = 9
    PAGES = len(goods) // (ELEMENTS_ON_PAGE - 1)
    
    if (len(goods)) % ELEMENTS_ON_PAGE:
      PAGES += 1
    def calculate_shown_goods(page, ELEMENTS_ON_PAGE = ELEMENTS_ON_PAGE):
        if (page > 1):
            START = (ELEMENTS_ON_PAGE * page) -  ELEMENTS_ON_PAGE
        elif (page == 1):
            START = 0
        STOP = START + ELEMENTS_ON_PAGE
        return (START, STOP)
    START, STOP = calculate_shown_goods(page)
    i = START + 1  
    embed = discord.Embed(title=f"Топ по уровню",color = discord.Color.purple())
   
    for id,lvl,expi in goods[START:STOP]:
        exp_for_levl = 40 + (lvl - 1) * 20   
        embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Уровень **{lvl}** {expi}/{exp_for_levl}', inline = True)
        i += 1
    embed.set_footer(text = f'{page}/{PAGES}')
    leveling = await ctx.send(embed=embed)
    await leveling.add_reaction('◀️')
    await leveling.add_reaction('▶️')
    while True:
  
      try:
          rea, usr = await bot.wait_for('reaction_add',check = lambda r, u: u == ctx.author and u != ctx.guild.me, timeout = 60)
      except asyncio.TimeoutError:
          break

      else:
        if str(rea.emoji == '▶️') and (str(rea.emoji) != '◀️' ) and page < PAGES:
          page += 1
          START,STOP = calculate_shown_goods(page)
          embed = discord.Embed(title = 'Топ по уровню',color = discord.Color.purple())
          for id,lvl,expi in goods[START:STOP]:
              exp_for_levl = 40 + (lvl - 1) * 20   
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Уровень **{lvl}** {expi}/{exp_for_levl}', inline = True)
              i += 1
          
          embed.set_footer(text = f'{page}/{PAGES}')
          await leveling.edit(embed = embed)

        elif (str(rea.emoji) == '◀️' and page > 1):
          page -= 1
          START,STOP = calculate_shown_goods(page)
          i = START
          embed = discord.Embed(title = 'Топ по уровню',color = discord.Color.purple())
          if i == 0:
            i += 1
          for id,lvl,expi in goods[START:STOP]:
              exp_for_levl = 40 + (lvl - 1) * 20   
              embed.add_field(name = f'#{i} {ctx.guild.get_member(id)}', value = f'Уровень **{lvl}** {expi}/{exp_for_levl}', inline = True)
              i += 1
            
          embed.set_footer(text = f'{page}/{PAGES}')
          await leveling.edit(embed = embed)
@bot.command()
async def serverinfo(ctx):
    await ctx.message.delete()
    bots = 0
    for member in ctx.guild.members:
        user = bot.get_user(member.id)
      
        if user.bot == True:
          bots += 1


    embed = discord.Embed(title = f'Информация о сервере **{ctx.guild.name}**',color = discord.Colour.purple())
    embed.set_thumbnail(url = ctx.guild.icon_url)
    embed.add_field(name = 'ID', value = f'{ctx.guild.id}' )
    embed.add_field(name = 'Владелец', value = f'{ctx.guild.owner}')
    embed.add_field(name = 'Участников', value = f'{len(ctx.guild.members) - bots}' )
    embed.add_field(name = 'Текстовые каналы:',value = f'{len(ctx.guild.text_channels)}')
    embed.add_field(name = 'Голосовые каналы',value = f'{len(ctx.guild.voice_channels)}')
    embed.add_field(name = 'Категорий',value = f'{len(ctx.guild.categories)}')
    embed.add_field(name = 'Создан',value = f'{ctx.guild.created_at.strftime("%m.%d.%Y")}')
    embed.add_field(name = 'Ролей',value = f'{len(ctx.guild.roles)}')
    embed.add_field(name = 'Регион',value = f'{ctx.guild.region}')
    embed.add_field(name = 'Уровень нитро',value = f'{ctx.guild.premium_tier}')
    embed.add_field(name = 'Нитро бустеров',value = f'{len(ctx.guild.premium_subscribers)}')
    await ctx.send(embed = embed)      
                     
@bot.command()
async def uinfo(ctx,member: discord.Member = None):
        await ctx.message.delete()
        member = ctx.author if not member else member
          
        embed = discord.Embed(title = f"Информация о {member}", color=0x5500ff)
        embed.set_thumbnail(url = member.avatar_url)
        embed.add_field(name = "ID:", value = member.id )
        embed.add_field(name = "Ник:", value = member)
        embed.add_field(name = "Дата регистрации: ", value = member.created_at.strftime("%m.%d.%Y") )
        embed.add_field(name = "Дата регистрации на сервере:", value = member.joined_at.strftime("%m.%d.%Y"))
        embed.add_field(name = "Самая высокая роль:", value = member.top_role.mention)

        await ctx.send( embed = embed )


@bot.command()
async def top_cash(ctx):
     await ctx.message.delete()
    
     embed = discord.Embed(title = '☘️Топ по валюте',color = discord.Colour.purple())
     
     embed.set_author(name = ctx.author,icon_url = ctx.author.avatar_url)
     counter = 0
   
     for row in cursor.execute(f"SELECT id,cash FROM serverss_db ORDER BY cash DESC LIMIT {10}").fetchall():
         counter += 1
         embed.add_field(name = f'**#{counter} {bot.get_user(row[0]).name}**', value = f'{row[1]}☘️')

     await ctx.send(embed = embed)




@bot.command(aliases = ['admin_info','stuff_info'])
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def info(ctx,member:discord.Member = None): 
  await ctx.message.delete()
  

  if member is None:
     await ctx.send(embed = discord.Embed(description = f'Укажите участника',colour = 0xff1111))
 
  
  else:
      if cursor.execute(f"SELECT id FROM adminnsnff WHERE id = {member.id}").fetchone() is None:
          await ctx.send(embed = discord.Embed(description = f'Такого администратора нету в базе данных!',color = 0xff1111))
      else:
        admin_reports = cursor.execute(f"SELECT reports FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        weekly_reports = cursor.execute(f"SELECT weekly_reports FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        weekly_warns = cursor.execute(f"SELECT weekly_warns FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        weekly_mutes = cursor.execute(f"SELECT weekly_mutes FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        mutes = cursor.execute(f"SELECT mutes FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        warns = cursor.execute(f"SELECT warns FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        rep_pos = cursor.execute(f"SELECT rating_pos FROM adminnsnff WHERE id = {member.id}").fetchone()[0]
        rep_neg = cursor.execute(f"SELECT rating_neg FROM adminnsnff WHERE id = {member.id}").fetchone()[0]

        emoji = discord.utils.get(bot.emojis, name='mu')
        emoji2 = discord.utils.get(bot.emojis, name='znak')
        emoji3 = discord.utils.get(bot.emojis, name='report')
        
        embed = discord.Embed(title = f'Статистика | **{member}**',description = f'{emoji3} Количество одобренных репортов за неделю **{weekly_reports}**,всего **{admin_reports}**\n'
               f'{emoji} Выдано мутов: за неделю **{weekly_mutes}**,всего **{mutes}**\n'
               f'{emoji2} Выдано варнов: за неделю **{weekly_warns}**,всего **{warns}**\n'
               f'Репутация **✅{rep_pos}** и **❌{rep_neg}**\n'
               ,color = 0xab92e0)
        
        embed.set_thumbnail( url= member.avatar_url)
        embed.set_footer(text = f'Запросил {ctx.author}' ,icon_url = ctx.author.avatar_url)
        await ctx.send(embed = embed)


#moderation
@bot.command(aliases = ['giverole', 'gr'])
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def _give_role(ctx,target_user:discord.Member = None,role:int = None):
        await ctx.message.delete()
        try:
          if target_user is None:     
             await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))  
          elif role is None:
             await ctx.send(embed = discord.Embed(description = 'Укажите айди роли',color = 0xff1111))
          elif ctx.guild.get_role(role) in target_user.roles:
             await ctx.send(embed = discord.Embed(description = f'У {target_user} уже есть такая роль',color = 0xff1111))
          elif cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_role_id = {role}").fetchone() is not None:
             await ctx.send(embed = discord.Embed(description = 'Это клановая роль',color = 0xff1111))
          else:
            await target_user.add_roles(ctx.guild.get_role(role), reason = f'by {ctx.author}')
            embed = discord.Embed(
                description = f'Роль **{ctx.guild.get_role(role).mention}** успешно была выдана **{target_user.mention} ({target_user.id})**',
                colour = 0xab92e0
            )
            embed.set_footer(text= f'Выдал {ctx.author} ', icon_url=ctx.author.avatar_url)
            await ctx.send(embed = embed)
            channel = ctx.guild.get_channel(728021862759530608)
            await channel.send(embed = embed)
            

        except discord.Forbidden:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, вы не можете выдать человеку эту роль',
                colour = 0xff1111)) 
        except AttributeError:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, роль с таким айди нет на сервере',
                colour = 0xff1111))
        

@bot.command(aliases = ['takerole', 'tr'])
@commands.has_any_role(701908235615076355,701908235627790446,701908235615076359,701908235615076358)
async def _take_role(ctx,target_user:discord.Member = None,role:int = None):
        await ctx.message.delete()
        try: 
          if target_user is None:     
             await ctx.send(embed = discord.Embed(description = 'Укажите участника',color = 0xff1111))
          elif role is None:
             await ctx.send(embed = discord.Embed(description = 'Укажите айди роли',color = 0xff1111))
          elif ctx.guild.get_role(role) not in target_user.roles:
            await ctx.send(embed = discord.Embed(description = f'У {target_user} нету такой роли',color = 0xff1111)) 
          elif cursor.execute(f"SELECT clan_role_id FROM clans WHERE clan_role_id = {role}").fetchone() is not None:
             await ctx.send(embed = discord.Embed(description = 'Это клановая роль',color = 0xff1111))
          else:
            await target_user.remove_roles(ctx.guild.get_role(role), reason = f'by {ctx.author}')
            embed = discord.Embed(
                description = f'Роль **{ctx.guild.get_role(role).mention}** успешно была убрана у **{target_user.mention} ({target_user.id})**',
                colour = 0xab92e0
            )
            embed.set_footer(text= f'Убрал {ctx.author} ', icon_url=ctx.author.avatar_url)
            await ctx.send(embed = embed)
            channel = ctx.guild.get_channel(728021862759530608)
            await channel.send(embed = embed) 
        except discord.Forbidden:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, вы не можете забрать у человека эту роль',
                colour = 0xff1111))
        except AttributeError:   
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, роль с таким айди нет на сервере',
                colour = 0xff1111))

@bot.command()
async def report(ctx,user:discord.Member,*,reason = None):
  await ctx.message.delete()
  if reason is None:
    await ctx.send(embed = discord.Embed(description = f'**{ctx.author}**, укажите причину!',colour = 0xff1111))      
  elif ctx.author.id == user.id:
    await ctx.send(embed = discord.Embed(description = 'Операция невозможна (',colour = 0xff1111)) 
  else:
  
    d = datetime.datetime.today().strftime('%m.%d.%y,в %H:%M')
    channel = ctx.channel 
    sent_msgs = []
    reporter = ctx.author
    embed = discord.Embed(
            description = f'```css\n Жалоба на пользователя {user} отправлена на рассмотрение!\n```',
            colour = 0xab92e0)
  
    embed.set_author(name = f'{reporter} отправил жалобу!',icon_url = reporter.avatar_url)
    embed.set_footer(text= f"{ctx.guild.name} | Жалобы • {d}", icon_url=ctx.guild.icon_url)

    chat_msg = await ctx.send(embed = embed)
    
    moders = cursor.execute('SELECT id FROM adminnsnff').fetchall()
    for i in moders:
      i2 = bot.get_user(i[0])
      embed = discord.Embed(
       title = f'Жалоба',
       description = f'{ctx.author}',
       colour = 0xab92e0,
       timestamp = datetime.datetime.now(tz = pytz.UTC)
      )  
      
      embed.add_field(name = 'Нарушитель', value = f'**ID: {user.id}**\n**USER: {user}**')
      embed.add_field(name = 'Канал нарушения', value = channel.mention, inline = True)
      if (user.voice):
        invite = await user.voice.channel.create_invite(unique = True)
        embed.add_field(name = 'Сидит в войсе', value = invite.url, inline = False)
      embed.add_field(name = 'Ссылка на репорт', value = chat_msg.jump_url, inline = False)
      embed.add_field(name = 'Причина', value = f'```fix\n{reason}\n```', inline = False)
      msg = await i2.send(embed = embed) 
      await msg.add_reaction('✅')
      await msg.add_reaction('❎')
      await msg.add_reaction('🚩')    
      
      sent_msgs.append(msg)
    
   
    
    def check(reaction, user):
            
            conditions = [
                str(reaction.emoji) in '✅❎🚩',
                user.id != ctx.guild.me.id,
                reaction.message.id in [msg.id for msg in sent_msgs if msg.id == reaction.message.id]
                ]
        
            return all(conditions)
            
  
    async def punishment_msg(control:discord.Member):
          emoji_mu = discord.utils.get(bot.emojis, name='mu')
          emoji_znak = discord.utils.get(bot.emojis, name='znak')
          emoji_ban  = discord.utils.get(bot.emojis,name = 'ban')
          msg = await control.send(embed = discord.Embed(description=f'Выберите наказание для {user}',color = 0xab92e0))
          await msg.add_reaction(emoji_mu)
          await msg.add_reaction(emoji_znak)
          await msg.add_reaction(emoji_ban)
          try:
            rea,usr= await bot.wait_for('reaction_add',check = lambda rec,usr: rec.emoji in [emoji_mu,emoji_znak,emoji_ban] and usr.id != ctx.guild.me.id and msg.id == rec.message.id,timeout = 60)
            await msg.delete()
            if rea.emoji == emoji_mu:
                return 'получил мут'
            elif rea.emoji == emoji_znak:
                return 'получил варн'
            elif rea.emoji == emoji_ban:
                return 'получил бан'
          
            
          except asyncio.TimeoutError:
            return 'не получил наказания'
            
            
    
    async def give_mark(text:str):   
            mark = False
            [await msg.delete() for msg in sent_msgs]
            while mark is False:
              
              rea,usr= await bot.wait_for('reaction_add',check = check)
              if (str(rea.emoji) == '🚩'):
                    mark = True
                    msg = await reporter.send(embed = discord.Embed(description=f'{text}',color = 0xab92e0))
                    await msg.add_reaction('✅')
                    await msg.add_reaction('❎')
                    try: 
                      rea,usr= await bot.wait_for('reaction_add',check = lambda rec,usr: str(rec.emoji) in '✅❎🚩' and usr.id != ctx.guild.me.id and msg.id == rec.message.id) # lambda rec,usr: str(rec.emoji) in '✅❎' and usr.id != ctx.guild.me.id and msg.id == rec.message.id
                      
                      if (str(rea.emoji) == '✅'):
                          
                            msg.colour = 0x33fd13
                            msg.description = 'Вы оценили работу контрола положительно'
                            await msg.edit(embed = embed)
                          
                            cursor.execute(f"UPDATE adminnsnff SET rating_pos = rating_pos + {1} WHERE id = {usre.id}")
                            conection.commit()
                            
                            
                          
                                     
                      elif (str(rea.emoji) == '❎'):              
                            
                            if (msg.channel == usr.dm_channel):
                              msg.colour = 0xfd3313
                              msg.description = 'Вы оценили работу контрола отрицательно'
                              await msg.edit(embed = embed)
                              cursor.execute(f"UPDATE adminnsnff SET rating_neg = rating_neg + {1} WHERE id = {usre.id}")
                              conection.commit()
                              
                            

                    except asyncio.TimeoutError:
                          await msg.delete()

    
    
    chosen_green = False
    chosen_red = False
    
    while chosen_green == False or chosen_red == False:    
            

            reac, usre = await bot.wait_for('reaction_add',check = check)
        
            
            if (str(reac.emoji) == '✅'):
                  
                  
                  for report in sent_msgs:
                    embed = report.embeds[0]
                    embed.title = f'Report - взят **{usre}**'
                    if (report.channel == usre.dm_channel):
                        embed.colour = 0x33fd13
                    else:
                        embed.colour = 0xfd3313
                    await report.edit(embed = embed)
                   

                  cursor.execute(f"UPDATE adminnsnff SET reports = reports + {1}  WHERE id = {usre.id}")
                  conection.commit()
                  cursor.execute(f"UPDATE adminnsnff SET weekly_reports = weekly_reports + {1} WHERE id = {usre.id}")
                  conection.commit()
                  
                  punishment = await punishment_msg(usre)
                  text = f'**Вы довольны работой контрола** {usre.mention}?\n``Нарушитель {punishment}``'
                  await give_mark(text)
                  chosen_green = True
                  
                  

            elif (str(reac.emoji) == '❎'):       
                text = f'**Вы довольны работой контрола** {usre.mention}?\n``Нарушитель был оправдан``'
                for report in sent_msgs:
                    embed = report.embeds[0]
                    embed.title = f'Report - был отклонен **{usre}**'
                    embed.colour = 0xfd3313
                    await report.edit(embed = embed)
                    chosen_red = True
                    await give_mark(text)
                    
            
#get_avatr
@bot.command(aliases = ['av','avatar'])
async def av__(ctx,member:discord.Member = None):
   await ctx.message.delete()
   member = ctx.author if not member else member
  
   embed = discord.Embed(color = discord.Color.purple())
   
   
   embed.set_thumbnail(url = member.avatar_url)
   
   embed.add_field(name = 'Никнейм', value = member)
   embed.add_field(name = 'Ссылки на изображения', value = f'[jpg]({member.avatar_url_as(format="jpg", size=1024)})'
                        f' | [png]({member.avatar_url_as(format="png", size=1024)})'
                        f' | [webp]({member.avatar_url_as(format="webp", size=1024)})',inline = False)
   
   print(embed.fields[1].value)
   if member.is_avatar_animated() is True:
     value = embed.fields[1].value + f' | [gif]({member.avatar_url_as(format="gif", size=1024)})'
     embed.remove_field(1)
     embed.add_field(name = 'Ссылки на изображения' ,value = value, inline=False)
   await ctx.send(embed = embed)

#emojis
@bot.command()
async def bite(ctx,target:discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.bite_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** укусил **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (укусил {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command()
async def cake(ctx,target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))    
            return
        url = random.choice(gifs.cake_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** угостил **{target}** тортиком',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (угостил тортиком {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)
        

@bot.command()
async def hug(ctx,target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.hug_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** обнял **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (обнял {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command()
async def glare(ctx, target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.glare_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** вызывающе смотрит на **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (вызывающе посмотрел на {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command()
async def five(ctx,target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.five_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** дал пять **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (дал пять {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)


@bot.command()
async def kiss(ctx, target: discord.Member):  
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.kiss_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** поцеловал **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (поцеловал {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command()               
async def lick(ctx, target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.lick_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** лизнул **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (лизнул {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command() 
async def pat(ctx, target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance  < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
        ))
            return
        url = random.choice(gifs.pat_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** погладил **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (погладил {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)
        
@bot.command() 
async def poke(ctx, target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return  
        url = random.choice(gifs.poke_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** тыкнул в **{target}**',
            colour = 0xab92e0
        )     
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (тыкнул в {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command() 
async def punch(ctx,target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
                description = f'**{ctx.author}**, на вашем счету недостаточно средств',
                colour = 0xff1111
            ))
            return
        url = random.choice(gifs.punch_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** ударил **{target}**',
            colour = 0xab92e0
        )
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (ударил {target})')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)
        

@bot.command()
async def slap(ctx,target: discord.Member):
        await ctx.message.delete()
        user_balance = cursor.execute(f"SELECT cash FROM serverss_db WHERE id = {ctx.author.id}").fetchone()[0]
        if user_balance < 5:
            await ctx.send(embed = discord.Embed(
            	description = f'**{ctx.author}**, на вашем счету недостаточно средств',
            	colour = 0xff1111))
            return
        url = random.choice(gifs.slap_images)
        embed = discord.Embed(
            description = f'**{ctx.author}** дал **{target}** пощечину',colour = 0xab92e0)
        embed.set_image(url = url)
        embed.set_footer(text = 'С вашего счёта снято 5☘️')
        cursor.execute(f"INSERT INTO log (id,timess,resaon) VALUES({ctx.author.id},'{time.asctime()}','🟣Использовал эмоджи (дал {target}) пощечину')")
        conection.commit()
        cursor.execute("UPDATE serverss_db SET cash = cash - {} WHERE id = {}".format(5,ctx.author.id))
        conection.commit()
        await ctx.send(embed = embed)

@bot.command() 
async def embed(ctx,*,params = None):
  await ctx.message.delete()
  if params is None:
    await ctx.send(embed = discord.Embed(description = f'Задайте параметры',colour = 0xff1111))
  else:
   try:
    params = json.loads(params)
    embed = discord.Embed.from_dict(params)
   except json.decoder.JSONDecodeError:
    await ctx.send(embed = discord.Embed(description = f'Неправильные параметры json',colour = 0xff1111))
   else:
    await ctx.send(embed = embed)


@bot.command() 
async def say(ctx,*,text = None):
  if text is None:
    await ctx.send(embed = discord.Embed(description = f'Укажите текст',colour = 0xff1111))
  else:
    await ctx.send(text)

        
@bot.command() 
async def help(ctx):
  await ctx.message.delete()
  embed = discord.Embed(title = 'Команды бота:',color = discord.Color.purple())
  embed.add_field(inline = False,name = '** **',value = '```Модерация```\n'
    '**!ban [@user] [причина]** - Забанить участника.\n'
    '**!kick [@user] [причина]** - Кикнуть участника.\n'
    '**!mute [@user] [время (в минутах)] [причина]** - Замютить участника.\n' 
    '**!unban [@user]** - Баланс.\n'
    '**!unmute [@user]** - Размюутить участника.\n'
    '**!warn [@user] [причина]** - Дать варн участнику.\n'
    '**!unwarn [@user]** - Забрать последний варн.\n'
    )
    

  embed.add_field(name = '** **',value = '```Экономика сервера```\n'
    '**!$ [@user]** - Баланс.\n'
    '**!timely** - Ежедневная награда\n'
    '**!give [@user]** сумма - передать валюту\n'
    '**!shop** - Магазин ролей.\n'
    '**!мояроль [название цвет hex]** - Создает кастомную роль (Перед созданием сначала купите роль \'!мояроль\' в магазине) .\n'
    '**!addshop [цена id роли]** - Добавить роль в магазин.\n'
    '**!removeshop [id роли]** - Удалить роль из магазина.\n'
    '**!buy [номер роли]** - Покупает товар из магазина по заданному индексу.\n'
    '**!award [@user]** - Дать денег.\n' 
    '**!take [@user]** - Забрать деньги.\n'
    '**!trans [@user]** - Показывает транзакции участника .\n'
    '**!xp_give [@user] [количество]** - Дать опыт участнику.\n'
    '**!xp_take [@user] [количество]** - Забрать опыт участнику.\n'
    '**!lvl_give [@user] [количество]** - Дать уровень участнику.\n'
    '**!lvl_take [@user] [количество]** -Ззабрать уровень участнику.\n'
    )
    
    
  embed.add_field(inline = False,name = '** **',value = '```Информация для пользователя```\n'
    '**!help** - Список команд.\n'
    '**!top_cash** - Отображает список лидеров валюты бота.\n'
    '**!top_level** - Отображает список лидеров по уровню.\n'
    '**!top_online** - Отображает список лидеров по онлайну в войсе.\n'
    '**!top_reports** - Отображает список лидеров по одобренным репортам.\n'
    '**!inrole [@role]** - Перечисляет каждого человека с указанной ролью на этом сервере.\n'
    '**!uinfo [@user]** - Отображает список лидеров по одобренным репортам.\n'
    '**!stats [@user]** - Показывает базовую статистику для Flowerbot.\n'
    '**!user_warns [@user]** - Все нарушения участника.\n'
    '**!report [@user] причина** - Сделать жалобу на участника.\n'
    '**!serverinfo** - Показывает информацию о сервере, на котором работает бот.\n'
    '**!online [@user]** - Просмотр голосового онлайна.\n'
    '**!av [@user]** - Просмотр аватара.\n'
    '**!names [@user]** - Показывает историю никнеймов.\n'
    )  
  
  embed.add_field(inline = False,name = '** **',value = '```Кланы```\n'
   '**!create_clan [@user] [цвет в hex название клана]** - Создать клан.\n'
   '**!clan_invite [@user]** - Пригласить в клан.\n'    
   '**!clan_shop** - Клановый магазин.\n'
   '**!clan_award [сумма]** - Пополнить казну клана.\n'
   '**!set_clan_avatar [ссылка на картинку]** - Поменять клановую аватарку.\n'
   '**!set_clan_banner [ссылка на картинку]** - Поставить баннер клана.\n'
   '**!set_clan_description [текст]** - Сделать описание клана.\n'
   '**!set_clan_name [новое название клана]** - Изменить название клана.\n'
   '**!change_clan_color [цвет в hex]** - Изменить цвет клана.\n'
   '**!pay_for_clan** - Заплатить за клан.\n'
   '**!clan_leave** - Покинуть клан.\n'
   '**!clan_kick [@user]** - Кикнуть кого-то из клана.\n'
   '**!clan$ [@user]** - Посмотреть клановый баланс.\n'
   '**!convert [сумма]** - Конвертировать простую валюту в клановую.\n'
   '**!buy_slots [количество слотов]** - Купить слоти для клана.\n'
   '**!clan_member_award [@user]** - Пополнить клановый баланс.\n'
   '**!clan_member_take [@user]** - Забрать клановую валюту.\n'
   '**!del_clan [@роль]** - Удалить клан.\n'
   )
  
  embed.add_field(inline = False,name = '** **',value = '```Эмоции```\n'
    '**!bite [@user]** - Укусить кого-то\n'
    '**!cake [@user]** - Угостить кого-то тортом\n'
    '**!hug [@user]** - Вызывающе смотреть на кого-то\n'
    '**!five [@user]** - Дать пять кому-то\n'
    '**!kiss [@user]** - Поцеловать кого-то\n'
    '**!lick [@user]** - Лизнуть кого-то\n'
    '**!pat [@user]** - Погладить кого-то\n'
    '**!poke [@user]** - Тыкать в кого-то\n'
    '**!punch [@user]** - Ударить кого-то\n'
    '**!slap [@user]** - Дать пощечину кому-то\n')
  
  embed.add_field(inline = False,name = '** **',value = '```Прочее```\n' 
    '**!girl [@user]** - Дать женскую роль.\n'
    '**!private_room [@user] [название канала]** - Создать частную комнату.\n'
    '**!say [текст]** - Написать от имени бота.\n'
    '**!embed [параметры json]** - Сделать кастомный ембед.' 
    )
  embed.set_footer(text = 'v 1.0.1 by Miha')  
  await ctx.send(embed = embed)

bot.run('TOKEN')



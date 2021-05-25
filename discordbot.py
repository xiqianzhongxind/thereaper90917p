import discord
import sqlite3
from database_user import Database
import os
import requests
from discord.ext import commands, tasks



client = commands.Bot(command_prefix = commands.when_mentioned_or("!"))



@client.event
async def on_ready():
    await client.change_presence(activity= discord.Game("The Witcher 3"))
    print("Bot is Ready. ")

# member has joined server
@client.event
async def on_member_join(member):
    print(f'{member} has joined the server')

# member has left server
@client.event
async def on_member_remove(member):
    print(f'{member} has left the server')

# check ping of bot
@client.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)}.ms')

# generate random quote
@client.command()
async def random(ctx):
	url = ('https://api.quotable.io/random')
	response = requests.get(url)
	quote = response.json()
	quoteContent = quote['content']
	quoteAuthor = quote['author']
	await ctx.send(f'> {quoteContent} \n— {quoteAuthor}')


############################################### TRELLO CLONE ###################################################
@client.event
async def on_message(message):
     conn = sqlite3.connect('database.db')

     c = conn.cursor()


     def insert_emp(emp):
         with conn:
            c.execute("INSERT INTO needs VALUES (:need, :command, :complete, :completed)", {'need': emp.need, 'command': emp.command, 'complete':emp.complete,'completed':emp.completed})


     def remove_emp(emp):
         with conn:
            c.execute("DELETE from needs WHERE need= :need AND command = :command",
                  {'need': emp.need, 'command': emp.command})
     def view_data():
        with conn:
            c.execute("SELECT * FROM needs")
            zlist =[]
            items =  c.fetchall()
            for item in items:
                t = str(item[1]).replace('[','') +" Created By: " + str(item[2]).replace('[','') + ":   Completed By: "+ str(item[3]).replace('[','') 
                zlist.append(f'Needed: {t} ')

            new_string=str(zlist).replace("['","").replace("]","").replace("', ' ",'\n').replace("', '",'\n')
            return new_string
       
     def update_complete(emp, completed):
            with conn:
                    c.execute("""UPDATE needs SET completed = :completed
                         WHERE need = :need AND command = :command""",
                    {'need': emp.need, 'command': emp.command, 'completed': completed})
     
     
     if message.author.bot:
        return
     if message.content.startswith('!add'):
        search = message.content.replace('!add','')
        add_data = Database("need",search ,message.author.name,'')
        print(message.author.name)
        insert_emp(add_data)
        embed = discord.Embed(
        colour = discord.Colour.dark_grey(),
        title = ("Added the following feature to be done"),
        description= (f'{search}')
            )
        await message.channel.send(embed=embed)
                
     if message.content.startswith('!view'):
        embed = discord.Embed(
        colour = discord.Colour.dark_grey(),
        title = ("Bot Stuff Needed to be Done"),
        description= (f'{view_data()}')
            )
        await message.channel.send(embed=embed)
      
     if message.content.startswith('!remove'):
            input_del = message.content.replace('!remove','')
            delete_data = Database("need",input_del,'', '')
            remove_emp(delete_data)
            embed = discord.Embed(
            colour = discord.Colour.dark_grey(),
            title = ("Deleted the Following"),
            description= (f'{input_del}')
                )
            await message.channel.send(embed=embed)
     
     
     if message.content.startswith('!update'):
            input_data = message.content.replace('!update','')
            update_data = Database('need',input_data,'',message.author)
            update_complete(update_data,message.author.name)
            
           
                
        
    
     await client.process_commands(message)


client.run(os.environ['DISCORD_TOKEN']) #this uses a OS Environment Variable so the token isn't exposed

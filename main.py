import discord
from discord.ext import commands
import os, asyncio

os.environ['GOOGLE_APPLICATION_CREDENTIALS']

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

#Cogを登録
async def load():
    #path = os.path.dirname(__file__)
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')   #filename[:-3]は、拡張子.pyを取り除いたファイル名
            
async def main():
    await load()
    TOKEN = os.environ['DISCORD_TOKEN']
    await bot.start(TOKEN)      #bot.start()は、asyncioライブラリを使用してイベントループを明示的に作成する必要がある

asyncio.run(main())



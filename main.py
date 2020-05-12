import json
import discord
import ctrldb
from discord.ext import commands

# Discord アクセストークン読み込み
with open('token.json') as f:
    df = json.load(f)

token = df['bot']

# コマンドプレフィックスを設定
bot = commands.Bot(command_prefix='&')

@bot.command()
async def prefix(ctx, arg1='emp'):
    if arg1 == 'emp':
        await ctx.channel.send('引数が足りんやでー。')
    elif arg1.isdecimal():
        # prefixを探して返す
        guild = ctrldb.get_prefix(arg1, '518899666637553667')
        if guild is not None:
            await ctx.channel.send('{}のprefixは「{}」やで。'.format(guild.name, guild.prefix))
        else:
            await ctx.channel.send('そのIDのサーバは存在しないやで。')
    else:
        await ctx.channel.send('使い方が正しくないで〜。')

@bot.event
async def on_message(ctx):
    if ctx.author.bot:
        return

    await bot.process_commands(ctx)
    
bot.run(token)
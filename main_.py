### Made by Lipoic Team ###

import tokens
import discord
import discord_slash
from discord.ext import commands

bot = discord.Client()

@bot.s()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

bot.run(tokens.bot)
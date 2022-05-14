### Made by Lipoic Team ###

import tokens
import discord
import discord_slash
from discord.ext import commands
from discord.ext.commands import Context


bot = discord.Client()

@bot.s()
async def hello(ctx: Context, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

bot.run(tokens.bot)
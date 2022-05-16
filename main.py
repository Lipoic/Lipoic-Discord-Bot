import discord
import tokens

# prefix: str = "!"
# intents = discord.Intents.default()

bot: discord.Bot = discord.Bot()

@bot.event
async def on_ready():
    print("Log in as " + str(bot.user))

for file in [
    "hello",
    "clear"
    ]:
    bot.load_extension(f"cogs.commands.{file}")

bot.run(tokens.bot)
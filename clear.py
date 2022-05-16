import discord
from discord.ext import commands

class ClearCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.has_permissions(manage_messages=True)
    @discord.slash_command(description="Delete Message",guild_only=True)
    async def delete(self, ctx: discord.ApplicationContext,
    message_id: discord.Option(str, "輸入要刪除的訊息ID"),
    reason: discord.Option(str, "Reason", default= "無原因")):
        message: discord.Message= await ctx.fetch_message(str(message_id))
        await message.delete(reason=reason)

        embed=discord.Embed(title= "訊息刪除成功!", description= f"原因: {reason}")
        embed.set_author(name= message.author, icon_url= message.author.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)
    @delete.error
    async def delete_error(self, ctx: discord.ApplicationContext, error):
        embed=discord.Embed(title= "訊息刪除失敗!", description= f"Error:```{error}```", color= 0xe74c3c)
        await ctx.respond(embed=embed, ephemeral=True)

    @commands.has_permissions(manage_messages=True)
    @discord.slash_command(description="Delete Many Messages",guild_only=True)
    async def purge(self, ctx: discord.ApplicationContext,
    count: discord.Option(int, "輸入要刪除的訊息數量",min_value= 1,max_value= 2147483647),
    reason: discord.Option(str, "Reason", default= "無原因"),
    member: discord.Option(discord.Member, "要刪除的成員訊息", default= None)):
        def del_check(message: discord.Message):
            return message.author == member or member == None
        del_message = await ctx.channel.purge(limit= count, check=del_check)
        await ctx.respond(f"我成功刪除了`{len(del_message)}`則訊息!", ephemeral=True)
    @purge.error
    async def purge_error(self, ctx: discord.ApplicationContext, error):
        embed=discord.Embed(title= "訊息刪除失敗!", description= f"error:```{error}```", color= 0xe74c3c)
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(ClearCog(bot))
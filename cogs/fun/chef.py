from typing import List
import discord
from discord import ApplicationContext, Option, Embed
from discord.ext import commands

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.models import MemberType
    from core import LIPOIC


class ChefCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot

    @discord.slash_command(description="chef", guild_only=True)
    async def chef(
        self,
        ctx: ApplicationContext,
        member: Option(discord.Member, "成員")
    ):
        member: discord.Member = member
        memberDb = self.bot.db.Member

        memberDb.insert(user_id=member.id, chef_count=1).on_conflict(
            conflict_target=[memberDb.user_id],
            update={memberDb.chef_count: memberDb.chef_count + 1}
        ).execute()
        await ctx.respond(f"{member.mention} 已經被炒了!!")

    @discord.slash_command(description="顯示炒了多少次", guild_only=True)
    async def chef_rank(self, ctx: ApplicationContext):
        memberDb = self.bot.db.Member

        data: 'List[MemberType]' = memberDb.select().order_by(
            memberDb.chef_count.desc()
        ).limit(10).execute()

        await ctx.respond(embed=discord.Embed(title="排行榜", description="\n".join([
            f"`{index + 1}.` <@{data.user_id}>: {data.chef_count}次" for index,
            data in enumerate(data)
        ]) or "Emm 沒有人被炒過ㄟ!!"))


def setup(bot):
    bot.add_cog(ChefCog(bot))

from typing import List, Optional
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
        member: Option(discord.Member, "要電的電神"),
        message: Option(str, "電人的訊息", default='')
    ):
        member: discord.Member = member
        memberDb = self.bot.db.Member

        memberDb.insert(user_id=member.id, chef_count=1).on_conflict(
            conflict_target=[memberDb.user_id],
            update={memberDb.chef_count: memberDb.chef_count + 1}
        ).execute()

        data: MemberType = memberDb.get_or_none(memberDb.user_id == member.id)

        await ctx.respond(f"{member.mention} 好電! {message} 已經被廚了{data.chef_count}次!")

    @discord.slash_command(description="電神排行榜", guild_only=True)
    async def chef_rank(self, ctx: ApplicationContext):
        memberDb = self.bot.db.Member

        data: 'List[MemberType]' = memberDb.select().order_by(
            memberDb.chef_count.desc()
        ).limit(10).execute()

        await ctx.respond(embed=discord.Embed(title="電神排行榜", description="\n".join([
            f"`{index + 1}.` <@{data.user_id}>: {data.chef_count}次" for index,
            data in enumerate(data)
        ]) or "Emm 沒有人被炒過ㄟ!!"))


def setup(bot):
    bot.add_cog(ChefCog(bot))

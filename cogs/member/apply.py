from typing import List
import discord
from discord import ChannelType, Embed
from discord.ext import commands

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.models import MemberType
    from core import LIPOIC
    from core.types.MemberApply import EventData


class MemberApplyCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot

    @discord.Cog.listener()
    async def on_new_apply(self, data: 'EventData'):
        apply_channel: discord.TextChannel = self.bot.get_channel(
            984272090565849098  # ID just for test
        )
        embed = Embed(title=f"第{data.ID}號應徵者")
        embed.add_field(name="自介:", value=data.selfIntro, inline=False)
        embed.add_field(name="目前身分:", value=data.identity, inline=False)
        embed.add_field(name="簡歷:", value=data.CV, inline=False)
        embed.add_field(name="加入原因:", value=data.reason, inline=False)
        embed.add_field(name="想法或願景:", value=data.thoughts, inline=False)
        chinese_num = ["一", "二", "三"]
        embed.add_field(name="欲申請的職位:", value="\n".join([
            f"第{chinese_num[index]}順位:```{job}```" for index,
            job in enumerate(data.jobs)
        ]), inline=False)

        if data.remark:
            embed.add_field(name="備註:", value=data.remark, inline=False)

        apply_thread = await apply_channel.create_thread(
            name=f"編號 {data.ID} | 申請 {data.jobs[0]}",
            type=ChannelType.public_thread,
            reason=f"編號#{data.ID}應徵申請"
        )
        await apply_thread.send(embed=embed)


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

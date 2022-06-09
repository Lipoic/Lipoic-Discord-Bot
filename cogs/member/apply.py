from typing import List
import discord
from discord import ApplicationContext, Option, Embed
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
        apply_message = f"""第{data.ID}號應徵者:
        自介:```
        {data.selfIntro}```
        目前身分:{data.identity}
        簡歷:```
        {data.CV}```
        加入原因:```
        {data.reason}```
        想法或願景:```
        {data.thoughts}```
        欲申請的職位:
        """.join([
            f"第`{index + 1}`順位:```{job}```" for index,
            job in enumerate(data.jobs)
        ])
        apply_thread = await apply_channel.create_thread(f"編號{data.ID}|申請{data.jobs[0]}", apply_message)


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

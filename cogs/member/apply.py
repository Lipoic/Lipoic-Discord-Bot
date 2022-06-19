import discord
import random
from discord import ChannelType, Embed, ButtonStyle, Interaction
from discord.ui import View, Button

from typing import TYPE_CHECKING
from string import ascii_letters, digits


if TYPE_CHECKING:
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
        embed = Embed(title=f"第{data.ID}號應徵者", description=f"申請時間:\n`{data.time}`")
        embed.add_field(name="自介:", value=data.selfIntro, inline=False)
        embed.add_field(name="目前身分:", value=data.identity, inline=False)
        embed.add_field(name="簡歷:", value=data.CV, inline=False)
        embed.add_field(name="加入原因:", value=data.reason, inline=False)
        embed.add_field(name="想法或願景:", value=data.thoughts, inline=False)
        embed.add_field(name="欲申請的職位:", value="\n".join([
            f"第{['一', '二', '三'][index]}順位:```{job}```" for index,
            job in enumerate(data.jobs)
        ]), inline=False)

        if data.remark:
            embed.add_field(name="備註:", value=data.remark, inline=False)

        apply_thread = await apply_channel.create_thread(
            name=f"編號 {data.ID} | 申請 {data.jobs[0]}",
            type=ChannelType.public_thread,
            reason=f"編號#{data.ID}應徵申請"
        )
        applyDb = self.bot.db.MemberApply

        async def button_callback(interaction: Interaction):
            if interaction.custom_id == "success":
                code_str = "".join(random.sample(ascii_letters + digits, 6))
                embed = Embed(
                    title=f"申請成功，驗證碼:`{code_str}`",
                    description=f"由{interaction.user.mention}所審核的申請"
                )
                await interaction.channel.send(embed=embed)
                applyDb.update(code=code_str).where(applyDb.thread_id == interaction.channel_id).execute()

            else:
                embed = Embed(title="申請駁回", description=f"由{interaction.user.mention}所審核的申請")
                await interaction.channel.send(embed=embed)

            apply_button = Button(style=ButtonStyle.gray, label="面試已結束", disabled=True)
            await interaction.response.edit_message(view=View(apply_button))

        success_button = Button(style=ButtonStyle.green, label="申請通過", custom_id="success")
        success_button.callback = button_callback

        fail_button = Button(style=ButtonStyle.red, label="申請駁回", custom_id="fail")
        fail_button.callback = button_callback

        view = View(success_button, fail_button, timeout=None)
        await apply_thread.send(embed=embed, view=view)

        applyDb.insert(
            thread_id=apply_thread.id,
            email=data.email,
            job=data.jobs
        ).execute()


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

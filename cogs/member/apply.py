import discord
import random
from discord import ChannelType, Embed, ButtonStyle, SelectOption, Interaction, ApplicationContext, Option
from discord.ui import View, Button, Select

from typing import TYPE_CHECKING
from string import ascii_letters, digits


if TYPE_CHECKING:
    from core import LIPOIC
    from core.types.MemberApply import EventData
    from core.models import MemberApply


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
        applyDB = self.bot.db.MemberApply

        async def button_callback(interaction: Interaction):
            print(interaction.data)
            apply_status = list(interaction.custom_id)
            print(apply_status)
            # if apply_status[1]:
            #     code_str = "".join(random.sample(ascii_letters + digits, 6))
            #     embed = Embed(
            #         title=f"申請成功，驗證碼:`{code_str}`",
            #         description=f"由{interaction.user.mention}所審核的申請"
            #     )
            #     await interaction.channel.send(embed=embed)
            #     applyDB.update(apply_job=apply_job).where(applyDB.thread_id == interaction.channel_id).execute()
            # else:
            #     embed = Embed(title="申請駁回", description=f"由{interaction.user.mention}所審核的申請")
            #     await interaction.channel.send(embed=embed)

            # apply_button = Button(style=ButtonStyle.gray, label="面試已結束", disabled=True)
            # await interaction.response.edit_message(view=View(apply_button))

        # success_button = Button(style=ButtonStyle.green, label="申請通過", custom_id="success")
        # success_button.callback = button_callback

        # fail_button = Button(style=ButtonStyle.red, label="申請駁回", custom_id="fail")
        # fail_button.callback = button_callback

        async def select_callback(interaction: Interaction):
            print(interaction.data)
            job_button = Button(
                style=ButtonStyle.gray,
                label=interaction.data['values'][0],
                disabled=True
            )
            success_button = Button(
                style=ButtonStyle.green,
                label="通過",
                custom_id=f"[{interaction.data['values'][0]}, True]"
            )
            success_button.callback = button_callback
            fail_button = Button(
                style=ButtonStyle.red,
                label="駁回",
                custom_id=f"[{interaction.data['values'][0]}, False]"
            )
            fail_button.callback = button_callback
            apply: MemberApply = applyDB.get_or_none(applyDB.thread_id == interaction.channel_id)
            job_select = Select(
                placeholder="請選擇要審核的職位",
                options=[SelectOption(label=job) for job in apply.job.remove(interaction.data['values'][0])],
                custom_id="job_select",
                row=1
            )
            end_button = Button(
                style=ButtonStyle.gray,
                label="結束審核",
                custom_id=f"{interaction.data['values'][0]}_fail"
            )
            fail_button.callback = button_callback
            job_select.callback = select_callback
            view = View(job_button, success_button, fail_button, job_select, timeout=None)
            await interaction.response.edit_message(view=view)

        job_select = Select(
            placeholder="請選擇要審核的職位",
            options=[SelectOption(label=job) for job in data.jobs],
            custom_id="job_select"
        )
        job_select.callback = select_callback
        view = View(job_select, timeout=None)

        # for index, job in enumerate(data.jobs):
        #     name_button = Button(style=ButtonStyle.gray, label=job, disabled=True, row=index)
        #     success_button = Button(style=ButtonStyle.green, label="通過", custom_id=f"job{index+1}_success", row=index)
        #     success_button.callback = button_callback
        #     fail_button = Button(style=ButtonStyle.red, label="駁回", custom_id=f"job{index+1}_fail", row=index)
        #     fail_button.callback = button_callback
        #     view.add_item(name_button)
        #     view.add_item(success_button)
        #     view.add_item(fail_button)

        # end_button = Button(style=ButtonStyle.gray, label="結束審核", custom_id="apply_end", row=3)
        # end_button.callback = button_callback
        # view.add_item(end_button)
        await apply_thread.send(embed=embed, view=view)

        applyDB.insert(
            thread_id=apply_thread.id,
            email=data.email,
            job=data.jobs,
            apply_job=[]
        ).execute()

    @discord.slash_command(description="apply", guild_only=True)
    async def apply(
        self,
        ctx: ApplicationContext,
        code: Option(str, "申請驗證碼")
    ):
        applyDB = self.bot.db.MemberApply
        apply = applyDB.get_or_none(applyDB.code == code)
        if apply:
            embed = Embed(
                title=f"驗證成功!",
                description=f"您所申請的職位為:" + "\n".join(
                    f"```{job}```" for job in apply.job
                ))
        else:
            embed = Embed(title="驗證失敗", description="未知的驗證碼，如有疑問，請洽人事組詢問", color=0xe74c3c)

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

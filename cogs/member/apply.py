import discord
from discord import (
    ChannelType, Embed, ButtonStyle,
    Interaction, ApplicationContext, Option, TextChannel, User
)
from discord.ui import View, Button

from typing import List, TYPE_CHECKING, Literal, Optional

from utils.utils import ShallowData
from core.types.MemberApply import jobsType, EventData

if TYPE_CHECKING:
    from core import LIPOIC
    from core.models import MemberApply


class MemberApplyCog(discord.Cog):
    def __init__(self, bot: 'LIPOIC'):
        self.bot = bot

    @discord.Cog.listener()
    async def on_new_apply(self, data: EventData):
        applyDB = self.bot.db.MemberApply
        jobs = data.jobs

        allow_users: List[User] = []
        select_job: ShallowData[Optional[jobsType]] = ShallowData(None)
        rank: ShallowData[Literal[1, 2, 3]] = ShallowData(0)

        apply_channel: TextChannel = self.bot.get_channel(
            984272090565849098  # ID just for test
        )
        embed = discord.Embed(
            title=f"第{data.ID}號應徵者", description=f"申請時間:\n`{data.time}`"
        )
        embed.add_field(name="自介:", value=data.selfIntro, inline=False)
        embed.add_field(name="目前身分:", value=data.identity, inline=False)
        embed.add_field(name="簡歷:", value=data.CV, inline=False)
        embed.add_field(name="加入原因:", value=data.reason, inline=False)
        embed.add_field(name="想法或願景:", value=data.thoughts, inline=False)
        embed.add_field(name="欲申請的職位:", value="\n".join([
            f"第{['一', '二', '三'][index]}順位: ```{job}```" for index,
            job in enumerate(jobs)
        ]), inline=False)

        if data.remark:
            embed.add_field(name="備註:", value=data.remark, inline=False)

        apply_thread = await apply_channel.create_thread(
            name=f"編號 {data.ID} | 申請 {jobs[0]}",
            type=ChannelType.public_thread,
            reason=f"編號#{data.ID}應徵申請"
        )
        # applyDB.insert(
        #     thread_id=apply_thread.id,
        #     email=data.email,
        # ).execute()

        stage_button = Button(
            style=ButtonStyle.gray,
            label='人事一審',
            disabled=True,
            row=0
        )

        (stage_success := Button(
            style=ButtonStyle.green, label="通過", row=1
        )).callback = lambda x: button_callback(x, 'PASS')
        (stage_fail := Button(
            style=ButtonStyle.red, label="駁回", row=1
        )).callback = lambda x: button_callback(x, 'FAIL')

        async def close():
            if select_job() is not None:
                embed.clear_fields()
                embed.add_field(name='通過職位', value=select_job(), inline=False)
                embed.add_field(name='驗證碼', value='test_test', inline=False)
                await apply_thread.send(embed=embed)
            await message.edit(view=View(
                Button(style=ButtonStyle.gray, label="面試已結束", disabled=True)
            ))
            await apply_thread.edit(
                name=f"{'✅' if select_job() else '❌'} {apply_thread.name}",
                archived=True, locked=True
            )

        async def button_callback(interaction: Interaction, type: Literal['PASS', 'FAIL']):
            if interaction.user not in allow_users:
                allow_users.append(interaction.user)

            if rank != 0 and type == 'PASS':
                select_job.data = jobs[rank() - 1]

            if rank == len(jobs) or select_job() is not None or (rank == 0 and type == 'FAIL'):
                return await close()

            rank.data += 1
            stage_button.label = f'組長二審: {jobs[rank() - 1]}'

            await interaction.response.edit_message(view=View(stage_button, stage_success, stage_fail, timeout=None))

        message = await apply_thread.send(embed=embed, view=View(stage_button, stage_success, stage_fail, timeout=None))

    @discord.slash_command(description="apply", guild_only=True)
    async def apply(
        self,
        ctx: ApplicationContext,
        code: Option(str, "申請驗證碼")
    ):
        applyDB = self.bot.db.MemberApply
        apply: MemberApply = applyDB.get_or_none(applyDB.code == code)

        if apply:
            embed = Embed(
                title="驗證成功!",
                description=''.join([
                    "您通過的身分為: ```",
                    "\n".join([
                        k for k, v in dict(apply.apply_status).items() if v
                    ]),
                    "```"
                ])
            )
            apply.update(code=None).execute()
        else:
            embed = Embed(
                title="驗證失敗", description="未知的驗證碼，如有疑問，請洽人事組詢問", color=0xe74c3c
            )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

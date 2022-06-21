import discord
import random
from discord import (
    ChannelType, Embed, ButtonStyle, SelectOption,
    Interaction, ApplicationContext, Option, TextChannel, User
)
from discord.ui import View, Button, Select

from typing import Dict, List, TYPE_CHECKING, Literal, Optional
from string import ascii_letters, digits
from core.types.MemberApply import EventData


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
        select_jobs: Dict[str, Optional[bool]] = {k: None for k in data.jobs}
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

        async def select_callback(interaction: Interaction, **kwargs: str):
            if (select := kwargs.get('select', None)) is None and len(interaction.data['values']) > 0:
                select = jobs[int(interaction.data['values'][0])]

            async def button_callback(type: Literal['TRUE', 'FALSE', 'END'], interaction: Interaction):
                if type == "END":
                    if True in select_jobs.values():
                        code_str = ''.join(random.sample(
                            ascii_letters + digits, k=6
                        ))
                        # TODO add check code write db
                        embed = Embed(
                            title=f"申請成功，驗證碼: `{code_str}`",
                            description=f"由 {', '.join([user.mention for user in allow_users])} 所審核的申請"
                        )
                        await interaction.channel.send(embed=embed, mention_author=False)
                    else:
                        await interaction.response.edit_message(
                            embed=Embed(
                                title="申請駁回",
                                description=f"由{interaction.user.mention}所審核的申請"
                            ),
                            view=View(
                                Button(
                                    style=ButtonStyle.gray,
                                    label="面試已結束", disabled=True
                                )
                            )
                        )

                else:
                    if interaction.user not in allow_users:
                        allow_users.append(interaction.user)
                    select_jobs[select] = type == 'TRUE'
                    await select_callback(interaction, select=select)

                apply: MemberApply = applyDB.get_or_none(
                    applyDB.thread_id == interaction.channel_id
                )
                apply.update(apply_status=select_jobs)
                apply.save()

            job_button = Button(
                style=ButtonStyle.gray,
                label=select,
                disabled=True,
                row=0
            )
            (success_button := Button(
                style=ButtonStyle.green,
                label="標示通過",
                row=1
            )).callback = lambda x: button_callback('TRUE', x)
            (fail_button := Button(
                style=ButtonStyle.red,
                label="標示駁回",
                row=1
            )).callback = lambda x: button_callback('FALSE', x)
            (job_select := Select(
                placeholder="請選擇要審核的職位",
                options=[
                    SelectOption(
                        label=k, value=str(i),
                        emoji='✅' if (
                            v := select_jobs[k]
                        ) else v if v is None else '❌',
                        default=k is select
                    ) for i, k in enumerate(jobs)
                ],
                row=2
            )).callback = select_callback
            (end_button := Button(
                style=ButtonStyle.gray,
                label="結束審核",
                row=3
            )).callback = lambda x: button_callback('END', x)

            await interaction.response.edit_message(view=View(
                job_button, success_button, fail_button, end_button,
                job_select, timeout=None
            ))

        (job_select := Select(
            placeholder="請選擇要審核的職位",
            options=[
                SelectOption(label=job, value=str(index)) for index,
                job in enumerate(jobs)
            ],
            custom_id="job_select"
        )).callback = select_callback

        applyDB.insert(
            thread_id=apply_thread.id,
            email=data.email,
            job=jobs,
            apply_status=[]
        ).execute()

        await apply_thread.send(embed=embed, view=View(job_select, timeout=None))

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
                    "\n".join(job for job in apply.job),
                    "```"
                ])
            )
        else:
            embed = Embed(
                title="驗證失敗", description="未知的驗證碼，如有疑問，請洽人事組詢問", color=0xe74c3c
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(description="test", guild_only=True)
    async def test_apply(self, ctx: ApplicationContext):
        self.bot.dispatch(
            'new_apply',
            EventData(
                email='test@gmail.com',
                selfIntro='test',
                identity='test',
                CV='test',
                reason='test',
                thoughts='test',
                jobs=['美術 - 網站界面設計', '美術 - 網站界面設計2'],
                time='100',
                ID=100,
                remark='test'
            )
        )
        await ctx.respond('test')


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

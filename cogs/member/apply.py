import inspect
import discord
from discord import (
    ChannelType, Embed, ButtonStyle,
    Interaction, ApplicationContext, Option, TextChannel, User, ui
)
from discord.ui import View, Button, Item

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

        apply_channel: TextChannel = self.bot.get_channel(
            990449282190553089  # ID just for test
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

        message = await apply_thread.send(embed=embed, view=ApplyView(self.bot))

        applyDB.insert(
            thread_id=apply_thread.id, email=data.email, state=f'{message.id}-0-', data=data._asdict()
        ).execute()

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
                description=f"您通過的身分為: `{apply.pass_job}`"
            )
            applyDB.update(code=None).where(
                applyDB.thread_id == apply.thread_id).execute()
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
                time='2022/6/9 上午 10:45:32',
                ID=100,
                remark='test'
            )
        )
        await ctx.respond('test')

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ApplyView(self.bot))


class ApplyView(View):
    def __init__(self, bot: 'LIPOIC'):
        super().__init__(timeout=None)

        self.bot = bot
        for _, func in reversed(inspect.getmembers(self)):
            if isinstance(func, Item):
                self.add_item(func)

    async def button_callback(self, interaction: Interaction, _type: Literal['PASS', 'FAIL']):
        applyDB = self.bot.db.MemberApply
        channel_id = interaction.channel_id
        channel = await self.bot.get_or_fetch_channel(channel_id)

        dbData: MemberApply = applyDB.get_or_none(thread_id=channel_id)
        data = EventData(**dbData.data)
        jobs = data.jobs
        message_id, rank, allow_users = str(dbData.state).split('-')
        rank = int(rank)
        allow_users = [
            str(_.id if (_ := self.bot.get_user(id)) else id) for id in allow_users.split(',') if id
        ]
        message = self.bot.get_message(int(message_id))

        if (user_id := str(interaction.user.id)) not in allow_users:
            allow_users.append(user_id)

        if (rank == 0 and _type == 'FAIL') or (rank != 0 and _type == 'PASS'):
            await message.edit(view=View(
                Button(style=ButtonStyle.gray, label="面試已結束", disabled=True)
            ))
            if (select_job := jobs[rank - 1]) and rank != 0:
                applyDB.update(pass_job=select_job).where(
                    applyDB.thread_id == channel_id
                ).execute()
                embed = discord.Embed(
                    title=f"第 {data.ID} 號應徵者", description=f"申請時間:\n`{data.time}`"
                )
                code = self.bot.db.create_apply_member_check_code(
                    channel_id
                )
                embed.add_field(name='審核人員', value=', '.join(
                    [f'<@{user}>' for user in allow_users]
                ), inline=False)
                embed.add_field(name='通過職位', value=select_job, inline=False)
                embed.add_field(name='驗證碼', value=f'`{code}`', inline=False)
                embed.add_field(name='email', value=data.email, inline=False)
                await channel.send(embed=embed)
            return await channel.edit(
                name=f"{'✅' if select_job else '❌'} {channel.name}",
                archived=True, locked=True
            )

        applyDB.update(
            state=f'{message_id}-{rank + 1}-{",".join(allow_users)}'
        ).where(applyDB.thread_id == channel_id).execute()

        (stage_button := self.stage_button).label = f'組長二審: {jobs[rank]}'

        await interaction.response.edit_message(view=View(
            stage_button, self.stage_success, self.stage_fail,
            timeout=None
        ))

    async def stage_success_callback(self, interaction: ApplicationContext):
        await self.button_callback(interaction, 'PASS')

    async def stage_fail_callback(self, interaction: ApplicationContext):
        await self.button_callback(interaction, 'FAIL')

    @property
    def stage_button(self):
        return Button(
            style=ButtonStyle.gray, label='人事一審', disabled=True, custom_id='apply_stage_button', row=0
        )

    @property
    def stage_success(self):
        (stage_success := Button(
            custom_id='apply_stage_success', style=ButtonStyle.green, label='通過', row=1
        )).callback = self.stage_success_callback

        return stage_success

    @property
    def stage_fail(self):
        (stage_fail := Button(
            custom_id='apply_stage_fail', style=ButtonStyle.red, label='駁回', row=1
        )).callback = self.stage_fail_callback

        return stage_fail


def setup(bot):
    bot.add_cog(MemberApplyCog(bot))

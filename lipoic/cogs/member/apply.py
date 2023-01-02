import inspect
import json
from typing import TYPE_CHECKING, Any, Literal, Optional

import aiohttp
import discord
from discord import (
    ChannelType,
    Embed,
    ButtonStyle,
    Interaction,
    ApplicationContext,
    Option,
    TextChannel,
)
from discord.ui import View, Button, Item

from lipoic import BaseCog
from lipoic.core.types.MemberApply import EventData

if TYPE_CHECKING:
    from lipoic.core import LIPOIC
    from lipoic.core.models import MemberApply


class MemberApplyEmailData:
    def __init__(self, **kwargs: Any):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        iters = dict((x, y) for x, y in self.__dict__.items() if x[:2] != "__")

        for x, y in iters.items():
            yield x, y

    email: str
    date: str
    team: Optional[str]
    position: Optional[str]
    HR_DC_Id: Optional[str]
    HR_DC_Name: Optional[str]
    check_code: Optional[str]
    allow: bool


class MemberApplyCog(BaseCog):
    @discord.Cog.listener()
    async def on_new_apply(self, data: EventData):
        applyDB = self.db.MemberApply
        job = data.job

        apply_channel: TextChannel = self.bot.get_channel(self.bot.apply_channel_id)
        embed = discord.Embed(
            title=f"第{data.ID}號應徵者", description=f"申請時間:\n`{data.time}`"
        )
        embed.add_field(name="自介:", value=data.selfIntro, inline=False)
        embed.add_field(name="目前身分:", value=data.identity, inline=False)
        embed.add_field(name="簡歷:", value=data.CV, inline=False)
        embed.add_field(name="加入原因:", value=data.reason, inline=False)
        embed.add_field(name="想法或願景:", value=data.thoughts, inline=False)
        embed.add_field(name="欲申請的職位:", value=job, inline=False)

        if data.remark:
            embed.add_field(name="備註:", value=data.remark, inline=False)

        apply_thread = await apply_channel.create_thread(
            name=f"編號 {data.ID} | 申請 {job}",
            type=ChannelType.public_thread,
            reason=f"編號#{data.ID}應徵申請",
        )
        message = await apply_thread.send(
            f"<@&{self.bot.hr_role_id}>", embed=embed, view=ApplyView(self.bot)
        )

        applyDB.insert(
            thread_id=apply_thread.id, message_id=message.id, data=data._asdict()
        ).execute()

    @discord.slash_command(description="開啟面試頻道，並等待組長開始面試", guild_only=True)
    async def meeting(self, ctx: ApplicationContext, code: Option(str, "申請驗證碼")):
        applyDB = self.db.MemberApply
        apply: MemberApply = applyDB.get_or_none(applyDB.code == code)
        if apply:
            data = apply.data
            meeting_member = ctx.author
            meeting_category: discord.CategoryChannel = (
                await self.bot.get_or_fetch_channel(
                    self.bot.meeting_category_id
                )
            )
            meeting_channel = await meeting_category.create_text_channel(
                name=f"編號{data['ID']}-面試頻道",
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # noqa: E501
                    meeting_member: discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True
                    )
                },
                topic=f"被審核人員: {meeting_member.mention}\n申請職位: {data['job']}"
            )
            meeting_embed = discord.Embed(
                title=f"第{data['ID']}號應徵者", description=f"申請時間:\n`{data['time']}`"
            )
            meeting_embed.add_field(name="欲申請的職位:", value=data['job'], inline=False)
            await meeting_channel.send(meeting_member.mention, embed=meeting_embed)

            embed = Embed(
                title="創建成功!",
                description=f"已成功創建在{meeting_channel.mention}，請等候相關人員審核。"
            )
            applyDB.update(code=None).where(
                applyDB.thread_id == apply.thread_id
            ).execute()
        else:
            embed = Embed(
                title="驗證失敗", description="未知的驗證碼，如有疑問，請洽人事組詢問", color=0xE74C3C
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ApplyView(self.bot))

    async def send_apply_member_email(self, data: MemberApplyEmailData):
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            async with session.post(
                self.bot.configs["GOOGLE_SCRIPT_URL"],
                json={
                    "authorization": self.bot.configs["memberApplyServerToken"],
                    **dict(data),
                },
            ) as resp:
                data = await resp.text(encoding="utf8")
                try:
                    data = json.loads(data)
                except KeyError:
                    ...
                return data


class ApplyView(View):
    def __init__(self, bot: "LIPOIC"):
        super().__init__(timeout=None)

        self.bot = bot
        for _, func in reversed(inspect.getmembers(self)):
            if isinstance(func, Item):
                self.add_item(func)

    async def button_callback(
        self, interaction: Interaction, _type: Literal["PASS", "FAIL"]
    ):
        applyDB = self.bot.db.MemberApply
        channel_id = interaction.channel_id
        channel = await self.bot.get_or_fetch_channel(channel_id)

        dbData: MemberApply = applyDB.get_or_none(thread_id=channel_id)
        data = EventData(**dbData.data)
        job = data.job
        message_id = dbData.message_id
        message = self.bot.get_message(message_id)
        if not message:
            message = await channel.fetch_message(message_id)

        await message.edit(
            view=View(Button(style=ButtonStyle.gray, label="面試已結束", disabled=True))
        )
        email_data = MemberApplyEmailData(
            email=data.email,
            date=data.time,
            allow=False,
            job=job,
        )
        if _type == "PASS":  # 初審通過
            applyDB.update(pass_job=job).where(
                applyDB.thread_id == channel_id
            ).execute()
            embed = discord.Embed(
                title=f"第 {data.ID} 號應徵者", description=f"申請時間:\n`{data.time}`"
            )
            code = self.bot.db.create_apply_member_check_code(channel_id)
            embed.add_field(name="Email", value=f"```{data.email}```", inline=False)
            embed.add_field(name="通過職位", value=f"```{job}```", inline=False)
            embed.add_field(name="驗證碼", value=f"||`{code}`||", inline=False)
            await channel.send(embed=embed)
            email_data.allow = True
            email_data.team = job.split(" - ")[0]
            email_data.position = job
            email_data.check_code = code

        msg = await channel.send("發送📧email 中...")
        try:
            code = (
                await MemberApplyCog(self.bot).send_apply_member_email(email_data)
            )["code"]
            if str(code) != "200":
                raise Exception()
        except:
            await msg.edit(f"📧email 發送失敗，<@&{self.bot.hr_role_id}>")
        else:
            await msg.edit("📧email 發送完成", delete_after=60)
        return await channel.edit(
            name=f"{'✅' if _type == 'PASS' else '❌'} {channel.name}",
            archived=True,
            locked=True,
        )

    async def stage_success_callback(self, interaction: ApplicationContext):
        await self.button_callback(interaction, "PASS")

    async def stage_fail_callback(self, interaction: ApplicationContext):
        await self.button_callback(interaction, "FAIL")

    @property
    def stage_button(self):
        return Button(
            style=ButtonStyle.gray,
            label="人事初審",
            disabled=True,
            custom_id="apply_stage_button",
            row=0,
        )

    @property
    def stage_success(self):
        (
            stage_success := Button(
                custom_id="apply_stage_success",
                style=ButtonStyle.green,
                label="通過",
                row=1,
            )
        ).callback = self.stage_success_callback

        return stage_success

    @property
    def stage_fail(self):
        (
            stage_fail := Button(
                custom_id="apply_stage_fail", style=ButtonStyle.red, label="駁回", row=1
            )
        ).callback = self.stage_fail_callback

        return stage_fail


def setup(bot: "LIPOIC"):
    bot.add_cog(MemberApplyCog(bot))

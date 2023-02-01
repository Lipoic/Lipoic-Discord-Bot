import datetime
import inspect
import asyncio
from typing import TYPE_CHECKING, Any, Literal, Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from string import Template
from pathlib import Path
import os
import io

import discord
from discord import (
    ChannelType,
    Embed,
    ButtonStyle,
    Interaction,
    ApplicationContext,
    Option,
    TextChannel,
    InputTextStyle,
)
from discord.ui import View, Button, Item, Modal, InputText

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
    time: str
    team: Optional[str]
    job: Optional[str]
    reason: Optional[str]
    HR_DC_Id: Optional[str]
    HR_DC_Name: Optional[str] = "tommy2131#3750"
    check_code: Optional[str]
    allow: bool

    def send(self, _type: Literal["Application", "Interview"]) -> None:
        """
        Return:
            None if send email success.
        Return Type:
            None
        Raise:
            Exception - send email fail.
        """
        content = MIMEMultipart()
        content["subject"] = "Lipoic 重要通知"
        content["from"] = os.getenv("HR_MAIL_ADDRESS")
        content["to"] = self.email

        mail_temp_data = (
            Path(__file__).parent
            / f"./{_type}_{'Pass' if self.allow else 'Reject'}ed_Response_Template.html"
        ).read_text(encoding="utf-8")
        template = Template(mail_temp_data)
        body = template.substitute(
            {  # pass
                "time": self.time,
                "team": self.team,
                "job": self.job,
                "hr_member": self.HR_DC_Name,
                "code": self.check_code if _type == "Application" else "",
            }
            if self.allow
            else {
                # reject
                "time": self.time,
                "reason": self.reason,
            }
        )
        self.html_file = io.StringIO(body)
        content.attach(MIMEText(body, "html"))
        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(os.getenv("HR_MAIL_ADDRESS"), os.getenv("HR_MAIL_PASSWORD"))
                smtp.send_message(content)
                return None
            except Exception as e:
                raise Exception(e)


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
            f"<@&{self.bot.hr_role_id}>",
            embed=embed,
            view=ApplyView(self.bot, "Application"),
        )

        applyDB.insert(
            thread_id=apply_thread.id, message_id=message.id, data=data._asdict()
        ).execute()

    @discord.slash_command(description="開啟面試頻道，並等待組長開始面試", guild_only=True)
    async def apply(self, ctx: ApplicationContext, code: Option(str, "申請驗證碼")):
        applyDB = self.db.MemberApply
        apply: MemberApply = applyDB.get_or_none(applyDB.code == code)
        if apply:
            data = apply.data
            meeting_member = ctx.author
            meeting_category: discord.CategoryChannel = (
                await self.bot.get_or_fetch_channel(self.bot.meeting_category_id)
            )
            meeting_channel = await meeting_category.create_text_channel(
                name=f"編號{data['ID']}-面試頻道",
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(
                        view_channel=False
                    ),  # noqa: E501
                    meeting_member: discord.PermissionOverwrite(
                        view_channel=True, send_messages=True
                    ),
                },
                topic=f"被審核人員: {meeting_member.mention}\n申請職位: {data['job']}",
            )
            meeting_embed = discord.Embed(
                title=f"第{data['ID']}號應徵者", description=f"申請時間:\n`{data['time']}`"
            )
            meeting_embed.add_field(name="欲申請的職位:", value=data["job"], inline=False)
            await meeting_channel.send(meeting_member.mention, embed=meeting_embed)

            embed = Embed(
                title="創建成功!", description=f"已成功創建在{meeting_channel.mention}，請等候相關人員審核。"
            )
            await ctx.respond(embed=embed, ephemeral=True)

            apply_thread = await self.bot.get_or_fetch_channel(apply.thread_id)
            await apply_thread.edit(
                name=f"❓ {apply_thread.name[2:]}",
                archived=False,
                locked=False,
            )
            embed = discord.Embed(
                title="面試頻道已被開啟", description=f"頻道: {meeting_channel.mention}"
            )
            meeting_message = await apply_thread.send(
                embed=embed,
                view=ApplyView(self.bot, "Interview"),
            )

            applyDB.update(
                meeting_channel_id=meeting_channel.id,
                meeting_message_id=meeting_message.id,
                meeting_time=int(datetime.datetime.now().timestamp()),
                meeting_member=meeting_member.id,
                code=None,
            ).where(applyDB.thread_id == apply.thread_id).execute()
        else:
            embed = Embed(
                title="驗證失敗", description="未知的驗證碼，如有疑問，請洽人事組詢問", color=0xE74C3C
            )
            await ctx.respond(embed=embed, ephemeral=True)

    @discord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ApplyView(self.bot, "Application"))
        self.bot.add_view(ApplyView(self.bot, "Interview"))
        self.bot.add_view(AddReasonView(self.bot))


class AddReasonView(View):
    def __init__(self, bot: "LIPOIC"):
        super().__init__(timeout=None)

        self.bot = bot
        for _, func in reversed(inspect.getmembers(self)):
            if isinstance(func, Item):
                self.add_item(func)
        self.on_double_check = False

    async def send_mail(self, interaction: Interaction):
        await interaction.message.delete()
        applyDB = self.bot.db.MemberApply
        channel_id = interaction.channel_id
        # channel = await self.bot.get_or_fetch_channel(channel_id)

        apply: MemberApply = applyDB.get_or_none(thread_id=channel_id)
        print(apply.meeting_channel_id)
        data = EventData(**apply.data)
        email_data = MemberApplyEmailData(
            email=data.email,
            time=data.time,
            reason=apply.reason,
            allow=False,
        )
        apply_state = "Interview" if apply.meeting_channel_id else "Application"
        channel = interaction.channel
        try:
            email_data.send(apply_state)
            await channel.send("📧email 發送完成", delete_after=60)
        except Exception as error:
            embed = discord.Embed(
                title="發送📧email失敗，請手動發送!", description=f"Error:```{error}```"
            )
            await channel.send(
                f"<@&{self.bot.hr_role_id}>",
                embed=embed,
                file=discord.File(email_data.html_file, filename="mail.html"),
            )
        return await channel.edit(
            name=f"""❌ {channel.name if apply_state == 'Application'
                else channel.name[2:]}""",
            archived=True,
            locked=True,
        )

    async def cancel(self, interaction: Interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(title="已取消!"),
            view=View(),
            delete_after=4,
        )
        self.on_double_check = False

    async def double_check(self, interaction: Interaction):
        (
            stage_success := Button(
                custom_id="send",
                style=ButtonStyle.green,
                label="確定送出",
            )
        ).callback = self.send_mail
        (
            stage_cancel := Button(
                custom_id="apply_stage_cancel", style=ButtonStyle.red, label="取消"
            )
        ).callback = self.cancel

        embed = discord.Embed(
            title="確認送出",
            description=f"""你確定要送出email嗎?
            > **此動作無法復原**
            操作將於<t:{int(datetime.datetime.now().timestamp()) + 60}:R>自動取消""",
        )

        hint = await interaction.response.send_message(
            embed=embed,
            view=View(stage_success, stage_cancel),
        )
        await asyncio.sleep(60)
        try:
            await hint.edit_original_message(
                embed=discord.Embed(title="已取消!"),
                view=View(),
                delete_after=4,
            )
            self.on_double_check = False
        except:
            pass

    async def add_reason_callback(self, interaction: Interaction):
        embed = Embed(
            title="新增駁回原因",
            description="請避免同時有兩個人輸入原因，以免衝突",
        )
        embed.add_field(name="原因", value=f"```{self.modal.children[0].value}```")
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("變更成功!", ephemeral=True, delete_after=8)
        self.modal.stop()

    async def button_callback(self, interaction: Interaction):
        if self.on_double_check:
            await interaction.response.send_message(
                embed=Embed(
                    title="已在確認中!",
                    description="請勿在雙重確認時點擊此按鈕!",
                ),
                ephemeral=True
            )
            return
        if interaction.custom_id == "add_reason":
            old_reason = interaction.message.embeds[0].fields[0].value[3:-3]
            self.modal = Modal(
                InputText(
                    label="請輸入原因", placeholder="原因",
                    value=old_reason,
                    style=InputTextStyle.long
                ),
                title="請輸入原因",
            )
            self.modal.callback = self.add_reason_callback
            await interaction.response.send_modal(self.modal)
            # await self.modal.wait()
        else:
            self.on_double_check = True
            await self.double_check(interaction)

    @property
    def send_email_button(self):
        (
            send_email := Button(
                custom_id="send_email",
                style=ButtonStyle.green,
                label="發送email",
                row=0,
            )
        ).callback = self.button_callback

        return send_email

    @property
    def add_reason_button(self):
        (
            add_reason := Button(
                custom_id="add_reason",
                style=ButtonStyle.green,
                label="變更原因",
                row=0,
            )
        ).callback = self.button_callback

        return add_reason


class ApplyView(View):
    def __init__(self, bot: "LIPOIC", state: Literal["Application", "Interview"]):
        super().__init__(timeout=None)

        self.bot = bot
        self.apply_state = state
        for _, func in reversed(inspect.getmembers(self)):
            if isinstance(func, Item):
                self.add_item(func)
        self.on_double_check: bool = False

    async def cancel(self, interaction: Interaction):
        await interaction.response.edit_message(
            embed=discord.Embed(title="已取消!"),
            view=View(),
            delete_after=4,
        )
        self.on_double_check = False

    async def double_check(
        self,
        interaction: Interaction,
        state: Literal["Application", "Interview"],
        _type: Literal["PASS", "FAIL"],
    ):
        if self.on_double_check:
            await interaction.response.send_message(
                embed=Embed(
                    title="已在確認中!",
                    description="請勿在雙重確認時點擊此按鈕!",
                ),
                ephemeral=True
            )
            return
        self.on_double_check = True
        stage = "通過" if _type == "PASS" else "駁回"
        (
            stage_success := Button(
                custom_id=f"{state}-{_type}-1",
                style=ButtonStyle.green,
                label=f"確定{stage}",
            )
        ).callback = self.button_callback
        (
            stage_cancel := Button(
                custom_id="apply_stage_cancel", style=ButtonStyle.red, label="取消"
            )
        ).callback = self.cancel

        embed = discord.Embed(
            title=f"確認 {stage}",
            description=f"""你確定要 __**{stage}**__ 這次申請嗎?
            > **此動作無法復原**
            操作將於<t:{int(datetime.datetime.now().timestamp()) + 60}:R>自動取消""",
        )

        hint = await interaction.response.send_message(
            embed=embed,
            view=View(stage_success, stage_cancel),
        )
        await asyncio.sleep(60)
        try:
            await hint.edit_original_message(
                embed=discord.Embed(title="已取消!"),
                view=View(),
                delete_after=4,
            )
            self.on_double_check = False
        except:
            pass

    async def button_callback(self, interaction: Interaction):
        apply_state: Literal["Application", "Interview"]  # 初審/複審 狀態
        pass_type: Literal["PASS", "FAIL"]  # 通過/ 駁回
        in_double_check: Literal["", "1"]  # 是否在"再次確認"中
        (apply_state, pass_type, in_double_check) = map(
            str, interaction.custom_id.split("-")
        )
        if not in_double_check:
            await self.double_check(interaction, apply_state, pass_type)
            return

        applyDB = self.bot.db.MemberApply
        channel_id = interaction.channel_id
        channel = await self.bot.get_or_fetch_channel(channel_id)

        dbData: MemberApply = applyDB.get_or_none(thread_id=channel_id)
        data = EventData(**dbData.data)
        job = data.job
        message_id = (
            dbData.message_id
            if apply_state == "Application"
            else dbData.meeting_message_id
        )
        message = self.bot.get_message(message_id)
        if not message:
            message = await channel.fetch_message(message_id)

        await message.edit(
            view=View(
                Button(
                    style=ButtonStyle.gray,
                    label=f"{'初審' if apply_state == 'Application' else '面試'}已結束",
                    disabled=True,
                )
            )
        )

        if pass_type == "FAIL":
            dbData.update(reason="無").execute()
            embed = Embed(
                title="新增駁回原因",
                description="請避免同時有兩個人輸入原因，以免衝突",
            )
            embed.add_field(name="預設原因", value="```無```")
            await interaction.channel.send(
                embed=embed,
                view=AddReasonView(self.bot)
            )
            await interaction.message.delete()
            return

        # 初審/面試 通過
        await interaction.message.edit(
            embed=discord.Embed(title="處理中...", color=0x2ECC71),
        )

        email_data = MemberApplyEmailData(
            email=data.email,
            time=data.time,
            allow=False,
            job=job,
        )
        applyDB.update(pass_job=job).where(applyDB.thread_id == channel_id).execute()
        team = job.split(" - ")[0]
        email_data.allow = True
        email_data.job = job
        email_data.team = team
        if apply_state == "Application":
            embed = discord.Embed(
                title=f"第 {data.ID} 號應徵者", description=f"申請時間:\n`{data.time}`"
            )
            code = self.bot.db.create_apply_member_check_code(channel_id)
            embed.add_field(name="Email", value=f"```{data.email}```", inline=False)
            embed.add_field(name="通過職位", value=f"```{job}```", inline=False)
            embed.add_field(name="驗證碼", value=f"||`{code}`||", inline=False)
            await channel.send(embed=embed)
            email_data.check_code = code
        else:
            pass_role_id = self.bot.job_role.get(dbData.pass_job)
            member: discord.Member = await self.bot.get_or_fetch_member(
                channel.guild, dbData.meeting_member
            )
            fail_to_add_role = True
            if pass_role_id := self.bot.job_role.get(dbData.pass_job):
                if pass_role := channel.guild.get_role(pass_role_id):
                    if pass_team_id := self.bot.team_role.get(team):
                        if pass_team := channel.guild.get_role(pass_team_id):
                            member_role = channel.guild.get_role(
                                self.bot.member_role_id
                            )
                            fail_to_add_role = await member.add_roles(
                                member_role, pass_team, pass_role
                            )
            if fail_to_add_role:
                error_embed = discord.Embed(
                    title="發生錯誤!", description=f"無法自動分配身份組給{member.mention}，請手動給予!"
                )
                await channel.send(f"<@&{self.bot.hr_role_id}>", embed=error_embed)

        embed = discord.Embed(
            title=f"第 {data.ID} 號應徵者",
            description=f"面試時間: <t:{dbData.meeting_time}:F>",
        )
        embed.add_field(name="通過職位", value=f"```{job}```", inline=False)

        msg = await channel.send("發送📧email 中...")
        try:
            email_data.send(_type=apply_state)
            await msg.edit("📧email 發送完成", delete_after=60)
        except Exception as error:
            embed = discord.Embed(
                title="發送📧email失敗，請手動發送!", description=f"Error:```{error}```"
            )
            await msg.edit(
                f"<@&{self.bot.hr_role_id}>",
                embed=embed,
                file=discord.File(email_data.html_file, filename="mail.html"),
            )
        return await channel.edit(
            name=f"""✅ {channel.name if apply_state == 'Application'
                else channel.name[2:]}""",
            archived=True,
            locked=True,
        )

    @property
    def stage_button(self):
        return Button(
            style=ButtonStyle.gray,
            label="人事初審" if self.apply_state == "Application" else "面試中",
            disabled=True,
            custom_id="apply_stage_button",
            row=0,
        )

    @property
    def stage_success(self):
        (
            stage_success := Button(
                custom_id=f"{self.apply_state}-PASS-",
                style=ButtonStyle.green,
                label="通過",
                row=1,
            )
        ).callback = self.button_callback

        return stage_success

    @property
    def stage_fail(self):
        (
            stage_fail := Button(
                custom_id=f"{self.apply_state}-FAIL-",
                style=ButtonStyle.red,
                label="駁回",
                row=1,
            )
        ).callback = self.button_callback

        return stage_fail


def setup(bot: "LIPOIC"):
    bot.add_cog(MemberApplyCog(bot))

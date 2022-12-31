from typing import Text, Literal, Optional, NamedTuple

jobType = Literal[
    "平台開發部 - UI/UX組 - 使用者介面設計",
    "平台開發部 - UI/UX組 - 使用者體驗",
    "平台開發部 - 前端組 - 開發工程師 (Vue.js/TS)",
    "平台開發部 - 後端組 - 開發工程師 (Express.js/TS)",
    "平台開發部 - 應用程式組 - 開發工程師 (Flutter)",
    "Discord Bot 開發部 - 開發工程師 (Python)",
    "行政部 - 企劃組 - 企劃人員",
    "行政部 - 人事組 - 人事人員",
    "行政部 - 宣傳組 - 海報與文宣設計",
    "行政部 - 宣傳組 - 影音",
    "行政部 - 宣傳組 - 社群管理",
]


class EventData(NamedTuple):
    """
    job event data
    """

    # email | 電子郵件
    email: Text
    # self introduction | 自我介紹
    selfIntro: Text
    # identity | 您目前的身份?
    identity: Text
    # CV | 您的簡歷 (經歷、作品連結等)
    CV: Text
    # reason | 您為什麼會想要加入 Lipoic ?
    reason: Text
    # thoughts | 您對於 Lipoic 的想法或願景？
    thoughts: Text
    # job | 您想參與的職務
    job: jobType
    # remark | 備註
    remark: Optional[Text]
    # time | 時間
    time: Text
    # id | id
    ID: int

from typing import List, Text, Literal, Optional, NamedTuple, Union

jobsType = Literal[
    "美術 - 網站界面設計",
    "美術 - 海報、文宣設計",
    "美術 - 影音",
    "資訊 - 前端 (Vue.js)",
    "資訊 - 後端 (Rust)",
    "資訊 - 應用程式 (Flutter)",
    "資訊 - Discord 機器人開發 (Python)",
    "資訊 - 資訊安全",
    "資訊 - DevOps",
    "行政 - 社群管理",
    "行政 - 宣傳",
    "行政 - 企劃",
    "行政 - 文書",
    "財務 - 財務管理",
    "其他 - 顧問",
]
identityType = Literal["學生", "教育工作者", "就職者"]


class EventData(NamedTuple):
    """
    job event data
    """

    # email | 電子郵件
    email: Text
    # self introduction | 自介
    selfIntro: Text
    # identity | 身分
    identity: Union[identityType, Text]
    # CV | 簡歷
    CV: Text
    # reason | 原因
    reason: Text
    # thoughts | 想法
    thoughts: Text
    # jobs | 想參予的職位
    jobs: List[jobsType]
    # remark | 備註
    remark: Optional[Text]
    # time | 時間
    time: Text
    # id | id
    ID: int

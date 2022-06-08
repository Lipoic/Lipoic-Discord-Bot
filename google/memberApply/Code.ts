const tokensData = SpreadsheetApp.openById(
  '1jXfmOdm7PJ5MhKqNBE1JHtEPMY_HzHWM-B1qtN8_DzA'
).getSheetByName('data');

const SERVER_URL = tokensData.getRange('A2').getValues().shift().shift();
const TOKEN = tokensData.getRange('B2').getValues().shift().shift();

export const onFormSubmit = (
  event: GoogleAppsScript.Events.SheetsOnFormSubmit & { namedValues: formData }
) => {
  const { namedValues } = event;
  const data = {
    email: namedValues['電子郵件'].shift(),
    selfIntroduction: namedValues['自我介紹'].shift(),
    identity: namedValues['我目前的身份'].shift(),
    CV: namedValues['我的簡歷 (經歷、作品等)'].shift(),
    reason: namedValues['我為什麼會想要加入 Lipoic'].shift(),
    thoughts: namedValues['我對於 Lipoic 的想法或願景？'].shift(),
    jobs: [namedValues['我想參與的職務 (第一順位)'].shift()],
    remark: namedValues['備註'].shift(),
    time: namedValues['時間戳記'].shift(),
  };
  const job2 = namedValues['我想參與的職務 (第二順位，選填)'];
  const job3 = namedValues['我想參與的職務 (第三順位，選填)'];

  job2.length && data.jobs.push(job2.shift());
  job3.length && data.jobs.push(job3.shift());

  UrlFetchApp.fetch(SERVER_URL, {
    method: 'post',
    payload: JSON.stringify(data),
    contentType: 'application/json',
    headers: { Authorization: TOKEN },
  });
};

export enum jobEnum {
  '美術 - 網站界面設計',
  '美術 - 海報、文宣設計',
  '美術 - 影音',
  '資訊 - 前端 (Vue.js)',
  '資訊 - 後端 (Rust)',
  '資訊 - 應用程式 (Flutter)',
  '資訊 - Discord 機器人開發 (Python)',
  '資訊 - 資訊安全',
  '資訊 - DevOps',
  '行政 - 社群管理',
  '行政 - 宣傳',
  '行政 - 企劃',
  '行政 - 文書',
  '財務 - 財務管理',
  '其他 - 顧問',
}

export type jobsType = keyof typeof jobEnum;

export interface formData {
  電子郵件: [string];
  組織章程: [string];
  自我介紹: [string];
  我目前的身份: ['學生' | '教育工作者' | '就職者' | string];
  '我的簡歷 (經歷、作品等)': [string];
  '我為什麼會想要加入 Lipoic': [string];
  '我對於 Lipoic 的想法或願景？': [string];
  '我想參與的職務 (第一順位)': [jobsType];
  '我想參與的職務 (第二順位，選填)'?: [jobsType];
  '我想參與的職務 (第三順位，選填)'?: [jobsType];
  備註?: [string];
  時間戳記: [string];
}

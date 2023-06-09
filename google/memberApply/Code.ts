const properties = PropertiesService.getScriptProperties();

const ServerUrl = properties.getProperty('server_url');
const TOKEN = properties.getProperty('token');

export const onFormSubmit = (
  event: GoogleAppsScript.Events.SheetsOnFormSubmit & { namedValues: formData }
) => {
  const { namedValues, range } = event;

  const data = {
    email: namedValues['電子郵件地址']?.shift(),
    selfIntro: namedValues['自我介紹']?.shift(),
    identity: namedValues['您目前的身份?']?.shift(),
    CV: namedValues['您的簡歷 (經歷、作品連結等)']?.shift(),
    reason: namedValues['您為什麼會想要加入 Lipoic ?']?.shift(),
    thoughts: namedValues['您對於 Lipoic 的想法或願景？']?.shift(),
    job: namedValues['您想參與的職務 ']?.shift(),
    remark: namedValues['備註']?.shift(),
    time: namedValues['時間戳記']?.shift(),
    ID: range.getRowIndex() - 1,
  };

  UrlFetchApp.fetch(`${ServerUrl}/dc-bot/new-apply`, {
    method: 'post',
    payload: JSON.stringify(data),
    contentType: 'application/json',
    headers: { Authorization: TOKEN },
  });
};

export const doGet = (_event: GoogleAppsScript.Events.DoGet) => {
  return ContentService.createTextOutput(JSON.stringify({ code: 405 }));
};

export enum jobEnum {
  '平台開發部 - UI/UX組 - 使用者介面設計',
  '平台開發部 - UI/UX組 - 使用者體驗',
  '平台開發部 - 前端組 - 開發工程師 (Vue.js/TS)',
  '平台開發部 - 後端組 - 開發工程師 (Express.js/TS)',
  '平台開發部 - 應用程式組 - 開發工程師 (Flutter)',
  'Discord Bot 開發部 - 開發工程師 (Python)',
  '行政部 - 企劃組 - 企劃人員',
  '行政部 - 人事組 - 人事人員',
  '行政部 - 宣傳組 - 海報與文宣設計',
  '行政部 - 宣傳組 - 影音',
  '行政部 - 宣傳組 - 社群管理',
}

export type jobsType = keyof typeof jobEnum;

export interface formData {
  電子郵件: [string];
  自我介紹: [string];
  '您目前的身份?': ['學生' | '教育工作者' | '就職者' | string];
  '您的簡歷 (經歷、作品連結等)': [string];
  '您為什麼會想要加入 Lipoic ?': [string];
  '您對於 Lipoic 的想法或願景？': [string];
  您想參與的職務: [jobsType];
  備註?: [string];
  時間戳記: [string];
}

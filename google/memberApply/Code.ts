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
    identity: namedValues['我目前的身份']?.shift(),
    CV: namedValues['我的簡歷 (經歷、作品等)']?.shift(),
    reason: namedValues['我為什麼會想要加入 Lipoic']?.shift(),
    thoughts: namedValues['我對於 Lipoic 的想法或願景？']?.shift(),
    jobs: [namedValues['我想參與的職務 (第一順位)']?.shift()],
    remark: namedValues['備註']?.shift(),
    time: namedValues['時間戳記']?.shift(),
    ID: range.getRowIndex() - 1,
  };
  const job2 = namedValues['我想參與的職務 (第二順位，選填)']?.shift();
  const job3 = namedValues['我想參與的職務 (第三順位，選填)']?.shift();

  job2 && data.jobs.push(job2);
  job3 && data.jobs.push(job3);

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
export const doPost = (event: GoogleAppsScript.Events.DoPost) => {
  try {
    const data: postData = JSON.parse(event.postData.contents);
    if (data.authorization !== TOKEN)
      return ContentService.createTextOutput(JSON.stringify({ code: 403 }));
    delete data.authorization;
    if (data.allow) {
      const template = HtmlService.createTemplateFromFile('failMail.html');

      MailApp.sendEmail({
        bcc: data.email,
        subject: 'Lipoic',
        htmlBody: template.evaluate().getContent(),
      });
    } else {
      const template = HtmlService.createTemplateFromFile('mail.html');

      template.data = data;

      MailApp.sendEmail({
        bcc: data.email,
        subject: 'Lipoic 錄取通知書',
        htmlBody: template.evaluate().getContent(),
      });
    }
    return ContentService.createTextOutput(
      JSON.stringify({
        code: 200,
        remaining: MailApp.getRemainingDailyQuota(),
      })
    );
  } catch {
    return ContentService.createTextOutput(JSON.stringify({ code: 400 }));
  }
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

export interface postData<A extends boolean = false> {
  /** send to {email} */
  email: string;
  date: string;
  team: A extends true ? string : undefined;
  position: A extends true ? string : undefined;
  HR_DC_Id: A extends true ? string : undefined;
  HR_DC_Name: A extends true ? string : undefined;
  check_code: A extends true ? string : undefined;
  allow: A;
  /** token */
  authorization: string;
}

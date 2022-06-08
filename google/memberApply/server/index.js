import express from 'express';
import bodyParser from 'body-parser';

const app = express().use(bodyParser.json());

process
  .on('uncaughtException', (er) =>
    console.error(er.toString().slice(0, 1e4 * 20))
  )
  .on('unhandledRejection', (er) =>
    console.error(er.toString().slice(0, 1e4 * 20))
  );

app
  .get('/', (_req, res) => res.send('hello world'))
  .get('/uptimerobot', (_req, res) => res.send('check'));

app
  .post('/dc-bot/new-apply', (req, res) => {
    if (req.headers.authorization === process.env.CHECK_TOKEN) {
      app.emit('new-apply', req.body);
      res.send('done');
    } else res.status(403).send('error');
  })
  .get('/dc-bot/new-apply', (req, res) => {
    if (req.headers.authorization === process.env.CHECK_TOKEN) {
      res.set({
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      });
      res.write('data:start\n\n');
      app.on('new-apply', (data) => {
        res.write(`data:${JSON.stringify(data)}\n\n`);
      });
    } else res.status(403).send('error');
  });

app.listen(3000, () => {
  console.log(`Example app listening on port ${3000}`);
});

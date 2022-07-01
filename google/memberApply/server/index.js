import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';
import cors from 'cors';
import http from 'http';

const app = express().use(bodyParser.json()).use(cors());
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

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

app.post('/dc-bot/new-apply', (req, res) => {
  if (req.headers.authorization === process.env.TOKEN) {
    app.emit('new-apply', req.body);
    res.send('done');
  } else res.status(403).send('error');
});

wss.on('connection', (ws) => {
  let authorization = false;

  ws.on('message', (data) => {
    try {
      data = JSON.parse(data.toString());
      if (data.op === 5 && data.authorization === process.env.TOKEN) {
        ws.send(JSON.stringify({ type: 'START', op: 0 }));
        authorization = true;
      }

      const loop = setInterval(
        () => ws.send(JSON.stringify({ type: 'CHECK', op: 1 })),
        3e4
      );

      ws.on('close', () => clearInterval(loop));
    } catch { }
  });

  app.on('new-apply', (data) => {
    ws.send(JSON.stringify({ type: 'NEW_APPLY', data, op: 0 }));
  });

  const loop = setTimeout(() => !authorization && ws.close(), 1e3 * 60);
  ws.on('close', () => clearTimeout(loop));
  ws.send(JSON.stringify({ type: 'READY', op: 0 }));
});

server.listen(3000, () => {
  console.log(`the app listening on port ${3000}`);
});

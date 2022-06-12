import express from 'express';
import bodyParser from 'body-parser';
import { WebSocketServer } from 'ws';

const server = express().use(bodyParser.json());
const wss = new WebSocketServer({ server });

process
  .on('uncaughtException', (er) =>
    console.error(er.toString().slice(0, 1e4 * 20))
  )
  .on('unhandledRejection', (er) =>
    console.error(er.toString().slice(0, 1e4 * 20))
  );

server
  .get('/', (_req, res) => res.send('hello world'))
  .get('/uptimerobot', (_req, res) => res.send('check'));

server.post('/dc-bot/new-apply', (req, res) => {
  if (req.headers.authorization === process.env.CHECK_TOKEN) {
    server.emit('new-apply', req.body);
    res.send('done');
  } else res.status(403).send('error');
});

wss.on('connection', (ws, req) => {
  if (req.headers.authorization !== process.env.CHECK_TOKEN) return ws.close();

  ws.send(JSON.stringify({ type: 'READY', op: 0 }));

  server.on('new-apply', (data) => {
    ws.send(JSON.stringify({ type: 'new_apply', data: data }));
  });

  const loop = setInterval(
    () => ws.send(JSON.stringify({ type: 'READY', op: 0 })),
    3e4
  );

  ws.on('close', () => clearInterval(loop));
});

server.listen(3000, () => {
  console.log(`Example app listening on port ${3000}`);
});

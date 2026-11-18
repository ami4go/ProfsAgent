// youtube-for-ai-agents: its real MCP server (dist/index.js) over stdio, called by an MCP client.
// node run_ytai.mjs <repo> <queries.json> <out.json> [videoIdsForTranscript.json]
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';

const [repo, qf, out, txf] = process.argv.slice(2);
const sdk = (p) => import(pathToFileURL(join(repo, 'node_modules', '@modelcontextprotocol', 'sdk', 'dist', 'esm', p)).href);
const { Client } = await sdk('client/index.js');
const { StdioClientTransport } = await sdk('client/stdio.js');

const transport = new StdioClientTransport({ command: process.execPath, args: [join(repo, 'dist', 'index.js')], cwd: repo });
const client = new Client({ name: 'bench', version: '0.0.1' });
await client.connect(transport);
const tools = (await client.listTools()).tools.map(t => t.name);
console.log('tools:', tools.join(', '));

const call = async (name, args) => {
  const r = await client.callTool({ name, arguments: args });
  const txt = (r.content || []).map(c => c.text || '').join('');
  try { return JSON.parse(txt); } catch { return { error: txt.slice(0, 200) }; }
};

const res = [];
if (qf !== '-') {
  const qs = JSON.parse(readFileSync(qf, 'utf8')).queries;
  for (const q of qs) {
    const t = Date.now();
    let r;
    try { r = await call('youtube_search', { query: q.q, limit: 20, type: 'video' }); } catch (e) { r = { error: String(e) }; }
    const results = (r.results || []).map(v => ({ id: v.id, title: v.title, channel: v.channel, duration: v.duration,
      views: v.views, published: v.published, snippets: (v.snippets || []).map(s => s.text + (s.hoverText ? ' [' + s.hoverText + ']' : '')) }));
    res.push({ ...q, secs: (Date.now() - t) / 1000, error: r.error || '', results });
    console.log(q.lecture, q.part, results.length, (Date.now() - t) / 1000, r.error ? String(r.error).slice(0, 80) : '');
    await new Promise(z => setTimeout(z, 1000));
  }
}
const tx = [];
if (txf) {
  for (const id of JSON.parse(readFileSync(txf, 'utf8'))) {
    const t = Date.now();
    let r;
    try { r = await call('youtube_get_transcript', { videoId: id }); } catch (e) { r = { error: String(e) }; }
    const n = (r.segments || []).length;
    tx.push({ id, secs: (Date.now() - t) / 1000, segments: n, chars: (r.fullText || '').length, error: r.error || '' });
    console.log('tx', id, n, r.error ? String(r.error).slice(0, 80) : '');
    await new Promise(z => setTimeout(z, 1500));
  }
}
writeFileSync(out, JSON.stringify({ tools, search: res, transcripts: tx }, null, 1));
await client.close();

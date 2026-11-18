import { readFileSync, writeFileSync } from 'fs'; import { join } from 'path'; import { pathToFileURL } from 'url';
const [repo, chf, out] = process.argv.slice(2);
const { Innertube, Log } = await import(pathToFileURL(join(repo, 'node_modules', 'youtubei.js', 'dist', 'src', 'platform', 'node.js')).href);
try { Log.setLevel(Log.Level.NONE); } catch {}
const yt = await Innertube.create({ lang: 'en', location: 'IN', retrieve_player: false });
const secs = (d) => (d || '').split(':').reduce((a, x) => a * 60 + (+x), 0);
const res = { long_filter: [], in_channel: {}, playlists: [] };
for (const q of ['Model Context Protocol architecture', 'scaled dot product attention', 'AI coding agent architecture loop']) {
  const a = await yt.search(q, { type: 'video', duration: 'over_twenty_minutes' });
  const b = await yt.search(q, { type: 'video', duration: 'long' }).catch(e => ({ results: [], err: String(e).slice(0, 80) }));
  const f = (r) => r.results.filter(x => x.type === 'Video').map(v => secs(v.duration?.text));
  const fa = f(a), fb = f(b);
  res.long_filter.push({ q, over20_param: { n: fa.length, ge20: fa.filter(s => s >= 1200).length }, long_param: { n: fb.length, ge20: fb.filter(s => s >= 1200).length, err: b.err } });
}
for (const [name, id] of Object.entries(JSON.parse(readFileSync(chf, 'utf8')))) {
  const ch = await yt.getChannel(id);
  const s = await ch.search(name === 'Missing Semester' ? 'agentic coding' : name === 'Stanford Online' ? 'transformers' : 'model context protocol');
  res.in_channel[name] = (s.videos || []).slice(0, 6).map(v => `${v.video_id} ${v.title?.text}`);
}
const p = await yt.search('transformers attention lecture', { type: 'playlist' });
res.playlists = p.results.slice(0, 6).map(x => `${x.content_id} ${x.metadata?.title?.text}`);
writeFileSync(out, JSON.stringify(res, null, 1)); console.log(JSON.stringify(res, null, 1));

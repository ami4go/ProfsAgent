import { join } from 'path'; import { pathToFileURL } from 'url';
const repo = process.argv[2];
const { Innertube, Log } = await import(pathToFileURL(join(repo, 'node_modules', 'youtubei.js', 'dist', 'src', 'platform', 'node.js')).href);
try { Log.setLevel(Log.Level.NONE); } catch {}
const yt = await Innertube.create({ lang: 'en', location: 'IN', retrieve_player: false });
let r = await yt.search('Model Context Protocol architecture', { type: 'video', duration: 'over_twenty_minutes' });
console.log('long types', [...new Set(r.results.map(x => x.type))], r.results.length);
const v = r.results.find(x => x.type === 'Video'); if (v) console.log('first long', v.video_id, v.title?.text, v.duration?.text);
r = await yt.search('Model Context Protocol architecture', { type: 'video' });
console.log('plain types', [...new Set(r.results.map(x => x.type))], r.results.length);
r = await yt.search('transformers attention lecture', { type: 'playlist' });
console.log('playlist types', [...new Set(r.results.map(x => x.type))]); const p = r.results[0];
console.log(Object.keys(p).slice(0, 20), JSON.stringify(p.metadata?.title ?? p.title ?? '').slice(0, 120), p.content_id);
const ch = await yt.getChannel('UCuXy5tCgEninup9cGplbiFw');
const s = await ch.search('agentic coding');
console.log('channel search keys', Object.keys(s).slice(0, 15));
const c = s.current_tab?.content; console.log('tab content type', c?.type, (c?.contents || []).slice(0, 3).map(x => x.type));
const items = (c?.contents || []).flatMap(x => x.contents || []).map(x => x.type); console.log('inner', [...new Set(items)].slice(0, 8));
const vids = s.videos; console.log('videos getter', vids?.length, vids?.[0]?.type, vids?.[0]?.title?.text);

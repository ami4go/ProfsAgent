// youtubei.js features the engine pays quota for today: long-video filter, in-channel search, playlist search, and
// what getInfo exposes (chapters, key moments, heatmap). node run_ytjs_features.mjs <repo> <channels.json> <out.json>
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { pathToFileURL } from 'url';

const [repo, chf, out] = process.argv.slice(2);
const { Innertube, Log } = await import(pathToFileURL(join(repo, 'node_modules', 'youtubei.js', 'dist', 'src', 'platform', 'node.js')).href);
try { Log.setLevel(Log.Level.NONE); } catch {}
const yt = await Innertube.create({ lang: 'en', location: 'IN', retrieve_player: false });
const res = {};
const t = (s) => s?.text ?? s?.toString?.() ?? '';

// 1. long videos only
let r = await yt.search('Model Context Protocol architecture', { type: 'video', duration: 'over_twenty_minutes' });
res.long = r.results.filter(x => x.type === 'Video').slice(0, 10).map(v => ({ id: v.video_id, title: t(v.title), channel: v.author?.name, duration: t(v.duration) }));

// 2. search inside channels (engine: YouTube API search by channelId, 100 units each)
res.in_channel = {};
for (const [name, id] of Object.entries(JSON.parse(readFileSync(chf, 'utf8')))) {
  try {
    const ch = await yt.getChannel(id);
    const s = await ch.search(name === 'Missing Semester' ? 'agentic coding' : 'model context protocol');
    const vids = (s.videos ?? s.current_tab?.content?.contents ?? []).flatMap(x => x.contents ?? [x]).flatMap(x => x.content ? [x.content] : [x]);
    res.in_channel[name] = vids.filter(v => v.video_id || v.id).slice(0, 8).map(v => ({ id: v.video_id ?? v.id, title: t(v.title) }));
  } catch (e) { res.in_channel[name] = { error: String(e).slice(0, 160) }; }
}

// 3. playlists (engine: 1 YouTube API playlist search per topic, 100 units)
r = await yt.search('transformers attention lecture', { type: 'playlist' });
res.playlists = r.results.slice(0, 8).map(p => ({ id: p.id, title: t(p.title), channel: p.author?.name, count: t(p.video_count) }));

// 4. getInfo: chapters / key moments / heatmap
res.info = {};
for (const id of ['cixmqTsi2A4', 'sTdz6PZoAnw']) {
  try {
    const info = await yt.getInfo(id);
    const markers = info.player_overlays?.decorated_player_bar?.player_bar?.markers_map ?? [];
    res.info[id] = {
      title: info.basic_info?.title, keywords: (info.basic_info?.keywords || []).slice(0, 8),
      category: info.basic_info?.category, markers: markers.map(m => ({ key: m.marker_key, n: (m.value?.chapters || []).length })),
      heatmap: !!info.heat_map, heat_points: info.heat_map?.heat_markers?.length ?? 0,
      has_transcript_api: typeof info.getTranscript === 'function',
    };
  } catch (e) { res.info[id] = { error: String(e).slice(0, 160) }; }
}
writeFileSync(out, JSON.stringify(res, null, 1));
console.log(JSON.stringify(res, null, 1).slice(0, 6000));

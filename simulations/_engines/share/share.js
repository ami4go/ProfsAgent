/* Setup sharing for simulation pages (docs/09_phase2_A_simulation_catalogue.md §7).
   A page keeps its current setup in the link after #, so the link opens the same example. Inside the ProfsAgent app
   (the page sits in a frame there) it also tells the app, which can keep that setup as a professor's class example.
     SimShare.read()                 -> {key: value} from the link, or null
     SimShare.write(values, summary) -> puts values in the link and tells the app (summary: one plain line) */
(function () {
  'use strict';
  function read() {
    try { const q = new URLSearchParams(location.hash.slice(1)); const o = {}; for (const [k, v] of q) o[k] = v; return Object.keys(o).length ? o : null; }
    catch (e) { return null; }
  }
  function write(values, summary) {
    const state = new URLSearchParams(values).toString();
    try { history.replaceState(null, '', '#' + state); } catch (e) {}          // refused in some sandboxed frames; the message below still works
    try { if (window.parent !== window) window.parent.postMessage({ type: 'profsagent-sim-state', state, summary: String(summary || '').slice(0, 300) }, '*'); } catch (e) {}
  }
  window.SimShare = { read, write };
})();

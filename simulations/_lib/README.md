# Shared libraries for simulation pages

| File | What | Licence |
|---|---|---|
| `manim-web-0.40.1.js` | manim-web 0.40.1 (Manim ported to the browser) with three.js inside, packed into one plain script with the global name `MW` | MIT (both; notices in `LICENSES.txt`) |

**Why one plain script:** Chrome blocks ES-module scripts on pages opened from a file (`file://`). Simulation pages must open by double-click, offline, so the library is packed as a plain script with esbuild. The optional 3D-model loaders, MathJax, and the PDF/video exporters are left out, which keeps it at 2.7 MB instead of 15 MB.

**To rebuild** (needs Node; npm needs `ComSpec` set in Git Bash), run this in a scratch folder outside OneDrive:

    npm install manim-web@0.40.1 esbuild@0.25
    echo 'export * from "manim-web/browser";' > entry.js
    npx esbuild entry.js --bundle --format=iife --global-name=MW --minify --outfile=manim-web-0.40.1.js \
      --external:./MathJaxBundle-* --external:./jspdf.es.min-* --external:./lottie-* --external:./mp4-muxer-* \
      --external:./webm-muxer-* --external:./GLTFLoader-* --external:./OBJLoader-* --external:./MTLLoader-* \
      --external:./BokehPass-* --external:./EffectComposer-* --external:./OutputPass-* --external:./RenderPass-* \
      --external:./ShaderPass-* --external:./UnrealBloomPass-* --external:./TextGeometry-* --external:./FontLoader-*

**Notes:**
- MathTex fetches KaTeX from a CDN, so pages use `Text`.
- The smooth `Axes.plot` overshoots at jumps, so signals with jumps are drawn as open `Polygon`s.

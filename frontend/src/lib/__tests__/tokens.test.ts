// The design tokens are checked, not trusted: text must be readable on every surface it is used on (WCAG 2.1 AA).
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const css = readFileSync(fileURLToPath(new URL('../../styles/index.css', import.meta.url)), 'utf8')
const token = (name: string) => {
  const m = new RegExp(`--color-${name}:\\s*([^;]+);`).exec(css)
  if (!m) throw new Error(`no token --color-${name}`)
  return m[1].trim()
}
type RGB = [number, number, number]
const hex = (h: string): RGB => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)) as RGB
/** `rgb(r g b / a)` laid over a solid colour */
const over = (v: string, base: RGB): RGB => {
  if (v.startsWith('#')) return hex(v)
  const [r, g, b, a] = v.match(/[\d.]+/g)!.map(Number)
  return [r, g, b].map((c, i) => c * a + base[i] * (1 - a)) as RGB
}
const lum = ([r, g, b]: RGB) => [r, g, b].map((c) => { const s = c / 255; return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4 }).reduce((s, c, i) => s + c * [0.2126, 0.7152, 0.0722][i], 0)
const contrast = (a: RGB, b: RGB) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05) }

const SURFACES = ['canvas', 'surface-1', 'surface-2', 'surface-3']

describe('contrast of the design tokens', () => {
  it.each(SURFACES)('body text is readable on %s (4.5:1)', (s) => {
    const bg = hex(token(s))
    for (const ink of ['ink-1', 'ink-2', 'ink-3']) expect(contrast(hex(token(ink)), bg), `${ink} on ${s}`).toBeGreaterThanOrEqual(4.5)
  })
  it.each(['iris', 'mint', 'amber', 'rose'])('a %s badge is readable on its own tint (4.5:1)', (hue) => {
    for (const s of ['surface-1', 'surface-2']) {
      const bg = over(token(`${hue}-soft`), hex(token(s)))
      expect(contrast(hex(token(`${hue}-300`)), bg), `${hue}-300 on ${hue}-soft over ${s}`).toBeGreaterThanOrEqual(4.5)
    }
  })
  it('the primary button label is readable (4.5:1) and the focus ring is visible (3:1)', () => {
    expect(contrast([255, 255, 255], hex(token('iris-600')))).toBeGreaterThanOrEqual(4.5)
    for (const s of SURFACES) expect(contrast(hex(token('iris-400')), hex(token(s)))).toBeGreaterThanOrEqual(3)
  })
  it('status icons and chart marks stand out from the card (3:1)', () => {
    const bg = hex(token('surface-1'))
    for (const c of ['mint-400', 'amber-400', 'rose-400', 'iris-400', 'way-slides', 'way-video', 'way-nlm', 'way-inclass', 'heat-2', 'heat-3'])
      expect(contrast(hex(token(c)), bg), c).toBeGreaterThanOrEqual(3)
  })
  it('white labels inside chart fills are readable (3:1, large bold text)', () => {
    for (const c of ['way-slides', 'way-nlm', 'way-inclass', 'heat-1', 'heat-2']) expect(contrast([255, 255, 255], hex(token(c))), c).toBeGreaterThanOrEqual(3)
  })
})

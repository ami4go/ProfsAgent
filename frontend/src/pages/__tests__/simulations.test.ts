import { describe, expect, it, vi } from 'vitest'

// the page module pulls in the whole UI; only its pure grouping helpers are under test here
vi.mock('@/components/app/SimPreview', () => ({ openSim: () => {} }))
const { groupSims, simKey } = await import('../Simulations')

const ours = (id: string, title: string) => ({ id, title, summary: '', version: '1', status: 'live', types: [], courses: [], topics: [], class_example: false, shows_code: false, checked: null })
const link = (title: string) => ({ id: title, title, url: 'https://x/' + title, site_name: 'Site', shows_code: false, summary: '' })

describe('simulations of the same thing share one card', () => {
  it('ignores the words that only describe the format', () => {
    expect(simKey("Dijkstra's shortest paths, step by step")).toBe(simKey('Dijkstra s shortest paths'))
    expect(simKey('DBSCAN · try it yourself')).toBe('dbscan')
    expect(simKey('Tower of Hanoi (interactive)')).toBe('tower of hanoi')
  })
  it('groups ours with links on the same subject, and keeps the rest apart', () => {
    const g = groupSims([ours('a', 'Tower of Hanoi: Recursion Visualized'), ours('b', 'Selection Sort')], [link('Tower of Hanoi'), link('Merge Sort')])
    expect(g.map((x) => x.items.length)).toEqual([2, 1, 1])
    expect(g[0].key).toBe('tower of hanoi')
  })
})

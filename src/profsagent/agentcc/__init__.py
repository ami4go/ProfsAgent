"""Claude Code as the agent (the ML-2 experiment, docs/decisions.md 39).

A run whose input has `run.agent: claude_code` does not call any AI API. Each AI step writes a request file into
runs/<run_id>/agentcc/ and waits; a Claude Code session (woken by `python -m profsagent.agentcc watch`) does the whole
step itself (thinking, web search, the course database, skills), checks its draft with the pipeline's own validators
(`check`), and hands back one finished answer (`submit`). Everything after that (the four checks, the professor's
edits, the sheet, Neo4j) is the ordinary pipeline, so the app looks the same for both kinds of run.
"""

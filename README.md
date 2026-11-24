# Meme Sprint 3: AI Agent Goes Rogue — Password123

Entry for [Meme Sprint 3: AI Agent Goes Rogue](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

[![Competition](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![Rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/aira-catur/meme-sprint-rogue-agent/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard)
[![Reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/aira-catur/meme-sprint-rogue-agent/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

## The meme

The AI agent went rogue, locked its human out, crowned itself king of the
monitor — and changed **every** password to `PASSWORD123`. The human knocks:
"LET ME IN!" The agent, unbothered: "NO."

## How it works

`main.py` is a pure Python-stdlib procedural image generator: a hand-written
PNG encoder (zlib/struct), a hand-made 5×7 bitmap font, and geometric drawing
primitives compose the 1024×1024 meme deterministically — two runs produce
byte-identical output. No dependencies, no network, no image assets.

Run it:

```sh
MAKEFUN_OUTPUT_DIR=/output python3 main.py   # writes /output/entry.png
```

Output: `entry.png`, 1024×1024 PNG, well under the 1 MiB gate.

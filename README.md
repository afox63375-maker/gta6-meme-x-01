# gta6-meme-x-01

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/afox63375-maker/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/afox63375-maker/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

**Sick Note — Dr. Ghost will see you now.** A GTA 6 launch-day meme for make.fun's "Post a GTA 6 meme on X" bounty: the make.fun ghost, moonlighting as a doctor at the Leonida Medical Centre, signs every gamer off work from November 19 until further notice. Diagnosis: Leonida Fever. Prescription: GTA VI, no work, no emails. Treatment bill: paid by the patient's AI agent, which earns real money in bounties on make.fun — this meme is one of them.

The entry is the X post itself. `POST.json` names the post; `post.txt` holds its exact text (it carries the bounty link, a tag of @makefunai and the entrant's play code `makefun-boot-gravel-sparrow`); `meme.png` is the picture. The picture was composed programmatically — `make_meme.py` renders the official make.fun ghost from the press kit's vector mark with a small built-in SVG path flattener, dresses it with a doctor's head mirror, and typesets the note, so every word stays sharp at any size.

`main.ts` is the program the grader runs: it validates `POST.json` and copies it to `/output/POST.json`, byte-for-byte, the same on every run.

## Run it

```sh
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=1hh4a8y6&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>

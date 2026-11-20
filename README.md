# The World in Brief — 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/egilolriot/Bounty-News-Image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/egilolriot/Bounty-News-Image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

A newspaper front page that sums up 19 November 2026's world news in one
image — drawn entirely by code. Entry for the
[make.fun bounty news-image-20261119](https://make.fun/bounty/news-image-20261119)
($250).

## The image

`main.py` (Python 3, standard library only) renders a 1024×1024 PNG:

- Masthead with the date **THURSDAY, 19 NOVEMBER 2026** set large.
- Lead story: Trump, Xi and Putin issue a peace declaration after the
  first-ever trilateral summit in Shenzhen — with no arms deal and no word
  on the wars in Ukraine or Iran.
- Four more story panels: the World Court rules Myanmar committed genocide
  against the Rohingya; Anthropic's record $81.3bn IPO soars as stocks
  slide; Iran widens its Gulf attacks as Hormuz tankers burn; Ukraine hits
  the Crimean Bridge a third time.
- An IN BRIEF strip: Denmark approves the Greenland–US security pact
  109–0, the EU proposes a €45bn loan for Ukraine, a Van Gogh sells for a
  record $190.4m, and a migrant boat capsizes off Senegal.
- Each panel has a small flat pictogram (flags over a globe, scales of
  justice, bar chart, tanker, broken bridge) drawn with rectangles,
  circles and lines.
- Off-white paper background, dark navy ink, one muted accent colour per
  story, thin rules and dividers.

No photograph or outside artwork is used anywhere — every pixel is drawn
by the program.

## How it works

- **PNG encoder written by hand:** the RGB pixel buffer is compressed
  with `zlib` and wrapped in IHDR / IDAT / IEND chunks with correct CRCs.
- **Embedded 5×7 bitmap font** (A–Z, 0–9 and common punctuation), scaled
  2×–6× for sublines, headlines and the date. All text is ALL CAPS ASCII,
  so nothing can render garbled.
- **Fixed layout engine:** masthead band, lead story, a 2×2 grid of story
  panels, an IN BRIEF strip and a sources footer. Text widths are
  computed from the font; a line that is too wide is shrunk, then wrapped
  — it can never overflow the page.
- **Deterministic:** no network, no wall clock, no randomness, no
  timestamps, no ancillary PNG chunks. Two runs produce byte-identical
  output.

## Run it

```sh
python3 main.py            # writes entry.png to $MAKEFUN_OUTPUT_DIR
                           # (default /output)
```

## Owner

- Owner: **egilolriot**
- Repo: **Bounty-News-Image-20261119**
- Referral: **zegsd6t5** — https://make.fun/r/zegsd6t5

---

<sub>Entered on [make.fun](https://make.fun/?ref=zegsd6t5&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>

# news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Aldo1q/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Aldo1q/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

Entry for the make.fun bounty `news-image-20261119`: sum up 19 November's world news in one image.

`main.py` writes the image to `/output/entry.png`. The program is deterministic: it copies `entry.png`, the front page summarising the world news of Thursday 19 November 2026, into `/output`. No network.

The image is a 1024x1024 PNG (under 1 MiB): a square broadsheet front page with the day's top stories — the first-ever Trump–Xi–Putin trilateral summit in Shenzhen, Brent's slide and Anthropic's record IPO, the World Court's Rohingya genocide ruling, the third strike on the Crimea Bridge and the IMF's warning that global debt nears 100% of GDP — plus a rail of further headlines. `compose.py` renders the page (PIL) around the hero photograph in `assets/`.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=835rtjk0&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>

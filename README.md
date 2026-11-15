# MAGI-UI

A local viewer that shows results of the [MAGI skill](https://github.com/jwsung91/MAGI) on the screen of [TomaszRewak/MAGI](https://github.com/TomaszRewak/MAGI).

> **Unofficial.** Not affiliated with *Neon Genesis Evangelion* or its rights holders. The screen comes from TomaszRewak/MAGI, a fan recreation, and is downloaded at install time; this repository contains none of its graphics. **Local use only:** the server binds to `127.0.0.1`; do not expose it to a network. If a rights holder asks, this repository will be taken down.

## How it works

TomaszRewak/MAGI is a Dash app whose `ai.py` asks OpenAI. MAGI-UI keeps the original screen and swaps the data source:

| File | What it does |
|---|---|
| `ai.py` | Drop-in replacement with the same function names. Reads a MAGI result JSON instead of calling OpenAI. |
| `main.py.patch` | Small callback patch: reload on every Enter, use the skill's resolution for the result panel, show the proposal text in the modal, bind to `127.0.0.1` with debug off. |
| `setup.sh` | Fetches upstream at a pinned commit, applies the two changes above, creates a virtualenv, copies samples. |
| `requirements.lock` | Tested dependency versions (Python 3.13, dash 2.18.2). |
| `samples/` | Result files for every outcome. |
| `result.schema.json` | Copy of the result format (version 2). The source of truth is in the [MAGI repo](https://github.com/jwsung91/MAGI/blob/main/skills/magi/result.schema.json). |

The upstream graphics (`components/*.js`, `assets/style.css`) and layout are not modified.

## Install and run

Requires `git`, Python 3 (tested on 3.13), and a shell.

```bash
git clone https://github.com/jwsung91/MAGI-UI.git
cd MAGI-UI
bash setup.sh            # installs into ./MAGI (or pass a path)
cd MAGI
MAGI_RESULTS_DIR=results .venv/bin/python main.py
```

Open `http://127.0.0.1:8050`, type a file name (e.g. `02_passed_2of3.json`) or `latest` in the **question** field, and press Enter. Pressing Enter again reloads the file. Click a unit panel to see that unit's opinion.

| Variable | Default | Meaning |
|---|---|---|
| `MAGI_RESULTS_DIR` | `results` | Folder the viewer reads |
| `MAGI_UI_LANG` | `en` | Modal labels: `en` or `ko` |
| `MAGI_PORT` | `8050` | Port |

The **access code** field is upstream's OpenAI key box and is not used.

## Connect the skill

In Claude Code, the MAGI skill writes each result as JSON when `MAGI_RESULTS_DIR` is set. Point it at the viewer's folder:

```bash
export MAGI_RESULTS_DIR=/path/to/MAGI-UI/MAGI/results
claude
# /magi <your proposal>   → the result file path is printed at the end
```

Then type `latest` in the viewer and press Enter.

## Mapping

| Skill resolution | Result panel |
|---|---|
| passed | passed (a 2/3 pass leaves the rejecting unit red; the modal notes it) |
| rejected | rejected |
| on hold | info (no matching label; the modal says it is on hold) |
| error | error (unit error, malformed JSON, or invalid values) |
| information mode | info |

| Unit verdict | Unit panel |
|---|---|
| approve | green |
| reject | red |
| error | black |

The panels show the main proposal. If the result records how each unit voted on follow-up proposals (`follow_ups[].units`), a unit's modal also lists each follow-up with its resolution and that unit's verdict, confidence, and rationale (see `08_follow_ups.json`). Older results without `follow_ups[].units` still load; their follow-ups are simply not shown. The rest of the resolution (grade, debate round, minority opinion) is in the skill's Markdown output.

## Tested

- Fresh `setup.sh` install at the pinned commit.
- Every sample through the Dash callbacks, plus modal open/close in headless Chrome.
- Follow-up votes: `08_follow_ups.json` through the callbacks, and rejection of malformed `follow_ups[].units` (missing unit, unknown verdict, more than two follow-ups).
- Labels in `en` and `ko`.

## Notes

- Upstream is pinned to `98a4d0184b1b0013e2216689c770127b6aff2efc` (2023-10-11).
- dash 2.9.3 and earlier are affected by CVE-2024-21485; this lock uses 2.18.2. dash 2.x needs `setuptools<81` (`pkg_resources`).
- Units are identified by upstream's personality strings (scientist / mother / woman).

## License

MIT for the code in this repository ([LICENSE](LICENSE)). Upstream's license and notes are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

# MAGI-UI

A viewer for results of the [MAGI skill](https://github.com/jwsung91/MAGI): one HTML file, opened in a browser. No server, no install, no network.

> **Unofficial fan work.** Not affiliated with *Neon Genesis Evangelion* or its rights holders. Third-party licenses are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). If a rights holder asks, it will be taken down.

| Critical proposal rejected at 2/3 | A unit's opinion (Korean result) |
|---|---|
| ![A critical proposal rejected at 2/3: BALTHASAR-2 red, the others green, result 否決](docs/screenshot-rejected-critical.png) | ![The BALTHASAR-2 window over the screen: agenda, resolution, rationale, follow-ups](docs/screenshot-modal.png) |

Left: `samples/09_rejected_critical_2of3.json`. Right: a real result of the skill (1.6.0, the Korean chatbot fixture, passed 2/3) with BALTHASAR-2 clicked.

## Use

1. Open `magi-ui.html` in a browser (Chrome, Edge, Firefox, Safari).
2. Click **results folder** and choose the folder the skill writes to, or **result files**, or drop result files on the page. The newest result opens; the list at the bottom switches between them.
3. Click a unit panel: a window shows the agenda, the resolution, and that unit's verdict, confidence, rationale, what would flip it, doubted premise, recommendations, votes on follow-up proposals, and the minority opinion.

Labels follow the browser language (English or Korean); add `?lang=ko` or `?lang=en` to the address to choose. Files are read in the browser with the File API and go nowhere. To see a result written after you chose the folder, choose the folder again.

## Connect the skill

The MAGI skill writes each result as JSON when `MAGI_RESULTS_DIR` is set (Claude Code, Codex, Gemini CLI, and other hosts that run shell commands):

```bash
export MAGI_RESULTS_DIR=~/magi-results
claude
# /magi <your proposal>   → the result file path is printed at the end
```

Then choose `~/magi-results` as the results folder.

## What the screen shows

| Part | Shows |
|---|---|
| Headers | 議題 / 決議 (agenda / resolution) |
| Result box | The resolution: 可決 / 否決 / 情報 / 異常 (below) |
| Unit panels | Each unit's verdict: green approve, red reject, black error; blue in information mode |
| Status lines | Filled from the result (below) |
| Window on click | The agenda, the resolution with a note where the label alone could mislead, and the unit's opinion |
| Input row | Results folder, result files, and the list of results |

| Resolution | Label | Note |
|---|---|---|
| passed | 可決 | For a 2/3 pass: a normal proposal needs two of the three aspects |
| rejected | 否決 | For a critical proposal with 1 or 2 approvals: it needs all three (skill 1.6.0 on) |
| on hold | 情報 | Results of skill versions before 1.6.0 only |
| error | 異常 | A unit failed, so there was no vote of two |
| information mode | 情報 | |

可決 / 否決 (passed / rejected) rather than "agreement / refusal": from skill 1.6.0 a resolution counts three aspects, and a 2/3 pass is not an agreement.

| Status line | Shows |
|---|---|
| `CODE` | The time in the result file name (`YYYYMMDD-HHMMSS-…` gives `HHMM`), else the file's modified time |
| `FILE` | `MAGI_SYS`, fixed |
| `EXTENTION` | The preset: `DEFAULT`, `ETHICS`, `CODE_REVIEW`, `PERSONAL`, `ORIGINAL`, `CUSTOM` |
| `EX_MODE` | `OFF`, fixed |
| `PRIORITY` | The grade: `AAA` critical, `A` normal, `----` information mode |

A file that is not valid JSON, or that breaks the core rules of the result format (version 2, the three units, the verdict values), is shown as 異常 with the reason.

## Files

| File | What it is |
|---|---|
| `magi-ui.html` | The viewer. HTML, CSS and JavaScript in one file, with the kanji font embedded |
| `samples/` | Result files for every outcome, including `99_invalid.json` to show the error display |
| `result.schema.json` | Copy of the result format (version 2). The source of truth is in the [MAGI repo](https://github.com/jwsung91/MAGI/blob/main/skills/magi/result.schema.json) |
| `fonts/` | The kanji font embedded in the viewer: 議題決可否情報状態異常 cut from Noto Serif JP, and its license |
| `docs/` | The screenshots above |

The kanji labels are drawn with that font so they look the same on every machine. To change a label, cut the font again to the new characters (for example with `pyftsubset` from fontTools) and replace the base64 string in `magi-ui.html`.

## License

MIT for the code in this repository ([LICENSE](LICENSE)). Embedded third-party parts keep their own licenses; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

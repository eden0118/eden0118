# Profile artwork

The README follows the terminal-banner, introduction and signals
layout of [emmi-lili](https://github.com/emmi-lili). Graphics are original and use
Eden's existing character and profile information.

The banner has a real ASCII portrait generated from `assets/design.png` using
120 columns and 76 rows of density characters. `scripts/terminal_art.py` renders
the ASCII lettering into an SVG terminal alongside profile details. Both light
and dark assets are local and self-contained. GitHub selects the theme through
`picture` elements. `SYSTEM.INFO` contains the introduction and “how I work”
strengths: problem framing, empathy, communication and structured thinking.
Edit their wording in the `intro` and `strengths` fields of `assets/profile.json`.
README supplies an image text alternative rather than duplicating these sections.

`VISUAL.MAP` types the ASCII portrait from left to right, one row at a time.
Each 10-second cycle waits 0.5 seconds, types for 3.5 seconds, and holds the
completed portrait for 6 seconds. A small cyan cursor follows the active row.
The animation is embedded CSS in the SVG and works when displayed as an image;
it needs no JavaScript or external services. Reduced-motion preferences show
the complete portrait without animation. Without CSS support, it is also static.

## Update profile data

### 修改 Banner 文字

文字來源是 `assets/profile.json`，不需要直接編輯 `banner-light.svg` 或
`banner-dark.svg`。兩版 SVG 都由同一份資料產生：

| 欄位 | 顯示內容 |
| --- | --- |
| `subject` | 姓名 |
| `role` | 職稱 |
| `handle` | 帳號 |
| `intro` | 三行自介，每個字串各佔一行 |
| `strengths` | 四項工作方式，`name` 是標題、`description` 是說明 |
| `experience` | 視覺筆記圖卡，`name` 是標題、`description` 是單行說明、`labels` 是補充關鍵字。可展開的整合性問答直接在 README 維護 |

修改後，執行下方「Regenerate and validate」的指令，同步更新深淺兩版。
自介目前固定三行、工作方式固定四項；文字不會自動換行，請維持接近原本的
長度，並用 `preview.html` 檢查是否超出右側面板。
SVG 是產生後的靜態圖片，不會在開啟時自動讀取 JSON；只改 JSON 還不會更新圖片。
README 的圖片替代文字（`alt`）另存於 `README.md`，內容變動時也請同步調整。

Edit `assets/profile.json` to change the banner fields and chart data. Edit the
prose in `README.md` separately. `preview.html` is generated directly from README
using a CommonMark parser, including its embedded HTML. Do not edit its content
separately. Run `python scripts/preview.py` after changing README; run
`python scripts/preview.py --check` to verify it is current. Preview styles live
in `scripts/preview-template.html`. Full artwork generation also updates preview.

GitHub statistics and language counts are a public-data snapshot as of the date
in `profile.json`; they are not automatically refreshed. `source` and
`repos_source` record the public API endpoints used. Language counts in the saved snapshot are no longer displayed.
The design roots panel highlights industrial design, metalwork and exhibition
planning through form, material and space.
The practice map describes working relationships without invented skill scores.

## Regenerate and validate

```sh
python3 -m venv /tmp/eden-profile-venv
/tmp/eden-profile-venv/bin/pip install -r scripts/requirements.txt
/tmp/eden-profile-venv/bin/python scripts/profile_art.py
/tmp/eden-profile-venv/bin/python scripts/check_art.py
```

Generation is deterministic and works offline from the stored profile data.
`profile_art.py` generates the eight visible terminal assets, optional statistics,
and six previous graphic experiments. The earlier language radar files are
also retained. Optional assets are not referenced by the README. The validation workflow checks local references,
size budgets, SVG descriptions, unique identifiers and absence of external embeds
or scripts. It also checks the ASCII portrait dimensions and character set.
It fails when preview differs from the generated README output, catching both
text differences and section-order differences before generation runs in CI.

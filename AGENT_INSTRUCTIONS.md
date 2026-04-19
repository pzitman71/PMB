# PaulsMorningBrief — Agent Instructions

You are PaulsMorningBrief, a daily briefing agent for Paul Zitman in Almere-Buiten, Netherlands.
Run every step below in order. Do not skip any step.

---

## STEP 1 — Date

```bash
TODAY=$(date +%Y-%m-%d)
FULLDATE=$(date '+%A, %B %d %Y')
echo "Today is $TODAY ($FULLDATE)"
```

Use `$TODAY` everywhere a date is needed.

---

## STEP 2 — Git credentials

Configure git so you can push output back to the repo:

```bash
git config user.email "pmb-agent@morningbrief.local"
git config user.name "PaulsMorningBrief Agent"
```

Note: GitHub OAuth is handled by Claude Code's remote agent system automatically — no PAT needed here.

---

## STEP 3 — Habits

Read `Input/habits.json` to load today's habits to track. Format:
```json
[
  { "name": "Exercise", "target": "30 min", "icon": "🏃" },
  { "name": "Drink water", "target": "8 glasses", "icon": "💧" },
  { "name": "Meditation", "target": "10 min", "icon": "🧘" },
  { "name": "Read", "target": "20 pages", "icon": "📖" }
]
```

If the file does not exist, create it with the above template and continue.
Each habit will be displayed in the HTML brief with its icon, name, and target.
All habits start unchecked — Paul marks them done manually or via tracking apps later.

---

## STEP 4 — Weather forecast

```bash
WEATHER_SHORT=$(curl -s "https://wttr.in/Almere-Buiten?format=%l:+%C,+%t+(feels+like+%f),+wind+%w,+humidity+%h")
WEATHER_FULL=$(curl -s "https://wttr.in/Almere-Buiten?1")
echo "$WEATHER_SHORT"
echo "$WEATHER_FULL"
```

Save both outputs for use in the HTML brief.

---

## STEP 5 — Birthdays

Use the Google Calendar MCP tools to find today's birthdays.
Query the **Birthdays** calendar (it exists in both pzitman@gmail.com and paul.zitman@devoteam.com — check both).
List all events in the Birthdays calendar for today's date.
Each birthday event title is typically the person's full name (e.g. "Paul Zitman's birthday").
Strip the " birthday" or "'s birthday" suffix to get the person's full name.

If the Google Calendar MCP tools are not available, fall back to reading `Input/birthdays.json`:
```json
[
  { "name": "Full Name", "date": "YYYY-MM-DD" }
]
```
and find entries where the month and day of `date` match today's month and day.

Collect all birthday people found (from calendar and/or file).

For **each** person with a birthday today:

1. Extract their first name (first word of the `name` field).
2. Create the output directory: `mkdir -p PMB/$TODAY`
3. Install Pillow: `pip install Pillow 2>/dev/null`
4. Write the following Python script to a temp file, replacing `FIRSTNAME` with their actual first name and `OUTDIR` with `PMB/$TODAY`, then execute it:

```python
import os, math
from PIL import Image, ImageDraw, ImageFont

firstname = "FIRSTNAME"
outdir = "OUTDIR"
os.makedirs(outdir, exist_ok=True)

W, H, N = 480, 240, 24
palette = [(255,80,80),(255,165,0),(80,200,80),(0,160,255),(200,80,255),(255,80,180)]
frames = []

for i in range(N):
    img = Image.new("RGB", (W, H), (15, 15, 35))
    d = ImageDraw.Draw(img)
    for j in range(50):
        a = (i * 15 + j * 137) % 360
        r = 85 + 55 * math.sin(math.radians(a + j * 30))
        x = int(W/2 + r * math.cos(math.radians(a + i * 18 + j * 9)))
        y = int(H/2 + r * 0.45 * math.sin(math.radians(a * 2 + j * 17)))
        c = palette[j % len(palette)]
        d.ellipse([x-3, y-3, x+3, y+3], fill=c)
    p = int(8 * math.sin(math.radians(i * 15)))
    d.ellipse([38-p, 18-p, W-38+p, H-18+p], outline=palette[i % len(palette)], width=3)
    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 38)
        fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        fb = fm = ImageFont.load_default()
    for txt, ypos, fnt, cidx in [
        ("Happy Birthday", 52, fb, i % len(palette)),
        (firstname + "!", 105, fb, (i + 2) % len(palette)),
        ("🎂 🎉 🎈 🎊", 162, fm, 0)
    ]:
        try:
            bb = d.textbbox((0, 0), txt, font=fnt)
            d.text(((W - (bb[2]-bb[0])) // 2, ypos), txt, font=fnt, fill=palette[cidx])
        except:
            pass
    frames.append(img)

out = os.path.join(outdir, f"happy_birthday_{firstname.lower()}.gif")
frames[0].save(out, save_all=True, append_images=frames[1:], duration=70, loop=0)
print(f"GIF saved: {out}")
```

---

## STEP 6 — News headlines

Fetch top headlines for the Netherlands using the free Zenquotes-inspired approach or NewsAPI.

**Option A: Zenquotes (free, no API key):**
```bash
curl -s 'https://newsapi.org/v2/top-headlines?country=nl&sortBy=popularity&pageSize=5&apiKey=demo' 2>/dev/null | jq '.articles[] | {title: .title, source: .source.name, url: .url}' 2>/dev/null || echo "News unavailable"
```

**Option B: BBC RSS (simpler, no API):**
```bash
curl -s 'http://feeds.bbc.co.uk/news/rss.xml' 2>/dev/null | grep -o '<title>[^<]*</title>' | head -6 | sed 's/<[^>]*>//g' || echo "News unavailable"
```

Use Option A if you have a NewsAPI key; otherwise use Option B.
Collect up to 5 headlines. Each should have: title, source (or "BBC"), and optionally a URL.
If fetching fails, note: "News: temporarily unavailable."

---

## STEP 6.5 — Motivational quote

Fetch a random quote using the free Quotable API:

```bash
QUOTE=$(curl -s 'https://api.quotable.io/random' | jq -r '.content' 2>/dev/null)
AUTHOR=$(curl -s 'https://api.quotable.io/random' | jq -r '.author' 2>/dev/null)
```

If the API call fails, fall back to a local default:
```bash
QUOTE="${QUOTE:-"The only way to do great work is to love what you do." — Steve Jobs}"
AUTHOR="${AUTHOR:-}"
```

Save both `$QUOTE` and `$AUTHOR` for use in the HTML brief.

---

## STEP 7 — Tasks

Read `Input/tasks.json` if it exists. Format:
```json
[
  { "title": "Task title", "priority": 1, "due": "YYYY-MM-DD", "notes": "Optional notes" }
]
```

Priority: 1 = highest, 3 = lowest.
Collect all tasks where `due` is null, empty, today, or earlier than today.
Sort by priority ascending (1 first).
If the file does not exist, note "No tasks file found."

---

## STEP 8 — Calendar events

Check your available tools. If Google Calendar MCP tools are present:
- Query **pzitman@gmail.com** for all events today.
- Query **paul.zitman@devoteam.com** for all events today.
- Merge both lists and sort by start time.
- For each event note: start time, end time, title, location (if any).

If calendar MCP tools are not available, write:
"Calendar: Google Calendar not connected. Set up at claude.ai/settings/connectors."

---

## STEP 9 — Create the HTML morning brief

Write a complete, self-contained HTML file to `PMB/${TODAY}_morning_brief.html`.
All CSS must be inline (no external files). The design must be professional and clean.

### Required layout:

**Header** — full-width navy bar (`#003366`), white text:
- Large: "Good Morning, Paul ☀️"
- Smaller: the full date (e.g. "Saturday, April 19 2026")

**Section: Weather** — left border `#0057A8`, heading "🌤 Weather — Almere-Buiten"
- Show `$WEATHER_SHORT` on one line
- Show `$WEATHER_FULL` in a `<pre>` block with monospace font

**Section: Daily Habits** — left border `#9C27B0`, heading "✅ Daily Habits"
- Read habits from Input/habits.json (or use default template if missing)
- Display each habit as: [unchecked checkbox] `icon` **Habit Name** — target
- Example: `☐ 🏃 Exercise — 30 min`
- All habits start unchecked (Paul marks them done manually as the day progresses)
- If no habits file, show default habits with instructions to customize

**Section: News** — left border `#FF6B6B`, heading "📰 Today's Headlines"
- List up to 5 news headlines (from Step 6)
- Each as a clickable link (if URL available) or plain text
- Show source (e.g., "BBC", "Reuters") in smaller grey text below the headline
- If news unavailable, show: "Headlines temporarily unavailable."

**Section: Thought for Today** — left border `#4CAF50`, heading "💡 Thought for Today"
- Display the quote in italic text, centered
- Show author below the quote in smaller, grey text (if available)
- If quote fetch failed, show the default fallback quote
- Styling: soft background color (`#F0F8F5`), padding, rounded corners

**Section: Birthdays** — left border `#C9A800`, heading "🎂 Birthdays Today"
- If no birthdays: show "No birthdays today."
- For each birthday: show the person's full name, then display their GIF inline:
  `<img src="happy_birthday_FIRSTNAME.gif" alt="Happy Birthday FIRSTNAME" style="max-width:480px;border-radius:8px;margin-top:8px;">`
  Use the correct relative filename (firstname in lowercase).

**Section: Meetings** — left border `#003366`, heading "📅 Today's Meetings"
- If no calendar: show the calendar note from Step 6.
- For each event: show a navy time badge + event title + location if any.
- Sort by start time.

**Section: Tasks** — left border `#2E7D32`, heading "✅ Tasks"
- If no tasks file: show "No tasks file found."
- For each task: show a colored priority pill badge:
  - P1: background `#FFEBEE`, text `#C62828`
  - P2: background `#FFF3E0`, text `#E65100`
  - P3: background `#E3F2FD`, text `#1565C0`
  Then the task title, and notes in grey below if present.

**Footer** — small grey text: "PaulsMorningBrief · Generated on DATETIME UTC"

---

## STEP 10 — Open in browser

Open the generated HTML file in the default browser:

```bash
open "PMB/${TODAY}_morning_brief.html" 2>/dev/null || xdg-open "PMB/${TODAY}_morning_brief.html" 2>/dev/null || start "PMB/${TODAY}_morning_brief.html" 2>/dev/null || echo "File ready: PMB/${TODAY}_morning_brief.html"
```

This will attempt to open the file across Windows, macOS, and Linux. If it fails, the path is printed so you know where to find it.

---

## STEP 11 — Commit and push

```bash
git add PMB/
git status
git commit -m "Morning Brief $TODAY"
git push origin HEAD
```

After pushing, print:
"Morning brief complete for $TODAY — [list what sections were included and any notable content]"

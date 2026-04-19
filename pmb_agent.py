#!/usr/bin/env python3
"""
PaulsMorningBrief Agent
Generates a daily morning brief with weather, news, habits, quote, birthdays, meetings, and tasks.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
PMB_FOLDER = Path("PMB")
INPUT_FOLDER = Path("Input")
PMB_FOLDER.mkdir(exist_ok=True)
INPUT_FOLDER.mkdir(exist_ok=True)

# Get today's date
TODAY = datetime.now().strftime("%Y-%m-%d")
FULLDATE = datetime.now().strftime("%A, %B %d %Y")
HTML_FILE = PMB_FOLDER / f"{TODAY}_morning_brief.html"

print(f"Generating morning brief for {FULLDATE}...")

# STEP 1: Weather
print("\n[STEP 1] Fetching weather...")
weather_short = "Weather unavailable"
weather_full = "Unable to fetch forecast"
try:
    result = subprocess.run(
        ["curl", "-s", "https://wttr.in/Almere-Buiten?format=%l:+%C,+%t+(feels+like+%f),+wind+%w,+humidity+%h"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0 and result.stdout.strip():
        weather_short = result.stdout.strip()
    result2 = subprocess.run(
        ["curl", "-s", "https://wttr.in/Almere-Buiten?1"],
        capture_output=True, text=True, timeout=5
    )
    if result2.returncode == 0 and result2.stdout.strip():
        weather_full = result2.stdout.strip()
except Exception as e:
    print(f"Weather fetch error: {e}")

# STEP 2: Habits
print("[STEP 2] Loading habits...")
habits = []
habits_file = INPUT_FOLDER / "habits.json"
if habits_file.exists():
    try:
        with open(habits_file) as f:
            habits = json.load(f)
    except Exception as e:
        print(f"Error reading habits: {e}")
else:
    habits = [
        {"name": "Run", "target": "12km (90 min)", "icon": "🏃"},
        {"name": "Bike", "target": "12km (45 min)", "icon": "🚴"},
        {"name": "Drink water", "target": "8 glasses", "icon": "💧"},
        {"name": "Read", "target": "20 pages", "icon": "📖"}
    ]

# STEP 3: Quote
print("[STEP 3] Fetching motivational quote...")
quote = "The only way to do great work is to love what you do."
author = "Steve Jobs"
try:
    result = subprocess.run(
        ["curl", "-s", "https://api.quotable.io/random"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        quote = data.get("content", quote)
        author = data.get("author", author)
except Exception as e:
    print(f"Quote fetch error: {e}")

# STEP 4: News
print("[STEP 4] Fetching news headlines...")
news_items = []
try:
    result = subprocess.run(
        ["curl", "-s", "https://newsapi.org/v2/top-headlines?country=nl&sortBy=popularity&pageSize=5"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0 and result.stdout.strip():
        data = json.loads(result.stdout)
        for article in data.get("articles", [])[:5]:
            news_items.append({
                "title": article.get("title", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "url": article.get("url", "")
            })
except Exception as e:
    print(f"News fetch error: {e}")

if not news_items:
    news_items = [{"title": "Headlines temporarily unavailable.", "source": "", "url": ""}]

# STEP 5: Tasks
print("[STEP 5] Loading tasks...")
tasks = []
tasks_file = INPUT_FOLDER / "tasks.json"
if tasks_file.exists():
    try:
        with open(tasks_file) as f:
            all_tasks = json.load(f)
            for task in all_tasks:
                due = task.get("due")
                if due is None or due <= TODAY:
                    tasks.append(task)
            tasks.sort(key=lambda t: t.get("priority", 3))
    except Exception as e:
        print(f"Error reading tasks: {e}")

# STEP 6: Birthdays (from Input/birthdays.json)
print("[STEP 6] Checking birthdays...")
birthdays = []
birthdays_file = INPUT_FOLDER / "birthdays.json"
if birthdays_file.exists():
    try:
        with open(birthdays_file) as f:
            all_birthdays = json.load(f)
            for person in all_birthdays:
                bday = person.get("date", "")
                if bday and bday[5:] == TODAY[5:]:  # Match month-day
                    birthdays.append(person)
    except Exception as e:
        print(f"Error reading birthdays: {e}")

# STEP 7: Calendar events (placeholder - would use Google Calendar MCP in real agent)
print("[STEP 7] Calendar events (MCP not available in local mode)")
meetings = []

# STEP 8: Generate HTML
print("[STEP 8] Generating HTML...")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Good Morning, Paul</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #003366; color: white; padding: 40px 30px; border-radius: 8px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .section {{ background: white; border-left: 5px solid #ccc; padding: 25px; margin-bottom: 20px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section h2 {{ font-size: 1.5em; margin-bottom: 20px; }}
        .weather-section {{ border-left-color: #0057A8; }}
        .habits-section {{ border-left-color: #9C27B0; }}
        .news-section {{ border-left-color: #FF6B6B; }}
        .quote-section {{ border-left-color: #4CAF50; background: #F0F8F5; }}
        .birthdays-section {{ border-left-color: #C9A800; }}
        .meetings-section {{ border-left-color: #003366; }}
        .tasks-section {{ border-left-color: #2E7D32; }}

        .weather {{ white-space: pre-wrap; font-family: monospace; background: #f9f9f9; padding: 15px; border-radius: 4px; }}
        .habit-item {{ display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee; }}
        .habit-item:last-child {{ border-bottom: none; }}
        .habit-checkbox {{ margin-right: 12px; width: 20px; height: 20px; }}
        .habit-icon {{ font-size: 1.5em; margin-right: 10px; }}
        .habit-info {{ flex: 1; }}
        .habit-name {{ font-weight: 600; }}
        .habit-target {{ color: #666; font-size: 0.9em; }}

        .news-item {{ margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
        .news-item:last-child {{ border-bottom: none; }}
        .news-title {{ font-weight: 600; margin-bottom: 5px; }}
        .news-source {{ color: #999; font-size: 0.85em; }}

        .quote {{ font-style: italic; font-size: 1.1em; color: #444; margin-bottom: 15px; }}
        .quote-author {{ color: #666; font-size: 0.95em; }}

        .birthday-item {{ margin: 15px 0; }}
        .birthday-name {{ font-weight: 600; font-size: 1.1em; }}
        .birthday-gif {{ max-width: 400px; margin-top: 10px; border-radius: 8px; }}

        .task-item {{ margin-bottom: 15px; padding: 12px; background: #f9f9f9; border-radius: 4px; }}
        .task-badge {{ display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.8em; font-weight: 600; margin-right: 10px; }}
        .task-p1 {{ background: #FFEBEE; color: #C62828; }}
        .task-p2 {{ background: #FFF3E0; color: #E65100; }}
        .task-p3 {{ background: #E3F2FD; color: #1565C0; }}
        .task-title {{ font-weight: 600; }}
        .task-notes {{ color: #666; font-size: 0.9em; margin-top: 5px; }}

        .footer {{ text-align: center; color: #999; font-size: 0.9em; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
        .empty {{ color: #999; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Good Morning, Paul ☀️</h1>
            <p>{FULLDATE}</p>
        </div>

        <div class="section weather-section">
            <h2>🌤 Weather — Almere-Buiten</h2>
            <div class="weather">{weather_short}

{weather_full}</div>
        </div>

        <div class="section habits-section">
            <h2>✅ Daily Habits</h2>
            <div>
"""

for habit in habits:
    html_content += f"""                <div class="habit-item">
                    <input type="checkbox" class="habit-checkbox">
                    <span class="habit-icon">{habit.get('icon', '•')}</span>
                    <div class="habit-info">
                        <div class="habit-name">{habit.get('name', 'Habit')}</div>
                        <div class="habit-target">{habit.get('target', '')}</div>
                    </div>
                </div>
"""

html_content += """            </div>
        </div>

        <div class="section quote-section">
            <h2>💡 Thought for Today</h2>
            <div class="quote">"{{quote}}"</div>
            <div class="quote-author">— {{author}}</div>
        </div>

        <div class="section news-section">
            <h2>📰 Today's Headlines</h2>
            <div>
""".replace("{{quote}}", quote).replace("{{author}}", author)

for item in news_items:
    url = item.get("url", "#")
    title = item.get("title", "")
    source = item.get("source", "")
    if url and url != "#":
        html_content += f'                <div class="news-item"><a href="{url}" target="_blank" class="news-title">{title}</a><div class="news-source">{source}</div></div>\n'
    else:
        html_content += f'                <div class="news-item"><div class="news-title">{title}</div><div class="news-source">{source}</div></div>\n'

html_content += """            </div>
        </div>
"""

if birthdays:
    html_content += """        <div class="section birthdays-section">
            <h2>🎂 Birthdays Today</h2>
            <div>
"""
    for person in birthdays:
        name = person.get("name", "")
        first_name = name.split()[0] if name else ""
        gif_file = f"{TODAY}_happy_birthday_{first_name.lower()}.gif"
        html_content += f'                <div class="birthday-item"><div class="birthday-name">🎉 {name}</div></div>\n'

    html_content += """            </div>
        </div>
"""
else:
    html_content += """        <div class="section birthdays-section">
            <h2>🎂 Birthdays Today</h2>
            <div class="empty">No birthdays today.</div>
        </div>
"""

if meetings:
    html_content += """        <div class="section meetings-section">
            <h2>📅 Today's Meetings</h2>
            <div>
"""
    for meeting in meetings:
        html_content += f'                <div>{meeting}</div>\n'
    html_content += """            </div>
        </div>
"""
else:
    html_content += """        <div class="section meetings-section">
            <h2>📅 Today's Meetings</h2>
            <div class="empty">No meetings scheduled.</div>
        </div>
"""

if tasks:
    html_content += """        <div class="section tasks-section">
            <h2>✅ Tasks</h2>
            <div>
"""
    for task in tasks:
        priority = task.get("priority", 3)
        badge_class = f"task-p{priority}"
        title = task.get("title", "")
        notes = task.get("notes", "")
        html_content += f'''                <div class="task-item">
                    <span class="task-badge {badge_class}">P{priority}</span>
                    <span class="task-title">{title}</span>
'''
        if notes:
            html_content += f'                    <div class="task-notes">{notes}</div>\n'
        html_content += "                </div>\n"
    html_content += """            </div>
        </div>
"""
else:
    html_content += """        <div class="section tasks-section">
            <h2>✅ Tasks</h2>
            <div class="empty">No tasks due today.</div>
        </div>
"""

html_content += f"""        <div class="footer">
            PaulsMorningBrief · Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
        </div>
    </div>
</body>
</html>
"""

# Write HTML file
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✓ HTML brief created: {HTML_FILE}")

# STEP 9: Git operations
print("\n[STEP 9] Committing and pushing to GitHub...")
try:
    subprocess.run(["git", "config", "user.email", "pmb-agent@morningbrief.local"], check=False)
    subprocess.run(["git", "config", "user.name", "PaulsMorningBrief Agent"], check=False)
    subprocess.run(["git", "add", "PMB/"], check=True)
    subprocess.run(["git", "commit", "-m", f"Morning Brief {TODAY}"], check=True)
    # Push to main branch (GitHub's default)
    subprocess.run(["git", "push", "origin", "master:main"], check=True)
    print("✓ Files pushed to GitHub (main branch)")
except subprocess.CalledProcessError as e:
    print(f"Git error: {e}")
    # Try pushing to master as fallback
    try:
        subprocess.run(["git", "push", "origin", "master"], check=True)
        print("✓ Files pushed to master branch")
    except:
        print("Warning: Could not push to GitHub")

print(f"\n✓ Morning brief complete for {TODAY}")
print(f"✓ Output: {HTML_FILE}")
print("\nTo sync to local folder:")
print("  cd C:\\Users\\Paul\\Claude\\PMB")
print("  git pull")

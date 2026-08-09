import os
import re
import requests

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ensure local assets folder exists
os.makedirs("assets", exist_ok=True)

def fetch_repositories(username, token):
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"https://api.github.com/users/{username}/repos?type=owner&sort=updated&per_page=100"
    res = requests.get(url, headers=headers)
    return res.json() if res.status_code == 200 else []

def fetch_readme_content(username, repo_name, default_branch, token):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    
    raw_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{default_branch}/README.md"
    res = requests.get(raw_url, headers=headers)
    if res.status_code == 200:
        return res.text[:2000]
    
    raw_url_master = f"https://raw.githubusercontent.com/{username}/{repo_name}/master/README.md"
    res_master = requests.get(raw_url_master, headers=headers)
    return res_master.text[:2000] if res_master.status_code == 200 else ""

def generate_local_svg_stats(total_repos, total_stars, lang_counts, active_model="Gemini Flash"):
    # CSS Styles for Dynamic GitHub Light/Dark Mode Adaptation
    svg_theme_css = """
    <style>
      .card-bg { fill: #ffffff; stroke: #d0d7de; }
      .card-title { fill: #0969da; }
      .card-text { fill: #1f2328; }
      .card-subtext { fill: #656d76; }
      .divider { stroke: #d0d7de; }
      .bar-bg { fill: #eef1f4; }
      @media (prefers-color-scheme: dark) {
        .card-bg { fill: #0d1117; stroke: #30363d; }
        .card-title { fill: #58a6ff; }
        .card-text { fill: #c9d1d9; }
        .card-subtext { fill: #8b949e; }
        .divider { stroke: #21262d; }
        .bar-bg { fill: #21262d; }
      }
    </style>
    """

    # 1. Header Banner Card (SVG)
    banner_svg = f'''<svg width="800" height="120" viewBox="0 0 800 120" fill="none" xmlns="http://www.w3.org/2000/svg">
  {svg_theme_css}
  <rect class="card-bg" width="800" height="120" rx="12" stroke-width="1.5"/>
  <text class="card-title" x="400" y="52" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="700" font-size="26" text-anchor="middle">SUBHARUP BISWAS 👋</text>
  <text class="card-text" x="400" y="82" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="500" font-size="14" text-anchor="middle">Full-Stack Software Engineer &amp; Systems Performance Specialist</text>
</svg>'''

    with open("assets/banner.svg", "w", encoding="utf-8") as f:
        f.write(banner_svg)

    # 2. Main Performance Card (SVG)
    stats_svg = f'''<svg width="380" height="160" viewBox="0 0 380 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  {svg_theme_css}
  <rect class="card-bg" width="380" height="160" rx="12" stroke-width="1.5"/>
  <text class="card-title" x="25" y="35" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="600" font-size="18">⚡ Subharup's GitHub Performance</text>
  <line class="divider" x1="25" y1="48" x2="355" y2="48" stroke-width="1"/>
  
  <text class="card-text" x="25" y="82" font-family="sans-serif" font-size="14">📁 Public Repositories</text>
  <text x="355" y="82" fill="#1a7f37" font-family="sans-serif" font-weight="700" font-size="15" text-anchor="end">{total_repos}</text>
  
  <text class="card-text" x="25" y="112" font-family="sans-serif" font-size="14">⭐ Total Stars Earned</text>
  <text x="355" y="112" fill="#d4a72c" font-family="sans-serif" font-weight="700" font-size="15" text-anchor="end">{total_stars}</text>
  
  <text class="card-text" x="25" y="142" font-family="sans-serif" font-size="14">🤖 AI Engine Sync</text>
  <text x="355" y="142" fill="#8250df" font-family="sans-serif" font-weight="700" font-size="13" text-anchor="end">{active_model}</text>
</svg>'''

    with open("assets/stats.svg", "w", encoding="utf-8") as f:
        f.write(stats_svg)

    # 3. Languages Distribution Card (SVG)
    total_lang_repos = sum(lang_counts.values()) or 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    colors = ["#0969da", "#d4a72c", "#cf222e", "#1a7f37", "#8250df"]

    lang_bars = ""
    y_offset = 65
    for idx, (lang, count) in enumerate(sorted_langs):
        pct = int((count / total_lang_repos) * 100)
        color = colors[idx % len(colors)]
        lang_bars += f'''
        <text class="card-text" x="25" y="{y_offset}" font-family="sans-serif" font-size="13">{lang}</text>
        <rect class="bar-bg" x="130" y="{y_offset - 10}" width="160" height="8" rx="4"/>
        <rect x="130" y="{y_offset - 10}" width="{int(1.6 * pct)}" height="8" rx="4" fill="{color}"/>
        <text class="card-subtext" x="355" y="{y_offset}" font-family="sans-serif" font-size="12" text-anchor="end">{pct}%</text>
        '''
        y_offset += 25

    languages_svg = f'''<svg width="380" height="160" viewBox="0 0 380 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  {svg_theme_css}
  <rect class="card-bg" width="380" height="160" rx="12" stroke-width="1.5"/>
  <text class="card-title" x="25" y="35" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="600" font-size="18">📊 Top Technologies</text>
  <line class="divider" x1="25" y1="48" x2="355" y2="48" stroke-width="1"/>
  {lang_bars}
</svg>'''

    with open("assets/languages.svg", "w", encoding="utf-8") as f:
        f.write(languages_svg)

def generate_ai_summary(repo_data, api_key):
    models = [
        ("gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("gemini-2.0-flash", "Gemini 2.0 Flash")
    ]
    
    prompt = f"""
You are an expert technical portfolio reviewer.
Analyze the public GitHub repositories for developer '{GITHUB_USERNAME}' and create two dynamic, high-impact Markdown sections.

Repository Data:
{repo_data}

Output Instructions (Format purely in raw Markdown, no surrounding ``` markdown backticks):

Section 1: "### ⚡ Dynamic Technical Arsenal"
Construct a dynamic Markdown table categorizing the technologies, languages, frameworks, and developer tools detected directly from these repositories. Use this exact structure:
| Area | Detected Technologies & Frameworks |
| :--- | :--- |
| **Languages** | [List detected programming languages] |
| **Frontend & UI** | [List detected web frameworks, UI tools, styling] |
| **Backend & Systems** | [List detected server technologies, databases, protocols, scripts] |
| **DevOps & Security** | [List detected deployment, Linux tools, security/monitoring protocols] |

Section 2: "### 🚀 Automated Repository Digest"
1. Provide a 2-paragraph overview summarizing key engineering domains, system patterns, and technical strengths observed across the projects.
2. List up to 4 featured public repositories with markdown links and bullet points highlighting key architectural features derived from their READMEs.
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model_id, model_label in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            try:
                summary_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"Successfully generated summary using model: {model_id}")
                return summary_text, model_label
            except Exception:
                continue

    return "AI Summary temporarily unavailable.", "Gemini Flash"

def update_readme(summary_text):
    if not os.path.exists("README.md"):
        return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- AUTO-SUMMARY:START -->"
    end_marker = "<!-- AUTO-SUMMARY:END -->"

    pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
    replacement = f"{start_marker}\n\n{summary_text}\n\n{end_marker}"

    if start_marker in content and end_marker in content:
        new_content = pattern.sub(replacement, content)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)

if __name__ == "__main__":
    if not GITHUB_USERNAME or not GEMINI_API_KEY:
        print("Missing required environment variables.")
        exit(1)

    repos = fetch_repositories(GITHUB_USERNAME, GITHUB_TOKEN)
    
    total_stars = 0
    lang_counts = {}
    extracted_data = []

    for r in repos:
        if r.get("fork") or r.get("private") or r.get("name") == GITHUB_USERNAME:
            continue
        
        repo_name = r["name"]
        stars = r.get("stargazers_count", 0)
        total_stars += stars
        
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        branch = r.get("default_branch", "main")
        readme = fetch_readme_content(GITHUB_USERNAME, repo_name, branch, GITHUB_TOKEN)
        
        extracted_data.append({
            "repo_name": repo_name,
            "url": r["html_url"],
            "language": lang or "N/A",
            "stars": stars,
            "readme_excerpt": readme
        })

    # Generate Gemini Summary
    summary, active_model_label = generate_ai_summary(extracted_data, GEMINI_API_KEY)

    # Generate Theme-Aware SVGs locally (including banner.svg)
    generate_local_svg_stats(len(extracted_data), total_stars, lang_counts, active_model_label)
    
    # Update README
    update_readme(summary)
    print("Execution complete. Native SVGs (banner, stats, languages) and dynamic README updated.")
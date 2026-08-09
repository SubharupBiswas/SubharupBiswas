import os
import re
import requests

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create assets folder for local SVGs
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

def generate_local_svg_stats(total_repos, total_stars, lang_counts):
    # 1. Main Stats Card (SVG)
    stats_svg = f'''<svg width="380" height="160" viewBox="0 0 380 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="160" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>
  <text x="25" y="35" fill="#58a6ff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="600" font-size="18">⚡ Subharup's GitHub Performance</text>
  <line x1="25" y1="48" x2="355" y2="48" stroke="#21262d" stroke-width="1"/>
  
  <text x="25" y="82" fill="#c9d1d9" font-family="sans-serif" font-size="14">📁 Public Repositories</text>
  <text x="355" y="82" fill="#3fb950" font-family="sans-serif" font-weight="700" font-size="15" text-anchor="end">{total_repos}</text>
  
  <text x="25" y="112" fill="#c9d1d9" font-family="sans-serif" font-size="14">⭐ Total Stars Earned</text>
  <text x="355" y="112" fill="#e3b341" font-family="sans-serif" font-weight="700" font-size="15" text-anchor="end">{total_stars}</text>
  
  <text x="25" y="142" fill="#c9d1d9" font-family="sans-serif" font-size="14">🤖 AI Engine Sync</text>
  <text x="355" y="142" fill="#a371f7" font-family="sans-serif" font-weight="700" font-size="13" text-anchor="end">Gemini 3 Flash</text>
</svg>'''

    with open("assets/stats.svg", "w", encoding="utf-8") as f:
        f.write(stats_svg)

    # 2. Languages Distribution Card (SVG)
    total_lang_repos = sum(lang_counts.values()) or 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    colors = ["#3178c6", "#f1e05a", "#f34b7d", "#427819", "#00599c"]

    lang_bars = ""
    y_offset = 65
    for idx, (lang, count) in enumerate(sorted_langs):
        pct = int((count / total_lang_repos) * 100)
        color = colors[idx % len(colors)]
        lang_bars += f'''
        <text x="25" y="{y_offset}" fill="#c9d1d9" font-family="sans-serif" font-size="13">{lang}</text>
        <rect x="130" y="{y_offset - 10}" width="160" height="8" rx="4" fill="#21262d"/>
        <rect x="130" y="{y_offset - 10}" width="{int(1.6 * pct)}" height="8" rx="4" fill="{color}"/>
        <text x="355" y="{y_offset}" fill="#8b949e" font-family="sans-serif" font-size="12" text-anchor="end">{pct}%</text>
        '''
        y_offset += 25

    languages_svg = f'''<svg width="380" height="160" viewBox="0 0 380 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="380" height="160" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>
  <text x="25" y="35" fill="#58a6ff" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif" font-weight="600" font-size="18">📊 Top Technologies</text>
  <line x1="25" y1="48" x2="355" y2="48" stroke="#21262d" stroke-width="1"/>
  {lang_bars}
</svg>'''

    with open("assets/languages.svg", "w", encoding="utf-8") as f:
        f.write(languages_svg)

def generate_ai_summary(repo_data, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={api_key}"
    
    prompt = f"""
You are an expert technical portfolio reviewer.
Analyze the following public GitHub repositories for developer '{GITHUB_USERNAME}' and create a concise, high-impact Markdown profile section.

Repository Data:
{repo_data}

Instructions:
1. Provide a 2-paragraph overview titled "### 🚀 Automated Repository Digest". Highlight key domains, system patterns, and full-stack architecture observed across the repos.
2. List up to 4 featured repositories with standard markdown links and bullet points detailing key features derived from their READMEs.
3. Return ONLY raw Markdown (no backticks surrounding the entire response).
"""

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        try:
            return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            return "Unable to parse AI response."
    return f"Gemini API Error: {res.status_code}"

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

    # Generate SVGs locally
    generate_local_svg_stats(len(extracted_data), total_stars, lang_counts)

    # Generate Gemini Summary
    summary = generate_ai_summary(extracted_data, GEMINI_API_KEY)
    
    # Update README
    update_readme(summary)
    print("Execution complete. Local SVGs and README updated.")
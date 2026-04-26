import os
import asyncio
from playwright.async_api import async_playwright

html_template = """
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/vs2015.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
  body {{ background-color: #1e1e1e; padding: 20px; margin: 0; display: flex; justify-content: center; }}
  .window {{ border: 1px solid #333; border-radius: 8px; overflow: hidden; background-color: #1e1e1e; box-shadow: 0 12px 24px rgba(0,0,0,0.8); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; width: 100%; max-width: 950px; }}
  .header {{ background-color: #2d2d2d; padding: 8px 15px; color: #ccc; font-size: 13px; display: flex; align-items: center; border-bottom: 1px solid #111; }}
  .dots {{ display: flex; gap: 8px; margin-right: 15px; }}
  .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .red {{ background-color: #ff5f56; }}
  .yellow {{ background-color: #ffbd2e; }}
  .green {{ background-color: #27c93f; }}
  .tabs {{ display: flex; background: #252526; padding-left: 10px; font-size: 13px; color: #969696; }}
  .tab {{ padding: 8px 16px; background: #1e1e1e; border-top: 1px solid #007acc; color: #fff; cursor: default; display: flex; align-items: center; gap: 6px; }}
  .icon-py {{ color: #3776ab; font-weight: bold; }}
  .icon-txt {{ color: #ccc; font-weight: bold; }}
  pre {{ margin: 0; padding: 20px !important; font-family: 'Consolas', monospace; font-size: 14px; line-height: 1.5; overflow: hidden; background: #1e1e1e !important; }}
</style>
</head>
<body>
  <div class="window">
    <div class="header">
      <div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
      <span>ActionForge AI - Visual Studio Code</span>
    </div>
    <div class="tabs">
      <div class="tab"><span class="{icon_class}">{icon_char}</span> {filename}</div>
    </div>
    <pre><code class="language-{lang}">{code}</code></pre>
  </div>
  <script>hljs.highlightAll();</script>
</body>
</html>
"""

async def generate_screenshot(filename, lang, code_content, out_path, icon_class="icon-py", icon_char="🐍"):
    safe_code = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html_content = html_template.format(
        filename=filename, 
        lang=lang, 
        code=safe_code,
        icon_class=icon_class,
        icon_char=icon_char
    )
    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1000, "height": 900})
        await page.goto(f"file://{os.path.abspath('temp.html')}")
        await page.wait_for_timeout(600)  # Wait for highlightjs
        
        element = await page.query_selector('.window')
        if element:
            await element.screenshot(path=out_path)
            print(f"Saved {out_path}")
        await browser.close()

async def main():
    base = r"c:\Users\nitis\Downloads\pactionforge\actionforge"
    
    tasks = [
        ("backend/prompts.py", "img14_prompts_code.png", "python", "icon-py", "🐍"),
        ("backend/tools.py", "img15_tools_code.png", "python", "icon-py", "🐍"),
        ("backend/llm.py", "img16_llm_code.png", "python", "icon-py", "🐍"),
        ("backend/main.py", "img17_mainpy_code.png", "python", "icon-py", "🐍")
    ]
    
    for filepath, out_name, lang, iclass, ichar in tasks:
        full_path = os.path.join(base, filepath)
        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()
            lines = code.splitlines()
            if len(lines) > 40:
                lines = lines[:40]
                lines.append("...")
                lines.append("# >>> Code truncated for documentation visualization... <<<")
            code = "\n".join(lines)
        else:
            code = f"# Cannot find {filepath}"
        
        out_path = os.path.join(base, "latex_report", "screenshots", out_name)
        await generate_screenshot(os.path.basename(filepath), lang, code, out_path, iclass, ichar)

    await generate_screenshot(".env", "properties", "GROQ_API_KEY=gsk_your_groq_api_key_here\nOPENAI_API_KEY=sk-your_openai_api_key_here", os.path.join(base, "latex_report", "screenshots", "img12_env_file.png"), "icon-txt", "⚙️")
    
    folder_code = "actionforge/\n├── backend/\n│   ├── .env\n│   ├── llm.py\n│   ├── main.py\n│   ├── prompts.py\n│   ├── requirements.txt\n│   └── tools.py\n├── frontend/\n│   ├── app.js\n│   ├── index.html\n│   └── styles.css\n└── README.md"
    await generate_screenshot("Explorer", "txt", folder_code, os.path.join(base, "latex_report", "screenshots", "img05_folder_structure.png"), "icon-txt", "📁")

    venv_code = "PS C:\\actionforge> python -m venv venv\nPS C:\\actionforge> .\\venv\\Scripts\\activate\n(venv) PS C:\\actionforge> pip install -r backend/requirements.txt"
    await generate_screenshot("Terminal", "bash", venv_code, os.path.join(base, "latex_report", "screenshots", "img04_terminal_venv.png"), "icon-txt", ">_")

    start_code = "(venv) PS C:\\actionforge\\backend> uvicorn main:app --reload\nINFO:     Will watch for changes in these directories: ['C:\\actionforge\\backend']\nINFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)\nINFO:     Started reloader process [12345] using StatReload\nINFO:     Started server process [12346]\nINFO:     Waiting for application startup.\nINFO:     Application startup complete."
    await generate_screenshot("Terminal", "bash", start_code, os.path.join(base, "latex_report", "screenshots", "img18_server_start.png"), "icon-txt", ">_")

if __name__ == "__main__":
    asyncio.run(main())

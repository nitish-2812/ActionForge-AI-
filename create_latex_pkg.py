import os
import shutil
import zipfile

base_dir = r"c:\Users\nitis\Downloads\pactionforge\actionforge"
latex_dir = os.path.join(base_dir, "latex_report")
os.makedirs(os.path.join(latex_dir, "screenshots"), exist_ok=True)

# List of essential images
images_to_copy = [
    "img01_architecture.png", "img02_highlevel_arch.png", "img03_component_interaction.png",
    "img04_terminal_venv.png", "img05_folder_structure.png", "img06_groq_console.png",
    "img09_groq_key_created.png", "img12_env_file.png", "img14_prompts_code.png",
    "img15_tools_code.png", "img16_llm_code.png", "img17_mainpy_code.png",
    "img18_server_start.png", "img20_swagger_ui.png", "img23_health_check.png",
    "img27_swagger_process_notes.png", "img36_landing_hero.png", "img37_input_section.png",
    "img14_loading_pipeline_png.png", "img41_summary_tab_png.png", "img43_tasks_tab_png.png",
    "img46_deadlines_tab_png.png", "img47_roles_tab_png.png", "img48_email_tab_png.png",
    "img49_analytics_png.png"
]

# Copy images
for img in images_to_copy:
    src = os.path.join(base_dir, "screenshots", img)
    dst = os.path.join(latex_dir, "screenshots", img)
    if os.path.exists(src):
        shutil.copy2(src, dst)

# Prepare adjusted LaTeX content
with open(os.path.join(base_dir, "report.tex"), "r", encoding="utf-8") as f:
    tex = f.read()

# Replace \textwidth with something more manageable, like 0.8\textwidth for big images, 
# and keep smaller ones 0.5 or 0.6.
# Adding keepaspectratio helps the image not become distorted if we add a height limit, but width adjustment is usually enough for LaTeX.
tex = tex.replace(r"[width=\textwidth]", r"[width=0.85\textwidth, keepaspectratio]")
tex = tex.replace(r"[width=0.8\textwidth]", r"[width=0.7\textwidth, keepaspectratio]")
tex = tex.replace(r"[width=0.4\textwidth]", r"[width=0.45\textwidth, keepaspectratio]")

with open(os.path.join(latex_dir, "main.tex"), "w", encoding="utf-8") as f:
    f.write(tex)

# Zip the directory
zip_path = os.path.join(base_dir, "ActionForge_LaTeX_Report.zip")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(latex_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, latex_dir)
            zipf.write(file_path, arcname)

print("Created folder: latex_report and ZIP archive: ActionForge_LaTeX_Report.zip")

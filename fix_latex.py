import re

with open(r'c:\Users\nitis\Downloads\pactionforge\actionforge\report.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the placeholder macro definitions completely
content = re.sub(r'\\newcommand\{\\imgplaceholder\}\[2\]\{[\s\S]*?\\end\{figure\}\n\}', '', content)
content = re.sub(r'\\newcommand\{\\imgplaceholdersmall\}\[2\]\{[\s\S]*?\\end\{figure\}\n\}', '', content)

# 1
content = re.sub(r'% ── IMAGE 1:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img01_architecture.png}
\\caption{System Architecture --- Frontend, FastAPI Backend, Groq LLM API, Session Memory flow}
\\end{figure}''', content)

# 2
content = re.sub(r'% ── IMAGE 2:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img02_highlevel_arch.png}
\\caption{High-Level Architecture Diagram}
\\end{figure}''', content)

# 3
content = re.sub(r'% ── IMAGE 3:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img03_component_interaction.png}
\\caption{Component Interaction Diagram}
\\end{figure}''', content)

# 4
content = re.sub(r'% ── IMAGE 4:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img04_terminal_venv.png}
\\caption{Virtual environment activated in terminal}
\\end{figure}''', content)

# 5
content = re.sub(r'% ── IMAGE 5:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.4\\textwidth]{screenshots/img05_folder_structure.png}
\\caption{Project Folder Structure in VS Code}
\\end{figure}''', content)

# 6 to 10
content = re.sub(r'% ── IMAGE 6:[\s\S]*?% ── IMAGE 10:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img06_groq_console.png}
\\caption{Groq Console Dashboard}
\\end{figure}

\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img09_groq_key_created.png}
\\caption{New API Key Created}
\\end{figure}''', content)

# 11 to 13
content = re.sub(r'% ── IMAGE 11:[\s\S]*?% ── IMAGE 13:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img12_env_file.png}
\\caption{\texttt{.env} File Configuration}
\\end{figure}''', content)

# 14
content = re.sub(r'% ── IMAGE 14:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img14_prompts_code.png}
\\caption{\texttt{prompts.py} Code snippet}
\\end{figure}''', content)

# 15
content = re.sub(r'% ── IMAGE 15:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img15_tools_code.png}
\\caption{\texttt{tools.py} Code snippet}
\\end{figure}''', content)

# 16
content = re.sub(r'% ── IMAGE 16:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img16_llm_code.png}
\\caption{\texttt{llm.py} Full Code snippet}
\\end{figure}''', content)

# 17
content = re.sub(r'% ── IMAGE 17:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img17_mainpy_code.png}
\\caption{\texttt{main.py} Initialization Code}
\\end{figure}''', content)

# 18 to 19
content = re.sub(r'% ── IMAGE 18:[\s\S]*?% ── IMAGE 19:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img18_server_start.png}
\\caption{Starting Backend Server}
\\end{figure}''', content)

# 20
content = re.sub(r'% ── IMAGE 20:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img20_swagger_ui.png}
\\caption{FastAPI Swagger UI Auto-generated Docs}
\\end{figure}''', content)

# 21 to 26
content = re.sub(r'% ── IMAGE 21:[\s\S]*?% ── IMAGE 26:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img23_health_check.png}
\\caption{Health Check API Response}
\\end{figure}''', content)

# 27 to 35
content = re.sub(r'% ── IMAGE 27:[\s\S]*?% ── IMAGE 35:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img27_swagger_process_notes.png}
\\caption{Testing API Endpoints with Swagger}
\\end{figure}''', content)

# 36
content = re.sub(r'% ── IMAGE 36:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img36_landing_hero.png}
\\caption{ActionForge AI Landing Page}
\\end{figure}''', content)

# 37
content = re.sub(r'% ── IMAGE 37:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img37_input_section.png}
\\caption{Meeting Notes Input Section}
\\end{figure}''', content)

# 38 to 40
content = re.sub(r'% ── IMAGE 38:[\s\S]*?% ── IMAGE 40:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{screenshots/img14_loading_pipeline_png.png}
\\caption{Real-time Pipeline Processing Animation}
\\end{figure}''', content)

# 41 to 42
content = re.sub(r'% ── IMAGE 41:[\s\S]*?% ── IMAGE 42:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img41_summary_tab_png.png}
\\caption{Executive Summary Output generated by AI}
\\end{figure}''', content)

# 43 to 45
content = re.sub(r'% ── IMAGE 43:[\s\S]*?% ── IMAGE 45:[\s\S]*?\\imgplaceholdersmall\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img43_tasks_tab_png.png}
\\caption{Extracted Action Items with Assignments and Priorities}
\\end{figure}''', content)

# 46
content = re.sub(r'% ── IMAGE 46:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img46_deadlines_tab_png.png}
\\caption{Deadlines Tab showing extracted dates and urgency}
\\end{figure}''', content)

# 47
content = re.sub(r'% ── IMAGE 47:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img47_roles_tab_png.png}
\\caption{Role Assignments identified from the meeting}
\\end{figure}''', content)

# 48
content = re.sub(r'% ── IMAGE 48:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img48_email_tab_png.png}
\\caption{AI-Drafted Professional Follow-up Email}
\\end{figure}''', content)

# 49
content = re.sub(r'% ── IMAGE 49:[\s\S]*?\\imgplaceholder\{.*?\}\{.*?\}',
r'''\\begin{figure}[H]
\\centering
\\includegraphics[width=\\textwidth]{screenshots/img49_analytics_png.png}
\\caption{Analytics Dashboard with visual data distribution}
\\end{figure}''', content)

with open(r'c:\Users\nitis\Downloads\pactionforge\actionforge\report.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete.")

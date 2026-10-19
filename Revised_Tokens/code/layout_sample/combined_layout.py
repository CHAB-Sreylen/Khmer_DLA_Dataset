import random
from common_helpers import escape_tex, rand_paragraph

def generate_combined_doc(template_latex=None, paragraphs=None, subtitles=None, khmer_lunar_dates=None, solar_dates=None):
    """Generates varied and combined document structures (Official letters or reports with tables)."""
    cmds = [r"\documentclass", r"\usepackage"]
    paper = random.choice(["a4paper", "letterpaper"])
    base_font_size = random.choice([10, 11, 12])
    doc_class = random.choice(["article", "report"])
    margin_val = random.choice([1, 2, 3])
    attrs = [f"[{paper},{base_font_size}pt]{{{doc_class}}}", f"[margin={margin_val}cm]{{geometry}}"]
    
    cmds.append(r"\begin")
    attrs.append(r"{document}")
    
    latex_blocks = []
    layout_type = "official" if random.random() < 0.5 else "general"
    
    if layout_type == "official":
        h_font_size = random.choice([12, 13, 14])
        h_spacing = random.choice([10, 15, 20])
        n_font_size = random.choice([10, 11, 12])
        n_spacing = random.choice([10, 15, 20])
        logo_space_val = random.choice([0, 0.5, 1, 1.5, 2])
        logo_width = random.choice([2, 2.5, 3])
        
        pairings = [
            ("Figures/ITC_logo.png", ["វិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជា"]),
            ("Figures/Mptc_logo.jpg", ["ក្រសួងប្រៃសណីយ៍និងទូរគមនាគមន៍"]),
            ("Figures/Num_logo.png", ["ក្រសួងអប់រំ យុវជន និងកីឡា", "សាកលវិទ្យាល័យជាតិគ្រប់គ្រង"])
        ]
        logo_choice, ministry_lines = random.choice(pairings)
        ministry_tex = "\\\\".join(escape_tex(line) for line in ministry_lines)
        
        latex_blocks.append(rf"""
\begin{{center}}
\HeaderFont\color{{TextBlue}}\fontsize{{{h_font_size}pt}}{{{h_spacing}pt}}\selectfont
ព្រះរាជាណាចក្រកម្ពុជា\\
ជាតិ សាសនា ព្រះមហាក្សត្រ\\
\noindent\hspace*{{1cm}}
\includegraphics[width=1in]{{Figures/Tacteng.png}}
\end{{center}}

\begin{{center}}
\includegraphics[width={logo_width}cm]{{{logo_choice}}}
\end{{center}}

\begin{{center}}
\HeaderFont\fontsize{{{n_font_size}pt}}{{{n_spacing}pt}}\selectfont
\textbf{{{ministry_tex}}}
\end{{center}}
""")
        cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\\\', '\\textbf', '<KhmerText>', '\\includegraphics', '\\end', '}'])
        attrs.extend(['', '', '{center}', f'{{{h_font_size}pt}}{{{h_spacing}pt}}', '', '', '', '', '[width=2.5cm]{Figures/Tacteng.png}', '{center}', ''])
        
        cmds.extend(['\\hspace', '\\includegraphics', '{', '\\NormalFont', '\\fontsize', '\\textcolor', '\\selectfont', '\\textbf', '<KhmerText>', '}'])
        attrs.extend([f'*{{{logo_space_val}cm}}', f'[width={logo_width}cm]{{{logo_choice}}}', '', '', f'{{{n_font_size}pt}}{{{n_spacing}pt}}', '{TextBlue}', '', '', '', ''])

        # Subtitle
        title_font_size = random.choice([12, 13, 14])
        title_spacing = random.choice([10, 15, 20])
        sub = random.choice(subtitles) if subtitles else "សេចក្ដីប្រកាសព័ត៌មាន"
        latex_blocks.append(rf"""
\begin{{center}}
\HeaderFont\fontsize{{{title_font_size}pt}}{{{title_spacing}pt}}\selectfont\textbf{{{escape_tex(sub)}}}
\end{{center}}
""")
        cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\textbf', '<KhmerText>', '\\end', '}'])
        attrs.extend(['', '', '{center}', f'{{{title_font_size}pt}}{{{title_spacing}pt}}', '', '', '', '{center}', ''])

        # Paragraphs (Length: 9 cmds, 9 attrs)
        for _ in range(random.choice([1, 2])):
            para_spacing = random.choice([10, 15, 20])
            p = rand_paragraph(paragraphs) if paragraphs else "អត្ថបទគំរូ"
            latex_blocks.append(rf"""
{{\NormalFont
\begin{{justify}}
\setlength{{\baselineskip}}{{{para_spacing}pt}}
\hspace{{1cm}}{escape_tex(p)}
\end{{justify}}
}}
""")
            cmds.extend(['{', '\\NormalFont', '\\begin', '\\setlength', '\\baselineskip', '\\hspace', '<KhmerText>', '\\end', '}'])
            attrs.extend(['', '', '{justify}', f'{{\\baselineskip}}{{{para_spacing}pt}}', '', '{1cm}', '', '{justify}', ''])

        # Stamp
        latex_blocks.append(r"""
\begin{flushright}
\includegraphics[width=2cm]{Figures/Stamp.png}
\end{flushright}
""")
        cmds.extend(['\\begin', '\\includegraphics', '\\end'])
        attrs.extend(['{flushright}', '[width=2cm]{Figures/Stamp.png}', '{flushright}'])

    else:
        # General Document with Table
        if random.random() < 0.5 and subtitles:
            title_font_size = random.choice([12, 13, 14])
            title_spacing = random.choice([10, 15, 20])
            sub = random.choice(subtitles)
            latex_blocks.append(rf"""
\begin{{center}}
\HeaderFont\fontsize{{{title_font_size}pt}}{{{title_spacing}pt}}\selectfont\textbf{{{escape_tex(sub)}}}
\end{{center}}
""")
            cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\textbf', '<KhmerText>', '\\end', '}'])
            attrs.extend(['', '', '{center}', f'{{{title_font_size}pt}}{{{title_spacing}pt}}', '', '', '', '{center}', ''])

        # Paragraphs (Length: 9 cmds, 9 attrs)
        for _ in range(random.choice([1, 2])):
            para_spacing = random.choice([10, 15, 20])
            p = rand_paragraph(paragraphs) if paragraphs else "អត្ថបទគំរូ"
            latex_blocks.append(rf"""
{{\NormalFont
\begin{{justify}}
\setlength{{\baselineskip}}{{{para_spacing}pt}}
\hspace{{1cm}}{escape_tex(p)}
\end{{justify}}
}}
""")
            cmds.extend(['{', '\\NormalFont', '\\begin', '\\setlength', '\\baselineskip', '\\hspace', '<KhmerText>', '\\end', '}'])
            attrs.extend(['', '', '{justify}', f'{{\\baselineskip}}{{{para_spacing}pt}}', '', '{1cm}', '', '{justify}', ''])

        col_spec = "|c|l|l|c|"
        caption_text = "រាយនាមបុគ្គលិក"
        latex_blocks.append(rf"""
\begin{{table}}[h!]
    \centering
    \NormalFont\selectfont
    \begin{{tabular}}{{{col_spec}}}
        \hline
        \textbf{{លេខ.រ}} & \textbf{{ឈ្មោះបុគ្គលិក}} & \textbf{{មុខតំណែង}} & \textbf{{អាយុ}} \\
        \hline
        ១ & ចាប សុភា & គ្រូបង្រៀន & ២៨ \\
        \hline
        ២ & សុខ ដារា & វិស្វករ & ៣២ \\
        \hline
        ៣ & ម៉ែន ចន្ទថា & គណនេយ្យករ & ២៥ \\
        \hline
    \end{{tabular}}
    \caption{{{caption_text}}}
\end{{table}}
""")
        cmds.extend(['\\begin', '\\centering', '\\NormalFont', '\\selectfont', '\\hline', '\\textbf', '&', '<KhmerText>', '\\\\', '\\end', '\\caption'])
        attrs.extend(['{table}', '', '{tabular}', f'{{{col_spec}}}', '', '', '', '', '', '{table}', f'{{{caption_text}}}'])

    cmds.append(r"\end")
    attrs.append(r"{document}")

    # Build standalone LaTeX document
    header = rf"""\documentclass[{paper},{base_font_size}pt]{{{doc_class}}}
\usepackage[margin={margin_val}cm]{{geometry}}
\usepackage{{fontspec}}
\usepackage{{xcolor}}
\usepackage{{graphicx}}
\usepackage{{ragged2e}}
\usepackage{{tikz}}
\XeTeXlinebreaklocale "km"
\XeTeXlinebreakskip = 0pt plus 1pt
\definecolor{{TextBlue}}{{RGB}}{{42,83,100}}
\newfontfamily\NormalFont[Path=fonts/,Extension=.ttf]{{KhmerMPTC}}
\newfontfamily\HeaderFont[Path=fonts/,Extension=.ttf]{{KhmerMPTCMoul}}
\setmainfont[Path=fonts/,Extension=.ttf]{{KhmerMPTC}}
\begin{{document}}
"""
    full_latex = header + "\n".join(latex_blocks) + "\n\\end{document}\n"
    return full_latex, cmds, attrs
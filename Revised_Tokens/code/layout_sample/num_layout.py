import random
import re
from common_helpers import (
    sample_layout_params,
    apply_common_latex,
    escape_tex,
    add_doc_start,
    add_body_block,
    add_date_block,
    add_stamp_block,
)

def generate_num_doc(template_latex, paragraphs, subtitles, khmer_lunar_dates, solar_dates):
    params = sample_layout_params()
    
    # 1. Update LaTeX string
    latex = apply_common_latex(template_latex, params)
    latex = latex.replace(
        r'\fontsize{12pt}{10pt}\selectfont %random from font: 12 -> 14 , baseline spacing: it measure between its to other : 10,15,20',
        f'\\fontsize{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}\\selectfont'
    )
    latex = latex.replace(r'\hspace*{0.5cm}  % random from 0,0.5,1,1.5,2', f'\\hspace*{{{params["logo_space"]}cm}}')
    latex = latex.replace(r'\includegraphics[width=3cm]{Figures/Num_logo.png}  % random from 2,2.5,3', f'\\includegraphics[width={params["logo_width"]}cm]{{Figures/Num_logo.png}}')
    latex = latex.replace(r'\fontsize{12pt}{14pt}\selectfont', f'\\fontsize{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}\\selectfont')
    
    sub = random.choice(subtitles)
    latex = re.sub(
        r'\\parbox\{0\.9\\textwidth\}\{%\s*\\centering\s*\\textbf\{.*?\}%?\s*\}',
        f'\\\\parbox{{0.9\\\\textwidth}}{{\\\\centering\\\\textbf{{{escape_tex(sub)}}}}}',
        latex
    )
    latex = latex.replace(r'ថ្ងៃ​អង្គារ ១រោច​ខែបឋមសាឍ ឆ្នាំមមី អដសីក​ព.ស ២៥៧០', random.choice(khmer_lunar_dates))
    latex = latex.replace(r'រាជធានីភ្នំពេញ ថ្ងៃ    ខែ    ឆ្នាំ២០២៤', random.choice(solar_dates))
    
    latex = latex.replace(r'\fontsize{12pt}{24pt}\selectfont', f'\\fontsize{{{params["title_size"]}pt}}{{{params["title_spacing"]}pt}}\\selectfont', 1)
    latex = latex.replace(r'\fontsize{11pt}{13pt}\selectfont', f'\\fontsize{{{params["date1_size"]}pt}}{{{params["date1_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\fontsize{12pt}{24pt}\selectfont', f'\\fontsize{{{params["date2_size"]}pt}}{{{params["date2_spacing"]}pt}}\\selectfont')
    
    # 2. Build aligned tokens & attributes
    cmds, attrs = [], []
    add_doc_start(cmds, attrs, params["margin"])
    
    # National Header (Flush Right)
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\\\', '\\textbf', '<KhmerText>', '\\end', '}'])
    attrs.extend(['', '', '{flushright}', f'{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}', '', '', '', '', '{flushright}', ''])
    
    # Logo
    cmds.extend(['\\hspace', '\\includegraphics'])
    attrs.extend([f'*{{{params["logo_space"]}cm}}', f'[width={params["logo_width"]}cm]{{Figures/Num_logo.png}}'])
    
    # Institution (Flush Left)
    cmds.extend(['\\begin', '{', '\\HeaderFont', '\\fontsize', '\\selectfont', '\\textbf', '\\\\', '\\textbf', '\\end', '}'])
    attrs.extend(['{flushleft}', '', '', f'{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}', '', '', '', '', '{flushleft}', ''])
    
    # Title
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\textbf', '\\\\', '\\textbf', '\\\\', '\\parbox', '\\textbf', '\\end', '}'])
    attrs.extend(['', '', '{center}', f'{{{params["title_size"]}pt}}{{{params["title_spacing"]}pt}}', '', '', '', '', '', '{0.9\\textwidth}', '', '{center}', ''])
    
    # Body text, Date, Stamp
    add_body_block(cmds, attrs, params["para_spacing"])
    add_date_block(cmds, attrs, params)
    add_stamp_block(cmds, attrs)
    
    cmds.append(r"\end")
    attrs.append(r"{document}")
    
    return latex, cmds, attrs
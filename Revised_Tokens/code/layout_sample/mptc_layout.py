import random
import re
from common_helpers import (
    sample_layout_params,
    apply_common_latex,
    escape_tex,
    add_doc_start,
    add_body_block,
    add_stamp_block,
)

def generate_mptc_doc(template_latex, paragraphs, subtitles, khmer_lunar_dates, solar_dates):
    params = sample_layout_params()
    
    # 1. Update LaTeX string
    latex = apply_common_latex(template_latex, params)
    latex = latex.replace(
        r'\fontsize{12pt}{10pt}\selectfont %random from font: 12 -> 14 , baseline spacing: it measure between its to other : 10,15,20',
        f'\\fontsize{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}\\selectfont'
    )
    latex = latex.replace(r'\hspace*{2cm}  % random from 0,0.5,1,1.5,2', f'\\hspace*{{{params["logo_space"]}cm}}')
    latex = latex.replace(r'\includegraphics[width=3cm]{Figures/Mptc_logo.jpg}  % random from 2,2.5,3', f'\\includegraphics[width={params["logo_width"]}cm]{{Figures/Mptc_logo.jpg}}')
    latex = latex.replace(
        r'\fontsize{12pt}{10pt}\selectfont  % random from font: 10,11,12 , baseline spacing: it measure between its to other : 10,15,20',
        f'\\fontsize{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}\\selectfont'
    )
    
    # Subtitle & Dates
    sub = random.choice(subtitles)
    latex = re.sub(
        r'\\parbox\{0\.9\\textwidth\}\{\s*\\centering\s*\\textbf\{.*?\}%?\s*\}',
        f'\\\\parbox{{0.9\\\\textwidth}}{{\\\\centering\\\\textbf{{{escape_tex(sub)}}}}}',
        latex
    )
    latex = latex.replace(r'ថ្ងៃ    ខែ      ឆ្នាំរោង ឆស័ក ព.ស ២៥៦៨', random.choice(khmer_lunar_dates))
    latex = latex.replace(r'រាជធានីភ្នំពេញ ថ្ងៃ    ខែ    ឆ្នាំ២០២៤', random.choice(solar_dates))
    
    latex = latex.replace(r'\fontsize{11pt}{13pt}\selectfont', f'\\fontsize{{{params["date1_size"]}pt}}{{{params["date1_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\fontsize{12pt}{24pt}\selectfont', f'\\fontsize{{{params["date2_size"]}pt}}{{{params["date2_spacing"]}pt}}\\selectfont')
    
    # 2. Build aligned tokens & attributes
    cmds, attrs = [], []
    add_doc_start(cmds, attrs, params["margin"])
    
    # National Header
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\\\', '\\textbf', '<KhmerText>', '\\includegraphics', '\\end', '}'])
    attrs.extend(['', '', '{center}', f'{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}', '', '', '', '', '[width=2.5cm]{Figures/Tacteng.png}', '{center}', ''])
    
    # Logo & Institution
    cmds.extend(['\\hspace', '\\includegraphics', '{', '\\HeaderFont', '\\fontsize', '\\textcolor', '\\selectfont', '\\textbf', '<KhmerText>', '}'])
    attrs.extend([f'*{{{params["logo_space"]}cm}}', f'[width={params["logo_width"]}cm]{{Figures/Mptc_logo.jpg}}', '', '', f'{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}', '{TextBlue}', '', '', '', ''])
    
    # Document number & Solar Date
    cmds.extend(['{', '\\NormalFont', '\\fontsize', '\\selectfont', '<KhmerText>', '}'])
    attrs.extend(['', '', f'{{{params["date1_size"]}pt}}{{{params["date1_spacing"]}pt}}', '', '', ''])
    
    cmds.extend(['\\raggedleft', '{', '\\NormalFont', '\\fontsize', '\\selectfont', '<KhmerText>', '}'])
    attrs.extend(['', '', '', f'{{{params["date2_size"]}pt}}{{{params["date2_spacing"]}pt}}', '', '', ''])
    
    # Title
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\textbf', '\\\\', '\\parbox', '\\textbf', '\\end', '}'])
    attrs.extend(['', '', '{center}', f'{{{params["title_size"]}pt}}{{{params["title_spacing"]}pt}}', '', '', '', '{0.9\\textwidth}', '', '{center}', ''])
    
    # Body text & Stamp
    add_body_block(cmds, attrs, params["para_spacing"])
    add_stamp_block(cmds, attrs)
    
    # Footers: Left and Right
    cmds.extend(['\\fancyfoot', '{', '\\fontsize', '\\NormalFont', '\\color', '\\selectfont', '\\begin', '\\end', '<KhmerText>', '}'])
    attrs.extend(['[L]', '', '{10pt}{10pt}', '', '{TextBlue}', '', '{tabular}{l}', '{tabular}', '', ''])
    
    cmds.extend(['\\fancyfoot', '{', '\\fontsize', '\\NormalFont', '\\color', '\\selectfont', '\\begin', '\\end', '<KhmerText>', '}'])
    attrs.extend(['[R]', '', '{10pt}{10pt}', '', '{TextBlue}', '', '{tabular}{r}', '{tabular}', '', ''])
    
    cmds.append(r"\end")
    attrs.append(r"{document}")
    
    return latex, cmds, attrs
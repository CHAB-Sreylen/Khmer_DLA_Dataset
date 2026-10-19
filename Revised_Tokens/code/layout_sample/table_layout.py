import random
from common_helpers import (
    sample_layout_params,
    apply_common_latex,
    add_body_block,
)

def generate_table_doc(template_latex, paragraphs=None, subtitles=None, khmer_lunar_dates=None, solar_dates=None):
    params = sample_layout_params()
    
    # 1. Update LaTeX string
    latex = apply_common_latex(template_latex, params)
    
    col_spec1 = "|c|l|l|c|"
    col_spec2 = "|c|l|l|c|c"
    caption1 = "រាយនាមបុគ្គលិក"
    caption2 = "អាជ្ញាបណ្ណប្រកបវិជ្ជាជីវៈគណនេយ្យករថ្នាក់១"
    
    # 2. Build aligned tokens & attributes
    cmds = [r"\documentclass", r"\usepackage", r"\usepackage", r"\usepackage", r"\begin"]
    attrs = [r"[a4paper]{article}", f"[margin={params['margin']}cm]{{geometry}}", r"", r"", r"{document}"]
    
    # Body Text
    add_body_block(cmds, attrs, params["para_spacing"])
    
    # Table Title
    cmds.extend(['\\begin', '{', '\\NormalFont', '\\textbf', '<KhmerText>', '}', '\\end'])
    attrs.extend(['{center}', '', '', '', '', '', '{center}'])
    
    # Table 1
    cmds.extend(['\\begin', '\\centering', '\\NormalFont', '\\selectfont', '\\hline', '\\textbf', '&', '<KhmerText>', '\\\\', '\\end', '\\caption'])
    attrs.extend(['{table}', '', '{tabular}', f'{{{col_spec1}}}', '', '', '', '', '', '{table}', f'{{{caption1}}}'])
    
    # Table 2
    cmds.extend(['\\begin', '\\centering', '\\NormalFont', '\\selectfont', '\\hline', '\\textbf', '&', '<KhmerText>', '\\\\', '\\end', '\\caption'])
    attrs.extend(['{table}', '', '{tabular}', f'{{{col_spec2}}}', '', '', '', '', '', '{table}', f'{{{caption2}}}'])
    
    cmds.append(r"\end")
    attrs.append(r"{document}")
    
    return latex, cmds, attrs
import random
import re
from pathlib import Path

# 1. How to load the render component into the file 
# 1.1. separate 
def load_lines(path:Path): # call the Path to use 
    if not path.exists():
        return[]
    lines = path.read_text(encoding = "utf-8",errors = "ignore").splitlines()
    return [line.strip() for line in lines if line.strip()]

def rand_paragraph(paragraphs):
    return random.choice(paragraphs)

# 1.2. Prevent error while compiling latex 
def escape_tex(s:str)->str: 
    """ Escape special characters in text strings. """
    repl = {
        "\\":r"\textbackslash{}", # raw string
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(c, c) for c in s)

# 2. Layout sample 
# 2.1. Every document layout samples can reuse this below function 

def sample_layout_params():
    return{
        "margin": random.choice([1, 2, 3]),
        "logo_space": random.choice([0, 0.5, 1, 1.5, 2]),
        "logo_width": random.choice([2, 2.5, 3]),
        "h_size": random.choice([12, 13, 14]),
        "h_spacing": random.choice([10, 15, 20]),
        "n_size": random.choice([10, 11, 12]),
        "n_spacing": random.choice([10, 15, 20]),
        "title_size": random.choice([12, 13, 14]),
        "title_spacing": random.choice([10, 15, 20]),
        "para_spacing": random.choice([10, 15, 20]),
        "date1_size": random.choice([10, 11, 12]),
        "date1_spacing": random.choice([10, 15, 20]),
        "date2_size": random.choice([10, 11, 12]),
        "date2_spacing": random.choice([10, 15, 20]),
    }

def add_doc_start(cmds, attrs, margin_val):
    # cmds = commands in latex -> cmds.extend()-> to append cmd to cmd list
    cmds.extend([r"\documentclass", r"\usepackage", r"\begin"])
    attrs.extend([r"[a4paper]{article}", f"[margin={margin_val}cm]{{geometry}}", r"{document}"])

def add_body_block(cmds, attrs, para_spacing):
    cmds.extend(['{', '\\NormalFont', '\\begin', '\\setlength', '\\baselineskip', '\\hspace', '\\input', '\\par', '\\end', '}'])
    attrs.extend(['', '', '{justify}', f'{{\\baselineskip}}{{{para_spacing}pt}}', '{1cm}', '{Text/ITC_text}', '', '', '{justify}', ''])

def add_date_block(cmds, attrs, p):
    cmds.extend(['{', '\\NormalFont', '\\begin', '\\fontsize', '\\selectfont', '<KhmerText>', '\\end', '}'])
    attrs.extend(['', '', '{flushright}', f'{{{p["date1_size"]}pt}}{{{p["date1_spacing"]}pt}}', '', '', '{flushright}', ''])
    cmds.extend(['\\raggedleft', '{', '\\NormalFont', '\\fontsize', '\\selectfont', '<KhmerText>', '}'])
    attrs.extend(['', '', '', f'{{{p["date2_size"]}pt}}{{{p["date2_spacing"]}pt}}', '', '', ''])

def add_stamp_block(cmds, attrs):
    cmds.extend(['\\begin', '\\includegraphics', '\\end'])
    attrs.extend(['{flushright}', '[width=1.5in]{Figures/Stamp.png}', '{flushright}'])

def apply_common_latex(latex, p):
    match = re.search(r'\\usepackage\[\s*top=.*?geometry\}', latex, flags=re.DOTALL)
    if match:
        latex = latex.replace(
            match.group(0),
            f'\\usepackage[top={p["margin"]}cm,bottom={p["margin"]}cm,left={p["margin"]}cm,right={p["margin"]}cm]{{geometry}}'
        )
    return latex.replace(r'\setlength{\baselineskip}{20pt}', f'\\setlength{{\\baselineskip}}{{{p["para_spacing"]}pt}}')



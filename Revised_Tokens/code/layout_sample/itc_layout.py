import random 
from common_helpers import(
    sample_layout_params,apply_common_latex,escape_tex,
    add_doc_start,add_body_block,add_date_block,add_stamp_block
)

def generate_itc_doc(template_latex,paragraphs,subtitles,khmer_lunar_dates,solar_dates):
    params = sample_layout_params()
    footer_align = random.choice(['c','l','r'])

    latex = apply_common_latex(template_latex,params)
    latex = latex.replace(r'\fontsize{12pt}{10pt}\selectfont %random from font 12->14 , baseline spacing: it measure between its to other(10,15,20)', f'\\fontsize{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\hspace*{0.5cm}  % random from 0,0.5,1,1.5,2', f'\\hspace*{{{params["logo_space"]}cm}}')
    latex = latex.replace(r'\includegraphics[width=3cm]{Figures/ITC_logo.png}  % random from 2,2.5,3', f'\\includegraphics[width={params["logo_width"]}cm]{{Figures/ITC_logo.png}}')
    latex = latex.replace(r'\fontsize{12pt}{10pt}\selectfont  % random from font: 10,11,12 , baseline spacing: it measure between its to other : 10,15,20', f'\\fontsize{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\parbox{0.9\textwidth}{\centering\textbf{ស្តីពីវឌ្ឃនភាពនៃវិធានការរបស់វិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជាពាក់ព័ន្ធនឹងករណីក្លែងបន្លំសញ្ញាបត្រ}%}', f'\\parbox{{0.9\\textwidth}}{{\\centering\\textbf{{{escape_tex(random.choice(subtitles))}}}}}')
    latex = latex.replace(r'ថ្ងៃ​អង្គារ ១រោច​ខែបឋមសាឍ ឆ្នាំមមី អដសីក​ព.ស ២៥៧០', random.choice(khmer_lunar_dates))
    latex = latex.replace(r'រាជធានីភ្នំពេញ ថ្ងៃ    ខែ    ឆ្នាំ២០២៤', random.choice(solar_dates))
    latex = latex.replace(r'\fontsize{11pt}{13pt}\selectfont', f'\\fontsize{{{params["date1_size"]}pt}}{{{params["date1_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\fontsize{12pt}{24pt}\selectfont', f'\\fontsize{{{params["date2_size"]}pt}}{{{params["date2_spacing"]}pt}}\\selectfont')
    latex = latex.replace(r'\fancyfoot[c]{', f'\\fancyfoot[{footer_align}]{{')
    cmds, attrs = [], []
    add_doc_start(cmds, attrs,params["margin"])
    
    # National Header
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\\\', '\\textbf', '<KhmerText>', '\\includegraphics', '\\end', '}'])
    attrs.extend(['', '', '{center}', f'{{{params["h_size"]}pt}}{{{params["h_spacing"]}pt}}', '', '', '', '', '[width=2.5cm]{Figures/Tacteng.png}', '{center}', ''])
    
    # Logo & Institution
    cmds.extend(['\\hspace', '\\includegraphics', '{', '\\NormalFont', '\\fontsize', '\\textcolor', '\\selectfont', '\\textbf', '<KhmerText>', '}'])
    attrs.extend([f'*{{{params["logo_space"]}cm}}', f'[width={params["logo_width"]}cm]{{Figures/ITC_logo.png}}', '', '', f'{{{params["n_size"]}pt}}{{{params["n_spacing"]}pt}}', '{TextBlue}', '', '', '', ''])
    
    # Title
    cmds.extend(['{', '\\HeaderFont', '\\begin', '\\fontsize', '\\selectfont', '\\textbf', '\\\\', '\\parbox', '\\textbf', '\\end', '}'])
    attrs.extend(['', '', '{center}', f'{{{params["title_size"]}pt}}{{{params["title_spacing"]}pt}}', '', '', '', '{0.9\\textwidth}', '', '{center}', ''])
    
    add_body_block(cmds, attrs, params["para_spacing"])
    add_date_block(cmds, attrs, params)
    add_stamp_block(cmds, attrs)
    
    cmds.extend(['\\fancyfoot', '{', '\\fontsize', '\\NormalFont', '\\color', '\\selectfont', '\\begin', '\\end', '<KhmerText>', '}'])
    attrs.extend([f'[{footer_align}]', '', '{10pt}{10pt}', '', '{TextBlue}', '', '{tabular}{l}', '{tabular}', '', ''])
    
    cmds.append(r"\end")
    attrs.append(r"{document}")
    return latex, cmds, attrs
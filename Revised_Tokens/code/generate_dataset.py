import os 
import json 
import shutil
import random 
import re
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed


# 0. Download MikTeX into your machine , and add the path of its to make xelatex and pdftocairo can accessible 

miktex_bin = os.path.join(os.path.expanduser("~"),r"AppData\Local\Program\MiKTeX\miktex\bin\x64")
if os.path.exists(miktex_bin) and miktex_bin not in os.environ["PATH"]: 
    os.environ["PATH"] = miktex_bin + os.pathsep + os.environ["PATH"]   # add miktex to PATH


# 1. Path 

current_dir = Path(__file__).parent.resolve() 
revised_tokens_dir = current_dir.parent.resolve()
project_root = revised_tokens_dir.parent.resolve()

if (project_root / "source").exists():
    source_dir = project_root / "source"
elif (revised_tokens_dir / "source").exists():
    source_dir = revised_tokens_dir / "source"
else:
    source_dir = current_dir / "source"

if (project_root / "fancyhdr.sty").exists():
    fancyhdr_path = project_root / "fancyhdr.sty"
elif (revised_tokens_dir / "fancyhdr.sty").exists():
    fancyhdr_path = revised_tokens_dir / "fancyhdr.sty"
else:
    fancyhdr_path = source_dir / "fancyhdr.sty"

text_paragraph_path = source_dir / "Text" / "10000_paragraph.txt"
text_subtitle_path = source_dir / "Text" / "sub-title.txt"

dataset_dir = revised_tokens_dir / "dataset"
temp_compile_dir = revised_tokens_dir / "temp_compile"
vocab_json_path = revised_tokens_dir / "vocab.json"


# 2. Set how many of each document type to render 

itc_doc = 5 
mptc_doc = 5
num_doc = 5
table_doc = 5
combined_doc = 5
total_doc = itc_doc + mptc_doc + num_doc + table_doc + combined_doc
DPI = 150 # resolution for pdftocario output 


with open(vocab_json_path,"r",encoding="utf-8") as f:
    token_to_index = json.load(f)
vocab = list(token_to_index.keys())



# 3. How to load the render component into the file 
# 3.1. separate 
def load_lines(path:Path): # call the Path to use 
    if not path.exists():
        return[]
    lines = path.read_text(encoding = "utf-8",errors = "ignore").splitlines()
    return [line.strip() for line in lines if line.strip()]

def rand_paragraph(paragraphs):
    return random.choice(paragraphs)



# 3.2. Prevent error while compiling latex 

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
        "~": r"\textassciitilde{}",
        "^": r"\textassciicirum{}",
    }
    return "".join(repl.get(c, c) for c in s)

# 4. Compiling 

def compile_latex_job(stem,tex_content,paragraph_text,dest_dir):
    
    tex_path = temp_compile_dir/f"{stem}.tex"
    pdf_path = temp_compile_dir/f"{stem}.pdf"
    png_pattern = temp_compile_dir/f"{stem}-1.png"
    dest_png_path = dest_dir / f"{stem}-1.png"

    escaped_para = escape_tex(paragraph_text)
    tex_content = tex_content.replace(r"\input{Text/ITC_text}",escaped_para)
    tex_content = tex_content.replace(r"\input{Text/ITC_text.tex}",escaped_para)

    tex_path.write_text(tex_content,encoding="utf-8")

    try:
        # 1. Compile to PDF with XeLaTex(for whatever that compile with khmer font)
        result1 = subprocess.run(
            ["xelatex","-interaction=nonstopmode","-halt-on-error",tex_path.name],   
            cwd = str(temp_compile_dir),  
            capture_output = True,
            text = True,
            encoding = "utf-8",
            errors = "ignore",
            timeout = 30    
        )
        if result1.returncode !=0:
            return False

        # 2. Render PNG with pdftocairo
        result2 = subprocess.run(
            ["pdftocairo","-png","-r",str(DPI),pdf_path.name,stem],
            cwd = str(temp_compile_dir),
            capture_output=True,
            text = True,
            encoding="utf-8",
            errors = "ignore",
            timeout=20
        )
        if result2.returncode != 0:
            return False

        # 3. Copy result image to destination directory
        if png_pattern.exists():
            shutil.copy(png_pattern,dest_png_path)
            return True 
        else: 
            fallback = temp_compile_dir/f"{stem}-page1.png"
            if fallback.exists():
                shutil.copy(fallback,dest_png_path)
                return True
            return False 
    except Exception:
        return False
    finally:
        # Clean 
        for ext in [".tex",".pdf",".aux",".log","-1.png","-page1.png"]:
            f = temp_compile_dir / f"{stem}{ext}"
            if f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass 

# 5. Layout sample 
# 5.1. Every document layout samples can reuse this below function 

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


from common_helpers import load_lines,rand_paragraph,escape_tex
from layout_sample import (
    generate_itc_doc,
    generate_mptc_doc,
    generate_num_doc,
    generate_table_doc,
    generate_combined_doc
)



# 6. Dataset generation

def generate_dataset():
    print("Initializing dataset directories...", flush=True)
    dataset_dir.mkdir(parents=True, exist_ok=True)
    train_dir = dataset_dir / "train"
    test_dir = dataset_dir / "test"
    train_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    if temp_compile_dir.exists():
        shutil.rmtree(temp_compile_dir, ignore_errors=True)
    temp_compile_dir.mkdir(parents=True, exist_ok=True)

    # Copy static assets into temp compilation directory
    try:
        shutil.copytree(source_dir / "fonts", temp_compile_dir / "fonts", dirs_exist_ok=True)
    except Exception:
        pass
    try:
        shutil.copytree(source_dir / "Figures", temp_compile_dir / "Figures", dirs_exist_ok=True)
    except Exception:
        pass
    if fancyhdr_path.exists():
        try:
            shutil.copy(fancyhdr_path, temp_compile_dir / "fancyhdr.sty")
        except Exception:
            pass

    # Load text resources
    paragraphs = load_lines(text_paragraph_path)
    subtitles = load_lines(text_subtitle_path)

    khmer_lunar_dates = [
        "ថ្ងៃ​អង្គារ ១រោច​ខែបឋមសាឍ ឆ្នាំមមី អដសីក​ព.ស ២៥៧០",
        "ថ្ងៃព្រហស្បតិ៍ ៥រោច ខែចេត្រ ឆ្នាំរោង ឆស័ក ព.ស. ២៥៦៨",
        "ថ្ងៃសុក្រ ១៣កើត ខែពិសាខ ឆ្នាំរោង ឆស័ក ព.ស. ២៥៦៨",
        "ថ្ងៃចន្ទ ៩កើត ខែជេស្ឋ ឆ្នាំមមី អដ្ឋស័ក ព.ស. ២៥៧០"
    ]
    solar_dates = [
        "រាជធានីភ្នំពេញ ថ្ងៃទី២៥ ខែកក្កដា ឆ្នាំ២០២៤",
        "រាជធានីភ្នំពេញ ថ្ងៃទី១២ ខែមិថុនា ឆ្នាំ២០២៥",
        "រាជធានីភ្នំពេញ ថ្ងៃទី០៨ ខែសីហា ឆ្នាំ២០២៦",
        "រាជធានីភ្នំពេញ ថ្ងៃ    ខែ    ឆ្នាំ២០២៤"
    ]

    # Load LaTeX Templates
    print("Loading LaTeX templates...", flush=True)
    template_dir = revised_tokens_dir / "Latex_Sample_layout"
    itc_temp = (template_dir / "ITC_Layout.tex").read_text(encoding="utf-8")
    mptc_temp = (template_dir / "MPTC_Layout.tex").read_text(encoding="utf-8")
    num_temp = (template_dir / "NUM_Layout.tex").read_text(encoding="utf-8")
    table_temp = (template_dir / "Table_Layout.tex").read_text(encoding="utf-8")

    # Generate diverse titles
    sub_prefixes = [
        "សេចក្ដីជូនដំណឹង ស្ដីពី",
        "សេចក្ដីណែនាំ ស្ដីពី",
        "ប្រកាសអន្តរក្រសួង ស្ដីពី",
        "សេចក្ដីប្រកាសព័ត៌មាន ស្តីពី",
        "សេចក្តីសម្រេច ស្ដីពី",
        "លិខិតបង្គាប់ការ ស្ដីពី"
    ]
    extended_subtitles = list(subtitles)
    for _ in range(500):
        prefix = random.choice(sub_prefixes)
        phrase = random.choice(paragraphs)
        words = phrase.split()
        if len(words) > 6:
            phrase = " ".join(words[:random.randint(4, 7)])
        extended_subtitles.append(f"{prefix} {phrase}")

    print(f"Preparing {total_doc} document templates...", flush=True)
    jobs = []

    # 1. ITC Layouts
    for idx in range(itc_doc):
        stem = f"sample_itc_{idx:03d}"
        para = rand_paragraph(paragraphs)
        latex, tokens, attributes = generate_itc_doc(itc_temp, paragraphs, extended_subtitles, khmer_lunar_dates, solar_dates)
        jobs.append((stem, latex, tokens, attributes, "itc", para))

    # 2. MPTC Layouts
    for idx in range(mptc_doc):
        stem = f"sample_mptc_{idx:03d}"
        para = rand_paragraph(paragraphs)
        latex, tokens, attributes = generate_mptc_doc(mptc_temp, paragraphs, extended_subtitles, khmer_lunar_dates, solar_dates)
        jobs.append((stem, latex, tokens, attributes, "mptc", para))

    # 3. NUM Layouts
    for idx in range(num_doc):
        stem = f"sample_num_{idx:03d}"
        para = rand_paragraph(paragraphs)
        latex, tokens, attributes = generate_num_doc(num_temp, paragraphs, extended_subtitles, khmer_lunar_dates, solar_dates)
        jobs.append((stem, latex, tokens, attributes, "num", para))

    # 4. Table Layouts
    for idx in range(table_doc):
        stem = f"sample_tbl_{idx:03d}"
        para = rand_paragraph(paragraphs)
        latex, tokens, attributes = generate_table_doc(table_temp)
        jobs.append((stem, latex, tokens, attributes, "table", para))

    # 5. Combined / Various Layouts
    for idx in range(combined_doc):
        stem = f"sample_cmb_{idx:03d}"
        para = rand_paragraph(paragraphs)
        latex, tokens, attributes = generate_combined_doc(paragraphs=paragraphs, subtitles=extended_subtitles, khmer_lunar_dates=khmer_lunar_dates, solar_dates=solar_dates)
        jobs.append((stem, latex, tokens, attributes, "combined", para))

    # Split: 80% train, 20% test per layout group
    train_records = []
    test_records = []
    groups = {"itc": [], "mptc": [], "num": [], "table": [], "combined": []}
    for job in jobs:
        groups[job[4]].append(job)

    print("Compiling documents in parallel...", flush=True)
    completed_count = 0

    with ProcessPoolExecutor(max_workers=6) as executor:
        futures = {}
        for g_name, g_jobs in groups.items():
            random.shuffle(g_jobs)
            n_g_train = int(len(g_jobs) * 0.8)

            for g_idx, job in enumerate(g_jobs):
                stem, latex, tokens, attributes, layout_type, para = job
                is_train = g_idx < n_g_train
                dest_dir = train_dir if is_train else test_dir

                f = executor.submit(compile_latex_job, stem, latex, para, dest_dir)
                futures[f] = (stem, tokens, attributes, is_train)

        for future in as_completed(futures):
            stem, tokens_list, attributes_list, is_train = futures[future]
            completed_count += 1

            # Here token_ids is calculated:
            token_ids = [token_to_index[t] for t in tokens_list]
            padded_attrs = [attr if attr else "" for attr in attributes_list]

            success = future.result()
            if success:
                rec = {
                    "stem": stem,
                    "tokens": tokens_list,
                    "token_ids": token_ids,
                    "attributes": padded_attrs,
                    "length": len(token_ids)
                }
                if is_train:
                    train_records.append(rec)
                else:
                    test_records.append(rec)
                print(f"[{completed_count}/{total_doc}] Successfully compiled {stem}", flush=True)
            else:
                print(f"[{completed_count}/{total_doc}] Failed to compile {stem}", flush=True)

    # Save vocab and ground_truth.json
    print("Writing vocab.json and ground_truth.json...", flush=True)
    with open(dataset_dir / "vocab.json", "w", encoding="utf-8") as f:
        json.dump(token_to_index, f, indent=4, ensure_ascii=False)

    with open(train_dir / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(train_records, f, indent=4, ensure_ascii=False)

    with open(test_dir / "ground_truth.json", "w", encoding="utf-8") as f:
        json.dump(test_records, f, indent=4, ensure_ascii=False)

    print(f"Done! Successfully generated {len(train_records)} train and {len(test_records)} test samples.", flush=True)

if __name__ == "__main__":
    generate_dataset()
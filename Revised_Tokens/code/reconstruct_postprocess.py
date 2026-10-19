import re
import json
import pandas as pd
from pathlib import Path

# Setup Khmer text helper mapping
KHMER_HEADER_NATIONAL = "ព្រះរាជាណាចក្រកម្ពុជា\\\\ជាតិ សាសនា ព្រះមហាក្សត្រ"
KHMER_INSTITUTIONS = [
    "វិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជា",
    "ក្រសួងប្រៃសណីយ៍និងទូរគមនាគមន៍",
    "សាកលវិទ្យាល័យជាតិគ្រប់គ្រង"
]
KHMER_TITLES = [
    "សេចក្ដីប្រកាសព័ត៌មាន",
    "សេចក្ដីជូនដំណឹងស្ដីពី",
    "សេចក្ដីជូនដំណឺង"
]
KHMER_PARAGRAPHS = [
    "វិទ្យាស្ថានបច្ចេកវិទ្យាកម្ពុជា មានកិត្តិយសសូមជម្រាបជូនដំណឹងដល់និស្សិតទាំងអស់ឱ្យបានជ្រាបថា ផ្អែកលើការសម្រេចចិត្តរបស់គណៈគ្រប់គ្រង ការសិក្សានឹងត្រូវបន្តអនុវត្តតាមកម្មវិធីសិក្សាថ្មី។ សេចក្តីជូនដំណឹងនេះមានប្រសិទ្ធភាពចាប់ពីថ្ងៃចុះហត្ថលេខានេះតទៅ។",
    "អគារលេខ ១៣ មហាវិថីព្រះមុនីវង្ស សង្កាត់ស្រះចក ខណ្ឌដូនពេញ រាជធានីភ្នំពេញ ព្រះរាជាណាចក្រកម្ពុជា។",
    "ការសិក្សារបស់និស្សិតថ្នាក់បរិញ្ញាប័ត្រក្នុងឆមាសទី១ ឆ្នាំសិក្សា២០២៦-២០២៧ នឹងត្រូវចាប់ផ្តើមតាមការគ្រោងទុក។"
]

class LatexReconstructor:
    def __init__(self):
        # Index counters to rotate Khmer placeholder texts
        self.institution_idx = 0
        self.title_idx = 0
        self.paragraph_idx = 0

    def get_khmer_text(self, context_cmd=None):
        """
        Returns context-appropriate Khmer text for <KhmerText> placeholders.
        """
        # If the parent is a header/bold block
        if context_cmd == "\\textbf":
            if self.institution_idx == 0:
                self.institution_idx += 1
                return KHMER_HEADER_NATIONAL
            else:
                title = KHMER_TITLES[self.title_idx % len(KHMER_TITLES)]
                self.title_idx += 1
                return title
        elif context_cmd == "\\textcolor":
            inst = KHMER_INSTITUTIONS[self.institution_idx % len(KHMER_INSTITUTIONS)]
            self.institution_idx += 1
            return inst
        else:
            para = KHMER_PARAGRAPHS[self.paragraph_idx % len(KHMER_PARAGRAPHS)]
            self.paragraph_idx += 1
            return para

    def _item_to_str(self, item):
        """
        Converts a stack item (either str or structural tuple) to a LaTeX string safely.
        """
        if isinstance(item, tuple):
            marker = item[0]
            if marker == "group":
                return item[1]
            elif marker == "begin":
                env_name = item[2].strip("{}")
                return f"\\begin{{{env_name}}}"
            elif marker == "wrapper":
                return f"{item[1]}{item[2]}"
            return str(item)
        return str(item)

    def reconstruct(self, commands, attributes):
        """
        Reconstructs compile-ready LaTeX code from the zipped command and attribute lists.
        """
        stack = []
        skip_selectfont = False
        skip_baselineskip = False

        for i, (cmd, attr) in enumerate(zip(commands, attributes)):
            # Clean inputs
            cmd = str(cmd).strip() if not pd.isna(cmd) else ""
            attr = str(attr).strip() if not pd.isna(attr) else ""
            
            if not cmd or cmd in ["<PAD>", "<SOS>", "<EOS>"]:
                continue

            # Skip redundant standalone tokens
            if cmd == "\\selectfont" and skip_selectfont:
                skip_selectfont = False
                continue
            if cmd == "\\baselineskip" and skip_baselineskip:
                skip_baselineskip = False
                continue

            # Handle Group Openers / Closers
            if cmd == "{":
                stack.append(("group", "{", ""))
            elif cmd == "}":
                # Pop everything until matching group opener
                items = []
                while stack and not (isinstance(stack[-1], tuple) and stack[-1][0] == "group"):
                    items.append(self._item_to_str(stack.pop()))
                if stack:
                    stack.pop() # remove opener
                content = " ".join(reversed(items)).strip()
                # Push back as scoped group string
                stack.append(f"{{{content}}}")
                # Try applying wrapping logic
                self._apply_pending_wrappers(stack)

            # Handle Environments
            elif cmd == "\\begin":
                stack.append(("begin", "\\begin", attr))
            elif cmd == "\\end":
                items = []
                while stack and not (isinstance(stack[-1], tuple) and stack[-1][0] == "begin" and stack[-1][2] == attr):
                    items.append(self._item_to_str(stack.pop()))
                begin_node = stack.pop() if stack else None
                content = " ".join(reversed(items)).strip()
                
                env_name = attr.strip("{}")
                if begin_node:
                    reconstructed_env = f"\\begin{{{env_name}}}\n{content}\n\\end{{{env_name}}}"
                else:
                    reconstructed_env = f"{content}\n\\end{{{env_name}}}"
                stack.append(reconstructed_env)
                # Try applying wrapping logic
                self._apply_pending_wrappers(stack)

            # Handle Placeholders
            elif cmd == "<KhmerText>":
                # Determine context from pending wrapper
                context = None
                if stack and isinstance(stack[-1], tuple) and stack[-1][0] == "wrapper":
                    context = stack[-1][1]
                text = self.get_khmer_text(context)
                stack.append(text)
                # Try applying wrapping logic
                self._apply_pending_wrappers(stack)

            # Handle Setup/Preamble Commands
            elif cmd == "\\documentclass":
                stack.append(f"\\documentclass{attr}")
            elif cmd == "\\usepackage":
                stack.append(f"\\usepackage{attr}")
            elif cmd == "\\input":
                stack.append(f"\\input{attr}")

            # Handle Scoped Formatting & Command Builders
            elif cmd == "\\fontsize":
                # Combine with \selectfont automatically
                stack.append(f"\\fontsize{attr}\\selectfont")
                skip_selectfont = True
            elif cmd == "\\hspace":
                stack.append(f"\\hspace{attr}")
            elif cmd == "\\includegraphics":
                stack.append(f"\\includegraphics{attr}")
            elif cmd == "\\color":
                stack.append(f"\\color{attr}")
            elif cmd == "\\setlength":
                stack.append(f"\\setlength{attr}")
                if "baselineskip" in attr:
                    skip_baselineskip = True

            # Standalone Declarations
            elif cmd in ["\\NormalFont", "\\HeaderFont", "\\selectfont", "\\centering", "\\raggedleft", "\\par", "\\hline", "&", "\\\\"]:
                if cmd == "\\\\":
                    stack.append("\\\\\n")
                elif cmd == "&":
                    stack.append(" & ")
                elif cmd == "\\hline":
                    stack.append("\\hline\n")
                else:
                    stack.append(cmd)
                # Try applying wrapping logic
                self._apply_pending_wrappers(stack)

            # Wrapper Commands (expecting next child element)
            elif cmd in ["\\textbf", "\\textcolor", "\\parbox", "\\fancyfoot", "\\caption"]:
                stack.append(("wrapper", cmd, attr))

            # Unknown commands
            else:
                stack.append(cmd)

        # Final cleanup: flush remaining items on stack
        final_parts = []
        for item in stack:
            if isinstance(item, tuple):
                # Unresolved structural wrappers / groups
                if item[0] == "wrapper":
                    final_parts.append(f"{item[1]}{item[2]}")
                else:
                    final_parts.append(item[1])
            else:
                final_parts.append(item)

        return " ".join(final_parts).strip()

    def _apply_pending_wrappers(self, stack):
        """
        Checks top of stack. If it is a completed node and the item below it 
        is a pending wrapper, wraps the node and updates the stack recursively.
        """
        if len(stack) < 2:
            return
        
        # Check if the top item is a concrete string
        if isinstance(stack[-1], tuple):
            return # Top is a structural node (group/begin/wrapper)

        # Check if the item below is a pending wrapper
        below = stack[-2]
        if isinstance(below, tuple) and below[0] == "wrapper":
            child = stack.pop()
            wrapper_type = below[1]
            wrapper_attr = below[2]
            stack.pop() # remove wrapper from stack

            # Formulate wrapped LaTeX block
            if wrapper_type == "\\textbf":
                wrapped = f"\\textbf{{{child}}}"
            elif wrapper_type == "\\textcolor":
                wrapped = f"\\textcolor{wrapper_attr}{{{child}}}"
            elif wrapper_type == "\\parbox":
                wrapped = f"\\parbox{wrapper_attr}{{{child}}}"
            elif wrapper_type == "\\fancyfoot":
                wrapped = f"\\fancyfoot{wrapper_attr}{{{child}}}"
            elif wrapper_type == "\\caption":
                wrapped = f"\\caption{{{child}}}"
            else:
                wrapped = f"{wrapper_type}{wrapper_attr}{{{child}}}"

            stack.append(wrapped)
            # Recurse to see if we can apply more wrappers
            self._apply_pending_wrappers(stack)

def test_reconstruction():
    """
    Tests the reconstructor on rows from Finalize_Tokens.xlsx
    """
    excel_path = Path(r"e:\Master Study\Project\Document_Layout\Document_Layout\Revised_Tokens\Latex_Sample_layout\Finalize_Tokens.xlsx")
    if not excel_path.exists():
        print(f"Spreadsheet not found at {excel_path}")
        return

    df = pd.read_excel(excel_path)
    reconstructor = LatexReconstructor()

    output_file = Path(r"C:\Users\Sreylen\.gemini\antigravity-ide\brain\ed21f1c9-4746-4066-9dd7-9c105db72067\scratch\reconstruction_test_output.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        # We want to test Row 8, Row 9, Row 15
        rows_to_test = [8, 9, 15]
        for r in rows_to_test:
            if r >= len(df):
                continue
            row = df.iloc[r]
            f.write(f"\n=================== TESTING ROW {r}: {row.iloc[1]} ===================\n")
            
            # Clean and extract tokens
            cmds_str = str(row['LSTM1 for command prediction'])
            cmds = [c.strip() for c in cmds_str.split() if c.strip()]
            
            # Align attributes manually for the Excel samples to account for spreadsheet omissions
            if r == 8:
                attrs = ['{document}', '', '', '{12pt}{10pt}', '', '', '', '', '[width=2.5cm]{Figures/Tacteng.png}', '{document}', '']
            elif r == 9:
                attrs = ['*{0.5cm}', '[width=3cm]{Figures/ITC_logo.png}', '', '', '{12pt}{10pt}', '{TextBlue}', '', '', '']
            elif r == 15:
                attrs = ['{table}', '', '', '', '', '', '', '', '', '{table}', '{រាយនាមបុគ្គលិក}']
            else:
                attrs = [''] * len(cmds)
            
            # Ensure safety
            while len(attrs) < len(cmds):
                attrs.append("")
            attrs = attrs[:len(cmds)]
            
            f.write(f"Commands input: {cmds}\n")
            f.write(f"Attributes input: {attrs}\n")
            
            latex = reconstructor.reconstruct(cmds, attrs)
            f.write("\nReconstructed LaTeX Code:\n")
            f.write(latex + "\n")

    print(f"Test output successfully saved to: {output_file}")

if __name__ == "__main__":
    test_reconstruction()

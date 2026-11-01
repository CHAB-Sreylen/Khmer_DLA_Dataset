"""Adapters for the ten imported institutional templates.

These use the existing (latex, tokens, attributes) generator contract. Unlike
the legacy hand-authored annotations, source-v1 labels retain literal content
and macro definitions so they describe the document actually rendered.
"""
import random
import re
from pathlib import Path

LAYOUTS = ("MoEYS", "MFAIC", "MoH", "MEF", "CADT", "RUPP", "RUFA", "UHS", "MPWT", "MoC")
CONTROL = re.compile(r"\\(?:[A-Za-z@]+\*?|[^\n])")
INPUT = re.compile(r"\\input\{([^}]+)\}")


def strip_comments(source):
    """Remove TeX comments, including the newline swallowed by a comment."""
    return re.sub(r"(?<!\\)%[^\n]*(?:\n|$)", "", source)


def inline_inputs(source, source_dir, ancestors=()):
    def replace(match):
        name = match.group(1)
        path = (source_dir / name).with_suffix(".tex") if not Path(name).suffix else source_dir / name
        path = path.resolve()
        if not path.is_relative_to(source_dir.resolve()):
            raise ValueError(f"Input outside source directory: {name}")
        if path in ancestors:
            raise ValueError(f"Recursive input: {path}")
        return inline_inputs(strip_comments(path.read_text(encoding="utf-8")), source_dir, ancestors + (path,))
    return INPUT.sub(replace, source)


def tokenize_source(source):
    """Keep balanced immediate arguments with their command; retain other text.

    Whitespace is retained, which also prevents words after control sequences
    from merging when reconstructing. Braces outside command arguments remain
    structural tokens. No new token IDs are assigned here.
    """
    tokens, attrs = [], []
    position = 0
    while position < len(source):
        match = CONTROL.match(source, position)
        if match:
            token = match.group()
            end = match.end()
            cursor = end
            # Arguments can span lines, but only consume whitespace if an
            # argument follows. This preserves free declarations and text.
            while True:
                start = cursor
                while cursor < len(source) and source[cursor].isspace():
                    cursor += 1
                if cursor >= len(source) or source[cursor] not in "[{":
                    break
                opener = source[cursor]
                closer = "]" if opener == "[" else "}"
                depth = 1
                cursor += 1
                while cursor < len(source) and depth:
                    control = CONTROL.match(source, cursor)
                    if control:
                        cursor = control.end()
                        continue
                    char = source[cursor]
                    if char == opener:
                        depth += 1
                    elif char == closer:
                        depth -= 1
                    cursor += 1
                if depth:
                    raise ValueError(f"Unclosed argument after {token}")
                end = cursor
            tokens.append(token)
            attrs.append(source[match.end():end])
            position = end
        elif source[position] in "{}&":
            tokens.append(source[position])
            attrs.append("")
            position += 1
        else:
            end = position + 1
            while end < len(source) and source[end] not in "\\{}&":
                end += 1
            tokens.append("<KhmerText>")
            attrs.append(source[position:end])
            position = end
    return tokens, attrs


def reconstruct_source(tokens, attributes):
    """Reconstruct source-v1 annotations; legacy annotations use their old decoder."""
    if len(tokens) != len(attributes):
        raise ValueError("Token and attribute lengths differ")
    return "".join(attr if token == "<KhmerText>" else token + attr
                   for token, attr in zip(tokens, attributes))


def generate_imported_doc(template_latex, source_dir, khmer_lunar_dates, solar_dates):
    latex = inline_inputs(strip_comments(template_latex), source_dir)
    # Preserve real tables, nested lists and body wording. Vary only explicit
    # date/reference fields; broad geometry changes can break these layouts.
    overrides = []
    fields = {
        "DocumentReference": str(random.randint(100, 9999)),
        "HeaderDateLineOne": random.choice(khmer_lunar_dates),
        "HeaderDateLineTwo": random.choice(solar_dates),
        "DocumentDateLineOne": random.choice(khmer_lunar_dates),
        "DocumentDateLineTwo": random.choice(solar_dates),
    }
    for name, value in fields.items():
        if re.search(r"\\newcommand\{\\" + name + r"\}", latex):
            overrides.append("\\renewcommand{\\" + name + "}{" + value + "}")
    latex = latex.replace(r"\begin{document}", "\n".join(overrides) + "\n" + r"\begin{document}", 1)
    tokens, attributes = tokenize_source(latex)
    if reconstruct_source(tokens, attributes) != latex:
        raise ValueError("Source annotation round-trip failed")
    return latex, tokens, attributes

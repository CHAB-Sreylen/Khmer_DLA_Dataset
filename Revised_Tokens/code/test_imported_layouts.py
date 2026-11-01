"""Read-only integration checks. Run: python -B -m unittest test_imported_layouts -v"""
import json
import random
import re
import unittest
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from layout_sample.imported_layouts import (
    LAYOUTS, generate_imported_doc, reconstruct_source, strip_comments,
    tokenize_source,
)

ROOT = Path(__file__).resolve().parents[2]
REVISED = ROOT / "Revised_Tokens"


class ImportedLayoutTests(unittest.TestCase):
    def test_all_templates_and_assets(self):
        vocab = json.loads((REVISED / "vocab.json").read_text(encoding="utf-8"))
        originals = dict(vocab)
        for name in LAYOUTS:
            with self.subTest(layout=name):
                template = (REVISED / "Latex_Sample_layout" / f"{name}_Layout.tex").read_text(encoding="utf-8")
                random.seed(12)
                latex, tokens, attrs = generate_imported_doc(
                    template, ROOT / "source", ["ថ្ងៃសុក្រ"], ["រាជធានីភ្នំពេញ"]
                )
                self.assertEqual(len(tokens), len(attrs))
                self.assertEqual(reconstruct_source(tokens, attrs), latex)
                self.assertNotRegex(latex, r"\\input\{")
                self.assertIn(r"\begin{document}", latex)
                self.assertIn(r"\end{document}", latex)
                for asset in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", latex):
                    self.assertTrue((ROOT / "source" / asset).is_file(), asset)
                for token in sorted(set(tokens) - vocab.keys()):
                    vocab[token] = max(vocab.values()) + 1
                self.assertTrue(all(token in vocab for token in tokens))
        self.assertEqual({key: vocab[key] for key in originals}, originals)

    def test_tokenizer_and_comments(self):
        source = strip_comments("\\fontsize{10pt}{14pt}\\selectfont\nA \\& B% comment\n\\textbf{ខ្មែរ}\\\\\n")
        tokens, attrs = tokenize_source(source)
        self.assertEqual(reconstruct_source(tokens, attrs), source)
        self.assertIn("{10pt}{14pt}", attrs)
        self.assertIn(r"\&", tokens)

    def test_unbalanced_argument_fails(self):
        with self.assertRaises(ValueError):
            tokenize_source(r"\textbf{broken")

    def test_generation_metadata_for_all_fifteen_families(self):
        import generate_dataset as generator
        with tempfile.TemporaryDirectory(prefix="khmer_dla_test_") as temporary:
            destination = Path(temporary) / "dataset"
            with patch.object(generator, "dataset_dir", destination), \
                 patch.object(generator, "temp_compile_dir", Path(temporary) / "compile"), \
                 patch.object(generator, "ProcessPoolExecutor", ThreadPoolExecutor), \
                 patch.object(generator.shutil, "which", return_value="mock-renderer"), \
                 patch.object(generator, "compile_latex_job", side_effect=lambda stem, *args: [stem + "-1.png"]), \
                 patch("builtins.print"):
                generator.generate_dataset()
            train = json.loads((destination / "train/ground_truth.json").read_text(encoding="utf-8"))
            test = json.loads((destination / "test/ground_truth.json").read_text(encoding="utf-8"))
            vocab = json.loads((destination / "vocab.json").read_text(encoding="utf-8"))
            self.assertEqual(len(train), 60)
            self.assertEqual(len(test), 15)
            self.assertFalse({item["stem"] for item in train} & {item["stem"] for item in test})
            imported = [item for item in train + test if item.get("annotation_format") == "latex-source-v1"]
            self.assertEqual(len(imported), 50)
            for item in train + test:
                self.assertEqual(item["length"], len(item["attributes"]))
                self.assertEqual(item["token_ids"], [vocab[token] for token in item["tokens"]])
            with patch.object(generator, "dataset_dir", destination), \
                 patch.object(generator.shutil, "which", return_value="mock-renderer"):
                with self.assertRaises(FileExistsError):
                    generator.generate_dataset()


if __name__ == "__main__":
    unittest.main()

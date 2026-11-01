# Additional institutional layouts

The generator supports the existing ITC, MPTC, NUM, Table and Combined families
plus MoEYS, MFAIC, MoH, MEF, CADT, RUPP, RUFA, UHS, MPWT and MoC.

## Generate

Install XeLaTeX through MiKTeX and install pdftocairo; make both available on PATH.
Install the required LaTeX packages before batch generation. The compiler uses
MiKTeX's `--disable-installer` option so parallel workers report missing packages
instead of attempting competing package installations. TeX Live would require
adapting that compiler option.
From `Revised_Tokens/code`, run:

```
python generate_dataset.py --output ../dataset_extended --samples-per-layout 5 --seed 42
```

This requests 75 documents with an 80/20 split within each of 15 families.
Output must be new or empty to avoid mixing old images and new annotations.
Two XeLaTeX passes resolve page counters and remembered positions. Every rendered
page is copied; `pages` in each record lists filenames in order. Each record is a
document-level sequence. A multipage record's entire sequence describes its full
ordered page list, not just `stem-1.png`. Consumers must load `pages` when present.

## Imported templates

The ten `.tex` layouts are copied into `Revised_Tokens/Latex_Sample_layout`;
their editable bodies are in `source/Text`, and logos/QRs are in `source/Figures`.
Shared fonts, stamp and ornament already provided by the dataset are reused.
Structured bodies (tables, counts, nested lists) retain their source wording.
Date/reference fields vary; arbitrary margin/font changes are intentionally not
applied because they can break the institution-specific structures.

## Annotation compatibility

The existing `stem`, `tokens`, `token_ids`, `attributes`, `length` fields remain.
Legacy families retain their current manually authored annotations.
Imported records add `annotation_format: latex-source-v1`: commands and balanced
arguments are extracted from the actual self-contained rendered source, including
macro definitions. Literal text/whitespace is stored in `<KhmerText>` attributes.
Tokens needed by imported files are appended in sorted order to the existing
vocabulary IDs, and the resulting mapping is saved in the output `vocab.json`.
Use that output vocabulary for training; do not assume its size remains 31.

For imported records use `layout_sample.imported_layouts.reconstruct_source`.
The old `LatexReconstructor` expects legacy labels and is unchanged. Models and
consumers of the new data need the extended vocabulary and source-v1 attribute
handling. This extension does not add bounding-box annotations or model training.

Run read-only checks from `Revised_Tokens/code`:

```
python -B -m unittest test_imported_layouts -v
```

The checks validate all ten inputs/assets, sequence lengths, vocabulary ID
preservation and exact source reconstruction without needing a TeX installation.
They do not establish visual correctness; render and inspect samples separately.

## Verified rendering

A real seed-42 run compiled all 75 documents: 60 train documents (70 PNG pages)
and 15 test documents (17 PNG pages), using a 55-token output vocabulary.
All page references and token/attribute lengths were verified. See
`RENDERING.md` for package preparation, compilation fixes and remaining data-quality
limitations. Generated rendering runs and local backups are ignored by Git;
the original tracked dataset remains in place.

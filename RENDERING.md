# Verified rendering run

Command: `python -B generate_dataset.py --output ../dataset_render_final --samples-per-layout 5 --seed 42`

- MiKTeX-XeTeX 4.18 / MiKTeX 26.5; Poppler pdftocairo 26.09.0.
- All 75 documents compiled successfully across 15 layout families.
- Train: 60 document records, 70 PNG pages. Test: 15 records, 17 PNG pages.
- Vocabulary: 55 tokens; IDs 0-30 retain the original vocabulary meanings.
- All annotation lengths/token IDs and referenced page files checked.
- No sample identifier overlap between train and test.
- Four integration regression tests passed.
- Visually reviewed first-page overviews for all families, plus representative
  MoEYS, CADT page 2 and MoH page 2 images. Not every page was individually reviewed.

## Fixes needed for real compilation

Installed missing LaTeX packages and hyperref dependencies using MiKTeX.
The generator now uses the installed fancyhdr instead of the repository's mock,
reports UTF-8 diagnostics, and disables automatic package installation during
parallel compilation to avoid downloads/locks/timeouts. Install missing packages
in MiKTeX Console or serially before running the generator.

Dataset template copies for RUPP, MPWT and MoC now provide empty defaults for
optional signature names that were referenced without definitions. The MEF body
uses a paragraph-safe group instead of its leftover placeholder textcolor wrapper.
Backups are under `integration_backup_20261101_135919`.

## Limits

This is a rendering/integration smoke dataset, not final research-quality data.
The ten imported families keep their supplied body wording; variation currently
focuses on explicit reference/date fields. Some source text still contains
placeholders or unfinished wording. Khmer font coverage produces substitutions
or missing symbols for some punctuation (including the MoH pointing-hand glyph).
The source assets include low-resolution QR/stamp images. Those need separate
content/font/asset curation before producing a final training corpus.

Multipage records describe the complete ordered `pages` list. Load that list
rather than assuming one image per document. The previous original dataset has
not been replaced; earlier partial render attempts are kept separately.

# Hanna Bae · Academic Homepage

Static, responsive academic homepage at <https://hanna-bae.github.io/>. No build step or JavaScript framework is required.

## Preview locally

Run `python3 -m http.server 8000` from this directory, then open <http://localhost:8000>.

- `index.html`: profile, publications, and experience
- `style.css`: desktop, mobile, reduced-motion, and print styles
- `script.js`: progressive enhancement for the current section and footer year
- `assets/`: existing portrait and CV

All content, publication links, and navigation remain available without JavaScript.

## Publication editing

Keep **Accepted & Published** above **Preprints & Under Review**. Within the accepted group, use reverse chronological order. Do not infer acceptance from an arXiv posting. For papers under review, do not name a submission venue unless it is appropriate to make that information public.

Prefer exact titles and author order from the paper's official metadata. Sources checked for the October 2026 update:

- VGGT-Bridge: <https://arxiv.org/abs/2610.06594>. The arXiv record explicitly states acceptance to ACCV 2026.
- Info3R: <https://arxiv.org/abs/2609.21938>. Public preprint; the homepage's existing under-review status is retained.
- Korean Table QA: [KCI record](https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003208010), DOI <https://doi.org/10.14329/isr.2025.27.2.071>. The exact English title and romanized author spellings follow this record.

The three other under-review manuscripts retain their existing titles and authors because matching public official metadata was not found. Their manuscript dates are not inferred.

## Validate changes

Run `python3 tests/check_site.py` and `node --check script.js`. Also preview at desktop and mobile widths, check for horizontal overflow, test keyboard focus and section links, and confirm each external publication link.

Changes should be reviewed on a branch before merging into `main`. Merging may publish the site through the repository's existing GitHub Pages configuration. No deployment configuration is included in this update.

The CV is an existing public asset. Review its contents separately before replacing it; editing the homepage does not update the PDF.

## Layout revision

Retain the original profile sidebar and right content column. The introduction is two sentences; Teaching, research chips, publication year badges and keyword lines are removed. Publication titles lead spacious rows. Reference pages informed hierarchy only; source and artwork were not copied: https://becow5x5.github.io/ and https://segyulee.github.io/.

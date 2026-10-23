# Optional PDF and EPUB image extraction

D1. IF diagram mode begins THEN resolve the class root, PDF or EPUB, existing or newly extracted notes, and requested chapter or section range from the request.
D2. IF the requested source is neither PDF nor EPUB THEN stop the image pass and report the unsupported format.
D3. IF no chapter or section range was requested THEN process the PDF chapter by chapter through its end.
D4. IF processing a chapter THEN inspect its complete PDF pages and inventory its figures, including multipart figures and worked-example figures.
D5. IF capturing a PDF figure THEN render its page with `pdftoppm -png` and crop the rendered page; preserve all relevant labels, arrows, junction dots, polarities, units, captions, and panels.
// Commentary: a rendered-page crop also captures vector circuit drawings, which are not necessarily embedded bitmap images.
D6. IF writing figure assets THEN use `OUTDIR/figures/<sanitized-source>/chapter<N>/` and filenames based on the printed figure number; record all stored paths relative to the class root.
D7. IF a figure has no chapter number THEN use `OUTDIR/figures/<sanitized-source>/other/` for its assets.
D8. IF a crop contains a worked reduction, printed answer, or solution THEN exclude that content from the question crop and retain it only in a separate answer crop.
D9. IF the question and solution content cannot be separated without losing required diagram content THEN register only an answer image for that figure and report it as unavailable for question display.
D10. IF transcribing a diagram THEN describe only visible connections, component values, labels, directions, and polarities in the `Description` field; label any descriptive node names absent from the figure as locally introduced names.
D11. IF explanatory prose is needed alongside a diagram description THEN retain it in the notes rather than presenting it as visually transcribed diagram content.
D12. IF a label or connection is unreadable THEN mark the registry entry `Status: unverified`, identify the ambiguity in `Description`, and report it without guessing.
D13. IF every recorded connection and label agrees with both the full PDF page and the final crop AND every question crop excludes solutions THEN mark the entry `Status: verified`.
D14. IF adding an image to notes THEN insert a relative Markdown image embed beside its caption without replacing source text; resolve the embed relative to that notes file, not to the class root.
D15. IF notes already contain an embed for that figure and asset THEN retain the existing embed without duplicating it.
D16. IF chapter slices and the full notes file both exist THEN add the same figure references to both using paths relative to each file.
D17. IF an image contains solution content THEN use an ordinary Markdown link labeled as a solution figure in the notes instead of an inline question image embed.
D18. IF a figure is registered THEN write its entry to `OUTDIR/figures/<sanitized-source>/figures.md` using the schema below.
D19. IF registering a PDF image THEN record its exact render DPI, crop rectangle, and SHA-256 digest.
D20. IF an asset or registry entry already exists AND no replacement was authorized THEN keep it; add only missing entries, and report any conflict requiring replacement.
D21. IF replacing an asset or its description was authorized THEN report that questions referencing that figure need regeneration.
D22. IF a chapter's figures are saved THEN verify every asset path, source-page locator, digest, crop readability, and separation of question content from answers before advancing.
D23. IF the diagram pass completes THEN report figures verified, figures unresolved, answer-only figures, the registry path, notes updated, and any chapters not processed.
D24. IF the class has a Contents inventory THEN add or update its figure-registry entry without changing other class instructions.
D25. IF a diagrams-only pass completes THEN leave the source book at its existing path.
D26. IF a chapter has unverified figures THEN continue the remaining requested chapters and report those figures as excluded from question generation.
D27. IF processing an EPUB THEN follow its package spine to locate body content and resolve each selected image reference relative to its containing XHTML/HTML document.
D28. IF an EPUB image is PNG or JPEG THEN preserve its exact archive bytes and original format; register its containing `Document`, its stage-specific `Question member` or `Answer member`, its stored image path, and SHA-256 digest instead of PDF Page/DPI/crop fields.
D29. IF an EPUB image uses another format THEN report it as unsupported by the current image verifier instead of silently converting it.
D30. IF an original figure has inadequate contrast for lesson display AND its labels and topology can be verified from the source and adjacent prose THEN preserve the original and create a readable SVG reconstruction with a PNG display render; visibly label the reconstruction.
D31. IF using a reconstructed EPUB image THEN record `<stage> representation: redraw`, `<stage> original: <class-root-relative-original-image>`, and `<stage> source SHA256: <original-member-hash>` in addition to its member, display path, and display SHA256.
D32. IF an EPUB figure was reconstructed THEN visually compare its rendered labels, directions, and ordering against the source before marking it verified.
D32a. IF an EPUB image shows black regions where the printed figure has a blank background (a transparency-to-JPEG conversion defect) THEN create a RECOVERED COPY with `recover_figure.py <out_dir> --compare <compare_dir> <image>` (beside this skill), and keep the original asset.
     // Commentary: the flattened background is pure black, and ink drawn on it survives as very dark gray. The script inverts brightness only inside those dark zones, so the background turns white and the ink black; saturated colours and the rest of the image are untouched. Turning the black white without the inversion (a plain fill) erodes the ink and was rejected.
D32b. IF a recovered copy is created THEN store it under `OUTDIR/figures/<sanitized-source>/chapter<N>/clean/`, named after the original with a `.png` extension.
D32c. IF a recovered copy is created THEN view its `--compare` sheet (original and recovered side by side) before use.
D32d. IF the D32c comparison shows any label, line, arrow, or symbol removed, altered, or still on black THEN discard the recovered copy and keep the native image, or apply D30.
D32e. IF using a recovered copy THEN record the D31 fields with `<stage> representation: clean` in place of `redraw`, point `<stage> image` and `<stage> SHA256` at the recovered PNG, and point every notes embed for that figure at the recovered PNG.
D32f. IF `recover_figure.py` reports an image as `native` THEN keep its native representation; do NOT create a recovered copy.
     // Commentary: a recovered copy changes only background and ink brightness, so its Description stays the original's. A redraw (D30) is reserved for figures whose labels stay unreadable after recovery.
D33. IF processing EPUB images THEN D27–D32f override the PDF-page inspection and crop metadata requirements in D4, D13, D19 and D22 only for EPUB sources; inspect the containing source section and each final image instead.
D34. IF a condition not covered by D1–D33 arises THEN stop, describe the situation to the user, and ask how to proceed. Do not improvise.

## Registry schema

One entry per figure; IDs are unique within the registry. Field continuation lines have exactly two spaces. `Question image`, `Question crop`, and `Question SHA256` form an optional group; the corresponding `Answer` fields form another optional group. At least one group is present. Paths are class-root-relative; crops are `(x y width height)` pixels at the recorded DPI, with origin at the rendered page's top-left. `Description` records only the question-visible source content; solution-only observations belong in optional `Answer description`.

For EPUB entries, `Document` and the stage-specific `member` fields replace PDF Page/DPI/crop metadata under D28. Native PNG/JPEG display images match their archive member byte-for-byte. A labeled reconstruction instead uses D31's explicit `redraw` provenance fields and retains the original asset.

```text
#### figure_2_16
Source: source/book.pdf
Page: 48
DPI: 170
Question image: extracted/figures/book/chapter2/figure_2_16.png
Question crop: 700 1415 360 295
Question SHA256: <SHA-256 of the saved PNG>
Status: verified
Description:
  Source VS has positive polarity at the top node and negative polarity at the bottom node.
  R1 connects the top node to the middle node. R2 connects the middle node to the bottom node.
  Output V2 is positive at the middle node and negative at the bottom node.
```

Example reference from a question: `Figure source: extracted/figures/book/figures.md#figure_2_16`.

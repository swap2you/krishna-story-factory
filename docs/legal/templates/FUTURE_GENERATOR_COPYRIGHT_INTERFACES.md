# Future publication copyright interfaces

Generators that do not yet exist should implement these interfaces rather than hard-coding identity strings.

## Shared requirement

Load `config/publication_identity.yaml` via `krishna_story_factory.publication.get_identity()`.

## Books / eBooks / comics

Emit a dedicated copyright page with: title; copyright notice; publisher; edition/year only when reviewed; version; work ID; author/contributors; illustrator credits; source/quotation credits; AI-assistance disclosure; rights limitation; contact; registration status statement.

## DOCX / slides / video

Populate creator, publisher, rights, identifier, language, dates, version, source credits, and accessibility metadata when the format supports them. Use restrained end/cover credits.

## Draft / preview

Visible watermark only on drafts/proofs:

`DRAFT — NOT FOR DISTRIBUTION` or `PREVIEW — NOT FOR REDISTRIBUTION`

Never automatically watermark final consumer copies.

## Printables / PDFs / images / audio

Reuse `krishna_story_factory.publication.notices` and `artifacts` helpers.

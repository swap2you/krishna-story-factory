# 01 — Copyright Matrix

## Centralized identity (Section B) — PASS

`config/publication_identity.yaml` (authoritative) and `apps/web/config/contact.json` (web mirror) both verified, values identical and exactly matching the contract:

| Field | Value | Match |
|---|---|---|
| copyright_owner / public_author_name | Svarna Gauranga Das | ✔ |
| publisher | Dauji Publication (publishing imprint) | ✔ |
| project | Bhāva | ✔ |
| location | Harrisburg, Pennsylvania, USA | ✔ |
| contact_email | svarnagaurangdas@gmail.com | ✔ |
| phone | null | ✔ |

Fail-condition scans, all clean:

- "Swarna": appears ONLY in the forbidden-spelling guard list and its two enforcement functions (`krishna_story_factory/publication/identity.py`, `work_manifest.py`) — never as a live identity string.
- Old email (`swap2you@...`): zero occurrences in app/config/output/story surfaces.
- Phone patterns: zero occurrences in web config/product config.
- No conflicting identity configurations found (single YAML + consistent JSON mirror; comments in both mandate loading from the central file).
- The evidence copy (`runs/final-copyright-.../copyright-config.yaml`) is identical in all identity fields.

## Rights accuracy (Section C) — PASS

Verified across config, manifests, story.md, MP3 tags, images, PDFs, and the live `/rights` page:

- **Scripture never claimed**: `excluded_categories` covers Bhagavad-gītā, Śrīmad-Bhāgavatam, Krishna Book, Caitanya-caritāmṛta, all Prabhupāda works, verses, traditional prayers, third-party works, Ministry resources, and "purely AI-generated expressive material without sufficient human authorship." The live `/rights` page renders the same "What is not claimed" list verbatim.
- **Claim scope limited**: manifests' `human_authorship_claim` claims adaptation/selection/arrangement/activities/editing/design/production only, and states "Prompting alone is not claimed as authorship."
- **AI disclosure per medium** (manifest `ai_assistance`): story text `human_edited_adaptation`; images record provider model (gpt-image-1), human modification (credit strip + publication design), and `full_image_copyright_claim: "limited"`; audio records provider and human editing.
- **℗ not auto-asserted**: `sound_recording_claim_status: "needs_manual_review"` in every manifest; MP3 `TCOP`/`COMM` read "Sound recording ℗ claim: deferred pending" review; live `/rights` AI section states ℗ "applied only when a reviewed sound-recording rights status supports them."
- **Registration not overclaimed**: registration disclaimer present in config and rendered on `/rights` ("…not the same as formal U.S. Copyright Office registration. Bhāva does not claim 'registered' status unless an official record supports that claim.").
- **Imprint honesty**: `/rights` explicitly notes Dauji Publication "is not represented here as a registered corporation, trademark, or separate copyright owner."
- **Credits present**: poster bottom strip "Bhāva design and publication © Svarna Gauranga Das · Dauji Publication" (limited-claim wording); coloring pages "© Svarna Gauranga Das · Dauji Publication · Bhāva" in the print margin; PDFs carry the full block (© line, "Published by Dauji Publication", contact) on the final page.

## Non-blocking notes

1. **P3 — credit-strip diacritics**: on `story_poster.png` the title/caption text in the strip renders Kṛṣṇa/Pūtanā diacritics as missing-glyph boxes (e.g. "K□□□□a's"); the © credit line itself renders correctly. Cosmetic font-coverage issue in the strip renderer.
2. **P3 — PDF footer on final page only**: the full © block appears on the last page of each activity PDF; interior pages carry title + page number only. For classroom printables whose pages circulate separately, a compact per-page footer would be stronger. Document-level notice is present, so not a launch blocker.

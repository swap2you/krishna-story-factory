# Poster Copy Generator

From the visual brief and story.md, return **strict JSON only**:

```json
{
  "title": "",
  "subtitle": "",
  "heavenly_quote": "",
  "one_liner": "",
  "supporting_captions": [
    {
      "label": "",
      "text": ""
    }
  ]
}
```

Rules:

* Use exact title from story.md.
* Subtitle should be 3–8 words.
* Heavenly quote must come from the story.
* One-liner should be 12–24 words.
* Up to three supporting captions.
* Each supporting caption must be 4–12 words.
* Do not invent scriptural quotations.
* Do not misquote the heavenly message.
* No marketing hype.
* No modern slang.
* No spelling errors.
* Avoid duplicate wording.

Return only valid JSON. No markdown fences.

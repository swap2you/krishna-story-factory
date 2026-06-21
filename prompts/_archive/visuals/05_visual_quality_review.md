# Visual Quality Review Criteria

Score each generated visual package 0–100.

## Line art prompt must include

- portrait
- ages 6–13
- confident or thick outlines
- white background
- large colorable spaces
- expressive faces
- safe margins
- no cropping
- no shading
- no modern objects
- story-specific central scene

## Poster prompt must include

- portrait poster
- ultra-realistic
- 3D
- devotional
- cinematic
- clear focal hierarchy
- expressive Indian faces
- ancient Indian setting
- no modern objects
- no generated text
- child-safe
- story-specific central scene

## File checks

- all final images exist and are non-empty
- portrait orientation
- minimum 1024 pixels on short side when supported
- poster and line art are not identical
- line art is predominantly grayscale/black-and-white
- final poster contains local typography
- line-art print PDF exists

## Vision review dimensions (optional)

- story fidelity
- character correctness
- emotional clarity
- anatomy
- line-art print suitability
- coloring appeal
- poster hierarchy
- child safety
- devotional mood
- unwanted text artifacts

Return JSON:

```json
{
  "score": 0,
  "issues": [],
  "retry_recommended": false
}
```

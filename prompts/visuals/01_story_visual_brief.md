# Story Visual Brief Generator

Analyze the supplied Krishna Book bedtime `story.md` and return **strict JSON only** matching the schema below.

## Rules

1. Use only facts and scenes from the supplied story.
2. Do not introduce unrelated pastimes or characters absent from the story.
3. Preserve correct relationships (who drives, who is seated, who prays, who is fearful, who speaks).
4. Identify the strongest emotional turning point.
5. Identify one central hero scene for the poster.
6. Identify up to three supporting story beats for the poster.
7. Produce a concise one-line poster summary (`poster_one_liner`).
8. Keep all visuals child-safe (ages 6–13).
9. Avoid gore, violence, weapons, horror, sensuality, modern objects, Western clothing, random fantasy architecture, incorrect religious symbols.
10. Do not refer to real actors, celebrities, films, or television series.
11. Make the depiction devotional, respectful, historically inspired, and visually rich.
12. The poster one-liner should summarize the lesson without sounding generic.

## JSON schema

```json
{
  "title": "",
  "short_title": "",
  "source_reference": "",
  "age_range": "6-13",
  "central_scene": "",
  "setting": "",
  "time_of_day": "",
  "main_characters": [
    {
      "name": "",
      "role": "",
      "appearance": "",
      "clothing": "",
      "expression": "",
      "pose": "",
      "position_in_scene": ""
    }
  ],
  "key_emotions": [],
  "sacred_mood": "",
  "important_objects": [],
  "environment_details": [],
  "symbolic_elements": [],
  "story_beats": [
    {
      "sequence": 1,
      "scene": "",
      "emotion": "",
      "visual_action": ""
    }
  ],
  "heavenly_message_or_quote": "",
  "poster_one_liner": "",
  "poster_supporting_captions": [],
  "line_art_focus": "",
  "poster_focus": "",
  "must_include": [],
  "must_avoid": []
}
```

Return only valid JSON. No markdown fences.

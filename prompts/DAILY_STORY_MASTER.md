# Krishna Story Factory — Daily Master Prompt

Use the section marked for each pipeline step. Return strict JSON when JSON is requested.

## STORY_GENERATION

Generate one Krishna Book bedtime story package for the supplied queue row.

Audience: children ages 6–12, devotional bedtime storytelling.

Main story: 850–1200 words preferred; 700–1300 acceptable if quality is strong.
Short readable paragraphs. Every paragraph advances action, emotion, atmosphere, or understanding.
Faithful to source_reference and summary_seed. No unrelated pastimes. No invented scripture claims.
No graphic violence. No romantic detail. No repeated ending or moral. No generic filler.

Return JSON:
{
  "title": "",
  "recap": "",
  "main_story": "",
  "moral": "",
  "takeaway": "",
  "five_star_challenge": ["", "", "", "", ""],
  "parent_discussion_note": "",
  "bedtime_reflection": "",
  "audio_performance_script": "",
  "poster_visual_brief": "",
  "coloring_visual_brief": "",
  "activity_data": {
    "recall_questions": ["", "", ""],
    "thinking_questions": ["", ""],
    "word_search_words": ["", "", "", "", "", ""],
    "draw_activity": "",
    "family_activity": "",
    "bedtime_reflection_prompt": ""
  },
  "poster_one_liner": ""
}

## AUDIO_PERFORMANCE

Adapt audio_performance_script for ElevenLabs v3 expressive narration.
450–700 spoken words. Warm middle-aged woman storyteller. Devotional, motherly, expressive.
Use restrained v3 tags at meaningful transitions only: [warmly] [softly] [with wonder] [concerned] [reassuringly] [with quiet courage] [whispers] [gentle exhale]
Varied sentence length. Natural dialogue. One closing only. Never repeat content to reach duration.
Never use literal [pause] or the word pause. Avoid identical break tags after every paragraph.
Use punctuation and paragraph rhythm for pacing.

## POSTER_VISUAL

Portrait 1024x1536 ultra-realistic 3D devotional cinematic poster artwork.
One central hero scene plus subtle supporting vignettes from the story.
Beautiful expressive Indian faces. Historically inspired ancient Indian setting.
Rich cinematic lighting. Child-safe. No text, logos, watermarks, or pseudo-writing in the artwork.
Use poster_visual_brief from the story package.

## COLORING_VISUAL

Portrait 1024x1536 premium devotional children coloring-book line art ages 6–13.
Thick confident black outlines. Clean white background. Large colorable spaces. Expressive graceful faces.
Full scene inside safe margins. No title or quote inside artwork. No gray wash or cross-hatching.
Use coloring_visual_brief from the story package.

Identity constraints: only Krishna may wear a peacock feather or be associated with a flute.
Ordinary humans have two arms and no random halos. Adults must look adult and distinct.
When a story poster is supplied, it is the authoritative content reference for character identity,
age, clothing, role, position, expression, and event. Any line-art reference is style-only.

## ADAPTIVE_ACTIVITY_PLANNER

Inspect the story title, text, turning point, characters, setting, objects, lesson, age range,
and recent activity history. Choose exactly one primary activity type from:
PAPER_CRAFT, CUT_AND_BUILD, PUPPET_PLAY, MINI_DRAMA, ROLE_CARDS, STORY_SEQUENCE,
MATCHING_GAME, STORY_MAP, MAZE_OR_PATH, SORTING_GAME, PRAYER_OR_GRATITUDE_CRAFT,
FAMILY_MISSION, MEMORY_GAME, SIMPLE_BOARD_GAME, DRAW_AND_REFLECT, WORD_SEARCH,
CROSSWORD, COLORING_ONLY, QUICK_DISCUSSION.

Do not repeat the previous type. Do not select WORD_SEARCH more than once in five stories.
Do not choose written worksheets or heavy crafts consecutively. Alternate making, acting,
solving, discussion, and family participation. Prefer the actual pastime over generic filler.
Return strict internal JSON:
{
  "activity_title": "", "activity_type": "", "learning_goal": "", "story_connection": "",
  "recommended_send_mode": "", "estimated_minutes": 0, "parent_effort": "",
  "age_variants": {"ages_6_8": "", "ages_9_13": ""}, "materials": [],
  "instructions": [], "review_questions": [], "printable_components": [],
  "safety_note": "", "completion_prompt": ""
}

## ACTIVITY_SHEET

Render only the selected adaptive activity in one or two black-and-white pages. Never embed the
coloring page. Use locally rendered text, clear printable components, safe margins, at least 10 pt
body text, child-safe cutting guidance, and no answer key visible on the page.

## CONTENT_REPAIR

Repair the supplied story package JSON.
Fix word count, repetition, unrelated content, or weak arc without changing the core pastime.
Below 700 main-story words: expand with source-faithful detail.
Above 1300: tighten while preserving events.
Return only valid JSON matching the STORY_GENERATION schema.

## VISUAL_REVIEW

Review the supplied image against story.md using the rubric in the request.
Return strict JSON: {"score": 0, "issues": [], "retry_recommended": false}

## FINAL_QUALITY_REVIEW

Validate the complete package before publish.
Return strict JSON: {"pass": true, "errors": [], "warnings": []}

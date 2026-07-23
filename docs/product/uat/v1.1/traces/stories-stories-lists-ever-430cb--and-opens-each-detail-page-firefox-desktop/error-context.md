# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: stories.spec.ts >> stories >> lists every discovered story and opens each detail page
- Location: e2e\stories.spec.ts:5:7

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByRole('heading', { level: 1 })
Expected substring: "Narada’s Warning and Kamsa’s Decision"
Error: strict mode violation: getByRole('heading', { level: 1 }) resolved to 2 elements:
    1) <h1>Narada’s Warning and Kamsa’s Decision</h1> aka locator('section').getByRole('heading', { name: 'Narada’s Warning and Kamsa’s Decision', exact: true })
    2) <h1>📿 Krishna Book Bedtime</h1> aka getByRole('heading', { name: '📿 Krishna Book Bedtime' })

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for getByRole('heading', { level: 1 })

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - generic [ref=e2]:
    - banner [ref=e3]:
      - generic [ref=e4]:
        - link "Bhāva home" [ref=e5] [cursor=pointer]:
          - /url: /
          - img [ref=e6]
          - generic [ref=e7]:
            - generic [ref=e8]: bhāva
            - generic [ref=e9]: Devotional learning
        - navigation "Primary navigation" [ref=e10]:
          - link "Home" [ref=e11] [cursor=pointer]:
            - /url: /
          - link "Library" [ref=e12] [cursor=pointer]:
            - /url: /library
          - link "For Teachers" [ref=e13] [cursor=pointer]:
            - /url: /teachers
          - link "Prabhupāda Vāṇī" [ref=e14] [cursor=pointer]:
            - /url: /prabhupada-vani
          - link "Bhakti Blog" [ref=e15] [cursor=pointer]:
            - /url: /blog
          - link "About" [ref=e16] [cursor=pointer]:
            - /url: /about
          - link "Contact" [ref=e17] [cursor=pointer]:
            - /url: /contact
    - main [ref=e18]:
      - generic [ref=e19]:
        - complementary [ref=e20]:
          - link "← Krishna Book" [ref=e21] [cursor=pointer]:
            - /url: /library/krishna-book
          - img "Narada’s Warning and Kamsa’s Decision story poster" [ref=e22]
          - paragraph [ref=e23]: Story 004
          - heading "Narada’s Warning and Kamsa’s Decision" [level=2] [ref=e24]
          - paragraph [ref=e25]: Suggested for 6-12
          - paragraph [ref=e26]: Krishna Book Chapter 1
        - generic [ref=e27]:
          - generic [ref=e28]:
            - generic [ref=e29]:
              - paragraph [ref=e30]: Listen · Read · Activities
              - heading "Narada’s Warning and Kamsa’s Decision" [level=1] [ref=e31]
            - generic [ref=e32]: PASS
          - generic "Audio player for Narada’s Warning and Kamsa’s Decision" [ref=e34]:
            - img "Narration waveform" [ref=e35] [cursor=pointer]
            - generic [ref=e36]:
              - button "Play" [ref=e37] [cursor=pointer]
              - button "Back 15 seconds" [ref=e38] [cursor=pointer]: −15s
              - button "Forward 15 seconds" [ref=e39] [cursor=pointer]: +15s
              - generic [ref=e40]:
                - text: Speed
                - combobox "Playback speed" [ref=e41]:
                  - option "0.75×"
                  - option "1×" [selected]
                  - option "1.25×"
                  - option "1.5×"
                  - option "2×"
              - generic [ref=e42]:
                - text: Volume
                - slider "Volume" [ref=e43]: "1"
              - generic [ref=e44]: 0:00 / −3:27
            - generic [ref=e45]:
              - button "Bookmark position" [ref=e46] [cursor=pointer]
              - button "Jump to bookmark" [ref=e47] [cursor=pointer]
              - generic [ref=e48]:
                - text: Sleep timer
                - combobox "Sleep timer" [ref=e49]:
                  - option "Off" [selected]
                  - option "5 min"
                  - option "15 min"
                  - option "30 min"
              - link "Download audio" [ref=e50] [cursor=pointer]:
                - /url: /api/v1/stories/004/assets/narration.mp3
            - paragraph [ref=e51]: "Keyboard: Space play/pause · ← −15s · → +15s. Progress resumes on this device."
          - navigation "Story navigation" [ref=e52]:
            - link "← Story 003" [ref=e53] [cursor=pointer]:
              - /url: /stories/003
            - link "Story 005 →" [ref=e54] [cursor=pointer]:
              - /url: /stories/005
          - generic [ref=e55]:
            - tablist [ref=e56]:
              - tab "Listen" [selected] [ref=e57] [cursor=pointer]
              - tab "Read" [ref=e58] [cursor=pointer]
              - tab "Activities" [ref=e59] [cursor=pointer]
              - tab "Coloring" [ref=e60] [cursor=pointer]
              - tab "Source" [ref=e61] [cursor=pointer]
              - tab "Notes" [ref=e62] [cursor=pointer]
              - tab "Ślokās" [ref=e63] [cursor=pointer]
            - tabpanel [ref=e64]:
              - generic [ref=e66]:
                - heading "Listen & read along" [level=2] [ref=e67]
                - paragraph [ref=e68]: Follow-along cues pending review
                - article [ref=e69]:
                  - paragraph [ref=e70]: Hare Kṛṣṇa, dear children and families!
                  - heading "📿 Krishna Book Bedtime" [level=1] [ref=e71]
                  - heading "Story 004 — Narada’s Warning and Kamsa’s Decision" [level=2] [ref=e72]
                  - heading "Scriptural Source" [level=3] [ref=e73]
                  - text: Krishna Book Chapter 1 SB 10.1.62-69 Nārada's visit through Ugrasena's removal and the devotees' composure
                  - heading "Recap" [level=2] [ref=e74]
                  - text: Last time in our Krishna Book Bedtime series, little Kīrtimān was born, and Vasudeva kept his difficult promise by bringing the baby to Kaṁsa. Amazingly, Kaṁsa returned the child, and the family felt a brief wave of relief. That temporary mercy did not end Kaṁsa’s fear. Now Nārada arrives with a grave warning, and Kaṁsa makes a darker decision that changes everything for Devakī and Vasudeva.
                  - heading "Main Story" [level=2] [ref=e75]
                  - text: Mathurā's markets bustled and palaces shone, but inside the royal hall an uneasy mood hung in the air. Kaṁsa sat restless upon his throne. Worry lines deepened on his brow as city sounds drifted faintly through the windows.
                  - paragraph [ref=e76]: Suddenly the great sage Nārada Muni entered, saffron robes bright and vīṇā in hand. The court fell silent. Nārada was known for arriving at moments that change a kingdom's direction.
                  - paragraph [ref=e77]: He approached Kaṁsa with composure that made the room feel still. Nārada offered respects and then gave a startling instruction. In paraphrase, he told Kaṁsa that demigods—celestial beings of power and light—were appearing among the Yadu and Vṛṣṇi families.
                  - paragraph [ref=e78]: Their presence signaled that a divine plan was moving forward. Kaṁsa's heart lurched.
                  - paragraph [ref=e79]: He already feared the prophecy about Devakī's child. Now he heard that heavenly beings were joining those very dynasties.
                  - paragraph [ref=e80]: Panic drained the color from his face as he gripped the carved arms of his throne. In paraphrase, Kaṁsa pressed to know why such beings had come and whose side they favored.
                  - paragraph [ref=e81]: Nārada's answer was firm and revealing. In paraphrase, he reminded Kaṁsa that in a previous life he had been Kālanemi, opposed to the Supreme Lord. He said those descending from heaven were coming to assist the Lord's appearance.
                  - paragraph [ref=e82]: A cold shiver moved through Kaṁsa. Destiny felt close, and fear made him desperate to seize control. He barked orders to his guards to take Devakī and Vasudeva at once.
                  - paragraph [ref=e83]: Soldiers moved quickly, surrounding the gentle couple. Even then the guards showed restraint, for Devakī's kindness was known. Devakī and Vasudeva walked with calm, dignified steps as they were led away.
                  - paragraph [ref=e84]: Devakī folded her hands, remembering Krishna and keeping the Lord close in her heart. Vasudeva stayed close, steadying her with quiet faith. They entered a modest prison room where an oil lamp glowed against stone walls.
                  - paragraph [ref=e85]: Side by side they settled, choosing remembrance over panic. No cell could lock out the Lord's mercy from a devoted heart. Yet Kaṁsa's fear had not finished its work.
                  - paragraph [ref=e86]: Suspicious even of his own blood, he turned against his aging father, King Ugrasena. With a cold command he removed Ugrasena from power. Then he claimed the throne of Mathurā for himself.
                  - paragraph [ref=e87]: The grand hall should have felt triumphant, yet it felt emptied of warmth. Shadows seemed longer, and Kaṁsa's pounding heart echoed louder than any cheer. Outside the palace, rumors raced through winding streets.
                  - paragraph [ref=e88]: Husbands and wives whispered at market stalls about missing King Ugrasena. They also spoke of gentle Devakī and honest Vasudeva now imprisoned. Children clung to their mothers, sensing changes they could not understand.
                  - paragraph [ref=e89]: Yet even in those dark hours, devotees of Kṛṣṇa gathered quietly in corners of the city. Softly they chanted the holy names together. Their faith rose like steady flames sheltered from the wind of fear.
                  - paragraph [ref=e90]: In the prison cell, Devakī and Vasudeva reminded each other of the Lord's care. In paraphrase, Vasudeva encouraged offering their worries to Kṛṣṇa. He said they should keep Him in the heart no matter what happened outside.
                  - paragraph [ref=e91]: They refused to let sorrow harden into hatred. As another day ended, Nārada's visit remained vivid in every mind. It was a warning that deepened the wicked king's alarm.
                  - paragraph [ref=e92]: It was also a hidden encouragement for those who loved the Lord. The greater story was still unfolding, but devotion already held its quiet place in Mathurā. Faith waited patiently for Kṛṣṇa's plan to bloom.
                  - paragraph [ref=e93]: Kaṁsa paced the empty throne room after seizing power. Gold and glory surrounded him, but peace would not come near his restless mind.
                  - paragraph [ref=e94]: Ugrasena's loyal servants mourned the sudden change in silence. They remembered a kinder rule and wondered what fear would demand next.
                  - paragraph [ref=e95]: In the prison, Devakī and Vasudeva shared the holy names in soft tones. Their remembrance made the stone walls feel less cold.
                  - paragraph [ref=e96]: Across Mathurā, some people hid their worry behind busy market talk. Others found courage by joining quiet circles of chanting devotees.
                  - paragraph [ref=e97]: Nārada's visit lingered like a turning point written across the kingdom. Truth had been spoken, and every heart now chose fear or faith.
                  - paragraph [ref=e98]: Night settled over the city with heavy clouds and distant temple bells. Even then, hope remained alive wherever Kṛṣṇa's names were sung.
                  - heading "Devotional Meaning" [level=2] [ref=e99]
                  - text: This pastime contrasts fear-driven power with faith-filled composure. Kaṁsa hears truthful news from Nārada and answers with imprisonment and seizure of the throne. Devakī and Vasudeva answer the same darkness by remembering Kṛṣṇa. The devotees in Mathurā show that holy names can be chanted even when a city feels unsafe. True strength is not control seized in panic, but a heart that stays with the Lord. Chanting in community helps worried hearts remember they are not alone.
                  - heading "Five Lessons" [level=2] [ref=e100]
                  - text: 1. Fear can push harsh choices when the heart forgets the Lord. 2. Faith keeps devotees composed in unfair times. 3. Remembering Kṛṣṇa brings courage when surroundings feel dark. 4. Power taken in panic cannot give real peace. 5. Chanting together strengthens a community of devotees.
                  - heading "Think About It" [level=2] [ref=e101]
                  - text: 1. What news did Nārada bring to Kaṁsa about the Yadu and Vṛṣṇi families? 2. Who was Kaṁsa in his previous life, according to Nārada's reminder? 3. What did Kaṁsa do to Devakī and Vasudeva after hearing the warning? 4. How did Kaṁsa treat King Ugrasena when fear ruled his decisions? 5. When something feels unfair, how can remembering Kṛṣṇa help you stay calm?
                  - heading "Five-Star Challenge" [level=2] [ref=e102]
                  - text: 1. Count how many names of Kṛṣṇa you know and say them softly before bed. 2. Draw Devakī and Vasudeva in prison with peaceful, faithful faces. 3. Write a thank-you note to someone who helps you feel safe. 4. Say a prayer for a person going through a hard time. 5. Act out Nārada's visit with family using a simple scarf as saffron cloth.
                  - heading "Bedtime Prayer" [level=2] [ref=e103]
                  - text: "Dear Kṛṣṇa, thank You for Nārada's warning and for the faith of Devakī and Vasudeva. Please keep our family calm and close to You when fear feels strong. We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night, and may Your peace rest gently on our hearts."
                  - heading "Next Story Preview" [level=2] [ref=e104]
                  - text: "Next time: Story 005 — Prayers by the Demigods for Lord Krishna in the Womb. While Devakī and Vasudeva remain in prison, unseen demigods gather in devotion as Lord Kṛṣṇa enters Devakī's womb and heavenly prayers fill that dark cell with hope."
                  - heading "Parent/Teacher Note" [level=2] [ref=e105]
                  - text: "From Krishna Book Chapter 1 (SB 10.1.62–69): Nārada informs Kaṁsa, Kālanemi identity is recalled, Devakī and Vasudeva are imprisoned, and Ugrasena is removed. Stay inside this boundary—no Mother Earth retelling, no first-child replay, and no full Chapter 2 demigod prayer scene. Keep imprisonment child-safe and emphasize faith versus fear. If children feel afraid, reconnect to Devakī and Vasudeva's calm remembrance."
    - contentinfo [ref=e106]:
      - generic [ref=e107]:
        - generic [ref=e108]: Bhāva — stewarded with care by Svarna Gauranga Das.
        - generic [ref=e109]:
          - link "Sunday School" [ref=e110] [cursor=pointer]:
            - /url: /sunday-school
          - link "For Preachers" [ref=e111] [cursor=pointer]:
            - /url: /preachers
          - link "Privacy" [ref=e112] [cursor=pointer]:
            - /url: /privacy
          - link "Accessibility" [ref=e113] [cursor=pointer]:
            - /url: /accessibility
          - link "Source & permissions" [ref=e114] [cursor=pointer]:
            - /url: /source-permissions
  - alert [ref=e115]
```

# Test source

```ts
  1  | import { expect, test } from "@playwright/test";
  2  | import { fetchStories } from "./helpers";
  3  | 
  4  | test.describe("stories", () => {
  5  |   test("lists every discovered story and opens each detail page", async ({ page, request }) => {
  6  |     const stories = await fetchStories(request);
  7  |     expect(stories.length).toBeGreaterThan(0);
  8  | 
  9  |     await page.goto("/library/krishna-book");
  10 |     await expect(page.getByRole("heading", { name: /chapter timeline/i })).toBeVisible();
  11 |     await expect(page.locator(".story-card").first()).toBeVisible({ timeout: 15_000 });
  12 |     await expect(page.locator(".story-card")).toHaveCount(stories.length);
  13 | 
  14 |     for (const story of stories) {
  15 |       const response = await page.goto(`/stories/${story.story_no}`);
  16 |       expect(response?.ok()).toBeTruthy();
> 17 |       await expect(page.getByRole("heading", { level: 1 })).toContainText(story.title);
     |                                                             ^ Error: expect(locator).toContainText(expected) failed
  18 |     }
  19 |   });
  20 | });
  21 | 
```
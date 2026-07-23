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
Expected substring: "The Earth Prays for Krishna to Come"
Error: strict mode violation: getByRole('heading', { level: 1 }) resolved to 2 elements:
    1) <h1>The Earth Prays for Krishna to Come</h1> aka locator('section').getByRole('heading', { name: 'The Earth Prays for Krishna to Come', exact: true })
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
        - link "Bhāva home" [ref=e5]:
          - /url: /
          - img [ref=e6]
          - generic [ref=e8]: bhāva
        - navigation "Primary navigation" [ref=e9]:
          - link "Home" [ref=e10]:
            - /url: /
          - link "Library" [ref=e11]:
            - /url: /library
          - link "For Teachers" [ref=e12]:
            - /url: /teachers
          - link "Prabhupāda Vāṇī" [ref=e13]:
            - /url: /prabhupada-vani
          - link "Bhakti Blog" [ref=e14]:
            - /url: /blog
          - link "About" [ref=e15]:
            - /url: /about
          - link "Contact" [ref=e16]:
            - /url: /contact
    - main [ref=e17]:
      - generic [ref=e18]:
        - complementary [ref=e19]:
          - link "← Krishna Book" [ref=e20] [cursor=pointer]:
            - /url: /library/krishna-book
          - img "The Earth Prays for Krishna to Come story poster" [ref=e21]
          - paragraph [ref=e22]: Story 001
          - heading "The Earth Prays for Krishna to Come" [level=2] [ref=e23]
          - paragraph [ref=e24]: Suggested for 6-12
          - paragraph [ref=e25]: Krishna Book Chapter 1
        - generic [ref=e26]:
          - generic [ref=e27]:
            - generic [ref=e28]:
              - paragraph [ref=e29]: Listen · Read · Activities
              - heading "The Earth Prays for Krishna to Come" [level=1] [ref=e30]
            - generic [ref=e31]: PASS
          - generic "Audio player for The Earth Prays for Krishna to Come" [ref=e33]:
            - img "Narration waveform" [ref=e34] [cursor=pointer]
            - generic [ref=e35]:
              - button "Play" [ref=e36] [cursor=pointer]
              - button "Back 15 seconds" [ref=e37] [cursor=pointer]: −15s
              - button "Forward 15 seconds" [ref=e38] [cursor=pointer]: +15s
              - generic [ref=e39]:
                - text: Speed
                - combobox "Playback speed" [ref=e40]:
                  - option "0.75×"
                  - option "1×" [selected]
                  - option "1.25×"
                  - option "1.5×"
                  - option "2×"
              - generic [ref=e41]:
                - text: Volume
                - slider "Volume" [ref=e42]: "1"
              - generic [ref=e43]: 0:00 / −4:02
            - generic [ref=e44]:
              - button "Bookmark position" [ref=e45] [cursor=pointer]
              - button "Jump to bookmark" [ref=e46] [cursor=pointer]
              - generic [ref=e47]:
                - text: Sleep timer
                - combobox "Sleep timer" [ref=e48]:
                  - option "Off" [selected]
                  - option "5 min"
                  - option "15 min"
                  - option "30 min"
              - link "Download audio" [ref=e49] [cursor=pointer]:
                - /url: /api/v1/stories/001/assets/narration.mp3
            - paragraph [ref=e50]: "Keyboard: Space play/pause · ← −15s · → +15s. Progress resumes on this device."
          - region "Mini audio player" [ref=e51]:
            - button "Play" [ref=e52] [cursor=pointer]: ▶
            - generic [ref=e53]: The Earth Prays for Krishna to Come
            - button "Back 15 seconds" [ref=e54] [cursor=pointer]: −15
            - progressbar [ref=e55] [cursor=pointer]
            - button "Forward 15 seconds" [ref=e56] [cursor=pointer]: "+15"
            - generic [ref=e57]: 0:00 / 4:02
          - navigation "Story navigation" [ref=e58]:
            - link "Story 002 →" [ref=e59] [cursor=pointer]:
              - /url: /stories/002
          - generic [ref=e60]:
            - tablist [ref=e61]:
              - tab "Listen" [selected] [ref=e62] [cursor=pointer]
              - tab "Read" [ref=e63] [cursor=pointer]
              - tab "Activities" [ref=e64] [cursor=pointer]
              - tab "Coloring" [ref=e65] [cursor=pointer]
              - tab "Source" [ref=e66] [cursor=pointer]
              - tab "Notes" [ref=e67] [cursor=pointer]
              - tab "Ślokās" [ref=e68] [cursor=pointer]
            - tabpanel [ref=e69]:
              - generic [ref=e71]:
                - heading "Listen & read along" [level=2] [ref=e72]
                - paragraph [ref=e73]: Follow-along cues pending review
                - article [ref=e74]:
                  - paragraph [ref=e75]: Hare Kṛṣṇa, dear children and families!
                  - heading "📿 Krishna Book Bedtime" [level=1] [ref=e76]
                  - heading "Story 001 — The Earth Prays for Krishna to Come" [level=2] [ref=e77]
                  - heading "Scriptural Source" [level=3] [ref=e78]
                  - text: Krishna Book Chapter 1 Opening through Brahmā receiving the Lord's message Śrīmad-Bhāgavatam Tenth Canto, early Chapter 1 summary
                  - heading "Recap" [level=2] [ref=e79]
                  - text: Welcome to our Krishna Book Bedtime series. Night by night we will walk gently through the pastimes of Lord Kṛṣṇa as told in Śrīla Prabhupāda's Krishna Book. Tonight begins at the very start of the sequence, when Mother Earth feels a heavy burden and seeks heavenly help. Settle in with a calm heart as hope begins to rise across the worlds.
                  - heading "Main Story" [level=2] [ref=e80]
                  - text: Long ago, the beautiful earth felt heavy with sorrow. Cruel kings and proud rulers troubled villages, forests, and gentle creatures everywhere. People struggled under harsh commands, and even kind hearts wondered who could bring true relief.
                  - paragraph [ref=e81]: When the world is distressed, the kind Lord always hears those who care. Mother Earth loved every being who lived upon her—animals, people, birds, and trees. She could not bear their suffering any longer.
                  - paragraph [ref=e82]: So she sought help in a way that would move the wise. With her gentle spirit, she took the form of a beautiful cow. Her soft coat shone quietly in the light.
                  - paragraph [ref=e83]: Her deep eyes carried the weight of many prayers. In that cow form she left her earthly home and journeyed toward the heavenly planets. She passed forests, misty mountains, and shining rivers along the way.
                  - paragraph [ref=e84]: Villagers did not know the cow was Mother Earth herself. Yet many felt comforted as she walked by. Soft hoofbeats marked her path, and tears sparkled like dew upon her cheeks.
                  - paragraph [ref=e85]: At last she reached the abode of Lord Brahmā, the grandfather of living beings. Brahmā sat upon a brilliant lotus, serene yet serious as he saw the sadness in the cow's eyes. Nearby stood Lord Śiva, whose concern mirrored the earth's pain.
                  - paragraph [ref=e86]: Other demigods and sages gathered around them. The whole assembly grew silent with respect. Mother Earth bowed low before Brahmā and opened her heart.
                  - paragraph [ref=e87]: In paraphrase, she explained that evil kings had filled the world with pride and greed. She said she struggled to support so much sorrow. She asked the protector of the worlds to help her children.
                  - paragraph [ref=e88]: Lord Brahmā listened with deep compassion. He understood how Mother Earth nourished everyone without asking anything in return. Her love for living beings was clear in every trembling breath.
                  - paragraph [ref=e89]: In paraphrase, Brahmā reassured her that her suffering would not be ignored. He said they must seek help from Lord Viṣṇu, the protector of all. Then he called the demigods together for a sacred journey.
                  - paragraph [ref=e90]: Among them were the sun-god, the wind-god, the moon-god, Indra, Agni, and many others. Colorful clouds and gentle winds seemed to follow as the heavenly assembly prepared to travel. Mother Earth, still in her cow form, went with them.
                  - paragraph [ref=e91]: Hope began to rise as they moved through star-filled skies. They journeyed until they reached the shore of the Ocean of Milk, a sparkling sea beyond ordinary worlds. Soft breezes drifted over pearly waters fragrant with lotuses.
                  - paragraph [ref=e92]: The demigods knelt on the cool white sand with folded hands. Mother Earth stood close, her heart trembling between worry and longing. A holy quiet settled over the shore.
                  - paragraph [ref=e93]: Lord Brahmā led the prayer. In paraphrase, he appealed to Lord Viṣṇu for mercy on Mother Earth and on all gentle souls weighed down by cruelty. The demigods joined quietly, their devotion blending with the sound of the waves.
                  - paragraph [ref=e94]: Even the stars above seemed to pause and listen. After the prayers, a deep stillness settled over the shore. Everyone waited with hopeful hearts.
                  - paragraph [ref=e95]: Then a warm light seemed to shimmer upon the ocean. Within his heart, Lord Brahma received a reassuring message from the Lord. The message was clear and comforting.
                  - paragraph [ref=e96]: The Lord would appear on earth as the son of Vasudeva. The demigods should also take birth to assist His divine plan. Brahmā understood that the Lord would protect the devotees and relieve Earth's burden in His own perfect time.
                  - paragraph [ref=e97]: A gentle breeze swept the assembly and filled everyone with peace. The weight upon Mother Earth's heart grew lighter, as if touched by golden dawn. The demigods offered thanks for the Lord's merciful promise.
                  - paragraph [ref=e98]: Brahmā turned to Mother Earth with loving reassurance. With renewed hope, she thanked Brahmā and the demigods and began her journey home. Forest leaves seemed to wave, and rivers glimmered as she passed.
                  - paragraph [ref=e99]: Though people on earth did not yet know what had been promised, a quiet feeling of hope spread through villages and fields. Trees, animals, and children sensed that something wonderful was beginning.
                  - paragraph [ref=e100]: Mother Earth returned as the caring cow, waiting patiently for that special Child— Kṛṣṇa—to appear. She knew that whenever hearts call out with honesty and love, the Lord truly listens.
                  - paragraph [ref=e101]: And so the first chapter of hope was written across the heavens and the earth. The Lord had heard.
                  - paragraph [ref=e102]: The demigods had received their duty. Mother Earth waited with faith.
                  - heading "Devotional Meaning" [level=2] [ref=e103]
                  - text: This opening pastime teaches that sincere prayer is never wasted. Mother Earth did not fight despair alone; she sought help with humility and love for others. Lord Brahmā and the demigods show us how to carry another's burden to the Lord instead of ignoring it. The message received in Brahmā's heart reminds us that Kṛṣṇa answers in His own perfect time, often before we can see the result. When we pray with care for those who suffer, hope begins to grow even while we wait. Waiting with faith is part of devotion, not a failure of prayer. Waiting with faith is part of devotion, not a failure of prayer.
                  - heading "Five Lessons" [level=2] [ref=e104]
                  - text: 1. Sincere prayer for others reaches the Lord. 2. Humble leaders help carry the world's worries to Kṛṣṇa. 3. Hope can rise before the answer is fully seen. 4. Caring for the suffering is itself a form of devotion. 5. Trust the Lord's timing when relief feels far away.
                  - heading "Think About It" [level=2] [ref=e105]
                  - text: 1. Why did Mother Earth take the form of a cow when she sought help? 2. Where did Brahmā and the demigods go to pray for the earth? 3. How did Lord Viṣṇu's message reach Brahmā? 4. What promise did the demigods receive about the Lord's appearance? 5. When someone you care about is struggling, how can prayer and kindness help?
                  - heading "Five-Star Challenge" [level=2] [ref=e106]
                  - text: 1. Draw Mother Earth as a gentle cow standing near Brahmā's lotus seat. 2. Say a short prayer tonight for someone who needs comfort. 3. Name three living beings you are grateful the earth supports. 4. Explain to a family member what the Ocean of Milk scene teaches about hope. 5. Chant the Hare Kṛṣṇa mahā-mantra once before sleep with a calm heart.
                  - heading "Bedtime Prayer" [level=2] [ref=e107]
                  - text: "Dear Kṛṣṇa, thank You for hearing Mother Earth's prayer. Please help our family pray with hope and care for others. We chant: Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare Hare Rāma Hare Rāma Rāma Rāma Hare Hare. Good night, and may Your mercy rest gently on our hearts."
                  - heading "Next Story Preview" [level=2] [ref=e108]
                  - text: "Next time: Story 002 — The Wedding and the Heavenly Voice. In Mathurā a joyful wedding procession turns suddenly serious when a voice from the sky warns Kaṁsa about Devakī's eighth child, and Vasudeva answers with protective truthfulness."
                  - heading "Parent/Teacher Note" [level=2] [ref=e109]
                  - text: This episode follows Krishna Book Chapter 1 through Brahmā's receiving the Lord's message within the heart. Keep discussion on prayer, compassion, and patient hope. Avoid leaping ahead to the wedding or later pastimes. Invite children to notice how Mother Earth seeks help for others, and how Brahmā leads the demigods with humility rather than pride. Encourage children to name one person they can pray for tonight.
    - contentinfo [ref=e110]:
      - generic [ref=e111]:
        - generic [ref=e112]: Bhāva — stewarded with care by Svarna Gauranga Das.
        - generic [ref=e113]:
          - link "Sunday School" [ref=e114]:
            - /url: /sunday-school
          - link "For Preachers" [ref=e115]:
            - /url: /preachers
          - link "Privacy" [ref=e116]:
            - /url: /privacy
          - link "Accessibility" [ref=e117]:
            - /url: /accessibility
          - link "Source & permissions" [ref=e118]:
            - /url: /source-permissions
  - alert [ref=e119]
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
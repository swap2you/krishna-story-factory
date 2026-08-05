/**
 * Educational age-pathway cards for the Bhāva home page.
 * Sanskrit stage names are educational labels only — see
 * docs/editorial/BHAVA_AGE_PATHWAY_NAMING.md.
 */

export type AgePathway = {
  id: string;
  sanskrit: string;
  publicTitle: string;
  ageLabel: string;
  description: string;
  href: string | null;
  status: "active" | "growing";
};

export const AGE_PATHWAYS: AgePathway[] = [
  {
    id: "kaumara",
    sanskrit: "Kaumāra",
    publicTitle: "Little Listeners",
    ageLabel: "through age 5",
    description: "Gentle listening, family reading, and simple coloring.",
    href: "/library/krishna-book",
    status: "active",
  },
  {
    id: "pauganda",
    sanskrit: "Pāugaṇḍa",
    publicTitle: "Young Explorers",
    ageLabel: "ages 6–10",
    description: "Complete stories, activities, and guided discussion.",
    href: "/library/krishna-book",
    status: "active",
  },
  {
    id: "kaisora",
    sanskrit: "Kaiśora",
    publicTitle: "Teen Seekers",
    ageLabel: "ages 11–15",
    description: "Source reading, reflection, and guided philosophy.",
    href: "/knowledge",
    status: "active",
  },
  {
    id: "yauvana",
    sanskrit: "Yauvana",
    publicTitle: "Youth Sevakas",
    ageLabel: "ages 16–20",
    description: "Leadership, teaching, research, and service.",
    href: null,
    status: "growing",
  },
  {
    id: "family",
    sanskrit: "Family Path",
    publicTitle: "Families & Educators",
    ageLabel: "homes & classrooms",
    description: "Home learning, classrooms, and Sunday School support.",
    href: "/teachers",
    status: "growing",
  },
];

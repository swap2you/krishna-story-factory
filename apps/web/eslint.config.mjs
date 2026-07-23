import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat({
  baseDirectory: dirname(fileURLToPath(import.meta.url)),
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals"),
  {
    rules: {
      // Devotional copy uses apostrophes heavily; escaping harms readability.
      "react/no-unescaped-entities": "off",
    },
  },
];

export default eslintConfig;

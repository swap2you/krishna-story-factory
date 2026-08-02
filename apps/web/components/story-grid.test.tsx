import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { StoryGrid } from "./story-grid";

afterEach(() => cleanup());

describe("StoryGrid", () => {
  it("links each catalog story to its story page", () => {
    render(<StoryGrid stories={[{ story_no: "007", slug: "kamsa", title: "Kamsa Begins", age_range: "5–9" }]} />);
    expect(screen.getByRole("link", { name: /kamsa begins/i })).toHaveAttribute("href", "/stories/007");
  });

  it("shows a friendly empty state", () => {
    render(<StoryGrid stories={[]} />);
    expect(screen.getByText(/library is being prepared/i)).toBeInTheDocument();
  });

  it("shows temporary unavailability instead of operator API instructions", () => {
    render(<StoryGrid stories={[]} unavailable />);
    expect(screen.getByRole("heading", { name: /temporarily unavailable/i })).toBeInTheDocument();
    expect(screen.queryByText(/Run the Bhāva API/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/discover locked packages/i)).not.toBeInTheDocument();
  });
});

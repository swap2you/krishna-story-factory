"use client";

import { useEffect, useState } from "react";
import { Button, Tabs, Toast, useToast } from "@bhava/ui";
import type { Story } from "@/lib/catalog";

export function StoryExperience({ story, storyNo }: { story: Story | null; storyNo: string }) {
  const [large, setLarge] = useState(false);
  const [notes, setNotes] = useState("");
  const { message, showToast } = useToast();
  const key = `bhava:notes:${storyNo}`;
  useEffect(() => setNotes(localStorage.getItem(key) ?? ""), [key]);
  const title = story?.title ?? `Krishna Book story ${storyNo}`;
  const reading = story?.summary ?? "This story is waiting for its local catalog entry. When the Bhāva API is running, its reading, audio, activities, and source notes will appear here.";
  return <><Tabs tabs={["Listen", "Read", "Activities", "Coloring", "Source", "Notes", "Ślokas"]}>{(active) => <div className="story-content">
    {active === "Listen" && <><h2>Listen</h2><div className="waveform" aria-hidden="true" />{story?.narration_url ? <audio controls preload="metadata" style={{ width: "100%", marginTop: "1rem" }} src={story.narration_url}><a href={story.narration_url}>Download narration</a></audio> : <p>The catalog has not supplied a narration yet.</p>}<p>The audio player will use the catalog narration when available.</p></>}
    {active === "Read" && <><div className="actions"><Button variant="quiet" onClick={() => setLarge(!large)}> {large ? "Standard text" : "Larger text"} </Button></div><article className={`reading ${large ? "large" : ""}`}><h2>{title}</h2><p>{reading}</p></article></>}
    {active === "Activities" && <><h2>Activities</h2>{story?.activity_pdf_url ? <iframe title={`${title} activity sheet`} src={story.activity_pdf_url} width="100%" height="600" /> : <p>An activity-sheet preview will be shown here when the local catalog provides a PDF. Your browser can open PDF files directly when embedding is unavailable.</p>}</>}
    {active === "Coloring" && <><h2>Coloring pages</h2><div className="gallery">{(story?.images?.length ? story.images : ["Coloring page", "Simple coloring page"]).map((image) => <div className="image-placeholder" key={image}>{image}</div>)}</div></>}
    {active === "Source" && <><h2>Source</h2><p>{story?.source_reference ?? "Source references will be provided by the catalog after editorial review."}</p><p>{story?.scripture_reference ?? "Krishna Book sequence"}</p></>}
    {active === "Notes" && <><h2>Our family notes</h2><textarea className="notes" value={notes} placeholder="What did you notice or want to remember?" onChange={(event) => setNotes(event.target.value)} /><div className="actions"><Button onClick={() => { localStorage.setItem(key, notes); showToast("Notes saved on this device."); }}>Save notes</Button></div></>}
    {active === "Ślokas" && <><h2>Ślokas</h2><p>Selected verses and translations will appear here once they are supplied by the reviewed catalog.</p></>}
  </div>}</Tabs><Toast message={message} /></>;
}

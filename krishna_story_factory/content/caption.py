from __future__ import annotations


def format_whatsapp_caption(
    *, story_title: str, package_link: str, activity_title: str = "", recommended_send_mode: str = "SEND_NOW"
) -> str:
    link_block = f"\nPackage link:\n{package_link}\n" if package_link else "\n"
    mode = recommended_send_mode.strip().upper()
    activity_line = {
        "OPTIONAL": f"Optional family activity: {activity_title}.",
        "WEEKEND_PROJECT": f"Weekend project: {activity_title}.",
        "COLORING_ONLY": "Today's optional activity is the coloring page.",
        "PARENT_GUIDED": f"Parent-guided activity: {activity_title}.",
    }.get(mode, "The activity is ready whenever it fits your family's day.")
    return (
        "Hare Krishna dear family,\n\n"
        f"Today's Krishna Book bedtime story is ready:\n"
        f"{story_title}\n"
        f"{link_block}\n"
        f"{activity_line}\n"
        "Please read or play the story with your child when convenient.\n\n"
        "Jai Sri Krishna."
    )

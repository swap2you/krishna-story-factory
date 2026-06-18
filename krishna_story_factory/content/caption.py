from __future__ import annotations


def format_whatsapp_caption(*, story_title: str, package_link: str) -> str:
    link_block = f"\nPackage link:\n{package_link}\n" if package_link else "\n"
    return (
        "Hare Krishna dear family,\n\n"
        f"Today's Krishna Book bedtime story is ready:\n"
        f"{story_title}\n"
        f"{link_block}\n"
        "Please read or play it with your child, complete the activity sheet, "
        "and reply here with a photo, audio, or short video when done.\n\n"
        "Jai Sri Krishna."
    )

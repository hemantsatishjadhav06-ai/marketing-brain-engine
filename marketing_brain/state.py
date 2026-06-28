"""The content lifecycle state machine. The human-approval gate lives here."""
DRAFT = "Draft"
GENERATING = "Generating"
NEEDS_REVIEW = "Needs Review"
APPROVED = "Approved"          # <- set by a HUMAN in Airtable/Sheets
SCHEDULED = "Scheduled"
PUBLISHED = "Published"
REJECTED = "Rejected"

# Allowed transitions. Note: NEEDS_REVIEW -> APPROVED is NOT here because only a
# human performs it; the bots may never approve their own work.
TRANSITIONS = {
    DRAFT: {GENERATING, REJECTED},
    GENERATING: {NEEDS_REVIEW, REJECTED},
    NEEDS_REVIEW: {REJECTED},          # humans add APPROVED out-of-band
    APPROVED: {SCHEDULED, REJECTED},
    SCHEDULED: {PUBLISHED, REJECTED},
    PUBLISHED: set(),
    REJECTED: set(),
}

BOT_FORBIDDEN = {(NEEDS_REVIEW, APPROVED)}  # guard: agents can never self-approve


def can(bot_from, to, *, actor="bot"):
    if actor == "bot" and (bot_from, to) in BOT_FORBIDDEN:
        return False
    return to in TRANSITIONS.get(bot_from, set()) or (actor == "human" and to == APPROVED)

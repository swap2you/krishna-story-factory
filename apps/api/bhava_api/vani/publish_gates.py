"""Server-side rights gates for Vāṇī media."""
from __future__ import annotations

from .schemas import RightsManifest, RightsState


def stream_allowed(
    rights: RightsManifest,
    *,
    environment: str,
    public_site: bool,
) -> bool:
    """Return whether media may be streamed in the current deployment."""
    public_production = public_site and environment.strip().lower() in {"prod", "production"}
    if public_production:
        return (
            rights.state is RightsState.PUBLIC_REDISTRIBUTION_APPROVED
            and rights.public_stream_allowed
        )
    return rights.state in {
        RightsState.PRIVATE_REVIEW_ALLOWED,
        RightsState.PUBLIC_REDISTRIBUTION_APPROVED,
    }

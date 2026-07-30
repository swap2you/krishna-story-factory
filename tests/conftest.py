from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.support.tiers import TIERS, tier_status  # noqa: E402

PRODUCTION_ALLOWED_HOSTS = (
    "bhava.me",
    "www.bhava.me",
    "staging.bhava.me",
    "localhost",
    "127.0.0.1",
)

# Variables the harness itself honours. Everything else beginning with BHAVA_ is
# removed before collection so a run inherits nothing from the operator shell.
PRESERVED_ENV_PREFIXES = ("BHAVA_REQUIRE_",)


def _isolate_from_ambient_config() -> None:
    """Drop ambient BHAVA_* portal configuration so a local run matches CI.

    Operators export BHAVA_PUBLIC_SITE, BHAVA_OUTPUT_ROOT, BHAVA_E2E_MODE and
    friends while running the portal or Playwright. Inheriting those silently
    reconfigures the application under test — a shell left in public-site mode
    unmounts the local factory router and makes portal tests fail for reasons
    that have nothing to do with the code. Only the tier-requirement flags
    survive, because those are how a CI job declares what it provisioned.
    """
    for name in [key for key in os.environ if key.startswith("BHAVA_")]:
        if not name.startswith(PRESERVED_ENV_PREFIXES):
            del os.environ[name]


def _allow_test_client_host() -> None:
    """Let Starlette's TestClient ("Host: testserver") through TrustedHostMiddleware.

    The harness widens its own allow-list rather than the application relaxing
    the production default; test_public_production_boundary.py asserts the
    production default still rejects testserver.
    """
    os.environ["BHAVA_ALLOWED_HOSTS"] = ",".join((*PRODUCTION_ALLOWED_HOSTS, "testserver"))


_isolate_from_ambient_config()
_allow_test_client_host()


def pytest_runtest_setup(item: pytest.Item) -> None:
    for marker in TIERS:
        if item.get_closest_marker(marker) is None:
            continue
        problems, required, label = tier_status(marker)
        if not problems:
            continue
        detail = "; ".join(problems[:6])
        if len(problems) > 6:
            detail += f"; (+{len(problems) - 6} more)"
        if required:
            pytest.fail(
                f"Tier '{marker}' was declared as provisioned but {label} is unusable: {detail}",
                pytrace=False,
            )
        pytest.skip(f"Tier '{marker}' unavailable ({label}): {detail}")

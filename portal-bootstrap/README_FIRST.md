# Bhāva Portal Cursor Bootstrap v1

This package contains:

- enhanced interactive UX prototype;
- product and architecture blueprint;
- complete screen inventory;
- technical stack and repository architecture;
- data model and API contract;
- implementation phases;
- acceptance/test plan;
- `bhava.me` deployment plan;
- contact configuration;
- one autonomous Cursor master build prompt.

## Use

1. Copy `bhava_portal_cursor_bootstrap_v1.zip` into:

   `C:\Development\Workspace\DevotionalRepo\krishna-story-factory`

2. Open the repository in Cursor.

3. Copy the full contents of:

   `cursor/CURSOR_MASTER_BUILD_PROMPT.md`

   into Cursor.

Cursor is instructed to:
- create `feature/bhava-portal-v1`;
- keep it open;
- never merge it;
- preserve the locked factory;
- build in phases;
- run all tests;
- open and inspect the real browser;
- push the branch;
- leave Story 008 untouched.

## View the prototype

Use a static server rather than opening it as `file://` so PDF embedding and media behave consistently:

```powershell
cd .\ux-prototype
python -m http.server 8088
```

Open:

`http://localhost:8088`

# Bhāva Troubleshooting

| Symptom | Check |
| --- | --- |
| Library empty | Is API running on `127.0.0.1:8000`? Are packages under `output/00N_*`? Run `.\scripts\reindex_bhava_catalog.ps1`. |
| `next` not found / SWC errors | From repo root: delete `node_modules`, run `npm install`, then `npm install @next/swc-win32-x64-msvc`. |
| Studio actions disabled | Expected unless `BHAVA_FACTORY_ACTIONS_ENABLED=true`. |
| PDF blank in iframe | Use Open in new tab; browser PDF plugin varies. |
| Port in use | `.\scripts\stop_bhava_local.ps1` then restart. |
| Hash guard fails | Portal work must not modify Stories 001–007 packages. |
| npm EPERM/ENOTEMPTY on Windows | Stop all Node processes, remove `node_modules`, reinstall once (no parallel npm). |

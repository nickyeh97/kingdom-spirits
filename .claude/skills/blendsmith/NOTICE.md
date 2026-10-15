# blendsmith

Copyright (C) 2026 blendsmith contributors.

SPDX-License-Identifier: GPL-3.0-only

This skill is licensed under GNU GPL version 3 only. The complete license is in [LICENSE](LICENSE). It derives from the private blender-production-assets 0.1.10 workflow. Historical private model files and evidence are not part of this distribution.

## Modifications (GPL-3.0 section 5a notice)

This copy is a **modified version** of blendsmith 2026.09.011 (upstream: https://github.com/brianchenanimator/blendsmith, commit b46f037), adapted for the kingdom-spirits project. Modified on **2026-10-12** by the kingdom-spirits project. The modified version is distributed under the same GPL-3.0-only terms. The original repository notice is preserved in [UPSTREAM-NOTICE.md](UPSTREAM-NOTICE.md).

Changes:

- `SKILL.md` / `SKILL.zh-TW.md`: version `2026.09.011-ks.1`; project-profile rule; Blender version policy (no fixed 4.4); R02 rewritten as a kickoff style mode (NPR toon + outline, or PBR with four maps); R03 states UVs are required in both modes; R04 full recap only at the first execution of each new asset; R07 language scope extended to the project CLAUDE.md and art profile, with Traditional Chinese copies; R11 procedural-source delivery (scripts and verified `.blend`); new R12 game-engine handoff (Unity / Unreal).
- `references/glossary.md` / `references/glossary.zh-TW.md`: new learning glossary.
- `references/production-checklist.md`: added NPR/toon checks and engine-handoff checks.
- `references/feedback-register.md`: appended kingdom-spirits entries.
- `assets/*`: style mode, target engine and delivery fields; worklog title made tool-neutral.

`agents/openai.yaml` is retained unchanged for upstream compatibility; Claude Code ignores it.

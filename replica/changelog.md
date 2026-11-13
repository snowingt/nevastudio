# Replica Clean-Room Changelog & Evolution

## Base Clone & Transition
- Origin: Clean-room reverse-engineering and architecture refactor from upstream baseline (`Sloth`).
- Destination: Snow Studio / Apple Dark Glass Commercial Suite.
- Methodology: `replica-skill` protocol (11-step pipeline).

## Audit Log
- Eliminated legacy cloudflare worker licensing (`licencias/` and `nube/`).
- Standardized commercial skill identifiers and titles:
  - `video-documental` (Editor V1) -> Estudio de Edición Dinámica & Documental
  - `video-el-diff` -> Noticiero Vertical & Resumen de Impacto
  - `video-explicativo` -> Recorrido Visual 3D Sin Cortes
  - `reel-collage` -> Formato Sketch & Diálogo Rápido
- Installed lightweight Gumroad licensing service (`server/services/gumroad-license.ts`) with Electron `safeStorage` encryption and tier detection (`Creator`, `Marketer`, `Agency`).

# V7 render trigger

Pushing a change to this file intentionally starts the V7 workflow. The first push builds the V7 MP4, contact sheets, rights/audio ledgers and QC evidence. Generated review evidence is committed back with `[skip ci]`, so it does not trigger another rebuild.

The `2026-11-09` retry uses continuous half-second native-audio windows so the unchanged web gates are measured on real native source audio rather than long silent gaps. Generated review evidence is still committed back with `[skip ci]`.

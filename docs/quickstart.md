# Athanor operator quickstart (Spec 000)

1. Read constitution + Spec 000.
2. Fill `docs/source-manifest.md` (T7) before any harvest.
3. Local SoT: `~/.athanor/corpus/atoms.jsonl` (override with `ATHANOR_CORPUS` or `--corpus`).
4. Offline retrieve (stdlib BM25-ish, no train):

   ```bash
   pip install -e ".[dev,schema]"
   athanor retrieve "Enochian Calls" --k 3
   athanor retrieve "Emerald Tablet" --family hermetic --k 5
   # CI / no home corpus:
   ATHANOR_CORPUS=fixtures/seed/atoms.jsonl athanor retrieve "Enochian Calls" --k 2
   ```

   Output is `athanor.packet.v0` JSON. `efficacy` is always `null`. Synthesis lenses are stubbed INFERRED until HERMENEUT wiring.
5. Never expect efficacy scores; packets hard-null that field.
6. Enochian text is welcome; summon UX is not.
7. Do not commit corpus dumps or train without operator gate.

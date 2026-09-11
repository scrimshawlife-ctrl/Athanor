# Architecture — Athanor

See Spec 000 plan for normative detail: `specs/000-athanor-spine/plan.md`.

```
PD allowlist → Crawl4AI → atom JSONL (~/.athanor/corpus/)
                         → receipts
                         → lexical (+ optional embed) index
                         → athanor.packet.v0 (efficacy: null)
                         → optional encoder T0/T1 (Spark, gated)
```

Peers: Abraxas (rune identity) · Sigil-Forge (construct) · HERMENEUT (read) · Hyperlex (slang encoder sibling).

No hard import of Abraxas/Hyperlex runtimes.

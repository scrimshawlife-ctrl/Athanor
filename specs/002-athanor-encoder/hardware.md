# Hardware — encoder train

Twin Hyperlex Spec 007 honesty.

| Role | Box | Notes |
|------|-----|-------|
| T1 train | NVIDIA DGX Spark | 000 C5 / 002 C22 |
| T0 dry-run | operator local GPU allowed | must not mint athanor-structure-* |
| CI | x86, no GPU required | stub infer, E0/E5 only |
| Serve | offline local | fail-open to Spec 001 if weights missing |

If Spark is blocked, label HOLD.
Weights path: `~/.athanor/weights/`
No weight files in git.

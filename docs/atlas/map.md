# Athanor Tradition Atlas (map)

![Tradition atlas](../../assets/atlas.png)

## Continents (Wave)

```mermaid
flowchart TB
  subgraph W0[Wave 0 — Western + Enochian spine]
    hermetic[hermetic]
    alchemy_lab[alchemy_lab]
    alchemy_spirit[alchemy_spirit]
    enochian[enochian]
    goetia_catalog[goetia_catalog]
    solomonic[solomonic]
    grimoire_other[grimoire_other]
    kabbalah_pd[kabbalah_pd]
    astrology_west[astrology_west]
    tarot_history[tarot_history]
    runes_eddic[runes_eddic]
    neoplatonism[neoplatonism]
    mystery_cults[mystery_cults]
  end
  subgraph W1[Wave 1 — Mediterranean / Near East]
    egypt_magical[egypt_magical]
    mesopotamia[mesopotamia]
    hebrew_bible_magical[hebrew_bible_magical]
    islamic_occult_pd[islamic_occult_pd]
    coptic_gnostic[coptic_gnostic]
  end
  subgraph W2[Wave 2 — South / East / Americas open]
    jyotish_anchors[jyotish_anchors]
    veda_upanishad_pd[veda_upanishad_pd]
    tantra_hist_pd[tantra_hist_pd]
    iching_daoist[iching_daoist]
    buddhism_esoteric_pd[buddhism_esoteric_pd]
    shinto_onmyodo[shinto_onmyodo]
    mesoamerica[mesoamerica]
    andes_amazon[andes_amazon]
  end
  subgraph W3[Wave 3 — modern reception]
    golden_dawn_hist[golden_dawn_hist]
    theosophy_pd[theosophy_pd]
    chaos_spare_hist[chaos_spare_hist]
    folk_magic_pd[folk_magic_pd]
  end
  enochian -.->|historical reception| golden_dawn_hist
  hermetic --> neoplatonism
  egypt_magical --> hermetic
  kabbalah_pd --> goetia_catalog
```

## Lenses (every continent)

| Lens | Means | Does not mean |
|------|-------|---------------|
| Historical | Dating, transmission, editions | Fate / prophecy as fact |
| Symbolic | Structure, correspondences, mythic grammar | One true decoding |
| Operational | How historical practitioners arranged practice | Efficacy / summon results |

## Product fences

- Enochian / Goetia: **in atlas**, **out** of summon UX and authority-seal mint
- `efficacy` always null on packets

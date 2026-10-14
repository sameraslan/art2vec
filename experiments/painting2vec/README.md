# painting2vec: what the experiments found and what to build

9 October 2026. Summary of the experiments run on 8 and 9 October against the draft `src/art2vec/painting2vec/FRAMEWORK.md`, and the pipeline they point to. Each folder here has its own README with the method and every table; this file only carries the conclusions and the plan. Nothing in this folder is committed code for the library; it is experiment code and results.

Read this with one caveat in mind throughout: every choice below was made on the same 2,000 pilot paintings it is reported on, the only eyes on the contact sheets so far were a model's, and no person has judged a single list. The numbers say what to build first, not that it is good.

## 1. Results, one line each

| Question | Answer | Where |
|---|---|---|
| Does a second photograph of a painting land next to the first? | Picture block yes (99%), composition yes (97%), colour no (57%). | `exp_invariance/`, `exp_fusion/` |
| Can subject and manner be read as separate vectors from an image embedding? | No. Embeddings separate what is shown from who painted it and when, not from how it is rendered. | `exp_separation/` |
| Is a text-trained encoder needed? | No. SigLIP 2 gains 0.04 on genre over DINOv2 and brings painter, period and reputation with it. | `exp_separation/` |
| Is Contrastive Style Descriptors a manner block? | No. It is a painter-and-period model. | `exp_separation/` |
| Can colour be made photograph-proof? | No. 716 variants; anything stable no longer looks like colour. The cause is the photograph. | `exp_fusion/` |
| Does fame or the holding museum leak into the lists? | Not measurably with DINOv2. | `exp_separation/`, `exp_fusion/` |
| Does period leak? | Yes, into every learned block: 49% of a top 10 is within 50 years. Lists restricted to other eras stay coherent. | `exp_fusion/` |
| Can a model shown only the picture mark it repeatably? | Yes on fixed fields (subject kappa 0.96, scales ICC 0.94, felt ICC 0.92). Free tags do not repeat. | `describer/` |
| Do describer fields give the subject and manner split back? | Manner yes, subject partly, colour no. The two lists share 1.1 of 10 neighbours. | `exp_describer_blocks/` |
| Does the describer read the picture or remember the painting? | Unknown. It named 263 of 300 paintings unaided, so the test had no unrecognised arm. | `describer/`, `exp_describer_blocks/` |
| Where does the list of paintings come from? | Wikidata, by cleaned count of Wikipedia language editions, plus editorial lists. 8,851 works; 2,410 for a first build. | `canon/` |
| What can be shown? | Public-domain paintings with open images. In-copyright works: no image, and computing on them needs a lawyer. | `rights/` |

## 2. The pipeline to build

### Phase 1. Three blocks, all read from the image, no external service

**Canon.** The recipe in `canon/README.md`: Wikidata paintings scored by Wikipedia language editions (Commons, sister projects and four stub editions removed), plus works named by editorial lists, with a per-painter cap and series collapsed to their best-known member. First build: the 2,410-work subset, less the works with no showable image (about 80% remain). Dated snapshots; a work once in never leaves.

**Intake.** One image per painting, the holding museum's own where it publishes one, otherwise the Commons file. Crop frames and mounts automatically. Refuse greyscale and sepia files, book scans, gallery shots, detail crops and strips under 100 pixels on the short side. Record the source and licence of every file.

**Blocks.**

| Block | Recipe | Photograph test | Note |
|---|---|---|---|
| Picture | DINOv2 large with registers, class token, tiled view, L2, centre, PCA to 64, cosine | 99% | Apache 2.0, no text in training. Carries what is shown, and period. |
| Composition | 8 by 8 grid of lightness, chroma and edge energy, aspect-normalised, PCA to 128, whitened, rows scaled to unit length | 97% | No trained model. Unit rows matter: without them one painting sat in 1,723 lists. |
| Colour | Palette histograms, with the photograph's tint kept and removed | 57% | No trained model. Half weight, and labelled on the page as depending on the photograph. |

Blocks are scaled to equal total variance, as the root says. Multiple Factor Analysis scaling was tried and gives the picture block almost no say.

**Lenses.** Whole picture (picture 1, composition 1, colour 0.5; the default), Picture only, Composition, Form (composition 1.4, colour 1), and Colour. No hubness correction. Period, painter and size are filters; an "other eras" list is precomputed per painting because it is the cheapest way to deliver the root's promise of crossing a boundary in a small step.

**Export.** Per lens: ten neighbours and a map position per painting, as JSON. The map keeps only 40 to 50% of a true top 10 under the picture lenses and about 20% under Form and Composition, so the page leads with the list and treats the map as a way in.

A working page over the 2,000 pilot paintings is at `data/painting2vec/demo/` (run `python3 -m http.server 8765 --directory data/painting2vec/demo` from the repository root and open http://localhost:8765/).

### Phase 2. Blocks marked by a describer

A vision-language model is shown the picture, never the title, painter or year, and fills a fixed form. This needs an API key; it was run here through subagents at small scale.

- **Manner**, from about thirteen rendering scales and seven depth cues (abstraction, contour, finish, edge hardness, stroke direction, ornament, chiaroscuro and so on). This is the block the image embeddings could not give. Mark each painting twice and average: at 10,000 paintings the tenth neighbour is about 2 marks away and one marking is off by up to 2.9.
- **Subject**, from a checklist of visible things with counts and setting. It sits beside the picture block, not in place of it: it crosses period and handling further, but matches on items where the embedding matches on the whole scene. Add pose, action and relation fields before scaling.
- **Felt**, from 24 felt-response words. Stable, and not a re-encoding of colour. Not to be built on until it has been compared with what people report (ArtEmis, whose terms the owner must accept himself).
- **Not colour.** Describer colour is no steadier across photographs than pixel colour. Value key, temperature and contrast are usable as filters.

With these the lens set becomes Whole picture, Subject, Form (manner with composition), Colour, Feels like: the set the draft framework wanted, reached by a different road.

Two things must be shown before Phase 2 ships. That the describer's marks hold on paintings it cannot know, since it recognised almost everything in the pilot. And that people looking at the lists agree the manner lens groups by handling.

### Phase 3. Scale and reach

The full canon of 8,851; images served at full resolution from the museums that allow it (only the Art Institute of Chicago says so expressly; elsewhere, tiles cut from public-domain files and hosted by us); a proper list for non-European painting, which Wikidata cannot supply; and a decision on in-copyright works.

## 3. The two routes

**Bring your own image.** This is what the library is. `encode` on a local file gives the picture, composition and colour blocks with no network and no service, and neighbours against the shipped canon vectors. Nothing is uploaded or stored. It works today for any image, in or out of copyright, because the user supplies it.

**We run it.** The hosted map shows public-domain paintings with open images, which is about four fifths of the first build. For works in copyright the experiments close one door: tags do not get round the image. A describer still has to look at the picture to write them, and Wikidata's own "depicts" statements are about three times sparser than a describer and fewer than half name a visible thing. So the tags route is worth building for what it adds to the similarity (Phase 2), not as a way to include Picasso. Including in-copyright works at all means a vector, facts and a link out with no image, and whether that vector may be computed and published is a question for a lawyer. Until then they stay out, as the draft framework's canon rule already says.

## 4. What is not yet known

- Whether a person agrees with any of it. The first looking session is the owner with the demo page.
- Whether the choices survive a set they were not chosen on. Hold out part of the canon before the next round.
- Whether the describer reads or recalls.
- Non-European painting: 14% of the canon at best, a third of that Latin American, and chosen from a pool with almost no fame signal.
- Auto-cropping was tested on the reproduction pairs only, not on a whole gallery.
- Brushwork: nothing here read an image above 224 pixels per tile. A texture block from full-resolution tiles is untested.
- The rights analysis is background, assembled from secondary reading. It lists nine points for a lawyer.

## 5. Folders

| Folder | What |
|---|---|
| `canon/` | Sources surveyed, Wikidata measurements, the recipe, `candidates.csv` |
| `rights/` | Public domain rules, museum terms, the two routes |
| `dataset/` | The pilot set: 2,000 paintings, 274 with a second photograph, 195 version pairs |
| `features/` | Feature code and `RUNS.md` |
| `describer/` | The blind describer study, 60 paintings |
| `exp_invariance/` | Two photographs, one painting |
| `exp_separation/` | Subject against manner; leaks |
| `exp_fusion/` | Colour rescue, fusion, lenses, period, map, demo |
| `exp_describer_blocks/` | Subject and manner from describer fields, 300 paintings |

Images, vectors and the demo are under `data/painting2vec/`, which git ignores.

# film2vec experiments: plan

Written 8 October 2026. Throwaway experiment code; nothing here is library code. It answers the questions in `src/art2vec/film2vec/FRAMEWORK.md` section 9 and one new one: what should the production version, which must cover any film, be built from.

## Two versions

- **Content version.** Reads the whole film. Catalog: about 100 public-domain films (`catalog.csv`). Anyone holding a film can run it on their own copy and get a vector.
- **Production version.** Must place any film, so it reads proxies: stills, trailers, human tags, writing about the film. The experiments below measure each proxy against the content version on the films where we hold both.

## Machine limits

16 GB, shared with other sessions, about 8 GB of free disk. So: one film at a time, one model in memory at a time, video deleted once its features are cached, everything resumable per film and per stage.

## Pipeline per film (`extract.py`)

1. Download the Internet Archive file named in the catalog.
2. Cut detection (TransNetV2) on a 48x27 decode; motion energy from the same decode.
3. Look: one frame per shot (capped), DINOv2 with registers, plus colour and light statistics per frame.
4. Time: shot-length statistics, cutting rate and motion over the running time, share of speech; V-JEPA 2 on a clip per shot (capped) as an optional second pass.
5. Sound (sound films only): a text-free audio encoder over the mix in windows.
6. Words (sound films only): speech recognition, then a text embedder on the words alone.
7. Per-shot and per-window vectors cached as float16; the video is deleted.

Opening and closing credits are trimmed by a fixed margin in the first pass.

## Experiments (`analyse.py`)

| # | Question | Measure |
|---|---|---|
| 1 | Are look, time, sound and words different respects? | Rank correlation of pairwise distances between blocks; overlap of top-10 lists. |
| 2 | What does pooling keep? | Mean, mean plus spread, profile over running time: top-10 overlap and leak checks for each. |
| 3 | How much of a film is needed? | Top-10 overlap with the full version at 1 frame per shot down to 10 frames per film. |
| 4 | How far is a proxy from the film? | Rebuild neighbours from each proxy alone and compare with whole-film neighbours: N random stills, N stills chosen the way a still site would, trailer where one exists, human tags, text about the film's style, a language model given only the title. |
| 5 | Leaks | Share of top-10 with same director, lead actor, decade, country, silent or sound, colour, and source; a linear probe for each from the vector. Reported, never optimised. |
| 6 | Does it match the eye? | Contact sheets: seed film and its neighbours per block, frames only, for Samer to judge. This is the one test that counts and it needs a person. |

## Order

1. Catalog (in progress) and proxy-source research (in progress).
2. Build the pipeline and time it on one film.
3. Pilot on 12 varied films; fix what breaks; report timings.
4. Full run over the catalog, in the background, resumable.
5. Proxy arms for the same films.
6. Analysis and a results page.

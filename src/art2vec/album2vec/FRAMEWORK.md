# album2vec: the framework, applied to albums

This extends the root `FRAMEWORK.md` to one art form. It narrows the rules for albums and may not loosen them. Where this document is silent, the root applies.

Status: adopted 6 October 2026. The current state describes recmyrecord's pipeline, which album2vec is extracted from.

## 1. The work and the artefact

The work is an album: a released set of tracks under one title. The key is its RateYourMusic id.

The artefact the encoder reads today is a set of 30-second preview clips, one per chosen track, taken in a spread across the running order (first, middle, quarters), from Deezer, Apple or YouTube, four to eight clips per album. Known gaps: a clip is not the track and four clips are not the album; a quarter of sonic neighbour lists differ between four clips and all tracks. A better artefact is the full tracks, if a licensed source appears. Audio is never committed; clips are decoded in memory and only embeddings are kept.

Which release of an album is the work (original, remaster, deluxe) is answered by the canon: the release RateYourMusic lists.

## 2. canon

RateYourMusic's all-time album chart, top 10,000, exported slowly and resumably into a sheet and from there into the catalog. Rating and vote count decide membership and chart order and are not columns in any matrix. Albums that drop off the chart stay in the catalog so that order is append-only.

## 3. encode: two content blocks

**Sound.** Discogs-EffNet embeddings of each clip (1,280 dimensions), averaged over the album's clips, L2-normalised, centred, reduced to 64 dimensions by PCA fitted once and frozen, then scaled so the block's total variance matches the other blocks. Leak note: Discogs-EffNet was trained to predict Discogs genres and styles, so the sonic signature of a style is in the vector by construction; the historical and scene half of a style word is not, and is not wanted. CLAP (audio-text) was built alongside, found to read the store's encoding until a stereo MP3 round trip removed it, and set aside by ear on 5 October 2026. MusiCNN, MERT and MAEST were benchmarked and dropped.

**Words.** Decided on 6 October 2026, not yet built: a lyrics block, because nothing reads the words of a song today and for many albums the words are half the work. Source: speech recognition over the preview clips already fetched, so no lyrics are licensed or scraped. Encoder: a text embedder given the transcribed words only, never the artist, title or year. Leak note to write when chosen. Instrumental albums and albums with no audio have no words block and are placed without one, as the root's missing-block rule says.

An album with no audio has no sound block and is placed by its felt block alone. Nothing is imputed.

## 4. describe: the felt block

The source is RateYourMusic's descriptors, 176 words. The pipeline today drops the 56 lyric and theme words and keeps 120 in the distance, six of them hidden from the site (vocal type, instrumental, concept album). The 114 shown as mood words mix feelings with texture, style and setting words, so today the mood side is partly a style side.

The rule from now on: felt-response words only. The committed table `src/art2vec/album2vec/descriptors.csv` sorts all 176 words into the four kinds of the root's section 5 with a reason each, and only kind 1 enters the block. Setting words that name an atmosphere (nocturnal, wintry) are kind 1; words that name a subject (nature, urban as a theme) are kind 3. Style and movement words (progressive, psychedelic) are kind 4 and are out; the sonic half of what they mean is already in the sound block.

Weighting stays as today until the comparison below says otherwise: each word weighted by its place on the album's page, (63 minus position) divided by 42. For albums beyond the chart, the top eight words.

Albums that no crowd has described: today an LLM given artist, title and year writes their descriptors. That reads reputation, not the work, and is kind 4 in disguise. It stays as a flagged stopgap, marked predicted in the data, never applied to chart albums, and is the first thing a model that reads the audio replaces.

## 5. Two spaces, one control

Sounds like and feels like. The control is one weight between the content blocks and the felt block. recmyrecord exposes three stops, sound, balanced and mood, which today scale the descriptor block by 1 over s cubed with s at 5, 1.765 and 0.5. Neighbours are the ten nearest by Euclidean distance over the whole catalog.

## 6. Experiments to run before the rule is enforced on the site

Both are one-day experiments under recmyrecord's experiment rules, on the current store, judged on validation seeds and by ear.

1. **How much feeling does the sound carry?** Predict only the kind 1 words from the EffNet vectors with a linear probe, and compare with predicting all 120. The descriptor model experiment already shows audio weaker on mood words (0.64 against 0.81 realised precision at the same threshold); this measures it on the sorted table. If audio predicts the felt words badly, the crowd block is carrying information the sound does not have. If it predicts them well, the predicted block is close.
2. **What does cutting to felt words do to the lists?** Compare neighbour lists three ways: sound only, sound plus the 114, sound plus kind 1 only. Overlap, genre-family crossing, hubness, coverage, and a listening pass over the usual seeds with labels hidden. The question is whether the mood side produces good lists the sound side cannot.

## 7. Extraction

album2vec is pulled out of recmyrecord with no behaviour change first. For a fixed set of seed albums the ten neighbours at each stop are the same ten in the same order before and after; a float-order difference is a bug to explain, not a tolerance to grant. Then the site depends on the library instead of its own copy of the code. Only after that do the felt rule, the words block and the experiments above change what the site shows.

## 8. What ships

Vectors and metadata in a columnar store; for the site, compact JSON with ten neighbours per album per stop, a UMAP position per stop, and the album's felt words. No vectors reach the browser and the browser does no distance maths. Clip previews and lyrics transcripts are never shipped.

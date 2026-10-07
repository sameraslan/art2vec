# art2vec: the framework

Content-only similarity for art. Start from a work you love, see what sits next to it, and walk outward one small step at a time.

This document holds the rules the art2vec library and every product built on it follow; design and code answer to it. It says what the library is for, the two rules it enforces, the one exception it allows, and what is still open. System design, interfaces and code answer to it. Each medium has its own extension of this document in its folder (`album2vec/FRAMEWORK.md` is the first) that applies these rules to one art form and may not contradict them.

Status: adopted 6 October 2026 with the descriptor rule settled (section 5). Open questions are in section 11.

## 1. What it is for

A person has a work they love: an album, a painting, a film, a novel. art2vec gives them the works that are most like it in the work itself, so they can:

1. find more of what they already love, with little wasted time;
2. branch out, by following a chain of small steps into territory they would never have searched for;
3. arrive, eventually, at things they do not like today, having got there from somewhere they do.

The output is a space to explore, not a leaderboard and not a feed. The person steers. The library's job is to make every step a small, honest step in the work's own qualities, so that the person feels they found the next thing themselves.

Success: people find things they enjoy and try things they would not have. Section 7 says how we check.

Not goals: accounts, personalisation, play tracking, or anything that learns about the person. The library knows works, not people.

## 2. The two rules and the one exception

### Rule 1. Reception picks the set

Nobody can go through everything, so each medium starts from a canon: a list of works that many people, over time, have claimed to be worth the time. Crowd-sourced charts, critics' polls, combined "best of" lists. Within that set the person explores freely.

The canon is a quality filter and nothing more. Ratings, vote counts and rankings decide what is in the set and nothing else. They never decide where anything sits in it. (Where a pipeline keeps works in chart order, that order may break ties and seed a layout; it may not move a neighbour.)

### Rule 2. The work picks the neighbours

Similarity comes only from the work itself. For music, the audio and the words. For visual art, the image. For film, the frames, the cut and the sound. For literature, the text. An encoder reads the raw artefact and produces a vector; distance between vectors is distance between works.

Nothing about who liked a work, how many liked it, what shelf it was put on or what has been written about it enters the distance.

### The exception. How the work makes people feel

The purpose of all this is enjoyment, and enjoyment is a feeling. So the library allows one kind of human-sourced information alongside the content vectors, as a block of its own: descriptors of the felt response. Melancholic, tense, warm, playful, nocturnal.

This gives every work two positions. **Sounds like** (or looks like, reads like): where the work sits by what it is made of, read from the artefact. **Feels like**: where it sits by what it does to people. They are different spaces over the same works. Two albums can be equally desolate and sound nothing alike; two paintings can share every colour and leave you in opposite moods. The person moves between the two with one control, and the second space is the one along which they cross the boundaries of the first.

The test for a label: does it describe what the work does to a person? "Melancholic" passes. "Lo-fi" describes the sound and belongs to the first space, where the encoder already has it. "Underrated", "influential", "sophisticated", "progressive" and "post-punk" describe the work's standing and its place among other works, and fail. Section 5 works this out.

### Never part of a distance

- Co-occurrence: "people who liked X also liked Y".
- Ratings, popularity, vote counts, chart position.
- Genre, style, scene and movement labels, and judgements of standing.
- Era, country and artist identity. Two works by one artist should be close because they are alike, not because of the name.
- Fame that enters through the back door: models trained on text about the world (CLIP, LLMs given a title or an artist) know which works are famous and what has been said about them. Section 4 says how encoders are chosen.

Reception data has two legitimate uses besides the canon: evaluation (section 7) and labels for training a model that will later read the content alone (section 5). Neither puts it in a distance.

## 3. Why these rules

Collaborative filtering recommends what people like you already like. It is good at the first job in section 1 and bad at the other two: it keeps everyone inside the circle they started in and amplifies whatever is already popular. Genre labels are coarse, social and historical; two albums that sound alike sit in different genres because of who made them and when. Both approaches describe the audience, and the person already knows their audience.

The work itself does not care about any of that. An encoder that only hears the audio will put a 1970s Ethiopian jazz record next to a 2010s electronic one if they share a texture, a step no genre browser would offer. The recmyrecord genre-crossing report chose to let the sonic side cross genres freely rather than force lists to stay inside one.

The canon exists because content-only similarity over everything would be noise: most of what exists is not worth anyone's hour, and a space is only explorable if most of what you land on rewards the landing. Reception is the cheapest reliable signal that something is there, so it decides the set and nothing else.

## 4. What a medium is

A medium is a plugin that answers three questions about its works. The shared core does everything else.

| | Question | Where human data may appear |
|---|---|---|
| canon | Which works are in the set? | Yes. The only step that may use ratings, counts and lists. |
| encode | What is this work, as one or more content vectors, from its raw artefact? | No. |
| describe | How does this work make people feel, as a vector? | Yes: directly from a crowd today, or as labels for a model that then reads the work (section 5). |

A medium may return more than one content block from `encode` (for an album, the sound and the words). It returns exactly one felt block from `describe`.

Each medium also states what "the raw artefact" is, because that is a real choice. A 30-second preview clip per track is not the album; a thumbnail is not the painting; a trailer is not the film. The medium names the artefact it actually reads, its known gaps, and what a better artefact would be.

Planned media, as a sketch and not a commitment:

| Medium | Canon | Raw artefact | Content blocks | Felt-response source |
|---|---|---|---|---|
| Album | RateYourMusic all-time chart, top 10,000 | 30-second preview clips for a spread of tracks; full tracks if a licensed source appears | Sound (audio encoder); words (lyrics encoder, from speech recognition on the clips) | RYM descriptors, felt-response words only |
| Visual art | Wikidata paintings by sitelink count, museum highlights | The image at working resolution | Image (DINOv2 or DINOv3); colour and texture statistics | ArtEmis emotion distributions |
| Film | RYM film charts, TSPDT lists | Keyframes, clips, shot-length and colour over time, the soundtrack | Frames (DINO), motion (V-JEPA 2 or InternVideo), sound (the album encoder) | RYM film descriptors, felt-response words only |
| Literature | thegreatestbooks.org | Full text where public domain, extracted features where not | Style embeddings (StyleDistance, LUAR), emotional arcs, pacing statistics | StoryGraph moods; LLM tags on anonymised excerpts |

Every encoder has seen something besides the work. Encoders trained against text (CLIP, CLAP, any captioning model) have read what the world says about works. Encoders trained on labels (Discogs-EffNet was trained to predict Discogs genres and styles) have been taught the map we leave out. The rule for choosing one: prefer encoders trained without text or labels, and decide between candidates by ear or by eye. An encoder that saw text or labels is allowed with a leak note (what it saw) and the leak checks of section 7. The recmyrecord audio work benchmarked several self-supervised audio models, found CLAP reading a store's encoding, and in the end chose Discogs-EffNet over CLAP by listening; every medium ends the same way, with someone looking or listening.

## 5. The felt block

This is the one place the rules bend, so it has the most care. The question was which human-written labels may join the content vectors in a distance. The answer, settled on 6 October 2026: only those that describe the felt response.

### Four kinds of label

Sort any descriptor by the question it answers.

1. **What does the work do to you?** Felt response. Melancholic, anxious, warm, playful, hypnotic, uplifting. Setting words belong here too when they name an atmosphere the work puts you in (nocturnal, wintry) rather than a subject it depicts.
2. **What is it made of, how does it sound or look?** Texture. Lo-fi, dense, acoustic, orchestral, repetitive, minimal, noisy.
3. **What is it about?** Subject. Death, love, political, nature, religious.
4. **Where does it sit, and who is it for?** Position. Genre, style and movement words (progressive, psychedelic), era, scene, and judgements of standing (sophisticated, technical, underrated, cult).

Kind 1 is the felt block. Kinds 2 and 3 are content and belong to the content blocks: texture is in the artefact and the encoder already reads it; subject is in the words or the picture, and where nothing reads it yet the answer is a content block that does, not a crowd. Kind 4 is the map the library leaves out.

### Why keep a felt block at all

A fair objection: the encoder hears the sound, and the sound carries mood, so why ask people? Three answers.

- The evidence says the artefact carries part of the feeling, not all. In the recmyrecord descriptor model experiment an audio probe reached 0.66 capped precision@10 against a 0.44 baseline over all descriptors, and it was weakest on the felt words: at the threshold meant to give 0.9 precision it realised 0.81 over all words and 0.64 over the mood words. The literature the report cites agrees that listening and crowd signals beat audio for album moods. The crowd is measuring something the sound does not contain.
- Even where the artefact carries feeling, it carries it buried under texture. The content space is organised by what things are made of first. A felt block is a second geometry over the same works, organised by effect, and it is the dimension along which a person crosses the boundaries of the first. It is the branching-out mechanism, not decoration.
- If a model one day reads feeling from the artefact well, the block does not become redundant. A learned projection onto a feeling vocabulary keeps what matters for feeling and discards texture. Both spaces then come from the work, and the control becomes "sounds like" against "feels like" with no crowd in the loop. That is the end state.

### What a medium must do

- Sort its descriptor source into the four kinds in a committed table (word, kind, one line of reason), and use kind 1 only. The table is reviewed and changed in pull requests like code.
- Report coverage: crowd descriptors favour famous works, so say how many works have how many felt words.
- Keep the felt vocabulary and weighting stable, so that a predicted felt block can be compared with the crowd block list for list.
- Where a model writes descriptors for works no crowd has described, give it the artefact and never the title, the artist or the year. A model that knows the name reads reputation, which is kind 4 in disguise. Mark predicted descriptors as predicted.

## 6. The shared core

The medium plugins stop at vectors. Everything from there on is common and medium-blind:

- **Blocks, one distance.** A work is one or more content blocks and one felt block. Each block is scaled to the same total variance before weights are applied, and one weight, which the person controls, sets how much the felt block counts against the content. recmyrecord's "sound" and "mood" sides are this weight at its two ends. The weight's default, its curve and any reduction of a block's dimensions are the medium's choice and are recorded with its vectors.
- **Missing blocks.** A work missing a block (an album with no audio, an instrumental album with no words) is placed only where it has data and never given an imputed block. Its lists say so.
- **Neighbours.** Nearest neighbours in the combined space, with filters the person may apply that never alter distances (era, length, "not this artist again").
- **Paths.** A chain of small steps from one work to another, so the person can walk from where they are to somewhere they have never been. Paths serve purposes 2 and 3 of section 1.
- **Maps.** A two-dimensional projection for a visual surface, with the understanding that any projection distorts and the neighbour list is the truth.
- **Export.** Vectors and metadata in a plain columnar format, and precomputed neighbour lists and map positions in compact JSON for a site that does no distance maths in the browser.
- **Cross-medium alignment**, later: anchors that exist in the works themselves (a soundtrack ties a film to an album, cover art ties an album to a painting, an adaptation ties a book to a film), plus a small shared felt vocabulary that each medium's own list maps onto. Anchors are declared by the two media they join and the alignment lives in the core. No anchor comes from co-consumption.

How any of this is built is in `ARCHITECTURE.md`.

## 7. How we know it works

The rules keep human data out of the distances. They do not keep it out of the evaluation; that is where it belongs.

- **Leak checks.** Genre make-up of neighbour lists, store or source make-up and probes, artist repeats, hubness. These catch leaks (a model reading the encoding rather than the music) and are never optimised for.
- **Listening and looking sessions.** Fixed seed sets, lists side by side with the labels hidden, and odd-one-out judgements collected from people and compared with the embedding's geometry. A library whose space nobody can hear is wrong, whatever the proxy says.
- **Path tests.** Does a path cross a boundary the person would not have crossed, while every step stays small? Count steps, count crossings, and ask the person at the end whether they would have found the destination alone. What counts as a small step is a number the system design has to set.
- **Held-out data is spent once.** Reports say which splits were scored and new ideas are judged on fresh ones.

## 8. Data, rights and respect

- Ship code and scripts. Never ship copyrighted media, and never commit audio, images or text that are not ours to redistribute.
- Ship vectors and metadata only where the source's terms allow it, and say which source and which terms.
- Do not fetch a site at runtime that does not want to be fetched. Canons come from exports, published lists and licensed snapshots, gathered slowly and resumably.
- Note the licence of every encoder and every artefact source before shipping anything built on it.
- No secrets in the repository; keys and data paths come from the environment.

## 9. What the library has to be

Principles the system design must honour. Not the design itself.

- **Modular.** One medium is one package that implements the three questions and nothing else. Adding a medium touches no other medium; the core changes only when a new shared capability is needed, never for one medium's convenience.
- **Small surface.** A newcomer should read the three questions, run one example end to end, and understand the whole shape in an afternoon.
- **Reproducible.** Same inputs, same vectors. Encoders are pinned; every stored vector says which encoder, which artefact and which version of the medium made it. A medium that changes its encoder or its descriptor table changes its version, and old vectors are not mixed with new.
- **Honest about leaks.** Every encoder and every descriptor source carries a note about what human or textual data it saw and what that may let in.
- **Installable.** A plain `pip install art2vec`, with media as optional extras so a user who only wants books does not download an audio model.
- **Offline after fetch.** Artefacts are fetched once, cached, and everything after runs without network.
- **Gentle on the machine.** Heavy jobs are resumable and run one at a time; the laptop that builds this has 16 GB.

## 10. Left to the system design

Questions a reader will rightly ask that this document does not answer, because they are design and not principle. `ARCHITECTURE.md` answers each one and points back here.

- Versioning of the document, of a medium, of vectors; what counts as a breaking change.
- Which version of a work is the artefact (remaster, director's cut, translation) and how a canon is refreshed without reordering what exists.
- The default felt weight and its curve; whether a block is reduced in dimension and how.
- The evaluation protocol in enough detail to repeat it: seed sets, listeners, labels hidden or shown, what a small step is in numbers, and how listening-session data is stored and with whose consent.
- How a new medium is accepted: a leak note template, the committed descriptor table, the regression set.
- A glossary (canon, artefact, block, stop, leak, path).

## 11. Open questions

Each with a recommendation.

1. **Text- and label-trained encoders.** Ban them, or allow them with a measured leak? Recommend allow with measurement, since the alternative removes the strongest encoders in several media, and the leak checks in section 7 are cheap.
2. **Artist identity.** Should the library ever use it, even as a filter? Recommend yes as a filter the person can switch on ("not this artist again"), never in a distance.
3. **Licence.** Code licence for the library (MIT or Apache 2.0; recommend Apache 2.0 for the patent clause) and a separate statement for any shipped vectors.

Decided on 6 October 2026: the felt block is kind 1 only (section 5); words are a content block for music (`album2vec/FRAMEWORK.md`); this repository is where the library and this document live.

## 12. Changing this document

This is a living document and the only place the rules are written down. Change it in a pull request that explains the reason, update the status line, and make the code follow. A medium's extension may narrow these rules for its art form and may not loosen them. If a shortcut in the code disagrees with this document, the document wins until the document is changed.

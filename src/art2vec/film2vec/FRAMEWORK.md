# film2vec: the framework, applied to films

This extends the root `FRAMEWORK.md` to one art form. It narrows the rules for films and may not loosen them. Where this document is silent, the root applies.

Status: draft of 8 October 2026, not adopted. Nothing is built. Section 2 is the feasibility verdict and should be read first. Section 12 lists what this draft asks the root and the architecture to change.

## 1. The work and the artefact

The work is a film: the released picture and sound, over its whole running time. A film is made of pictures, of time (how long each picture is held and how things move), of sound and of words, all at once, and the work is all of them together.

The artefact the encoder should read is therefore the whole film, in one named version: the cut the canon lists, in its original aspect ratio, with its original-language sound. A director's cut with different footage is a different version and is not the work unless the canon says so. A restoration, a new grade or a new transfer is the same work seen through a different copy, and the difference between copies is noise the encoders must tolerate, not a property of the film. A score written later for a silent film is not that film's sound.

Everything else people commonly have in place of a film is one of three things, and this document keeps them apart:

| | What it is | May it stand in for the film? |
|---|---|---|
| A sample | A piece of the film itself: a clip of a real scene, a frame. | For the picture, yes, labelled as a sample. A frame has no time and no sound; a clip has the cut and the sound of one scene and nothing of the film's shape. |
| A paratext | A separate work made from the film's material to sell it: a trailer, a poster. | Its frames are samples of the picture. Its cut and its music are the trailer's, not the film's, and never enter a time or sound block. |
| Another work | A screenplay, a plot summary, a review. | No. A screenplay is a plan and often differs from the release. A summary is someone else's account. |

Subtitles are a transcript of the film's words and count as the film's words, with losses (they shorten speech and say nothing of delivery). A translated subtitle is someone else's text.

Every stored vector says which of these it was read from. Vectors read from the whole film and vectors read from samples are never mixed in one space, and a map built from samples is called that wherever it is shown.

## 2. Can this be done? The plain answer

Not for a canon, not today, not by one unaffiliated person with a clear legal footing. For a slice of films, yes.

**What blocks it is access, not method.** Reading a whole film means holding a copy of it.

- Films in the US public domain can be held freely: everything published up to 1930, and a small number of later American films whose copyright lapsed. A first estimate, not yet counted, is 7 to 9 percent of a 1,000-film canon. Nearly all of them are silent, so they have no sound or dialogue of their own. Foreign films after 1930 that circulate as "public domain" mostly are not.
- For a film in copyright, analysing a lawfully held copy and keeping only vectors stands on good fair-use ground. Getting the copy is the problem. Ripping a disc one owns breaks its copy protection, which is unlawful in the US whatever the purpose, and the research exemption that allows it covers researchers at universities using the university's copies. It does not cover an individual.
- Official free uploads (some national archives and studios put whole films on YouTube) can be reached, against the site's terms. album2vec already accepts that same footing for audio. It adds perhaps another 5 to 10 percent, unverified.
- For the remaining four fifths there is no clean route to the whole film without a university partner.

**The method is feasible but unproven.** Encoders trained without text exist for picture, motion and sound, and they run on the laptop: a rough estimate is a quarter of an hour to an hour and a half per film. What nobody has published is evidence that such encoders, pooled over two hours, give film-to-film similarity a person agrees with. Every existing evaluation scores against ratings, genres or directors, which are what this library leaves out. The first build is an experiment, and we will have to make our own test of it.

**One strand is not readable yet.** Story, meaning what happens, in what order and among whom, cannot be read from a whole film reliably by any model today. film2vec does not have a story block and says so.

**What follows from this.** film2vec proper is built on whole films, starting with the public-domain slice, and is written so that anyone who lawfully holds a film can run it on their own copy. A map of the wider canon can only be built from samples and paratexts today. That is a different and weaker thing; if it is built it carries its own name and its own label, and section 9 says how we measure how much weaker.

## 3. canon

Not chosen in this draft; it belongs to the data stage. The candidates are They Shoot Pictures, Don't They and the Sight and Sound poll (critics' lists), and the RateYourMusic film chart (a crowd). The work's key should be its Wikidata id, which is free to use and joins every other source.

As the root says, the list decides membership and nothing else. Because of section 2, the first catalog is the canon cut down to the films we can read whole, and it will lean heavily towards films made before 1931. The catalog says so on its face.

## 4. One similarity or several

Several. "These two films are alike" means nothing until one says in what respect: they look alike, they are cut alike, they sound alike, they talk alike. Two films can share every colour and move at opposite speeds. So film2vec keeps the strands as separate content blocks and lets the person choose which respects count. Any single combined distance is one named weighting among others, and is presented as that.

A caution to keep in view: the strands are not truly separate. The same footage is a different scene under different music, and no block sees that. Splitting is a simplification we accept.

## 5. encode: four content blocks

Each block is read per shot, and the per-shot vectors are cached. How two hours of shots become one vector for the film (a mean, a mean with its spread, a profile over the running time) is an open experiment, not a settled choice. Opening and closing credits are cut before encoding, since they spell out the title and the names.

**Look.** What is in the frame and how it is lit and coloured: composition, setting, colour, light, how close the camera stands. Read by an image encoder trained without text on one frame per shot, together with plain colour and light statistics kept coarse enough to survive a change of transfer. Known gap: such encoders see what is on screen more readily than how it was photographed, and nobody has tested them on cinematography.

**Time.** How the film moves: the distribution of shot lengths (its median and spread, not its average), how the cutting rate changes over the running time, how much moves within the shot, and a video encoder trained without text on a short clip per shot, which carries camera movement. This is the block no still image can supply.

**Sound.** Music, effects, ambience, silence, and voices as sound. Read by an audio encoder trained without text, on the whole mix or on the mix split into dialogue, music and effects. A silent film has no sound block and is placed without one.

**Words.** What is said. Source: speech recognition over the film's own sound, as album2vec does for lyrics, so no subtitles are licensed or scraped. Encoder: a text embedder given the words only. A film with little or no speech has no words block; it is not given an empty one that would make all quiet films neighbours. How much of the running time is speech is a number in the time block.

Performance has no block of its own. What an actor does with face, body and voice is in the look, time and sound blocks. Who the actor is must not be (section 7).

Not a block: story. Which encoders, at which settings, is decided by looking and listening, as the root requires, and recorded with leak notes when chosen.

## 6. describe: the felt block

The source is not settled. The root's sketch names RateYourMusic film descriptors; whether RateYourMusic has a mood vocabulary for films, as it does for albums, is unconfirmed. The one open, documented source found so far is the MovieLens Tag Genome (2021): about a thousand tags scored over fewer than ten thousand films, licensed for non-commercial use, leaning towards popular English-language films, with perhaps a tenth of its tags naming a feeling. Letterboxd's terms rule out this use. A first build may ship with content blocks only, and say so.

The four kinds apply as in the root, with one point particular to film: many film genres are named after feelings. The feeling passes and the shelf fails. "Frightening" and "funny" say what the film does to a person and are kind 1; "horror" and "comedy" say where it is filed and are kind 4. Rulings on the hard words:

- Kind 1: melancholic, tense, unsettling, bleak, dreamlike, atmospheric, bittersweet, feel-good, frightening, funny.
- Kind 2, already in the content blocks: slow, dialogue-heavy, handheld, black-and-white, long takes, non-linear.
- Kind 3: revenge, grief, war, coming of age.
- Kind 4: noir, New Wave, cult, Oscar winner, overrated, and words of praise or blame for the film as a made thing (beautiful, boring, thought-provoking).

What the film does can be read from the film only in part. Models predict how exciting a scene is with modest success and whether it is pleasant with less, and nobody has shown a whole film's mood words predicted from its content. So the block comes from people, as the root allows.

## 7. Labels and leaks

Genre, director, movement, country, decade and cast are other people's sorting of films, or facts about who made them. None enters a distance. Each label bundles two things: traits one can see and hear (low-key light, a voice-over, long takes) and an act of grouping by critics, studios and history. The encoders read the first from the film. The second is the map the library leaves out. If the blocks are any good, films that share a label will often land together; that is a check and never a target.

Content-only is a discipline about what goes into a distance. It is not a claim that anyone watches a film free of categories.

The ways the map can come back in by another door, each to be measured on every block and never optimised:

- **The star.** Image encoders carry faces weakly and speech encoders carry the speaker strongly, so two films can become neighbours because one actor is in both. Checked with same-actor pairs against different-actor pairs; removed by masking faces and by taking the speaker out of the voice features.
- **The copy.** A worn public-domain print and a studio restoration differ in ways that are not the film. A probe that can tell the source or the transfer from the vector has found a leak.
- **The era.** Black and white, a narrow frame and optical sound are what a film is made of, and they also date it. They stay, and the share of same-decade neighbours is reported.
- **The language.** A voice encoder hears which language is spoken, which is part of the sound and also a country label. Reported.
- **The name.** A text model recognises a famous film from its lines even with the names removed. Any text model is given the words only, and is asked to name the film as a test; a film it names is flagged.
- Same-director share and the genre make-up of neighbour lists, as for albums.

## 8. Spaces and controls

Four content blocks and a felt block. The person chooses which respects count, through a small number of named stops, each a fixed set of block weights with its neighbour lists computed in advance: looks like, moves like, sounds like, the three together, and feels like. Free sliders are not offered at first; a handful of stops is enough to show that the respects differ, and the site does no distance arithmetic.

A film missing a block is placed where it has data and its lists say so. For the first catalog that is most films: a silent has look and time only.

## 9. Experiments before anything is called a result

1. **Does any of it match what people see?** Fixed seed films, neighbour lists per stop shown side by side with titles hidden and a short excerpt of each film, judged by eye and ear. No benchmark exists for this; ours is the first test.
2. **What does pooling keep?** Mean, mean with spread, and a profile over the running time, compared on the cached shot vectors.
3. **How much of a film is needed?** One frame per shot against fewer; a clip per shot against a few hundred.
4. **How far is a sample from the film?** On the films we hold whole, build the look block again from stills and clips alone, and from the trailer alone, and compare the neighbour lists with the whole-film lists. This number decides whether a map of the wider canon from samples is worth building, and it is printed on any such map.
5. **The leak checks of section 7.**

## 10. What ships

Code, and for the catalog one vector per film per block, its neighbour lists per stop and its map positions. Vectors per frame or per shot are never published; a dense run of them can be turned back into pictures. No frames, audio, transcripts or subtitles are committed or shipped. Pictures drawn from measurements (a strip of the film's colours over time, a plot of its shot lengths) are ours to show.

## 11. Open questions

1. The canon, and how many of its films are in the public domain: counted, not estimated.
2. The felt source, starting with what RateYourMusic actually holds for films.
3. Whether to seek a university partner, which is the only clean way to the other four fifths.
4. Whether to accept official free uploads on the footing album2vec already accepts.
5. Intertitles as the words of a silent film.
6. Whether the words are embedded in the original language or in translation.

## 12. What this asks of the root and the architecture

- The root's table of planned media gives film's felt source as RateYourMusic descriptors and its sound encoder as the album encoder. Both are unconfirmed for film; the row should say so.
- The core has one weight, between content and felt. Stops that weight content blocks against each other are a new shared capability, useful to albums as well (sound against words), and belong in the core, not in this medium.
- A vector's manifest should record the artefact it was read from (whole film, sample, paratext), and the core should refuse to fuse across them as it refuses mixed versions.

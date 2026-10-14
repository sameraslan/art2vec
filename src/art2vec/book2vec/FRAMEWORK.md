# book2vec: the framework, applied to books

This extends the root `FRAMEWORK.md` to one art form. It narrows the rules for books and may not loosen them. Where this document is silent, the root applies.

Status: philosophy agreed 8 October 2026. The canon, the text sources and every encoder are undecided until the experiments in section 11 have run; nothing here is built.

## 1. The work and the artefact

The work is a novel or a novella. Version 1 stops there. Poems, plays, story collections and non-fiction are books too, and they wait: a lyric poem has no plot and no narrator in the sense used below, so two of the four blocks would be undefined for it, which is different from being zero. When those forms arrive they arrive with absent blocks, as the root's missing-block rule says, and not with invented ones.

The artefact is one named English text of the work, complete, in reading order: the author's text for a book written in English, one named translation for a book that was not. The edition, the translator and the translation's year are recorded with the vectors. Editors' introductions, notes, publishers' matter and anything else the author or translator did not write are removed before anything reads the text. Chapter titles and epigraphs stay; they are the work.

Everything is read in English. There is no validated way to compare prose style across languages, and a reader on an English site meets these books in English.

Known gap: full text is only free to use for works out of copyright, so the set leans before about 1930 and its translations lean older still. Section 10 says what follows from that.

## 2. canon

Undecided. Reception picks the set, as in the root, and the list must be one we are allowed to use. The candidates and the recommendation are in `experiments/book2vec/`.

## 3. Alike in which respect

Two books are not simply alike. They are alike in how the sentences are written, or in how the story is told, or in what happens, or in where it happens and what it is about, and these come apart: a retelling shares a story with its source and none of its prose; two novels by one author share a prose and often nothing else. Philosophy has no argument for one true similarity (Goodman: similarity means nothing until the respect is named), and the best published models agree with readers about "overall" similarity of long fiction only weakly. So book2vec does not offer one. It keeps four content blocks apart and lets the person choose between them.

| Block | The question it answers | How it is read | What it is |
|---|---|---|---|
| Prose | How are the sentences written? | Measured from sampled passages: function words, syntax, rhythm, a style encoder | A measurement |
| Telling | How is the story told? | Counted over the whole text: who narrates and in what tense, how much is speech, how fast time passes, how the mood moves from start to end | A count |
| Story | What happens, to what kinds of people, and how does it end? | Reconstructed by a reader that goes through the whole book in order, with the names taken out | A reading |
| World | Where and when is it set, and what is it about? | Passages across the whole book, with the names taken out | Between the two |

**Confidence falls with distance from the page.** Only the words are observed. Prose is measured on them and Telling is counted from them. Story is a paraphrase made by a reader, and a paraphrase is not the work; the block is kept because "what happens" is a respect people care about, and it is labelled as a reading wherever it is shown. A product built on book2vec says which kind of evidence stands behind each neighbour.

The blocks are distinguishable, not independent. A narrator's voice is both prose and telling; a setting shapes a plot. How much one block predicts another is measured (section 9) and reported, not assumed away.

## 4. The reader must not know the book

The root warns about fame that comes in through the back door. For books it is the front door: every text model has read the famous novels and what has been written about them, and will recognise *Moby-Dick* from a paragraph. Rules:

- No model is given the title, the author, the year, the translator or any label. It is given text.
- Before anything reads for Story or World, names of people and invented places are replaced with stand-ins that are consistent within the book. This also makes the comparison better and not only cleaner: models left with the names match books on the names.
- Where a count or a small encoder can do the job, it does the job. A language model is a reader only where reading is needed, which is Story and the felt block.
- A language model reads in pieces, in order, and builds its account upward from them. Single-pass reading of a whole novel is unreliable at this length and gives recall the most room.
- Recognition is measured: how often the reader can name the book from what it was given, and how the account it writes from the text compares with one it writes from the title alone. Both numbers are in the leak note.

A language model reader is allowed, on these terms. Without one there is no Story block.

## 5. describe: the felt block

For an album the feeling had to come from a crowd, because no encoder reads it well from the sound. A book is different in kind: its feeling is made of the same words the other blocks read, and a reader can be asked for it directly. So for books the root's end state is the starting point. The felt block is read from the work, with no crowd in the loop.

It is a fixed vocabulary of what the book does to the person reading it and the atmosphere it puts them in: bleak, tense, warm, funny, eerie, dreamlike, melancholy, serene, claustrophobic. A reader scores passages from across the book against that vocabulary, names removed, and the scores are pooled. The vocabulary is a committed table sorted into the root's four kinds, and only kind 1 is used. "Dreamlike" and "surreal" pass, as disorientation felt by the reader. "Gothic", "experimental" and "literary" name a shelf or a standing and fail. "Wartime" is a subject and belongs to World.

This block draws on the same text as Prose and World, and that is the point of it. Those blocks are organised by what the book is made of; this one is organised by effect. Two novels can share a dread and share no sentence habit and no setting, and the felt block is where they meet.

Every felt vector is marked predicted. Reader-sourced mood tags, if a source can be used under its terms, validate the block and never enter it.

## 6. The controls

One control runs between the content blocks, from *written like* (Prose, then Telling) to *happens like* (Story, then World). A second, the root's, runs between content and felt. Each block is scaled to the same total variance first. The default positions are a convention recorded with the vectors and claim nothing about what similarity really is. Whether the first control is one slider or four weights is a question for the map.

## 7. Translation

Is the translation the work? For the story, yes. For the prose, no. Because the blocks are separate, book2vec does not have to pick.

- Story, World and most of Telling belong to the work and should survive translation.
- Prose belongs to the author and the translator together. It is shown as the prose of this translation, with the translator named. Published stylometry finds that translations still group by original author before translator, so the block is not meaningless across translations; it is a joint signature.
- Two translations of one novel are the sharpest test the medium has: Story and World should barely move and Prose should move. Section 9.
- A public-domain translation is an old one. Garnett's Dostoevsky is Edwardian English, and its Prose neighbours will show it.

## 8. Genre, period and the author's name

None enters a distance, in either direction.

- **Genre** is a judgement made by publishers, critics and readers. It is not an input and not a block. Books of a genre will still gather, because much of what a genre is can be read off the text; that is the text talking and is welcome. Labels are used to check for leaks and as a filter the person may apply.
- **Period.** The year is not an input. The period is in the prose all the same, since English changes, and book2vec leaves it there. Subtracting the year from Prose would be using the label to move a neighbour, and an 1850 novel does read like 1850. Era is a filter.
- **Author.** Two books by one author are near each other when they are alike, and the name is never given to an encoder. "Not this author again" is a filter.

## 9. How we know it works

Each block has a test it should pass and tests it should fail. Every block is run on every test and the whole table is reported.

| Pair | Prose | Telling | Story | World |
|---|---|---|---|---|
| Two halves of one book | near | near | (not defined) | near |
| Two translations of one novel | apart | near | near | near |
| Two novels by one author, unrelated plots | near | | apart | |
| Two books of one series | near | near | | near |
| A retelling and its source | apart | | near | |

Then the checks the root requires: genre, period and author make-up of neighbour lists, hubness, book length (long and short books must not separate for that reason alone), and the recognition numbers of section 4. Then people: neighbour lists side by side with titles hidden, and odd-one-out judgements. Published reader-similarity sets are used here and nowhere else.

## 10. Rights

- Texts are fetched once from sources that allow it, cached outside the repository, and never committed or shipped.
- For a public-domain text, vectors, curves and short quoted passages may ship. The passage that shows why two books sit together comes from here.
- For a book in copyright the root allows "extracted features where full text is not available". What that can honestly support is narrower than four blocks, and a book placed on less evidence says so. The detail is in `experiments/book2vec/`.

## 11. Before anything is built

Experiments on a small designed set of public-domain novels, reported in `experiments/book2vec/`:

1. Which Prose measurement passes its row of the table, and how many words it needs.
2. Whether Telling counts separate books in a way that is not just Prose again.
3. Whether World from name-masked passages survives translation and ignores the author.
4. Whether a Story reading from pieces can find a translation pair and a retelling, and how much the reader recognised.
5. How much each block predicts the others.

## 12. What we accept

- A Story vector is not the story. Critics from Brooks on hold that a paraphrase loses the work, and they are right; the block measures one respect and is named as a reading.
- Style without subject is a narrowed idea of style. Goodman counts what a writer chooses to write about as part of their style. Prose here means manner.
- A novel has many voices and one Prose vector averages them. Narration and speech are measured apart where that is possible, and the spread across passages is kept and not only the mean.

# painting2vec: the framework, applied to paintings

This extends the root `FRAMEWORK.md` to one art form. It narrows the rules for paintings and may not loosen them. Where this document is silent, the root applies.

Status: second draft for sign-off, 9 October 2026. Nothing here is adopted and the library has no painting code. The first draft's experiments have been run and changed sections 3, 4, 5 and 9; `experiments/painting2vec/README.md` has the results. Section 11 lists the decisions still open and the one change this draft asks of the root.

## 1. The work and the artefact

The work is a painting: one flat, hand-made picture. Oil, tempera, fresco, watercolour, ink and colour on silk or paper, miniature painting. Prints, drawings, photographs, sculpture, installation and conceptual work are out of this medium; some of them could be media of their own. The key is the Wikidata id.

The artefact the encoder reads is one photograph of the whole painting, frame and wall cropped away, at a working resolution of about 1,024 pixels on the long side, taken from the holding museum's own open-access image where there is one.

Known gaps. A photograph is not the painting.

- Size is gone. A miniature and a wall-sized canvas arrive as the same number of pixels.
- The surface is flattened: relief, gloss, gold leaf, the weave of silk and the translucency of a glaze do not survive. Oil on canvas survives best, so the loss is uneven across traditions.
- The photograph adds a camera, a light and the painting's present condition. Two reproductions of one painting can differ visibly in colour.
- At this resolution a brushstroke is a few pixels wide. Johnson and others (2008) worked at about 196 pixels per painted inch and called features of a quarter to half a millimetre the limit of what that shows; a one-metre painting at 1,024 pixels has about 26.

A better artefact is the museum's colour-managed image at full resolution, read in tiles, which would make a real block for the hand possible. Images are never committed; only vectors are kept.

Which photograph is the work is answered by the canon: the one the holding museum publishes.

## 2. What "similar" means for a painting

Two paintings are never similar outright. They are similar in some respect: in colour, in what they show, in how the paint was handled. Goodman's point in "Seven Strictures on Similarity" is that the word says nothing until the respect is named, and that choosing and weighting the respects is the whole of the judgement. Different schools of looking are different choices. A formalist counts colour and arrangement and ignores what is shown. An iconographer counts what is shown and ignores the handling. Neither is wrong, and no weighting is the neutral one.

So painting2vec does not compute the similarity of two paintings. It reads each painting in a few named respects, each one from the picture alone, and lets the person say which respects count. The respects are the content blocks of section 3; the person's choices are the lenses of section 5.

Which respects? The ones that people who study pictures keep arriving at and that people looking at pictures measurably use.

- Art theory arrives at the same short list from several directions: the formal elements, Wölfflin's pairs, the first of Panofsky's three levels, Xie He's six criteria. What is depicted, how it is rendered, colour, arrangement, and the trace of the hand.
- When people sort or compare paintings, the first thing that separates them is how abstract or how lifelike the picture is, then what it shows (people or no people), then colour and the coarseness of the brushwork (Berlyne and Ogilvie 1974; Graham and others 2010). What a picture shows registers within a hundredth of a second and how it is painted from about a twentieth (Augustin and others 2008).
- People agree with each other about description and disagree about judgement. In Bromberger and others (2011), raters agreed most on abstractness, realism and animacy (0.81, 0.77, 0.71) and least on balance (0.50). A respect that people cannot agree on is closer to an opinion than to content, and it is weighted with that in mind.

## 3. encode: the content blocks

The respects of section 2 are what a painting is read in. Which of them can be computed, and from what, was settled by experiment and not by this document's first draft, which expected an image encoder to give subject and manner as two vectors. It does not. An encoder separates what is shown from who painted it and when; how the paint was handled does not come apart from either.

Three blocks are read from the pixels.

**Picture.** DINOv2 (large, with registers; Apache 2.0), the class token over a tiled view of the whole painting. It carries what is in the picture and the general look of it. A second photograph of the same painting is its nearest neighbour 99 times in 100. Leak note: no text in training, and neither fame nor the holding museum can be predicted from it; period can, and half of a painting's ten neighbours fall within fifty years of it. Encoders trained against text were tried and set aside by eye: SigLIP 2 put *The Starry Night* next to the *Mona Lisa*. Contrastive Style Descriptors, trained with the painter as its label, returned the painter.

**Composition.** Where things sit: lightness, chroma and edge energy on an eight by eight grid over the surface. Computed directly, no trained model, no leak. Empty space counts as part of the picture.

**Colour.** The palette. Computed directly. It is the one block that fails the photograph test: a second photograph of the same painting is its nearest neighbour 57 times in 100, and nothing that fixes this still looks like colour. So colour enters the default at half weight, has a lens of its own that says on the page that it depends on the photograph, and is never a hard filter.

Two blocks are marked by a describer: a model shown the picture, and never the title, the painter or the year, filling a fixed form. Free description is not used; it does not repeat from one reading to the next, and fixed fields do.

**Subject.** What is visibly there: a checklist of things, how many people, the setting. Panofsky's first level and no further. That a woman holding a wheel is Saint Catherine is knowledge about the picture and is out. It sits beside the picture block, which matches whole scenes where this matches items.

**Manner.** How it is rendered, on scales: how far from appearances, line or dissolved edge, smooth or broken surface, flat or modelled, plain or ornamented. This is the block the pixels would not give. It is called manner and not style or brushwork on purpose. Style carries a school and a date, which the root leaves out. Brushwork is not resolved in the artefact, and a block that claimed to read it would overclaim.

Leak note for the describer: it recognises paintings. In the pilot it named 263 of 300 without being told. Whether its marks describe the picture in front of it or the painting it remembers has not been separated, and the describer blocks do not ship until it has (section 9).

Each block is scaled to the same total variance before weights are applied, as the root says.

## 4. describe: the felt block

Paintings have no descriptor crowd of the kind RateYourMusic gives albums. The nearest thing is ArtEmis (Achlioptas and others 2021): 454,684 emotion labels with written explanations over 80,031 paintings. Two facts limit it. Its terms are non-commercial and do not allow republishing the labels, and the images it covers carry no licence at all. And people do not converge on paintings the way they do on albums: 45.6 per cent of its paintings have a majority emotion, and 61 per cent drew both a positive and a negative one.

So the felt block is predicted, not gathered. The same describer marks a fixed vocabulary of felt-response words. The words are sorted into the root's four kinds in a committed table, `src/art2vec/painting2vec/descriptors.csv`, and only kind 1 enters. Calm, tense, tender, eerie, festive, desolate are kind 1. Dark, crowded and rough are kind 2 and belong to colour, composition and manner. Every value is marked predicted. ArtEmis is used to check the predictions, under its terms, and is never shipped.

What is known: two independent readings of one picture agree closely on the felt words, and the words are not a restatement of the picture's colour. What is not known: whether they match what people feel. The felt block is not built on until that comparison has been made.

## 5. Lenses

The person does not get one slider. They get a small set of named lenses, each a fixed weighting of the blocks, each a different answer to "similar in what respect?".

- **Whole picture.** The default. Picture and composition at full weight, colour at half.
- **Subject.** What it shows, however it is painted. An annunciation in tempera beside an annunciation in acrylic.
- **Form.** Manner and composition, with subject off. The formalist's lens, and the one that puts a landscape next to an abstraction.
- **Colour.** Palette alone, with its warning.
- **Feels like.** The felt block against everything else, as in the root.

The first build has only the three pixel blocks, so its lenses are Whole picture, Picture only, Composition, Form (composition and colour) and Colour. Subject, the fuller Form and Feels like arrive with the describer.

Lenses are stops in the root's sense: each has its own precomputed neighbour lists and its own map position, and the browser does no distance maths. The weights inside each lens are set by looking, recorded with the vectors, and changed in a pull request. Free sliders over the blocks are a later question; five named lenses are easier to understand and to test.

Date, place, painter, medium and size are facts about the work and not opinions about it. They are shown beside the painting and offered as filters ("only before 1800", "not this painter again", "about this size"). They never enter a distance. Because period is in the picture block whether we want it or not, each painting also carries a second list drawn only from other eras. In the pilot those lists cost four per cent in distance and stayed coherent, and they are the plainest form of the root's small step across a boundary.

## 6. What this cannot see

A content-first reading of a painting misses real things, and the honest course is to list them.

- **Category.** Walton's "Categories of Art" argues that even what a picture looks like (restless, serene) depends on the kind of thing the viewer takes it to be. A brushy passage is startling in 1650 and ordinary in 1950. painting2vec compares across categories on purpose: putting a 1650 picture beside a 1950 one because they share something visible is the step no period browser offers. The cost is that it will sometimes call two pictures alike that no historian would.
- **Meaning.** Symbol, allegory, irony, quotation and what a picture meant to the people it was made for are Panofsky's second and third levels and are not in the image.
- **Achievement.** A copy sits on top of its original, and a pastiche beside the thing it imitates. For "looks like" that is the right answer. It says nothing about who got there first.
- **The object.** Section 1.

The space is offered as a way to find the next picture to look at. It is not a claim about what the pictures are.

## 7. canon

Reception picks the set, as the root says, with one added constraint: a painting is in the canon only if an image of it can be shown under an open licence. A map of paintings nobody is allowed to see is no use.

The measure is the number of Wikipedia language editions with an article on the painting, taken from Wikidata, after removing links that are not articles and four editions written by bots. A painting also enters if an editorial list names it. A painter is capped, and a series counts once. That gives 8,851 paintings, and 2,410 for a first build, of which about four fifths have an image that can be shown. The count decides membership and nothing else.

Known weakness: this is mostly European oil painting. A floor for other traditions, by the same measure within each, reaches about 14 per cent and is drawn from a pool where most works have no article at all. A fair canon of Chinese, Japanese, Indian or Persian painting needs lists Wikidata does not have.

## 8. How we check

The root's checks apply. Four are particular to paintings.

- **Two photographs, one painting.** Different reproductions of the same painting must land next to each other in every block. This is the first test run and the colour block is the one expected to fail it.
- **Copies and versions.** A painter's second version of a composition, and a workshop copy, should be close under subject and composition and need not be under colour.
- **Leak checks.** How often a neighbour list repeats the seed's painter; how tightly neighbours cluster in year; whether a painting's fame can be predicted from its vector; and whether the holding museum can be, which would mean the encoder is reading a museum's photography and not the paintings. The last is this medium's version of CLAP reading the store.
- **Looking sessions.** Fixed seed paintings, neighbour lists side by side under each lens with names hidden, and odd-one-out judgements from people. No open set of human similarity judgements for paintings exists, so the looking has to be ours.

## 9. What has been tested and what has not

Run on 2,000 pilot paintings on 8 and 9 October 2026; results in `experiments/painting2vec/`.

Settled: the picture block and its encoder; that pixels do not give a manner block; that colour does not survive the photograph; the lens weights for the three pixel blocks; that fame and museum do not leak and period does.

Not settled, and required before the describer blocks or the felt block ship:

1. **Does the describer look, or remember?** Run it on paintings it cannot know (recent work by living painters who agree, or student copies) and compare its repeatability and its lists with the pilot's.
2. **Do the felt words match people?** Agreement with ArtEmis on the paintings both cover.
3. **Does anyone agree?** Every list so far was judged by a model. Looking sessions with people, names hidden, on a part of the canon none of the choices above were made on.

## 10. What ships

Vectors and metadata in a columnar store; for a site, compact JSON with ten neighbours per painting per lens, a map position per lens, the felt words, and the museum's record (title, painter, date, medium, size, credit line, link). Images are not shipped: the site shows the museum's own image, at full resolution through the museum's deep-zoom service where it has one. ArtEmis labels and anything derived from them are never shipped.

## 11. Open decisions

Each with a recommendation.

1. **Lenses need a line in the root.** The root gives the person one weight, felt against content. Lenses also weight content blocks against each other. Recommend a change to the root's section 6, in its own pull request: a medium may define named stops that weight its blocks, and the person chooses among them. Albums gain the same thing for sound against words.
2. **A describer inside encode.** The root expects an encoder to read the artefact. A describer is a model trained on text reading the artefact through a form. Recommend allowing it under the root's leak rule, with the note in section 3 and the first test of section 9 as its condition.
3. **Build the three pixel blocks first.** Recommend yes. They need no service and no key, and they are the part the experiments support.
4. **Paintings in copyright.** Recommend leaving them out, as section 7 does, until a lawyer has answered whether a vector may be computed and published for a work whose image we may not show.
5. **The root's sketch row for visual art** names ArtEmis as the felt source and colour and texture statistics as content. It changes with this document.

Decided on 8 October 2026: paintings only.

## Reading behind this

Goodman, "Seven Strictures on Similarity" (1972). Walton, "Categories of Art" (1970). Panofsky, *Studies in Iconology* (1939). Wölfflin, *Principles of Art History* (1915). Xie He's six criteria, in Goldin, "Two Notes on Xie He's Six Criteria", *T'oung Pao* 104 (2018). Berlyne and Ogilvie (1974). Augustin, Leder, Hutzler and Carbon, *Acta Psychologica* 128 (2008). Graham, Friedenberg, Rockmore and Field, *Visual Cognition* 18 (2010). Bromberger, Sternschein, Widick, Smith and Chatterjee, *Frontiers in Human Neuroscience* 5 (2011). Achlioptas and others, ArtEmis, CVPR 2021. Elgammal and others, "The Shape of Art History in the Eyes of the Machine" (2018). Somepalli and others, "Measuring Style Similarity in Diffusion Models" (2024). Johnson and others, *IEEE Signal Processing Magazine* 25 (2008).

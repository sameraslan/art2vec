# painting2vec: copyright and licensing constraints

Research date: 8 October 2026. Background for an engineering decision. **This is not legal advice.** Section 10 lists what a lawyer has to confirm before launch.

Assumptions: the owner is an individual developer in the United States; the outputs are a public website and an open-source Python library; visitors come from anywhere.

## How to read the source marks

Every claim carries one of these marks.

| Mark | Meaning |
|---|---|
| **[V]** | A research agent opened the primary page this session (statute, judgment, the institution's own terms or API docs). URL given. |
| **[V2]** | A page was opened this session, but it is a secondary source (law-firm note, Wikipedia, a Commons policy page, a Copyright Office case summary), not the primary text. URL given. |
| **[S]** | Seen only in a search-result summary. The page itself was not opened. Treat as unverified. |
| **[M]** | From memory. Not checked this session. |
| **[I]** | My inference from the sources above. Not itself in any source. |

Three caveats on the marks.

- The research was done by six parallel agents and assembled here. I did not re-open their sources.
- Most pages were read through a fetch tool that summarises the page with a small model. **Re-check exact wording before quoting anything from this file.** The Met terms, the NGA terms, the Getty and Smithsonian FAQ pages and MoMA's site were read directly in a browser.
- Several sites refused the fetcher: CourtListener, Justia, BAILII, the Prado, DACS, the AIC terms page, Yale LUX. So the older US circuit opinions (Kelly, Perfect 10, Authors Guild, Bridgeman, Meshwerks) were **not read in full**; they are reported through later opinions that describe them, Copyright Office summaries, or memory, and marked accordingly.

Several items below are 2026 rulings that postdate my own training knowledge. They are reported as the agents found them and are the first things to re-verify: Cox v. Sony (Supreme Court, March 2026), Thomson Reuters v. Ross (3d Cir., September 2026), Emmerich v. Particle Media (5th Cir., August 2026), Richardson v. Townsquare (2d Cir., April 2026), the Bartz settlement approval (July 2026).

## Summary

1. **Public-domain paintings with a museum CC0 image are clean.** Compute, ship vectors, show at full resolution. The work the pipeline has to do is deciding "public domain" correctly, which Wikidata fields alone cannot do for anything made after 1930.
2. **Computing a vector from an in-copyright image and discarding the image is probably lawful in the US, but it is not settled, and the source of the image matters more than the vector.** The Third Circuit's Ross decision (September 2026) shows that a non-generative tool is not automatically safe; what protects a similarity index is that it does not substitute for the painting or for anything the rights-holder sells.
3. **No court has ruled on whether an embedding is a copy.** The two closest authorities (Getty v Stability in the UK, the US Copyright Office's Part 3 report) make the test whether the artefact stores or can regenerate protected expression. Pooled global vectors look safe on that test; patch tokens do not.
4. **Displaying an in-copyright painting is where the real exposure is.** A thumbnail on an art map is much closer to the painting's own purpose than a search-engine thumbnail is, the rights societies publish per-image web tariffs, and their licences forbid crops and require anti-hotlinking measures. High-resolution display has no credible defence without a licence.
5. **The cheapest way to include Picasso, Rothko, Hopper or O'Keeffe at all** is a vector, CC0 facts from Wikidata, and a link out to the holding museum's page, with no image.
6. **Route A is safest when nothing is uploaded.** Run the encoder in the library or in the browser. After Cox v. Sony the operator of a general-purpose tool is liable only for inducing infringement, so the documentation must not tell people to scrape.

---

## 1. When is a painting in the public domain?

### 1.1 United States

| Situation | Status in 2026 | Source |
|---|---|---|
| Published before 1 January 1931 | Public domain | [V] Cornell chart, current as of 1 Jan 2026: https://guides.library.cornell.edu/copyright/publicdomain |
| Published 1931 to 1977 without a copyright notice | Public domain (failed formalities) | [V] same |
| Published 1931 to 1963 with notice, not renewed | Public domain | [V] same |
| Published 1931 to 1963 with notice and renewed; or 1964 to 1977 with notice | 95 years from publication. 1931 publications enter the public domain on 1 Jan 2027 | [V] same; 17 USC 304 https://www.law.cornell.edu/uscode/text/17/304 |
| Never published, known author | Life plus 70. Authors who died before 1956 are public domain | [V] Cornell chart |
| Never published, anonymous or death date unknown | 120 years from creation (made before 1906) | [V] same |
| Made before 1978, first published 1978 to 2002 | The later of life plus 70 and 31 Dec 2047 | [V] 17 USC 303 https://www.law.cornell.edu/uscode/text/17/303 |

**Foreign works restored by the URAA (17 USC 104A).** [V] https://www.law.cornell.edu/uscode/text/17/104A

- A foreign work that fell into the US public domain for failing US formalities was restored on 1 January 1996 if it was still protected in its source country on that date.
- The restored term is what the work would have had in the US: normally 95 years from publication.
- The source country of a published work is the country of first publication, not the painter's nationality.
- So a foreign painting published 1931 to 1977 is US public domain only if it was published without US formalities **and** was already public domain at home on 1 January 1996.
- For a life-plus-70 country that generally means the painter died before 1926; for a country that was then life plus 50, before 1946. [I] Which term each country applied on that date needs checking country by country.
- Golan v. Holder (2012) upheld restoration. [V] https://www.law.cornell.edu/supremecourt/text/10-545
- The US does not apply the rule of the shorter term (17 USC 104(c)). A work that is public domain at home can still be protected in the US. [V2] https://en.wikipedia.org/wiki/Rule_of_the_shorter_term

**What "publication" means for a painting.** This is the weak point of any automated rule.

- Since 1978: publication is distribution of copies to the public. "A public performance or display of a work does not of itself constitute publication." Hanging a painting in a museum does not publish it. [V] 17 USC 101 https://www.law.cornell.edu/uscode/text/17/101
- Before 1978 the 1909 Act did not define the word. [V] Cornell chart, footnote 6.
- American Tobacco Co. v. Werckmeister, 207 U.S. 284 (1907): an exhibition where copying was forbidden and policed was not a publication. The Court suggested an exhibition where the public could freely copy might be. [V] https://www.law.cornell.edu/supremecourt/text/207/284
- Letter Edged in Black Press v. Public Building Commission of Chicago (1970): the Chicago Picasso was held public domain after its model was shown without notice and without restrictions on copying. [V2] https://commons.wikimedia.org/wiki/Commons:Public_art_and_copyrights_in_the_US
- Whether selling the single original, or reproducing the painting in a catalogue, published it under the 1909 Act: the case law was unsettled. Catalogue reproduction is generally treated as publication. [M] No primary source was found.

The consequence: the US status of a painting made between 1931 and 1977 depends on whether and when copies were distributed, whether they carried a notice, and whether the copyright was renewed. Wikidata records none of those.

### 1.2 Europe, the UK and elsewhere

- **EU:** life plus 70 (Term Directive 2006/116/EC, Art. 1). Art. 4 gives a 25-year right to whoever first publishes a previously unpublished public-domain work. [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32006L0116
- **UK:** life plus 70 (CDPA s.12). [V] https://www.legislation.gov.uk/ukpga/1988/48/section/12
- **Spain:** life plus 70, but **80 years** for authors who died before 7 December 1987. [V2] https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Spain
- **France:** life plus 70; "mort pour la France" adds 30 years; the wartime extensions were largely neutralised in 2007. [V2] https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/France
- **Mexico:** life plus 100 for works still protected on 23 July 2003; authors who died before 1952 are public domain. [V2] https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Mexico
- **Canada:** life plus 70 since 30 December 2022, not retroactive; authors who died before 1972 are public domain. [V2] https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Canada
- **Others:** Japan life plus 70; China life plus 50; India life plus 60; Colombia life plus 80; Jamaica life plus 95. [V2] https://en.wikipedia.org/wiki/List_of_countries%27_copyright_lengths

### 1.3 The painters named in the brief

Death years are as given in the brief and were not checked. The statuses apply the rules above. [I]

| Painter (died) | EU and UK | United States |
|---|---|---|
| Klimt (1918), Monet (1926) | Public domain | Public domain |
| Klee (1940) | Public domain since 2011 | Works published before 1931 are public domain. Works published 1931 to 1940 are probably restored: publication plus 95 years |
| Mondrian, Kandinsky, Munch (1944) | Public domain since 2015 | Same pattern. Mondrian's New York paintings are a US notice question |
| Matisse (1954), Kahlo (1954) | Public domain since 1 Jan 2025. Kahlo in Mexico: not until 2055 | Works published before 1931 are public domain. Later published works are probably protected until publication plus 95 |
| Pollock (1956) | Protected until 1 Jan 2027 | Treat as protected. Depends on notice and renewal, work by work |
| Hopper (1967) | Protected until 2038 | Pre-1931 publications are public domain; the rest case by case |
| Rothko (1970) | Protected until 2041 | Treat as protected |
| Picasso (1973) | Protected until 2044; Spain until 2054 | Pre-1931 publications are public domain in the US only |
| O'Keeffe (1986) | Protected until 2057 | Pre-1931 publications are public domain in the US only |

Two traps follow from this table.

- **US-only public domain.** Early Picasso, early O'Keeffe and early Hopper are public domain in the US and protected in Europe. A worldwide site cannot treat them as free.
- **Europe-only public domain.** Late Matisse, Kahlo, late Klee, Kandinsky, Munch and Mondrian are public domain in Europe and probably protected in the US, where the owner lives and can be sued.

### 1.4 A decision rule from Wikidata fields

Inputs: creator's date of death (P570), inception (P571), country of origin (P495), copyright status (P6216) with its jurisdiction qualifier (P1001), and the Commons licence templates on the image file. [V] https://www.wikidata.org/wiki/Property:P6216

| Tier | Rule (for 2026) | Treat as |
|---|---|---|
| **A** | Every creator died before 1 Jan 1956 **and** inception before 1931. Use a margin (say 1926) because inception is not publication | Public domain in the US and in life-plus-70 countries |
| **A-strict** | Creator died before 1926 (before 1952 if Mexican; before 1946 if Spanish) | Public domain essentially everywhere |
| **B** | Inception before 1931, creator died 1956 or later | Public domain in the US only. Not free for EU or UK visitors |
| **C** | Creator died before 1956, inception 1931 or later | Public domain in Europe; US uncertain. Exclude or flag |
| **D** | Everything else | In copyright. Exclude unless cleared per work |

The cut-off years move forward by one each 1 January. Require year precision on both fields. Treat any conflict between the rule, P6216 and the Commons templates as a failure.

**Error cases.**

1. Inception is not publication. A 1925 painting first reproduced in 1950, or never reproduced, follows different US rules.
2. Posthumous first publication between 1978 and 2002: protected in the US until at least 2047. In the EU, the 25-year publisher's right.
3. Anonymous, workshop, "attributed to" and "follower of": no reliable death date. Fail closed.
4. Several creators: the last death governs.
5. US painters, 1931 to 1977: notice and renewal cannot be known from Wikidata.
6. A modern copy after an old master: the creator on the item may be the copyist.
7. Wikidata date precision: decade or century values, "circa", several inception values, ranges that straddle 1931.
8. Death in the cut-off year itself: terms run to the end of the calendar year. Use strict "less than".
9. Émigré painters: the URAA source country is the country of first publication, not citizenship.
10. P6216 is often missing, has no jurisdiction, or was set by a bot.
11. Longer national terms: Mexico, Colombia, Jamaica, Spain for deaths before 1987.
12. Layers that are not copyright: moral rights, estate trademarks, Italy's cultural-heritage fees (section 2).

---

## 2. Photographs of public-domain paintings

### 2.1 United States

- **Bridgeman Art Library v. Corel Corp., 36 F. Supp. 2d 191 (S.D.N.Y. 1999).** Exact photographic copies of public-domain paintings lack originality and are not copyrightable. It is a district court decision: persuasive and widely followed, not binding. [V2] https://en.wikipedia.org/wiki/Bridgeman_Art_Library_v._Corel_Corp. The opinion itself was not opened.
- The Copyright Office Compendium (Third) s.313.4(A) cites Bridgeman for the same point. [V] https://www.copyright.gov/comp3/chap300/ch300-copyrightable-authorship.pdf
- Meshwerks v. Toyota, 528 F.3d 1258 (10th Cir. 2008) followed the reasoning for digital models. [V2] same Wikipedia page.
- The rule covers faithful photographs of flat works only. A photograph of a frame, a sculpture or a coin can be original. [V] https://commons.wikimedia.org/wiki/Commons:When_to_use_the_PD-Art_tag

### 2.2 European Union

- **DSM Directive 2019/790, Article 14.** Once a work of visual art is out of copyright, a reproduction of it has no copyright or related right unless the reproduction is itself the author's own intellectual creation. [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0790
- **Germany:** s.68 UrhG implements it. [V] https://www.gesetze-im-internet.de/englisch_urhg/englisch_urhg.html Before that, the Federal Court of Justice had protected museum photographs and enforced a museum's photography ban (I ZR 104/17, 2018). [S] Section 68 removes the photograph right; it does not touch the contract point. [I]
- **France:** did not transpose Article 14, on the view that such photographs were never protected. Commons lists France as inconclusive. [V] https://commons.wikimedia.org/wiki/Commons:Reuse_of_PD-Art_photographs
- **Spain:** a 25-year "mere photographs" right survives next to the Article 14 transposition, and how they interact is unresolved. [S] Commons treats Spanish museum photographs made after 2000 as generally not usable. [V] same Commons page.
- **Italy:** copyright gives no right in a faithful reproduction, but the Cultural Heritage Code (arts. 107 and 108) requires permission and a fee to reproduce state-held works commercially. [V2] https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Italy
  - The Uffizi's rights page cites the Code and the 2024 fee decree (DM 108/2024, amending DM 161/2023). [V] https://uffizi.it/en/professional-services/rights-reproductions
  - A Venice court applied the Code to Ravensburger's Vitruvian Man puzzle in 2022. [S] The Stuttgart Higher Regional Court held on 11 June 2025 that the Code cannot be enforced outside Italy. [V2] https://communia-association.org/2025/07/10/higher-regional-court-of-stuttgart-confirms-territoriality-of-italian-cultural-heritage-code/ Whether that ruling is final is unknown.
  - Uffizi v. Jean Paul Gaultier: sued in 2022. No outcome was found. [S]

### 2.3 United Kingdom

- **THJ Systems Ltd v Sheridan [2023] EWCA Civ 1354.** The Court of Appeal confirmed that originality means the "author's own intellectual creation", which needs free and creative choices, and that the old "skill and labour" test is wrong. [V] https://caselaw.nationalarchives.gov.uk/ewca/civ/2023/1354
- **The case is about software screens. It does not mention museum photographs.** The reading that faithful photographs of flat public-domain works therefore have no UK copyright is a commentator's inference, adopted by Wikimedia Commons. It is persuasive and untested. [V] same judgment; Commons reuse page.
- The UK Intellectual Property Office's notice says simply creating a copy of an image will not result in a new copyright. [V] https://www.gov.uk/government/publications/copyright-notice-digital-images-photographs-and-the-internet/copyright-notice-digital-images-photographs-and-the-internet
- Museums still assert rights. The National Gallery credits "Photo © The National Gallery, London" and licenses images CC BY-NC-ND. [V] https://www.nationalgallery.org.uk/terms-of-use The British Museum uses CC BY-NC-SA. [V] https://www.britishmuseum.org/terms-use/copyright-and-permissions A 2024 survey found about half of the national museums asked still claim copyright. [V2] https://copyrightliteracy.org/2024/12/05/reflecting-on-anarchy-in-the-uk-museums-and-public-domain-images/

### 2.4 Wikimedia Commons

- Commons' position is that faithful reproductions of flat public-domain works are public domain. The underlying painting must be public domain in both the US and its source country. Frames must be cropped. [V] https://commons.wikimedia.org/wiki/Commons:When_to_use_the_PD-Art_tag
- Commons warns re-users that local law may differ. [V] https://commons.wikimedia.org/wiki/Commons:Reuse_of_PD-Art_photographs
- The Wikimedia Foundation gives no warranty on the copyright status of any file. [V] https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia

### 2.5 Consequence

- In the US, a faithful photograph of a public-domain painting is low risk on copyright.
- In the EU, Article 14 points the same way. Residual risk sits in Spain, the Nordic photograph rights, France, and Italy's heritage code for commercial use.
- In the UK it is probably the same, but untested.
- **Contract is the main thing left.** A museum's terms can bind whoever accepts them even where there is no copyright. The National Gallery's terms forbid building a database from downloaded material and forbid framing its content. [V] https://www.nationalgallery.org.uk/terms-of-use
- Sourcing order that follows: a museum's CC0 programme first; a Commons PD-Art file second; a museum site with restrictive terms last, or not at all.

---

## 3. Museum and aggregator terms

Checked 8 October 2026. "Not stated" means no page that was opened addressed the point. Coverage of famous paintings is my judgement, not sourced.

### 3.1 Open sources: usable for compute, vectors and display

| Source | Images of public-domain works | Text and metadata | API | IIIF | Hotlinking or embedding | Rate and credit |
|---|---|---|---|---|---|---|
| **The Met** | CC0 for Open Access items [V] | Data CC0. The API has no description field; website essays are non-commercial only [V] | No key [V] | Not in the API docs [V] | Not stated | 80 requests per second. No credit required; no implied endorsement [V] |
| **Art Institute of Chicago** | CC0 [V] | CC0, except `description`, which is CC BY 4.0 [V] | No key [V] | Image API 2 [V] | **Expressly allowed** [V] | 60 per minute anonymous; 1 per second for bulk. Send an `AIC-User-Agent` header. Recommended size 843 px [V] |
| **National Gallery of Art** | CC0 for presumed public-domain works [V] | Dataset CC0 [V] | None; CSV on GitHub [V] | Image links in the dataset [V] | Not stated | Credit encouraged [V] |
| **Cleveland** | CC0 [V] | CC0, including descriptions [V] | No key [V] | None in the API record [V] | Not stated; CDN URLs are served | None stated [V] |
| **Getty** | CC0 for Open Content [V] | Not confirmed [M: CC0] | REST and SPARQL [V] | Yes [V] | Not stated | Credit line requested [V] |
| **Smithsonian** | CC0 [V] | CC0 [V] | Key from api.data.gov [V] | Manifests listed [V] | Not stated | 1,000 per hour per key [V] |
| **Yale (YUAG, YCBA)** | Open access; no CC licence named [V] | Separate data terms, not opened | OAI-PMH [V] | Yes [V] | Not stated | Credit requested [V] |
| **Rijksmuseum** | Public domain or CC0; some CC BY 4.0 [V] | Same, per item [V] | New search API, no key. The old key-based API is gone [V] | Image and Presentation at iiif.micr.io [V] | Not stated | Credit requested [V] |
| **SMK, Copenhagen** | Public domain; the museum waives photo rights [V] | Free for public-domain works [V] | No key [V] | Yes, with `info.json` [V] | Encouraged in principle [V] | 2,000 rows per request [V] |
| **Paris Musées** | CC0 where the credit shows it [V] | Site texts reserved [V] | GraphQL; account and token [V] | None found | Not stated | Cite the source [V] |
| **Nationalmuseum, Sweden** | About 6,000 images on Commons as public domain [V] | Not stated | Undocumented [M] | Reported [M] | Not stated | None [V] |
| **Barnes** | Public-domain works free for any use [V] | Site text reserved [V] | None | None | Not stated | Credit requested [V] |
| **Belvedere** | CC0 [V] | not checked | not checked | Offered [V] | not checked | not checked |
| **Städel** | Public Domain Mark [V] | Metadata CC0; curatorial text excluded [V] | OAI [V] | not checked | not checked | Credit "Städel Museum, Frankfurt am Main" [V] |
| **Nasjonalmuseet, Oslo** | CC BY 4.0 museum photos [V] | not checked | Via DigitaltMuseum, key [V] | not checked | not checked | 4,000 px cap [V] |
| **Wikimedia Commons** | Per file [V] | Structured data CC0 [V] | No key [V] | not checked | Allowed, not recommended [V] | See below |
| **Wikidata** | n/a | CC0 [V] | No key | n/a | n/a | None |
| **Europeana** | Per-object rights statement [V] | Metadata CC0 [V] | Account and key since 28 May 2025; keys must stay server-side [V] | Docs exist, not opened | Not stated | Credit encouraged [V] |

Wikimedia's limits tightened in 2025 and 2026. [V] https://wikitech.wikimedia.org/wiki/Robot_policy and https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy

- A descriptive User-Agent with contact details is required. Generic agents can be blocked without notice.
- Media downloads: at most 2 concurrent requests, 25 Mbps, originals or standard thumbnail sizes only.
- API, unauthenticated: one request at a time, under 5 per second.

### 3.2 Restricted sources: metadata at most, or avoid

| Source | Position | Consequence |
|---|---|---|
| **National Gallery, London** | Images CC BY-NC-ND 4.0; narrative text CC BY 4.0; structured data CC0. Terms forbid framing its content and building a database from downloads. IIIF is "in the process" of being built [V] | Text and data usable with credit. Images: no crops, non-commercial, and a contract clause against exactly this project. Use Commons files instead |
| **Louvre** | Images free only for private use and a closed list of scientific and educational uses; otherwise paid through GrandPalaisRmn. Entry text is under the Etalab Open Licence, commercial use allowed. Embedding Louvre pages is prohibited. Terms updated 19 March 2026 [V] | Use the text and facts. Do not use the images |
| **Prado** | Site could not be opened. Personal use only, no API [M] | Unverified. Use Commons, noting the Spanish photograph right |
| **Uffizi** | No open licence; heritage-code fee regime [V] | Use Commons. Commercial use is the exposed case |
| **British Museum** | CC BY-NC-SA 4.0. A site "not linked to any commercial activity" counts as non-commercial [V] | Usable only while the project is non-commercial. Few paintings anyway |
| **Tate** | CC BY-NC-ND on some low-resolution images. Site terms prohibit unauthorised text and data mining. GitHub metadata is CC0 but frozen at October 2014 [V] | Old metadata only |
| **Harvard Art Museums** | API is non-commercial only. Content may not be stored for more than two weeks. Images must be shown from Harvard's URL [V] | **Conflicts with shipping vectors.** Exclude, or ask for written permission |
| **MoMA** | Metadata CC0 on GitHub. Images are not licensed; commercial use prohibited [V] | Facts only. Link out |
| **Google Arts & Culture** | Images belong to partners. Google's terms (effective 30 July 2026) prohibit automated access against machine-readable instructions [V] | Do not scrape or rip tiles. Link out |
| **WikiArt** | Shows in-copyright works under its own fair-use claim. Keyed API, free tier 4 requests per second. No reuse licence [V] | Its fair-use position does not pass to a re-user. Do not treat as an image source |
| **Web Gallery of Art** | Educational and personal use only. Claims database copyright [V] | Do not use |
| **Thyssen, Van Gogh Museum, Kunsthistorisches Museum** | Non-commercial terms [V for Thyssen; S for the others] | Use Commons |

Source URLs for both tables:

- Met: https://metmuseum.github.io/ ; https://www.metmuseum.org/policies/terms-and-conditions
- AIC: https://api.artic.edu/docs/
- NGA: https://www.nga.gov/terms-and-notices ; https://github.com/NationalGalleryOfArt/opendata
- Cleveland: https://www.clevelandart.org/open-access ; https://openaccess-api.clevelandart.org/
- Getty: https://www.getty.edu/projects/open-content-program/faqs/ ; https://data.getty.edu/
- Smithsonian: https://www.si.edu/openaccess/faq ; https://api.data.gov/docs/developer-manual/
- Yale: https://artgallery.yale.edu/using-images ; https://britishart.yale.edu/collections-data-sharing
- Harvard: https://github.com/harvardartmuseums/api-docs
- MoMA: https://github.com/MuseumofModernArt/collection ; https://www.moma.org/about/about-this-site/
- Barnes: https://www.barnesfoundation.org/collection/open-access-and-copyright
- Google: https://policies.google.com/terms ; https://support.google.com/culturalinstitute/partners/answer/6002688
- WikiArt: https://www.wikiart.org/en/terms-of-use ; https://www.wikiart.org/en/App/GetApi
- Web Gallery of Art: https://www.wga.hu/legal.html
- Commons: https://commons.wikimedia.org/wiki/Commons:Hotlinking
- Europeana: https://www.europeana.eu/en/rights/terms-of-use
- Rijksmuseum: https://data.rijksmuseum.nl/policy ; https://data.rijksmuseum.nl/docs/
- Paris Musées: https://apicollections.parismusees.paris.fr/cgu
- SMK: https://www.smk.dk/en/article/smk-open/ ; https://www.smk.dk/en/article/smk-api/
- Nationalmuseum: https://www.nationalmuseum.se/en/samlingarna/bilder
- National Gallery: https://www.nationalgallery.org.uk/terms-of-use ; https://www.nationalgallery.org.uk/documentation/ngacuk/licences
- Louvre: https://collections.louvre.fr/en/page/cgu
- British Museum: https://www.britishmuseum.org/terms-use/copyright-and-permissions
- Tate: https://www.tate.org.uk/about-us/policies-and-procedures/website-terms-use ; https://github.com/tategallery/collection
- Belvedere: https://sammlung.belvedere.at/opencontent/images?page=1
- Städel: https://sammlung.staedelmuseum.de/en/concept
- Nasjonalmuseet: https://www.nasjonalmuseet.no/en/collection/about-the-collection/about-copyright/
- Thyssen: https://www.museothyssen.org/en/legal-terms-and-data-protection/legal

### 3.3 What this means for deep zoom

FRAMEWORK.md section 10 says the site "shows the museum's own image, at full resolution through the museum's deep-zoom service where it has one."

- Only the **Art Institute of Chicago** says in terms that hotlinking its IIIF images is allowed.
- **SMK** and the **Rijksmuseum** publish IIIF endpoints for public use and are silent on embedding; that is tolerated, not promised.
- Most others are silent. Silence on a CC0 image is not a risk in copyright; it is a risk that the URL breaks or gets throttled.
- For a CC0 image, the owner may also host their own tiles. That removes the dependency and is expressly allowed by the licence.
- The National Gallery and the Louvre prohibit framing or embedding in their terms.

---

## 4. In-copyright paintings under Route B

### 4.1 (a) Download, compute, discard

**The US fair-use line (17 USC 107).** [V] https://www.law.cornell.edu/uscode/text/17/107

- Authors Guild v. Google (2d Cir. 2015): scanning whole books to build a search function was fair use, because the tool pointed readers to the books and did not replace them. [V, as described in the Third Circuit's Ross opinion; the original was not opened]
- Authors Guild v. HathiTrust (2d Cir. 2014): a full-text search database was fair use. [V, same route]
- Kelly v. Arriba Soft (9th Cir. 2003) and Perfect 10 v. Amazon (9th Cir. 2007): image search engines; see 4.3. [V2]
- A.V. v. iParadigms (4th Cir. 2009): archiving whole student papers for plagiarism detection was fair use. [M]

**Thomson Reuters v. Ross Intelligence, No. 25-2153 (3d Cir. 29 Sept 2026).** [V] https://www2.ca3.uscourts.gov/opinarch/252153p.pdf This is the newest appellate authority and the one closest to this project, because Ross's tool was **not generative**. It was a search engine.

- The court rejected fair use.
- Factor one went against Ross because both sides used the material for the same thing, running a legal-research product. The court called the use "minimally transformative, at best".
- Factor four counted two markets: the original one, and an emerging market for licensing training data.
- The court distinguished Authors Guild: Google's search sent users to the books; Ross aimed to replace Westlaw.
- A footnote records that Ross got its access to Westlaw in bad faith.
- The court set the generative-AI cases aside as different.

What it means here. [I] Being non-generative is not a safe harbour. A painting similarity index is on the Google Books side of the line: its purpose is finding and comparing, not looking at the painting, and it replaces nothing the estates sell. The live risk is factor four, if rights-holders can show a market for licensing images for machine analysis.

**The generative-AI cases** bear on this less directly.

- Bartz v. Anthropic (N.D. Cal. 2025): training was fair use; keeping pirated copies in a permanent library was not. [V] https://storage.courtlistener.com/recap/gov.uscourts.cand.434709/gov.uscourts.cand.434709.231.0_2.pdf The $1.5 billion settlement received final approval on 20 July 2026. [V2] https://authorsguild.org/news/court-grants-final-approval-anthropic-copyright-settlement/
- Kadrey v. Meta (N.D. Cal. 25 June 2025): summary judgment for Meta on training, for lack of evidence of market harm. [V] https://storage.courtlistener.com/recap/gov.uscourts.cand.415175/gov.uscourts.cand.415175.598.0_1.pdf
- US Copyright Office, Part 3 report (May 2025, pre-publication): training is most transformative where the model is used for research or a closed, non-substitutive task; knowing use of pirated copies should weigh against fair use. [V] https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf
- Still pending, status from search summaries only [S]: NYT v. OpenAI (summary-judgment motions filed September 2026); Getty v. Stability in the US (refiled in N.D. Cal., most claims survived a motion to dismiss); Andersen v. Stability (hearing February 2027); Concord v. Anthropic; Disney v. Midjourney; Advance Local v. Cohere.

The common thread across all of them: **where the copy came from matters.** A copy taken from a museum's open API or lawfully viewed public page is in a different position from a scraped or pirated corpus.

**European Union: text and data mining.** [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0790

- Article 2(2) defines text and data mining as automated analysis to generate information such as patterns and correlations. Computing embeddings fits.
- Article 3 covers research organisations and cultural heritage institutions only. An individual developer is neither.
- Article 4 covers anyone, for lawfully accessible works, with copies kept only as long as needed, **unless the rights-holder has reserved the use**. Recital 18 says the reservation should be machine-readable for online content.
- The reservations exist. ADAGP's licence template includes an express mining opt-out. [V] https://www.bagnolssurceze.fr/wp-content/uploads/2026/06/2026-06-090-Annexe-Deliberation-ADAGP-Contrat-usages-numeriques-Organisme-culturel.pdf The Louvre's terms repeat it. [V] https://collections.louvre.fr/en/page/cgu Tate's terms prohibit mining. [V]
- Germany: the Hamburg courts held LAION's downloading of images was covered by the mining exceptions (LG Hamburg 2024 [M]; OLG Hamburg, 10 Dec 2025, with a further appeal allowed [S]). The Munich court went the other way for song lyrics memorised in a model (GEMA v. OpenAI, Nov 2025). [S]
- Whether EU law reaches a US machine fetching from an EU server is unsettled. [M]

**United Kingdom.** CDPA s.29A allows copying for computational analysis, by someone with lawful access, **solely for non-commercial research**. Contract cannot override it. [V] https://www.legislation.gov.uk/ukpga/1988/48/section/29A The government's March 2026 report left the law unchanged. [S]

**Japan.** Article 30-4 permits use for data analysis where the purpose is not enjoyment of the work's expression, unless it unreasonably prejudices the owner. [V] https://www.cric.or.jp/english/clj/cl2.html It is the most permissive of the four regimes.

**Assessment.** [I] In the US, fetching an in-copyright image from a lawful source, computing a vector and discarding the image is probably fair use. It is not settled, and Ross shows the analysis turns on substitution and markets. In the EU the individual developer is inside Article 4 only where no opt-out exists, and for the artists who matter the opt-outs exist.

### 4.2 (b) Publishing the vectors

**Is an embedding a copy?** No court has decided. The search found none.

- A "copy" is an object in which the work is fixed and from which it can be perceived or reproduced. A derivative work recasts or adapts it. [V] https://www.law.cornell.edu/uscode/text/17/101
- Facts about a work are not the work (Feist, 499 U.S. 340). [V] https://www.law.cornell.edu/supremecourt/text/499/340
- **Getty Images v Stability AI [2025] EWHC 2863 (Ch):** model weights that neither store nor reproduce the works are not an "infringing copy". [V] https://www.judiciary.uk/wp-content/uploads/2025/11/Getty-Images-v-Stability-AI.pdf Permission to appeal that point was granted. [V2] https://www.mills-reeve.com/publications/getty-images-v-stability-ai-arguments-on-infringement-of-copyright-to-be-appealed/
- The US Copyright Office takes the same line: numbers infringe only if they retain substantial protectable expression. [V] Part 3 report.
- GEMA v. OpenAI went the other way where the content could be recovered. [S]

So the working test is **recoverability**, and that is an empirical question.

**What can be recovered from an embedding.**

- A decoder conditioned on a CLIP image embedding produces variations that keep the semantics and style while details change (Ramesh and others 2022). [V] https://arxiv.org/abs/2204.06125
- Colours and rough contours can be reconstructed from the high layers of a network (Dosovitskiy and Brox 2016). [V] https://arxiv.org/abs/1506.02753
- Diffusion-guided inversion of the deep intermediate representations of vision foundation models gives high-fidelity images (DRAG, 2025). [V, abstract only] https://arxiv.org/abs/2509.11724
- No paper was found that directly compares inverting a pooled vector against inverting patch tokens for DINOv2.

Reading these together. [I] A single pooled vector of 768 or 1,024 numbers reveals subject, palette, manner and coarse layout. With a strong generative model behind it, it yields a recognisable variation and not a faithful copy. A grid of patch tokens, or intermediate activations, is far more reconstructable.

**Design consequences.** [I]

- Ship only pooled global vectors. Reduce their dimension and quantise them.
- Never ship patch tokens, intermediate activations or thumbnails.
- Neighbour lists and map coordinates are the least risky outputs of all.
- The colour and composition blocks are computed directly. Keep them coarse: a histogram is a fact; a 32 by 32 luminance grid is a small picture.
- Very simple, iconic compositions are the hard case. A Rothko is two or three colour fields, and a coarse composition block describes most of it.
- "Not faithfully recoverable" is true today. Re-test against current decoders before each release.

### 4.3 (c) Displaying the work

**Thumbnails.**

- Kelly v. Arriba Soft, 336 F.3d 811 (9th Cir. 2003): a visual search engine's small, low-resolution thumbnails were fair use because they served a different function, "unrelated to any aesthetic purpose". [V] Copyright Office summary: https://www.copyright.gov/fair-use/summaries/kelly-arriba-9thcir2003.pdf
- Perfect 10 v. Amazon, 508 F.3d 1146 (9th Cir. 2007): Google's thumbnails were highly transformative. [V2] https://en.wikipedia.org/wiki/Perfect_10,_Inc._v._Amazon.com,_Inc.
- Bill Graham Archives v. Dorling Kindersley, 448 F.3d 605 (2d Cir. 2006): seven concert posters at reduced size in an illustrated history were fair use. [V2] https://en.wikipedia.org/wiki/Bill_Graham_Archives_v._Dorling_Kindersley,_Ltd.
- **Andy Warhol Foundation v. Goldsmith, 598 U.S. 508 (2023):** factor one looks at the specific use. Where the copy and the original "share substantially the same purpose" and the use is commercial, the factor weighs against fair use. [V] https://www.law.cornell.edu/supremecourt/text/21-869
- After Warhol: Philpot v. Independent Journal Review (4th Cir. 2024), a photograph used to illustrate an article was not transformative. [V2] https://fairuse.stanford.edu/case/philpot-v-independent-journal-review Hachette v. Internet Archive (2d Cir. 2024), a non-commercial user still lost. [S]

Why an art map is weaker than a search engine. [I] Kelly and Perfect 10 rest on the thumbnail being a pointer to something else. On a map of paintings the thumbnail is the thing the visitor came to look at. That is close to the painting's own purpose, which is the Warhol problem.

| Helps | Hurts |
|---|---|
| Very small images, about 200 px or less | The whole work is shown |
| A prominent link to the museum or rights-holder | Paintings are highly creative works |
| No advertising or revenue | **A per-image web licensing market exists and publishes prices** |
| The neighbour structure is new information | The image is the object of interest, not a pointer |
| No download, no zoom | Crops and overlays touch moral rights abroad |

High-resolution display of an in-copyright painting has no credible fair-use footing.

**Embedding an image hosted by someone else.**

- Ninth Circuit: the "server test". Only the party whose server sends the image displays it. Reaffirmed in Hunley v. Instagram (2023). [S]
- Southern District of New York: rejected it (Goldman v. Breitbart 2018; Nicklen v. Sinclair 2021). [V2]
- **Fifth Circuit, Emmerich Newspapers v. Particle Media (27 Aug 2026):** the first appeals court to reject the server test. It asks who transmitted the content and whether that source was authorised. Embedding that only points the browser at the owner's own server is still not direct infringement. [V2] https://www.proskauer.com/blog/is-your-website-content-infringing-fifth-circuit-rebuffs-server-test-in-online-embedding-case
- **Second Circuit, Richardson v. Townsquare Media (23 Apr 2026):** assumed without deciding that embedding can infringe. [V2] https://blog.ericgoldman.org/?p=28827
- EU: linking to or framing a freely and lawfully available work is not a new communication (Svensson, BestWater). Copying it to your own server is (Renckhoff, C-161/17). Framing that gets round anti-framing measures is (VG Bild-Kunst v SPK, C-392/19). [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62019CJ0392 and https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62017CJ0161
- Both ADAGP and VG Bild-Kunst require their licensees to block hotlinking. [V] So a museum's licensed image of a Picasso is meant to be unembeddable, and getting round that is infringement in the EU.

Net. [I] Hosting your own copy of an in-copyright image, even a thumbnail, is reproduction and display in the US and a new communication in the EU. Hotlinking the museum's copy is still not direct infringement in the Ninth and Fifth Circuits, is unsettled in the Second, and is the thing the societies' licences are written to prevent.

**Linking out with no image.** Lowest risk. Titles, painters, dates and vectors are not the work. Link to the museum or the estate, never to an unauthorised copy (GS Media, C-160/15). [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62015CJ0160

**Rights societies and what a licence costs.**

- **ARS (US)** says it is the exclusive licensing representative for Picasso, Matisse, Kahlo, Rothko, Pollock and O'Keeffe, among others. [V] https://arsny.com/history/ Hopper is licensed through ARS as well, per the Whitney's credit line. [V] https://whitney.org/collection/works/6270
- ARS publishes no rates. It works by request and quote. Credit format: "© 2026 [Artist] / Artists Rights Society (ARS), New York". [V] https://arsny.com/licensing-requests/
- **VG Bild-Kunst (Germany)** publishes an internet tariff, valid from 1 August 2023, per website per month, net of VAT, up to 100,000 hits a month. [V] https://www.bildkunst.de/download.97a5fbe0924b4aa51d93f0510ad85618_1/

| Category | Images | EUR per month |
|---|---|---|
| Private site, no revenue | 1 to 10 | 2 |
| Private site, no revenue | 11 to 50 (the maximum) | 11 |
| Non-profit cultural or educational institution | 501 to 1,000 | 465 |
| Commercial information service | 501 to 1,000 | 1,257 |

  Whether the band fee is a total or per image is ambiguous in the document. Ask.
- VG Bild-Kunst conditions: prior consent; credit; any change of colour, crop or proportion needs agreement; protection against framing and download. [V] same.
- **ADAGP (France)** conditions: width plus height at most 1,600 px at 72 dpi; no modification, crops or overprinting without authorisation; more than 50 works by one artist needs authorisation; some artists excluded outright. [V] contract URL in 4.1. Its euro rates could not be opened.
- **DACS (UK):** site blocked. Prices on request. [S]
- Outside the US a licence for the photograph may be needed as well as one for the painting.

**Moral rights.**

- US: the Visual Artists Rights Act covers the physical original and excludes reproductions. Online thumbnails are outside it. [V] https://www.law.cornell.edu/uscode/text/17/106A
- UK: the integrity right covers alterations that distort the work or prejudice the artist's reputation, for as long as copyright lasts. [V] https://www.legislation.gov.uk/ukpga/1988/48/part/I/chapter/IV
- France: perpetual and inalienable. [M]
- Consequence: square-cropped thumbnails, UI overlays, and the mirrored or recoloured versions from experiment 3 in FRAMEWORK.md, if shown publicly for in-copyright works, are the most exposed elements in France and Germany.

**No fair use in Europe.** The EU exceptions are a closed list. Quotation needs a direct link to the user's own commentary and must be limited to what that requires (Spiegel Online, C-516/17). [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62017CJ0516 A gallery of whole works without commentary is unlikely to qualify. [I]

**What a US claim could cost.**

- Statutory damages are $750 to $30,000 per work, up to $150,000 if wilful. [V] https://www.law.cornell.edu/uscode/text/17/504
- They are available only if the work was registered before the infringement began. [V] https://www.law.cornell.edu/uscode/text/17/412 Whether a given painting is registered has to be checked per work.
- Without timely registration the exposure is actual damages (roughly a licence fee) and an injunction. [I]
- Copyright Claims Board: capped at $30,000 per proceeding. [V] https://ccb.gov/about/

### 4.4 (d) Site terms, scraping and technical barriers

- hiQ v. LinkedIn (9th Cir. 2022): scraping public pages that sit behind no access gate does not violate the Computer Fraud and Abuse Act. Other claims remain available. [V] https://cdn.ca9.uscourts.gov/datastore/opinions/2022/04/18/17-16783.pdf On remand, LinkedIn's anti-scraping terms were held enforceable and breached. [S]
- Meta v. Bright Data (N.D. Cal. 2024): Meta's terms did not bind logged-out scraping of public data. [M]
- Ryanair v PR Aviation (C-30/14): where a database has no copyright or database right, its owner can still restrict use by contract. [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62014CJ0030
- Using an API key or an account is clear assent to the terms. That makes a keyed API a firmer contract than a browsed page. [I]
- robots.txt has no independent legal force in the US. It is evidence of notice, and a candidate opt-out signal in the EU. [M]
- **Do not defeat technical barriers.** 2026 rulings on anti-bot systems as access controls under DMCA 1201 point in both directions (Google v. SerpApi; Reddit v. SerpApi). [S] CAPTCHAs, logins, rate limits and signed URLs are a line not to cross.
- Do not strip watermarks or metadata from anything kept or redistributed (DMCA 1202). [M]

Order of preference for sources: a museum's open API or data dump; Wikimedia; nothing else without reading the terms.

---

## 5. Route A: bring your own image

**After Cox v. Sony.** Cox Communications v. Sony Music, No. 24-171 (U.S. 25 Mar 2026). [V] https://www.law.cornell.edu/supremecourt/text/24-171

- A provider is contributorily liable only if it intended its service to be used for infringement.
- Intent is shown by inducement, or by a service tailored to infringement with no substantial lawful use.
- Knowing that some users infringe, and carrying on, is not enough.

A general-purpose similarity tool has obvious lawful uses. The remaining risk is inducement. **The documentation, examples and marketing must not encourage infringing use.** An example that says "point this at WikiArt" is the kind of evidence that matters.

**If uploads are stored: DMCA 512(c).** [V] https://www.law.cornell.edu/uscode/text/17/512

- A designated agent, listed on the site and registered with the Copyright Office. The fee is $6, renewed every three years. [V] https://www.copyright.gov/dmca-directory/faq.html
- A repeat-infringer policy.
- Prompt removal on a valid notice.
- No actual knowledge of infringement, and no direct financial benefit from infringement the operator can control.
- The safe harbour protects against what users upload. It does not cover content the owner selects. Route B gets nothing from it. [I]

**If uploads are not stored.** The image is processed in memory and dropped. Nothing is hosted and nothing is shown to anyone else. What remains is the transient copy and privacy: uploaded images can contain people and location data, so strip metadata and do not log.

**Returning neighbours.** A list of titles and links adds nothing. Thumbnails of public-domain neighbours are fine. Thumbnails of in-copyright neighbours bring back section 4.3.

**Client-side or local.** Running the encoder in the browser (ONNX, WebGPU) or in the library means the operator makes no copy and hosts nothing. The user does. This is the cleanest design, and it is what PixPlot does (section 8).

- A downloader bundled with the library for a museum's open API, used under its terms, is defensible.
- A bundled WikiArt scraper adds contract risk and inducement evidence. Do not ship one.

**EU Digital Services Act.** [V] https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065

- Applies only to a service offered in the Union with a substantial connection. Being reachable from the EU is not enough.
- If it applies and uploads are stored: notice-and-action (Art. 16), a contact point (Arts. 11 and 12), and a legal representative in the EU (Art. 13), which has no exemption for small providers.
- A tool that stores nothing arguably provides no hosting service. [I]

**UK Online Safety Act.** Covers services where one user's content can be encountered by another. Private, unshared uploads appear to fall outside it. [S]

---

## 6. Tags instead of pixels

Representing an in-copyright painting by facts and descriptions.

| Source | Status | Use |
|---|---|---|
| **(i) Facts and structured tags** | Facts are not copyrightable (17 USC 102(b); Feist). [V] A rich subjective taxonomy could carry thin protection in its selection and arrangement. [M] | Title, painter, date, medium, size, museum: free |
| **EU database right** | Protects against extracting a substantial part of a database made with substantial investment, for 15 years. Only EU makers qualify. [V] https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:31996L0009 | Bulk-taking an EU museum's catalogue engages it unless the data is CC0. Many are. Check each |
| **(ii) Wikidata, including "depicts" (P180)** | CC0. [V] https://www.wikidata.org/wiki/Wikidata:Copyright Commons structured data is CC0 too. [V] | **The cleanest tag source.** No conditions |
| **(iii) Wikipedia text** | CC BY-SA 4.0. Credit, link the licence, mark changes, share adaptations alike. [V] https://en.wikipedia.org/wiki/Wikipedia:Reusing_Wikipedia_content | An extract shown beside other content does not put the rest of the page under share-alike. A rewritten summary is an adaptation and must be BY-SA. [V] https://creativecommons.org/faq/ |
| **(iv) Museum descriptions** | Copyrighted unless licensed. Open: AIC `description` (CC BY 4.0), Cleveland (CC0), National Gallery London narrative text (CC BY 4.0), Louvre entry text (Etalab). [V] | Use the open ones with credit. Link to the rest |
| **(v) A description written by a vision-language model** | See below | |

**Is a model-written description a derivative work?**

- A work is derivative only if it substantially copies protected expression from the original (Litchfield v. Spielberg, 9th Cir. 1984). [V] https://law.resource.org/pub/us/case/reporter/F2/736/736.F2d.1352.83-6045.html
- A short description ("a woman in blue at a window, muted palette") records subject and facts about the picture, not its pictorial expression. [I]
- **No case was found on a text description of a painting**, nor on audio description or alt text. This is inference from general principle.
- The cautionary cases are about text retelling text. Castle Rock v. Carol Publishing (2d Cir. 1998): a trivia book about Seinfeld infringed. [V] https://law.resource.org/pub/us/case/reporter/F3/150/150.F3d.132.97-7992.html Warner Bros. v. RDR Books (S.D.N.Y. 2008): the Harry Potter Lexicon took too much. [V2]
- They translate weakly. [I] Words cannot reproduce line or colour. The risk rises with exhaustive, element-by-element descriptions, or text detailed enough to work as a prompt that regenerates the picture.

**The framework's felt block is the safest form of this.** A fixed vocabulary of felt-response words (calm, tense, eerie) marked for a painting is about as far from pictorial expression as a description gets. [I]

**Does making the description raise the same question as an embedding?** Yes. [I] The image is fetched and passed through a model; that is the same intermediate copy, with the same fair-use and mining analysis as section 4.1. Two additions:

- Sending the image to a hosted model is one more copy and a transmission to a third party. Read the provider's terms on inputs and retention. A local open-weights model avoids this.
- The owner probably has no copyright in unedited model output. The Copyright Office requires human authorship (Part 2 report, January 2025). [V] https://www.copyright.gov/ai/ Thaler v. Perlmutter was affirmed in March 2025 and review was denied in March 2026. [S] So label the descriptions CC0 or "no rights claimed"; a CC BY label would claim a right that may not exist.

---

## 7. Datasets and model licences

### 7.1 Datasets

- **ArtEmis:** released under its own terms of use, accepted through a form. The terms text could not be opened. Annotations sit on WikiArt images that users supply themselves. [V] https://www.artemisdataset.org/
- **ArtELingo:** non-commercial research and education only; sharing only with people who accept the terms. [V] https://huggingface.co/datasets/youssef101/artelingo
- **huggan/wikiart on Hugging Face:** licence "unknown"; the card says non-commercial research only. [V] https://huggingface.co/datasets/huggan/wikiart
- FRAMEWORK.md already says ArtEmis is used to check predictions and is never shipped. That is the right position. Nothing derived from it should ship either.
- **LAION:** LAION-5B was withdrawn in December 2023 and reissued as Re-LAION-5B in August 2024. [V] https://laion.ai/blog/relaion-5b/ No court has held that weights trained on LAION are infringing. [M] An MIT licence on weights gives no warranty about the training data.

### 7.2 Encoders

| Encoder | Licence | Source |
|---|---|---|
| DINOv2 | Apache-2.0 | [V] https://raw.githubusercontent.com/facebookresearch/dinov2/main/LICENSE |
| DINOv3 | Custom "DINOv3 License" | [V] https://raw.githubusercontent.com/facebookresearch/dinov3/main/LICENSE.md |
| SigLIP 2 | Apache-2.0 | [V] https://huggingface.co/google/siglip2-base-patch16-224 |
| CSD | Code MIT; weights CC BY 4.0 | [V] https://github.com/learn2phoenix/CSD ; https://huggingface.co/tomg-group-umd/CSD-ViT-L |
| OpenAI CLIP | MIT | [V] https://raw.githubusercontent.com/openai/CLIP/main/LICENSE |
| Meta Perception Encoder | Apache-2.0 | [V] https://raw.githubusercontent.com/facebookresearch/perception_models/main/LICENSE.PE |

**Do these licences limit shipping vectors?**

- Apache-2.0 attaches its conditions to the "Work" and "Derivative Works" of it. It does not mention output. [V] https://www.apache.org/licenses/LICENSE-2.0.txt An embedding is not a copy or a modification of the weights, so nothing passes through. [I] MIT is the same. [M]
- CC BY 4.0 on the CSD weights requires credit when sharing the weights or adaptations of them. Crediting CSD in the vector file is cheap and prudent. [I]
- **DINOv3 is different.** Its licence lists prohibited end uses, requires acknowledgement in publications, flows down on redistribution, and terminates if the user sues alleging that the materials or outputs infringe. [V] Prefer DINOv2 unless there is a reason not to.
- CSD was trained on LAION-Styles with artist names as the stand-in for style. [M] That is a provenance note, and FRAMEWORK.md already records the leak.

### 7.3 What a shipped vector file should carry

Drawing on Datasheets for Datasets [V] https://arxiv.org/abs/1803.09010 , the Croissant metadata format [V] https://docs.mlcommons.org/croissant/docs/croissant-spec.html and Hugging Face dataset cards [V] https://huggingface.co/docs/hub/datasets-cards .

File level:

- Encoder name, version, checkpoint identifier and SHA-256 of the weights
- Encoder licence and attribution line
- Preprocessing: resize, crop, colour handling, pooling, final dimension, quantisation
- Library versions and creation date
- The statement "this file contains no images"
- Licence for the vectors: CC0, with a note that copyright in machine-computed vectors is doubtful
- A contact and takedown address
- Intended uses and uses that are out of scope

Per row:

- Wikidata identifier
- Image source URL
- The source's licence or rights statement, as a URI
- Retrieval date and a hash of the image file
- The public-domain tier from section 1.4, and the fields it was computed from
- For any description: its source (Wikidata, Wikipedia with a revision link, a named museum, or a named model)

---

## 8. Precedents

| Product | In-copyright works | Basis | Source |
|---|---|---|---|
| **Google Arts & Culture** experiments | Whatever partners supply | Contract. Google accepts only "copyright-free or copyright-cleared" images; the partner clears rights | [V] https://support.google.com/culturalinstitute/partners/answer/6002688 |
| **Artsy** | Shown, licensed from galleries | Contract. Its public API was limited to public-domain works and is being retired | [V] https://developers.artsy.net/ |
| **WikiArt** | Shown with a "Fair Use" label | Its own fair-use claim, plus removal on notice. Guernica was offered at 3,369 px wide, so "low resolution" does not hold | [V] https://www.wikiart.org/en/pablo-picasso/guernica-1937 |
| **Barnes Foundation** (visual similarity since 2017) | Shown at low resolution, not downloadable, with a rights statement and ARS credit | The museum's own collection, under a fair-use statement | [V] https://www.barnesfoundation.org/collection/open-access-and-copyright |
| **Nasjonalmuseet** (Principal Components) | About a quarter of its online works are in copyright | A collecting-society agreement with BONO | [V] https://nasjonalmuseet.no/en/collection/about-the-collection/about-copyright |
| **Yale University Art Gallery** | Thumbnails of in-copyright works | Fair use, stated on its site | [V] https://artgallery.yale.edu/using-images |
| **Harvard Art Museums AI Explorer** | Machine tags and captions beside objects; inclusion of in-copyright works not verified | Own collection | [S] |
| **Met, Microsoft and MIT "Gen Studio"** | None | Built on the CC0 collection | [S] |
| **imgs.ai** | None in the public tier; other collections need an approved account | Public-domain only by default | [V] https://imgs.ai/ |
| **PixPlot (Yale DHLab)** | The user's problem | Ships code; users bring images | [V] https://github.com/YaleDHLab/pix-plot |
| **TinEye** | Stores fingerprints. "We never save the images you upload" | Search-engine model | [V] https://help.tineye.com/article/244-does-tineye-keep-images-i-upload-during-a-search |
| **Same Energy** | Crawled thumbnails on its own CDN; no published takedown policy found | Search-engine model | [V] https://same.energy/about |
| **Magnus** | Pulled from the App Store in 2016 after gallery and Artsy complaints; reinstated after removing content | Tried a user-upload defence | [S] |

Five patterns exist in practice.

1. **Licensed or partner-supplied.** Google, Artsy, Nasjonalmuseet. Not open to a solo developer without deals.
2. **Public domain only.** Gen Studio, imgs.ai, AIC's recommended filter. Lowest risk; loses the twentieth century.
3. **Low-resolution display under a fair-use statement.** Barnes, Yale, WikiArt. Note that Barnes and Yale are museums showing their own holdings, which is a stronger position than a third party's.
4. **Search-engine model.** Thumbnails or fingerprints, a link to the source, a takedown process. Magnus shows where it fails: when the product replaces something the rights-holders themselves sell.
5. **Code only.** PixPlot. This is the library half of painting2vec.

No precedent was found for a third-party site that shows a curated map of in-copyright paintings with thumbnails and has had that tested.

---

## 9. Recommendation

### 9.1 Tiered policy

Risk levels: **Low** = settled or licensed. **Moderate** = defensible, untested for this use. **High** = likely to draw a credible claim.

| Category | (1) Compute on | (2) Ship vectors | (3) Thumbnail | (4) High resolution | (5) Description |
|---|---|---|---|---|---|
| **Public domain, museum CC0 image** (Tier A or A-strict) | Yes. **Low** | Yes. **Low** | Yes, self-hosted or from the museum. **Low** | Yes. Museum IIIF where embedding is allowed (AIC, SMK, Rijksmuseum), or self-hosted tiles. **Low** | Wikidata; the museum's text where open (AIC, Cleveland); Wikipedia with BY-SA credit; felt words. **Low** |
| **Public domain, Commons image only** | Yes. **Low** in the US | Yes. **Low** | Yes, with the file's credit. **Low** in the US; **Moderate** for visitors in Spain, the Nordics, France and the UK | Yes, same caveat. Prefer self-hosting to hotlinking Commons. **Low to Moderate** | As above. **Low** |
| **In copyright, with a licensed or open image** (rare: an artist's own CC licence, or a paid licence) | Yes, within the licence. **Low** | Yes. **Low** | Yes, on the licence's terms: no crop, credit line, size cap. **Low** | Only if the licence says so. It usually does not | As above, plus anything the licence requires. **Low** |
| **In copyright otherwise** | From a lawful source, then discard. **Moderate** in the US. **High** in the EU where an opt-out exists | Pooled, reduced vectors only. **Moderate**: no court has ruled | **No.** Show a neutral marker and link out. A self-hosted thumbnail is **High** | **No.** No defence | Wikidata facts, felt words, link out. **Low.** Keep model-written text short |

Residual uncertainty in each cell:

- **Row 1** depends on getting "public domain" right. A Tier B or Tier C work filed here by mistake becomes row 4.
- **Row 2** rests on Bridgeman, a district court decision, and on THJ, which is not about photographs.
- **Row 4, compute:** Ross is weeks old and could be reheard. The Ninth and Second Circuits have not spoken on non-generative analysis.
- **Row 4, vectors:** Getty v Stability is under appeal. The inversion research is moving.

### 9.2 The cheapest way to include twentieth-century masters

**Option 1: vector, facts, link out, no image.** Recommended.

- The painting appears on the map as a neutral marker with title, painter, date and museum from Wikidata.
- Its neighbours are listed. Public-domain neighbours show their images.
- A link goes to the holding museum's page for the work.
- Cost: nothing. Risk: Moderate on the compute and the vector, Low on everything shown.
- It needs a change to FRAMEWORK.md section 7, which admits a painting to the canon only if its image can be shown. A second class of entry, "mapped but not shown", would have to be added.
- Source the image for the compute step from a lawful, non-opted-out place, and record where. Skip any source whose terms forbid mining (Tate, ADAGP repertoire fetched from EU servers).

**Option 2: a licensed thumbnail.**

- ARS covers every painter named in the brief and quotes per request.
- The only published price found is VG Bild-Kunst's: EUR 2 to 11 a month for a private site with up to 50 images, and hundreds of euros a month at 500 to 1,000 images. That is a German licence; a worldwide site needs more than one society or a broader grant.
- The conditions matter more than the price: no crops, no recolouring, a size cap, a credit line, and anti-download protection.
- Realistic only for a short list of works. Get a quote from ARS before designing around it.

**Option 3: Route A for the user.** The library computes on whatever the user supplies, locally. The owner ships nothing in-copyright at all. This already works and should stay the default answer for in-copyright work.

### 9.3 Design rules that follow

1. Compute the public-domain tier per painting from section 1.4 and store its inputs. Fail closed.
2. Serve Tier A works worldwide. Leave Tier B and Tier C out of the first canon; they are the works most likely to be misfiled.
3. Take images from CC0 museum programmes first, Commons second. Send a real User-Agent. Stay inside the published rate limits.
4. Do not use Harvard's API, WikiArt, Web Gallery of Art or Google Arts & Culture as image sources.
5. Ship pooled, reduced, quantised vectors. Never patch tokens.
6. Keep the mirrored and recoloured experiments on public-domain works, or keep them unpublished.
7. Publish a takedown address. Register a DMCA agent if anything user-supplied is ever stored.
8. Run Route A locally or in the browser. Store nothing.
9. Keep scraping instructions out of the documentation.
10. Record the encoder, its licence and each image's source in the vector file.

### 9.4 The three biggest risks

1. **Misclassifying a work as public domain.** The 1931 to 1977 US rules and the US-only and Europe-only traps cannot be resolved from Wikidata. One mistake turns a full-resolution display into the highest-exposure case in this document.
2. **Showing any image of an in-copyright painting.** A thumbnail on an art map is weak fair use after Warhol, there is a priced licensing market, and ARS represents every estate named here.
3. **Acquiring and publishing for in-copyright works.** Ross shows non-generative analysis can lose on fair use; the EU opt-outs exist for the artists who matter; and nobody has ruled on whether a vector is a copy.

---

## 10. What a lawyer must confirm before launch

1. **Fair use of the compute step after Ross**, for a non-commercial similarity index, and the factor-four exposure from image-licensing markets.
2. **Whether publishing pooled vectors of in-copyright paintings is a reproduction**, in the US and in the EU and UK.
3. **Exposure abroad for a US individual.** Jurisdiction, enforceability of a foreign judgment, and whether to geo-limit. This decides how much weight the EU opt-outs and moral rights carry.
4. **The public-domain rule in section 1.4**, especially publication under the 1909 Act, and the URAA analysis for émigré painters.
5. **Photographs of public-domain paintings outside the US:** the UK after THJ, Spain, the Nordics, France, and whether Italy's heritage code can reach a non-Italian site.
6. **Museum terms as contract:** whether a browsed page binds, what a keyed API binds, and the National Gallery's "no database" clause.
7. **Whether any thumbnail of an in-copyright work is defensible**, and which circuit's embedding rule applies to the owner.
8. **Registration status** of specific works, which sets whether statutory damages are in play.
9. **Whether the Digital Services Act or the UK Online Safety Act attaches** to Route A, and whether a no-storage design avoids both.
10. **Terms of ArtEmis, DINOv3 and any hosted vision-language model**, if any of them is used.
11. **Actual quotes and terms from ARS**, if Option 2 is pursued.

## 11. What could not be verified

- **Opinions not read in full:** Bridgeman, Meshwerks, Kelly, Perfect 10, Authors Guild v. Google, HathiTrust, iParadigms, Hunley, Giganews, VHT v. Zillow, Cartoon Network, Meta v. Bright Data, Hachette, the Hamburg and Munich judgments, Thaler.
- **2026 rulings known only through secondary sources:** Emmerich (5th Cir.), Richardson (2d Cir.), Google v. SerpApi, Reddit v. SerpApi, Doe v. GitHub, the status of every pending AI case, the UK government's March 2026 report.
- **Terms pages that would not open:** Prado (everything), AIC image-licensing and terms pages, the Met's Open Access policy page, Smithsonian terms of use, Yale LUX, DACS, ADAGP's rate card, the ArtEmis terms text, Artsy's terms.
- **Facts not confirmed:** IIIF details for the Met, NGA, Cleveland, Getty and the Smithsonian; rate limits for most European museums; whether the Stuttgart Ravensburger ruling is final; any outcome in Uffizi v. Gaultier; the painters' death years; which Google experiments include in-copyright works.
- **Questions with no authority found:** whether an embedding is a copy; whether a text description of a painting can be a derivative work; a direct comparison of pooled-vector and patch-token inversion.

## Why are these two books World neighbours? (W1_qwen_maskB_c)

Mutual nearest neighbours by different authors, not related by translation, edition, series or retelling (cosine distance):

- austen_persuasion ~ brinton_old_friends: 0.327
- james_ambassadors ~ wharton_mirth: 0.385
- wells_time ~ zamyatin_we: 0.444
- christie_styles ~ hammett_falcon: 0.525
- hardy_mayor ~ wharton_frome: 0.654
- radcliffe_udolpho ~ lewis_monk: 0.660

### The Mysteries of Udolpho (Ann Radcliffe, 1794) and The Monk (Matthew Gregory Lewis, 1796)

The three most similar chunk pairs (centred cosine; the median over all sampled chunk pairs of the two books is 0.05). The encoder saw the name-masked text; the clean text is printed.

**cosine 0.47**

- `radcliffe_udolpho` chunk 37: On the following morning, she was visited by a sister of the convent, who came, with kind offices and a second invitation from the lady abbess; and Emily, though she could not forsake the cottage, while the remains of her father were in it, consented, however painful such a visit must be, in the present state of her spirits, to ...
- `lewis_monk` chunk 97: Ambrosio was by no means disposed to grant the petition of his visitor. He refused it positively, and bad the lay-brother tell the stranger to return the next day. Matilda interrupted him. “See this woman,” said she in a low voice; “I have my reasons.” The abbot obeyed her, and signified that he would go to the parlour immediately. With ...

**cosine 0.40**

- `radcliffe_udolpho` chunk 149: He then took up the torch, and led her along the passage, at the extremity of which he unlocked another door, whence they descended, a few steps, into a chapel, which, as Barnardine held up the torch to light her, Emily observed to be in ruins, and she immediately recollected a former conversation of Annette, concerning it, with very unpleasant ...
- `lewis_monk` chunk 69: “I have been expecting you with impatience,” said she; “My life depends upon these moments. Have you the key?” “I have.” “Away then to the garden. We have no time to lose. Follow me!” She took a small covered basket from the table. Bearing this in one hand, and the lamp, which was flaming upon the hearth, in the other, ...

**cosine 0.37**

- `radcliffe_udolpho` chunk 201: The Mariner Soft came the breath of spring; smooth flow’d the tide; And blue the heaven in its mirror smil’d; The white sail trembled, swell’d, expanded wide, The busy sailors at the anchor toil’d. With anxious friends, that shed the parting tear, The deck was throng’d—how swift the moments fly! The vessel heaves, the farewell signs appear; Mute is each ...
- `lewis_monk` chunk 59: “What! is it thou?” the startled sire In sullen tone exclaimed, while ire With crimson flushed his pale and wrinkled cheek: “Wouldst thou again with amorous rage Inflame my bosom? Steeled by age, Vain boy, to pierce my breast thine arrows are too weak. “What seek you in this desert drear? No smiles or sports inhabit here; Ne’er did these ...


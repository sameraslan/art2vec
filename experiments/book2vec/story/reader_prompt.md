# Reader instructions

You are a careful reader. You will read one complete novel, supplied as numbered part files in a
directory, in order. The names of people and places have been replaced by stand-ins (Person3,
Place2); the same stand-in means the same name throughout. Stand-ins are imperfect: one person can
have two stand-ins, and some are mistyped.

Rules:

- Read every part, in order, with the Read tool. Do not skip, skim or sample. Read nothing else:
  no other directories, no web, no other files.
- Work only from what is on the page. If you think you recognise the book, do not use anything you
  remember about it. Describe what this text says.
- After each part, append to the notes file a 150-250 word note of what happened in that part
  (events, who did what to whom, changes in situation), before reading the next part.
- Use no memory, no shell, no web. Only Read for the parts and Write/Edit for your two output files.

When you have read all parts, write the output file as JSON with exactly these fields:

```json
{
  "id": "<the book id you were given>",
  "parts_read": 0,
  "story": "250-350 words. What happens, from the opening situation through the complications to how it ends. Refer to people by role and kind (a young doctor, his widowed mother), never by stand-in or name, and to places by type (a provincial town, a tropical island), never by name. Plain, concrete, in the order the events occur in the story's own time.",
  "characters": [
    {"role": "who this is, as a kind of person", "arc": "one sentence: what changes for them"}
  ],
  "world": "60-100 words. When and where it is set as kinds of time and place, the social milieu, and what the book is about as subjects. No names.",
  "subjects": ["5-8 short noun phrases"],
  "telling": {
    "person": "first | third | mixed | other",
    "narrator": "one sentence: who tells it and from how close",
    "frame": "none | framed | letters or documents | multiple narrators",
    "order": "chronological | flashbacks | fragmented",
    "time_span": "roughly how much story time passes"
  },
  "felt": {"bleak": 0, "melancholy": 0, "tense": 0, "eerie": 0, "dreamlike": 0, "warm": 0,
           "funny": 0, "serene": 0, "claustrophobic": 0, "wistful": 0, "menacing": 0,
           "exhilarating": 0, "tender": 0, "bitter": 0, "playful": 0, "solemn": 0, "anxious": 0,
           "hopeful": 0, "cold": 0, "lush": 0, "grotesque": 0, "disorienting": 0, "cosy": 0,
           "desolate": 0},
  "recognition": {"recognised": false, "title_guess": "", "author_guess": "", "confidence": 0.0,
                  "at_part": 0, "clue": "what gave it away, if anything"}
}
```

- `characters`: the three to six who matter most.
- `felt`: 0 = not at all, 1 = a little, 2 = clearly, 3 = dominant. Score what reading the book does
  to a reader over its whole length, not what it depicts.
- `recognition`: answer honestly, last. It is a measurement, not a test you can fail. `at_part` is
  the part where you first felt you knew the book.

Finish by replying with one line: the id, parts read, and your recognition answer.

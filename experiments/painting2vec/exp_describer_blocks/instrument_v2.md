# Painting description instrument (v2)

You will be given a list of image files. Each is a photograph of a painting. For every image, look at the picture and fill in the record below. Describe what you see in this picture, not what you know about it. If you think you know the painting, set that aside while you mark the first five sections; the last section is where you say so.

Mark every field for every image. Use the whole range of each scale across the batch; most felt words should be 0 for most pictures.

## Record

Return one JSON object per image with exactly these keys.

### `felt` : what the picture does to a viewer

Rate each word 0 to 3 for how strongly the picture, as it looks, produces that feeling or atmosphere in someone looking at it. 0 = not at all, 1 = slightly, 2 = clearly, 3 = strongly. Integers only. Rate the feeling, not the subject: a picture of a party can feel desolate.

`calm`, `tense`, `tender`, `eerie`, `festive`, `desolate`, `joyful`, `melancholy`, `awed`, `uneasy`, `intimate`, `playful`, `solemn`, `alarming`, `sensual`, `lonely`, `hopeful`, `oppressive`, `dreamlike`, `energetic`, `still`, `warm`, `cold`, `mysterious`

(`awed` = it inspires awe; `alarming` = violent or frightening; `still` = a hush, a sense that nothing moves; `warm` and `cold` are feelings of emotional warmth or chill, not colour temperature.)

### `subject` : what is visibly there

Only what can be seen. Not who the figures are, not what the scene means, not the story it illustrates. A woman holding a wheel is "woman, wheel", not a named saint. If the picture depicts nothing, say so with zeros and `"setting": "none"`.

- `people`: one of `"0"`, `"1"`, `"2"`, `"3-5"`, `"6+"` (human or human-like figures, including tiny distant ones)
- `animals`: one of `"0"`, `"1"`, `"2"`, `"3-5"`, `"6+"` (real or imaginary creatures)
- `setting`: one of `"interior"`, `"landscape"`, `"townscape"`, `"seascape"`, `"garden"`, `"sky_or_heaven"`, `"plain_background"`, `"mixed"`, `"none"`
- `things`: an object with every one of the following keys set to 1 (visibly present) or 0 (not visible):
  `sky`, `clouds`, `sun_or_moon`, `water`, `trees`, `mountains_or_hills`, `rocks`, `field_or_grass`, `flowers`, `fruit_or_food`, `snow_or_ice`, `fire_or_smoke`, `buildings`, `window_or_door`, `furniture`, `bridge`, `road_or_path`, `boat_or_ship`, `cart_or_carriage`, `horse`, `dog`, `cattle_or_sheep`, `bird`, `fish`, `other_animal`, `man`, `woman`, `child`, `old_person`, `nude`, `crowd`, `dead_or_wounded_body`, `soldier_or_armour`, `weapon`, `book_or_paper`, `musical_instrument`, `vessel_or_tableware`, `curtain_or_drapery`, `hat_or_headdress`, `jewellery_or_crown`, `flag_or_banner`, `halo`, `wings`, `cross`, `skull_or_skeleton`, `written_text`
  (`nude` = an unclothed or mostly unclothed human body; `crowd` = more than about ten figures; `child` includes infants; `halo`, `wings`, `cross` are marked only as visible things; `written_text` = legible or illegible writing, inscription, seal or signature large enough to notice.)
- `main_action`: free text, 8 words at most, what is happening (e.g. "woman pours milk from a jug", "nothing; empty landscape")
- `tags`: up to 8 short free tags, lower case, for visible things not covered above

### `manner` : how it is rendered

Integers 0 to 4.

- `abstraction`: 0 lifelike, 4 non-representational
- `contour`: 0 forms bounded by clear line or edge, 4 forms dissolved into paint or atmosphere
- `finish`: 0 smooth with no visible strokes, 4 broken with visible strokes or marks throughout
- `detail`: 0 sparse and summary, 4 minute detail everywhere
- `depth`: 0 flat pattern on the surface, 4 deep modelled space
- `palette_breadth`: 0 one hue or monochrome, 4 many distinct hues
- `saturation`: 0 grey or muted, 4 vivid
- `colour_temperature`: 0 cool (blue, green, grey), 2 balanced, 4 warm (red, orange, brown, gold)
- `darkness`: 0 very light overall, 4 very dark overall
- `contrast`: 0 even light, 4 strong light against dark
- `crowding`: 0 mostly empty, 4 packed edge to edge
- `symmetry`: 0 strongly asymmetric, 4 strictly symmetric
- `closeness`: 0 distant view, 4 close-up
- `edge_hardness`: 0 every edge soft or blurred, 4 every edge crisp and sharp
- `outline`: 0 no drawn outlines anywhere, 4 every form enclosed by a drawn line
- `stroke_direction`: 0 no stroke direction to be seen, 4 visible strokes run in strong directions or rhythms across the whole surface
- `flat_colour`: 0 colour graded continuously inside every form, 4 forms filled with flat unmodulated colour
- `modelling`: 0 forms not shaded at all, 4 forms modelled in the round by strong light and shadow
- `ornament`: 0 no pattern or ornament, 4 surface covered with pattern (patterned textiles, gilding, decorative borders, repeated motifs)
- `idealisation`: 0 particular and unflattering (individual faces, blemishes, awkwardness, accident), 4 idealised or conventional types. With no figures, judge the things or the land the same way.
- `distortion`: 0 natural proportions and shapes, 4 strongly elongated, simplified or distorted shapes

### `space` : how depth is shown

- `depth_cues`: an object with every one of the following keys set to 1 (the picture uses it) or 0:
  `linear_perspective` (receding lines that converge), `atmospheric_perspective` (distance shown by paler, bluer or hazier colour), `overlap` (nearer things cover farther ones), `size_diminution` (farther things drawn smaller), `cast_shadows`, `foreshortening` (bodies or objects shortened because they point towards the viewer), `stacked_space` (farther things placed higher up the surface with little or no change of size; bird's-eye or tilted ground)

### `colour` : the colours of the painting

Judge the painted surface. Ignore a frame, a mount or a wall if the photograph includes one. Judge what the painting's colours are, as well as you can tell, not how this particular photograph happens to be lit or tinted.

- `hues`: an object with every one of the following keys set to 1 (that hue family covers about a tenth of the surface or more) or 0:
  `red`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `brown`, `gold`, `black`, `white`, `grey`
  (`brown` includes ochre, tan and umber; `gold` is metallic gold or gilding only; `white` includes cream and bare pale paper or silk; skin goes under whichever family it looks like.)
- `main_hue`: the one family from that list that covers the most surface
- `accent_hue`: one family from that list for a small area of strong colour that stands out against the rest, or `"none"`
- `value_key`: one of `"high"` (mostly light tones), `"mid"`, `"low"` (mostly dark tones)

### `recognition` : answered last

- `recognised`: true or false. Do you recognise this specific painting?
- `title`: your title for it if recognised, else `""`
- `painter`: the painter if recognised, else `""`
- `confidence`: 0 to 3 (0 = not recognised, 1 = a guess, 2 = fairly sure, 3 = certain)
- `guess_school`: your best guess at the painter or school from the look of it (always answer)
- `guess_century`: an integer century, e.g. 17 (always answer)

## Output

Write one JSON file to the output path you are given, and nothing else to disk:

```json
{"batch": 0, "records": [
  {"code": "abc1234",
   "felt": {"calm": 0, "tense": 0, "...": 0},
   "subject": {"people": "1", "animals": "0", "setting": "interior",
               "things": {"sky": 0, "...": 0},
               "main_action": "", "tags": []},
   "manner": {"abstraction": 0, "...": 0},
   "space": {"depth_cues": {"linear_perspective": 0, "...": 0}},
   "colour": {"hues": {"red": 0, "...": 0}, "main_hue": "brown", "accent_hue": "none", "value_key": "mid"},
   "recognition": {"recognised": false, "title": "", "painter": "", "confidence": 0,
                   "guess_school": "", "guess_century": 17}}
]}
```

One record per image, in the order given, every key present, valid JSON.

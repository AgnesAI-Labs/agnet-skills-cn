# Evidence-based video quality review

Review against the user's stated goal and the intended relationship between
shots. Do not apply a universal aesthetic or claim checks AgnesCode cannot
actually perform.

## Contents

- Use truthful acceptance language
- Convert hard requirements into evidence gates
- Review keyframes before generation
- Review each generated segment
- Review actual cut boundaries
- Review audio and subtitle timing
- Review the assembled film
- Respect inspection limits
- Repair narrowly and bound retries

## Use truthful acceptance language

Keep artifact arrival, technical validity, visual review, and acceptance
separate.

- A returned path means `generated-uninspected`.
- A successful `probe` proves decodability and reports technical properties.
- A contact sheet supports broad visual sampling only.
- Inspected first and last frames support boundary findings only.
- `accepted` means the evidence required for the shot's intended use passed.
- `rejected` means a material failure and required recheck are recorded.

Never use “通过质检”, “连续”, “同步”, or “最终完成” as progress language before
the relevant evidence exists. A transport-level success containing an error
payload is not a generated artifact.

## Convert hard requirements into evidence gates

Identify requirements whose failure would invalidate the shot or sequence, such
as recurring identity, wardrobe construction, prop geometry and hand, exact
screen direction, readable product form, narration placement, subtitle sync, or
duration tolerance.

For each hard requirement record:

- the accepted reference or expected observable fact;
- the file and time or boundary that must show it;
- the evidence used to accept or reject it;
- the repair and recheck needed after failure.

Repeated descriptive text does not prove visual continuity. When the generation
strategy cannot reliably preserve a hard requirement, either redesign the shot
so the requirement is not exposed or record a material tradeoff.

## Review keyframes before generation

Inspect every keyframe that constrains a continuity-critical video. Check only
attributes relevant to the shot:

- identity and stable physical features;
- wardrobe, props, object counts, hand, and object state;
- location layout, time, lighting direction, palette, and style;
- camera height, framing, screen direction, and composition;
- required starting or ending action state;
- hands, faces, text, logos, or geometry expensive to repair after animation.

Compare a shared boundary with both neighboring shot purposes. Accept it only
when it can credibly end one segment and begin the next. When only one reference
is supported, treat a planned end frame as evidence, not a pretend tool input.

## Review each generated segment

Run `probe`. Reject or repair when the video is missing, undecodable, has
incompatible technical properties, or contains unexpected streams that cannot
be normalized safely.

Create and inspect a modest contact sheet. Extract exact first or last frames
when boundaries matter. Review:

- whether the shot fulfills its one intended purpose;
- subject, action, camera behavior, setting, and intentional ending;
- identity, wardrobe, prop, location, palette, lighting, and style consistency;
- object counts, hand use, faces, text, logos, and geometry;
- duplicated subjects, disappearing objects, transformations, frozen or
  corrupted tails, and unwanted camera motion;
- whether the actual ending is safe to reuse.

Do not accept a segment because only its first frame matches. Do not propagate a
tail until it has been extracted and inspected. Scale sampling with duration,
action complexity, and defect risk. Start, middle, and end coverage is the
minimum shape of evidence, not a fixed frame count; add samples for each
material action phase so a long unsampled interval cannot hide a transformation,
freeze, duplicated subject, or broken motion.

## Review actual cut boundaries

Review the outgoing frame from the chosen trim and the incoming frame from the
next chosen trim. Recheck after any trim, reorder, transition, speed change, or
render that changes timing.

For continuous action, check physical state, action phase, identity, wardrobe,
prop state, hand, location, lighting, screen direction, eyeline, camera height,
scale, and movement. Reject accidental jumps, duplicate action, impossible
position, or visible style collapse.

For a sequential scene, confirm preserved story facts remain understandable and
intentional changes read as a cut. For montage, prioritize rhythm, contrast,
theme, and legibility rather than physical continuity.

A broad final contact sheet cannot substitute for exact boundary evidence. A
dissolve cannot repair contradictory subject or object state.

## Review audio and subtitle timing

Treat audio stream presence, audible content, narration placement, transcript,
and subtitle synchronization as different claims.

For narration or dialogue:

1. Synthesize and probe one representative semantic unit before batching;
   record the selected voice/backend and measured cadence.
2. Keep later speech assets short enough to serve as defensible caption units,
   then probe every source and record its actual duration.
3. Choose and record each intended start on the picture timeline.
4. Place it with deterministic timing, such as
   `add-audio --start-at <seconds>`.
5. Build subtitle cues from the same start and actual spoken duration rather
   than an approximate shot label.
   When phrase-level timestamps are unavailable, use one cue for a short
   narration over the audible interval instead of inventing timing for pieces
   of the sentence.
6. Confirm every cue starts at or after zero, ends before the final duration,
   and overlaps the intended audible interval.
7. Probe the rendered file and verify returned audio timing metadata.
8. Inspect sampled subtitle frames for safe margins, readability, line breaks,
   terminology, and punctuation.

For multiple timed audio assets, preserve one explicit timeline with the exact
source path, start, source duration, end, loop behavior, and volume of every
track. Prefer the bundled `mix-audio-timeline` operation, whose returned track
metadata is the timing evidence for subtitles and downstream reports. If the
first asset starts after picture time zero, verify the mix remains anchored at
zero rather than allowing a muxer to normalize the first audible sample to
zero. A correct total audio duration does not by itself prove that internal cue
positions survived mixing.

Accept the mix only when one successful timeline result reports the expected
track count and exact source paths. If mixing times out or fails, treat any
partial output as untrusted and probe it before deciding whether it exists at
all. Retry or repair the same manifest into a fresh output after diagnosis.
Never emulate a multi-track timeline by repeatedly adding one audio file to an
evolving video; successive mixes can overwrite the source, attenuate earlier
speech, and silently change placement.

Inspect every risk-selected time returned by subtitle burn-in. The first cue is
not representative of a long program: include the longest rendered line, the
cue with the most explicit lines, and the final cue. Treat approximate display
column counts as risk selection only; accept layout from the rendered frame,
not character count. Rewrap, reduce size, or repair only affected cues when text
crosses safe margins or is clipped.

Use the subtitle helper's canvas-derived sizing unless the user specifies a
visual style. Its font, outline, and vertical-margin overrides are output-pixel
values. A cue that fails the default two-line preflight must be split and
retimed at semantic speech boundaries, or deliberately rendered with a smaller
size or higher line limit and then inspected. Do not allow one long cue to force
captions across most of the frame.

If playback, waveform analysis, or transcription is available, use it for
material dialogue requirements. Otherwise state that pronunciation, acting,
intelligibility, exact word timing, and loudness balance remain unverified.
Never label subtitles synchronized merely because both an audio stream and an
SRT file exist.

## Review the assembled film

Probe each candidate render and inspect broad coverage plus critical boundaries.
Check:

- required streams, duration tolerance, canvas, orientation, frame rate, and
  container;
- whether every shot advances story, explanation, mood, evidence, or an edit
  bridge;
- shot order, pacing, reactions, demonstrations, and motivated transitions;
- black gaps, duplicate segments, frozen tails, missing shots, corrupt frames,
  or unintended level changes;
- recurring identity, products, props, locations, palette, lighting, wardrobe,
  and style at the strength required by the request;
- exact picture duration against the user's hard range and the accepted-clip
  ledger, including transition overlap rather than planned labels;
- every planned narration/dialogue path against the successful timeline
  result, plus subtitle cues from its actual values;
- an intentional ending rather than the accidental tail of the final clip.

For a promised mask, overlay, title replacement, or removal, inspect an exact
frame at a time where the original unwanted content would be visible. The
absence of a defect later in a generated shot does not prove that it was covered
earlier, and an instruction or subtitle event is not evidence that a compositor
operation occurred.

Inspect a new render after an edit that changes timing, canvas, audio layout,
subtitles, or boundaries. Do not assume a deterministic operation used the
intended inputs merely because it exited successfully.

Before registration, reconcile the production record with the exact render
inputs. Every included shot must have an accepted path or a disclosed material
limitation, superseded strategies must not look active, and every claimed local
repair must point to its post-render evidence.

## Respect inspection limits

Separate evidence from inference:

- probe does not prove visible content or audible quality;
- contact sheets do not prove motion, exact timing, or audio;
- endpoint frames do not prove the middle of a segment;
- audio duration does not prove wording, pronunciation, or intelligibility;
- visual inspection does not prove provenance, rights, or factual accuracy.

State material limits in the production record and final delivery. Ask for a
human listen or review only when it is an actual acceptance requirement and no
available capability can inspect it—not as a routine workflow checkpoint.

## Repair narrowly and bound retries

Log each material issue with:

- **Evidence:** exact file, time range or boundary, and observation.
- **Expected:** user requirement, accepted reference, shot purpose, or neighbor
  constraint.
- **Repair scope:** reference, generation, cut, timing, subtitle cue, narration
  placement, mix, or render.
- **Verification:** evidence needed after repair.

Prefer the smallest repair that can satisfy the expectation. Reinspect the
repaired layer and affected boundaries. Respect active retry ceilings; do not
disguise repeated attempts as new workflow steps. After the same failure
persists without improvement, change strategy or request a material tradeoff.

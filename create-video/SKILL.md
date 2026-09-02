---
name: create-video
description: Plan, generate, assemble, inspect, and revise videos from text, images, generated clips, audio, subtitles, or user-supplied media. Use for multi-shot or long-form video, short drama, explainer, ad, montage, narrated video, continuity across clips, keyframe or storyboard planning, autonomous end-to-end production without routine checkpoints, local editing, voice-over, subtitle burn-in, or any request that needs more than one isolated generation call.
author: agnes
version: "1.0"
tags:
  - video
  - media
  - production
  - workflow
---

# Create Video

Own the requested deliverable through the normal AgnesCode agent loop. Treat
generation tools and bundled scripts as atomic capabilities. Make creative,
continuity, inspection, repair, and operation-order decisions from the user's
goal, active tool contracts, and observed media. Do not instantiate a fixed
video workflow or assume that every request needs the same stages.

## Own the interaction policy

Treat an explicit end-to-end request such as “直接做到最终成片”, “不用再问我”,
or “由你决定” as standing authorization for normal, in-scope, reversible
production work. Continue automatically through generation, inspection, local
post-production, repair, rendering, and artifact registration. Progress updates
must be non-blocking; never ask the user to reply “继续” merely to advance the
agent loop.

Ask only when continuing requires a material user choice, new authority, paid
or online capability outside the accepted scope, missing user-owned input,
rights or safety confirmation, or a quality/cost/time tradeoff after bounded
strategies fail. Honor checkpoints when the user explicitly requests them.

This Skill owns completion of the parent production. When a generation Skill is
loaded as an atomic sub-capability inside an already-authorized production,
standalone response rules such as “reply briefly and stop after success” end
that atomic substep, not the parent production. Return control to this loop,
inspect the result, and continue. Apply standalone per-request attempt ceilings
to each intended shot or asset, not as user-driven pagination of the parent
task. Hard authorization, safety, cost, schema, and retry restrictions still
apply. Keep total generation bounded by the requested deliverable. Never retry
an authentication or quota failure when the active capability forbids it, and
never hide a real runtime-imposed turn boundary as a request for creative
approval.

## Protect intent and validation integrity

- Preserve explicit requirements for content, audience, duration, format,
  language, style, supplied media, continuity, and delivery.
- Infer reversible details when reasonable. Do not silently relax a hard
  requirement to finish faster.
- Keep source media immutable. Write derived files to a dedicated directory in
  the current workspace unless the user selected another allowed destination.
- Use dynamically available AgnesCode generation tools and their active
  schemas. Never search for credentials, call hosted media APIs from shell,
  reproduce provider polling, or bypass authorization, cost, retry, or safety
  limits.
- Treat a generated path as `generated-uninspected`, not accepted. A successful
  tool envelope whose payload contains an error is a failure, not a usable
  artifact.
- When the user asks for generated moving footage, a short drama, or cinematic
  video, do not silently replace available video generation with pans, zooms,
  slideshows, or other animation of still images. Use those only when they are
  intentional creative elements or a recorded fallback whose lost motion and
  continuity guarantees remain compatible with the request.
- State only checks supported by actual evidence. A contact sheet does not
  prove motion, audio, timing, identity, or cut-boundary quality.

## Run an adaptive production loop

Use the smallest useful cycle:

1. Understand the outcome and inspect supplied media.
2. Decide the purpose and neighbor relationship of the next shot or edit.
3. Choose only the references and continuity constraints it needs.
4. Record the intended action and acceptance evidence before an expensive call.
5. Take one atomic action or a safe batch of independent local actions.
6. Observe the actual result without waiting for a meaningless user
   confirmation.
7. Mark it accepted, rejected, or still uninspected from evidence.
8. Repair the smallest failing layer or continue to the next useful action.
9. Assemble and review progressively until the deliverable is defensible.

Do not impose multi-shot planning on a one-shot request. For multi-shot,
multi-turn, or autonomous work, keep one compact production record in the task
directory. Use any readable format; do not create a workflow state machine or
universal schema. At minimum keep:

- requirements and user-approved interaction policy;
- stable references and exact local paths;
- each shot's purpose, relationship, strategy, actual status, accepted path,
  and next action;
- the observed generation capability for the current run, including schema,
  reference support, retry ceiling, raw seconds per call, conservative usable
  seconds after trimming, dimensions, and frame rate;
- a picture-duration ledger that separates story beats from atomic generation
  units and accounts for accepted clip durations and transition overlap;
- continuity-relevant parameters, inspection evidence, fallback decisions,
  and known limitations;
- actual trim points, narration placement, subtitle timing, render paths, and
  final registration result.

Use truthful states such as `planned`, `generated-uninspected`, `accepted`,
`rejected`, and `blocked`. Update the record before a generation that may
interrupt the loop and immediately after inspection or a strategy change. The
record, not conversational memory or a todo list, is authoritative for resume
and final reporting. Replace or explicitly supersede obsolete active plans;
never append a correction while leaving contradictory rows looking current.

Load `references/production-guidance.md` for multiple shots, continuity,
keyframes, autonomous execution, or resume across a long run.

## Design continuity before spending generation calls

Establish only project-level references the work needs, such as character,
location, wardrobe, prop, palette, or style. Inspect every reference image with
`read_image` before accepting or using it.

Classify adjacent shots:

- **Continuous action:** preserve identity, physical state, screen direction,
  environment, and a credible visual boundary.
- **Sequential scene:** preserve necessary story facts and visual anchors while
  allowing an intentional camera or time change.
- **Independent montage:** optimize each shot for its own purpose without
  artificial frame continuity.

Choose the lightest strategy that can satisfy the relationship:

- Generate a self-contained clip directly when precise continuity is not
  required.
- Accept a first-frame reference before image-to-video when identity,
  composition, wardrobe, prop state, or location matters.
- Plan both first and end boundaries when a physical action or transition needs
  an explicit handoff. Pass both only when the active schema supports them.

When only one video reference is supported, inspect and pass the accepted first
frame, describe the intended ending concisely, then inspect the actual tail.
Reuse that tail only when it remains good enough. Never invent an `end_frame`
parameter or propagate a degraded tail.

For a shot planned from an accepted image, one failed or rejected
image-to-video attempt does not justify silently switching to text-to-video.
When the active contract permits retry, retry the same reference at least once;
for a visual-quality rejection, narrow the action or camera prompt before using
the remaining attempt allowance. Do not retry authentication, authorization,
quota, or explicitly non-retryable failures. Use text-to-video after such a
failure only when the shot is redesigned as a genuinely independent insert,
montage unit, obscured angle, or intentional scene break whose reduced
continuity guarantee still satisfies the requirement. Record the redesign
before calling it.

For continuity chains, reason in a rolling window such as `K0 -> K1`, then
`K1 -> K2`. Do not pre-generate every boundary. Generate high-risk identity,
object-state, close-up, action, and transition evidence before low-risk
atmosphere or montage shots consume the budget.

If a reference-based strategy becomes unavailable and the fallback removes its
continuity guarantee, record that downgrade before acting. Use an intentional
cut, obscured angle, insert, new accepted keyframe, or another defensible
strategy. Do not accept independent text-to-video as proof of hard identity or
prop continuity merely because the prompt repeats the same description.

## Use generation capabilities honestly

Select capability by intent and confirm the active schema before calling:

- Text-to-image creates a new reference or keyframe.
- Image editing creates a controlled variation of an accepted image.
- Text-to-video creates a self-contained moving shot.
- Image-to-video animates from an accepted visual reference.

Choose text-to-video as an up-front shot strategy for self-contained material,
not as an invisible error handler for a planned reference-controlled shot.

Follow active prompt and retry contracts. Preserve the user's wording as the
original prompt when required. Keep each shot prompt concise: one purpose, one
visible action, camera behavior, and only relevant continuity anchors. Preserve
exact local paths and metadata. Use stable labels instead of “the latest image”
once several assets exist.

Before repeating an expensive generation configuration, validate it with one
representative shot: confirm the active schema, call limits, returned duration,
dimensions, frame rate, motion, and suitability for the planned edit. Treat the
observed result as authoritative. Before batching, convert the requested
picture-duration range into feasible atomic generation units using conservative
usable seconds per call and transition overlap. A creative beat that needs more
time than one call can supply must be planned as linked units or intentional
coverage before generation, never represented as one impossible-duration row.
Reconcile the full planned sequence against the lower duration bound and keep a
small editorial coverage reserve; do not generate arbitrary filler near the end
or discover a provider duration limit only after a full batch. Audio overlays do
not add picture duration.

Assemble only the explicit ordered list of accepted paths in the production
record. Never discover render inputs by globbing or sorting a generation
directory: rejected attempts, retries, alternates, and late title cards must not
enter the film merely because they exist or were generated earlier.

Do not reload the same Skill or reference when its current contract is already
available and unchanged. After a successful generation, return to this parent
loop, record the result as uninspected, and inspect it before another expensive
generation that depends on it.

AgnesCode generation results may provide paths and metadata without placing
media bytes in model vision context. Inspect returned images with `read_image`;
inspect videos through extracted frames or contact sheets. Never claim visual
QA from a path or UI preview alone.

## Inspect before accepting

For an existing or returned video:

1. Run `probe` for decodability, duration, dimensions, frame rate, and streams.
2. Create a duration- and risk-proportional contact sheet and inspect it. Cover
   the start, middle, end, and each material action phase; sparse samples of a
   long generated shot do not support a whole-shot quality claim.
3. Extract exact first or last frames for continuity-sensitive boundaries.
4. Compare visible evidence with the shot purpose, hard constraints, accepted
   references, and neighboring shots.
5. Record the evidence and only then mark the shot accepted or rejected.

After trimming, recheck the new boundary. Before accepting a rough or final
cut, inspect each continuity-sensitive outgoing/incoming pair rather than
inferring continuity from a broad final contact sheet.

Load `references/quality-review.md` for acceptance language, keyframe, segment,
boundary, audio/subtitle, and final-render criteria.

## Control context growth

Long productions must not retain unnecessary repeated instructions and review
material. Load only the reference needed for the current decision. Prefer the
smallest contact sheet that gives adequate coverage, then inspect exact frames
only for material risks. Summarize accepted evidence into the production record
and do not repeatedly re-inspect accepted media without a downstream reason.

Do not trade away validation to save context. When context pressure becomes
material, compact around the production record and accepted artifact paths
rather than relying on positional conversation history.

## Use bundled scripts for deterministic local work

Supporting files are listed with resolved absolute paths when this Skill is
loaded. Use those paths because commands run in the session working directory.

Select Python 3.9 or newer:

- Windows: prefer `py -3`, then `python`.
- macOS/Linux: prefer `python3`, then `python`.

Before local operations, load `references/local-media-tools.md` and run the
relevant doctor command. Media operations use `auto` runtime selection: prefer
an already-prepared, pinned Docker FFmpeg image when the Docker engine is ready,
then fall back to already-installed native `ffmpeg` and `ffprobe`. Never install
host packages or pull an image implicitly. A missing image may be pulled only
with the explicit script flag after dependency acquisition is authorized. Local
TTS uses an already-installed native backend by default; never choose an online
TTS backend without explicit approval.

Use `scripts/media_ops.py` for inspection, frame extraction, evidence-based
trimming, concatenation, transitions, timed audio placement, multi-track audio
timelines, mixing, and subtitle burn-in. Use `scripts/tts.py` for one local
narration asset. Scripts do not decide story, shot order, continuity, or repair
policy.

For Docker-backed media work, retain the `operation_id` emitted before the first
container starts. If the shell call times out or is interrupted, use the
script's exact `cancel --operation-id` operation, then list that same operation
to verify absence before retrying. Treat any output left by interruption as
untrusted and render the recovery into a fresh path. If no ID survived, inspect
`managed-containers` and use only the fail-closed stale cleanup documented in
`references/local-media-tools.md`. Never issue broad Docker stop, kill, or prune
commands and never touch an unlabelled or unowned container. Cleaning up this
production's own interrupted operation is part of autonomous technical
recovery, not a reason to ask the user for routine confirmation.

Subtitle burn-in must pass the script's font-file and actual-glyph coverage
preflight. The script uses an existing host or explicitly supplied font, mounts
only the selected file into Docker, and fails when the renderer reports missing
glyphs. Omit subtitle sizing flags by default so the script derives safe output-
pixel sizing and margins from the probed canvas. Treat `--font-size`,
`--outline`, and `--margin-v` as output pixels, not ASS style units. Keep each
cue within the default two-line preflight by splitting and retiming speech at
semantic boundaries; do not shrink an entire long-form program merely to fit a
few overloaded cues. After burning, extract and inspect every returned
`subtitle_check_times[].time`, including the longest-line and multi-line cues;
metadata checks alone are insufficient.

Choose trim points from observed frames; never remove a universal fixed amount
from every clip. When narration should begin later than the picture, use
`add-audio --start-at <seconds>` and build subtitle cues from the same actual
start and source-audio duration. Verify the returned timing metadata and final
streams. Without phrase-level timing evidence, keep a short narration in one
cue over its audible interval instead of inventing sequential cue durations. Do
not claim synchronized subtitles when only stream presence was checked.

For several narration, dialogue, music, or ambience assets, use
`mix-audio-timeline` with one explicit JSON timeline instead of constructing an
ad hoc FFmpeg delay graph. Build captions from the returned per-track `start`
and `end` values. The command anchors silence at picture time zero so a delayed
first asset cannot cause the muxer to shift the whole program earlier.

Design narration and dialogue as caption-sized semantic units before batch TTS.
Synthesize one representative line first, record its actual duration and active
voice/backend, then use measured cadence to budget the remaining speech. Probe
every returned audio asset and rebuild the timeline from actual durations. A
multi-track mix is accepted only when one successful `mix-audio-timeline`
result reports the expected track count and exact paths. On timeout or failure,
cancel and verify absence of any reported managed Docker operation first. Probe
any reported output but treat it as untrusted; diagnose or retry the same
manifest into a fresh path. Never fall back to repeatedly applying `add-audio`
to one evolving video, because that can overwrite the source, attenuate earlier
tracks, and invalidate timing.

Keep paths quoted. Do not build shell commands from media filenames. Refuse
destructive overwrites unless replacement was explicitly requested or a
versioned output is impractical.

## Repair locally and narrowly

Classify failure before acting:

- Regenerate or revise a reference for content, identity, or physical-state
  failure.
- Change a cut point, trim, order, or motivated transition for edit failure.
- Rebuild only affected cues for subtitle failure.
- Resynthesize, reposition, or remix only affected narration for voice failure.
- Shorten, cover, reframe, or regenerate only the defective shot when possible.

Inspect the repaired layer and every boundary or render it affects. Bound
retries under the active capability contract. Change strategy when repeated
evidence shows the same repair is not improving. Ask the user only when the
remaining choice is material and cannot be inferred within the standing
authorization.

## Deliver verified artifacts

For a locally composed final result:

- Probe the file and inspect broad coverage plus continuity-critical boundaries.
- Confirm requested duration tolerance, canvas, subtitle mode, and stream
  presence.
- Verify the final picture duration from the assembled accepted clips rather
  than a planned estimate. A missed hard tolerance blocks completion.
- Reconcile every planned narration/dialogue asset with the successful final
  timeline result and verify subtitle cue timing from its actual values; state
  any audio inspection limit. Stream presence or one audible sample cannot
  prove that all tracks survived.
- Verify every promised mask, overlay, text removal, or local visual repair at
  a timestamp where the original defect would otherwise be visible.
- Reconcile the production record so every included shot and active render is
  accepted or carries an explicit material limitation; no stale `planned`
  entry or superseded strategy may support a completion claim.
- Keep editable intermediates when revision is likely.
- Register the final video and separately requested subtitle or audio files
  with `agnes_artifacts__present_artifacts`.
- Derive the final report from the production record and registered artifact,
  not memory.
- Reply with the exact registered path and material verified limitations.

Do not register a built-in generation result again when its active Skill
already presented it.

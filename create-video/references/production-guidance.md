# Adaptive production and continuity guidance

Use this reference to support decisions inside the normal AgnesCode agent loop.
It defines production invariants, not a mandatory pipeline, project schema, or
replacement runtime.

## Contents

- Set the interaction policy once
- Start with concept and content structure
- Keep one truthful production record
- Classify relationships between shots
- Establish reusable visual foundations
- Choose an adaptive keyframe strategy
- Respect the active reference boundary
- Handle capability fallback honestly
- Shape concise shot prompts
- Plan against observed atomic capability
- Spend generation calls by risk
- Control context growth
- Resume without user-driven polling
- Compose and repair from evidence

## Set the interaction policy once

Infer the interaction policy from the user's request and retain it in the
production record.

- **Autonomous:** the user asks for a complete deliverable or explicitly says
  not to ask at each step. Continue through all normal reversible production
  work. Send progress without blocking.
- **Checkpointed:** the user explicitly requests review at selected creative or
  delivery milestones. Stop only at those checkpoints.
- **Consultative:** a missing choice materially changes intent, rights, cost, or
  the acceptable outcome. Ask the smallest necessary question.

Autonomous execution is standing task authorization, not unlimited authority.
Stop for authentication, quota, new paid or online capability, missing required
user media, rights or safety issues, or a non-converging material tradeoff.
Never require “继续” merely because an atomic tool returned.

The parent production owns completion. Response-shortening rules from a
standalone generation Skill do not convert an atomic success into a user
checkpoint inside an authorized parent production. Apply standalone attempt
ceilings per intended shot or asset instead of using them to paginate the parent
task through user messages. Authorization, schema, safety, cost, and retry
restrictions remain hard limits, and the requested deliverable bounds total
generation.

## Start with concept and content structure

Clarify what the viewer should understand, feel, or do before writing prompts.
Identify audience, delivery surface, approximate duration, aspect ratio,
language, style, and non-negotiable content. Preserve supplied media or scripts
as sources rather than silently replacing them.

Choose a structure appropriate to the request. A drama may need intent, action
beats, reactions, and scene changes. An explainer may be led by narration,
demonstrations, labels, or supplied media. A montage may be organized by mood or
contrast. These are creative decisions, not fixed templates.

Give every proposed shot one clear purpose. Remove or merge a shot that does not
serve story, explanation, mood, evidence, or an edit bridge.

## Keep one truthful production record

For one isolated result, conversation context and one returned path may be
enough. For multi-shot, multi-turn, autonomous, or resumable work, keep a compact
record in the task workspace. It is the source of truth for planning, resume,
acceptance, and final reporting.

Useful facts include:

- requested outcome, delivery constraints, interaction policy, and unresolved
  material choices;
- user media and provenance or usage restrictions;
- accepted character, location, wardrobe, prop, palette, typography, voice, or
  music references;
- each shot's purpose, neighbor relationship, approximate duration, intended
  strategy, actual strategy, status, exact path, and next action;
- the current run's observed generation contract: accepted inputs, reference
  boundary, retry ceiling, returned seconds, conservative usable seconds,
  dimensions, frame rate, and relevant call limits;
- the requested picture-duration range and a live ledger of planned atomic
  units, accepted usable durations, trim loss, transition overlap, reserve, and
  remaining deficit;
- prompts, dimensions, frame rate, seed, source reference, and other
  continuity-relevant metadata;
- inspection evidence, exact boundary or time range, repair decisions,
  capability fallback, and known limitations;
- trim points, narration start and duration, subtitle cue range, render paths,
  and registered artifact identity.

Use truthful states such as:

- `planned`: no artifact exists;
- `generated-uninspected`: an artifact arrived but has not passed review;
- `accepted`: evidence supports its intended use;
- `rejected`: evidence identifies a material failure;
- `blocked`: continuation needs authority, capability, or a user tradeoff.

Never mark work complete in a todo list while the production record still
describes an obsolete strategy. Update the record before an expensive call,
after every inspection, and whenever fallback changes the guarantee.

Treat a strategy change as a record reconciliation, not an appended diary note.
Mark the prior strategy `superseded`, update every affected shot's active
strategy and next action, and leave one unambiguous current plan. Before final
registration, verify that every media item used by the render points to an
accepted path and that no included shot remains merely `planned`.

## Classify relationships between shots

Classify each important boundary before choosing generation or editing tactics.

### Continuous action

Preserve physical state, identity, wardrobe, prop state, location, time,
lighting direction, screen direction, and camera geometry needed at the cut.
The next shot must begin from a credible boundary, not merely a similar prompt.

### Sequential scene

Preserve story facts and visual anchors needed for comprehension while allowing
purposeful changes in framing, angle, action phase, or time. Do not demand
pixel-level continuity where an intentional cut communicates the change.

### Independent montage

Join shots through topic, rhythm, contrast, or mood rather than physical
continuity. Optimize independently and let editing create the relationship.

## Establish reusable visual foundations

When consistency matters, establish a small visual basis before critical clips:

- character identity, body, hair, wardrobe, and distinguishing features;
- location layout, palette, time, and lighting;
- product or prop shape, material, markings, state, and scale;
- rendering medium, texture, contrast, color, and photographic character.

Inspect every reference with `read_image`. Reject contradictions, malformed
hands, faces, text, logos, props, or geometry before animation. Do not create
references for attributes the request does not need to preserve.

## Choose an adaptive keyframe strategy

Use the least restrictive strategy that can satisfy the shot.

### Direct generation

Use text-to-video for self-contained establishing shots, atmosphere, abstract
motion, inserts, or montage material where precise starting identity and
composition are not hard requirements. Select it intentionally while planning;
do not treat it as the automatic error path for a reference-controlled shot.

### Accepted first frame

Use image-to-video from an inspected first frame when identity, composition,
wardrobe, object state, location, or camera setup must start predictably.

### Planned first and end boundaries

Plan both boundaries when a physical handoff, reveal, transformation, or
transition depends on the ending. Treat the pair as a creative constraint even
if the active runtime cannot submit both images.

For a chain, reason about `K0 -> K1`, then `K1 -> K2`. Work in a rolling window:

1. accept the next required boundary;
2. generate the segment under the active schema;
3. inspect its actual ending;
4. accept the tail, restore a planned boundary, or repair;
5. only then constrain the next segment.

This keeps the plan adaptive and prevents visual damage from propagating.

## Respect the active reference boundary

Confirm the active image-to-video schema. When it accepts one reference:

1. inspect and pass the accepted first frame;
2. describe action and intended ending concisely;
3. probe and inspect broad coverage after generation;
4. extract and inspect the exact last frame when it affects the next shot;
5. reuse the tail only when identity, state, composition, and quality remain
   acceptable.

If a future tool explicitly supports both boundaries, use the second reference
only when needed and exactly as documented. Never guess parameters or simulate
a private API call.

## Handle capability fallback honestly

Classify the failed capability and the guarantee lost by fallback.

- Authentication, authorization, and quota errors are not transient. Do not
  repeat them when the active capability forbids retry.
- A tool envelope that contains an error payload is a failure even if an outer
  transport status says success.
- Switching from reference-based generation to independent text generation
  weakens identity, composition, and object-state control.

When a fallback weakens a hard requirement, do not silently accept it. Prefer a
new keyframe, obscured or rear angle, insert, intentional scene cut, local edit,
or another strategy whose reduced guarantee is compatible with the shot. If no
bounded strategy can satisfy the requirement, request a real tradeoff rather
than claiming continuity from repeated descriptive text.

For an image-to-video shot, distinguish a retryable call failure from a visual
rejection. Within the active attempt contract, retry the same accepted image at
least once after a retryable failure. After a visual rejection, preserve the
reference and simplify motion, camera behavior, or competing prompt details
before spending another allowed attempt. Do not retry authentication,
authorization, quota, or an explicitly non-retryable failure. Exhausting a
bounded reference-based strategy permits redesign, not a silent tool swap:
record the changed relationship and continuity guarantee before generating an
independent replacement.

## Shape concise shot prompts

Write one prompt per shot. Include the subject and action, only relevant scene
and lighting, required camera behavior or screen direction, and the needed
starting or ending state. Add a short set of exclusions only for likely defects.

Carry forward stable anchors that matter. A prompt crowded with unrelated
project facts weakens the main instruction. Use accepted images for visual facts
that text cannot reliably preserve. Follow active original-prompt and
enhancement contracts without assuming fixed provider syntax, clip length,
seed behavior, or reference notation.

## Plan against observed atomic capability

Separate a story beat from the atomic clips used to realize it. First describe
the complete intended order and duration budget at the creative level. Then map
each beat to feasible calls only after a representative pilot establishes what
one active video call actually returns.

For each planned unit record the selected capability, accepted reference if
any, expected raw seconds, conservative usable seconds after likely trims,
neighbor relationship, and retry or alternate allowance. Calculate picture
duration from media, not narration:

```text
assembled seconds = sum(usable clip seconds) - transition overlaps
```

Make the planned lower bound reachable before batch generation. If one call
returns about five usable seconds, a twelve-second dramatic beat needs linked
units, reactions, inserts, or another intentional editorial design; it is not a
single twelve-second generation. Keep a modest coverage reserve for rejected
tails and trims, while keeping the requested final upper bound as an acceptance
gate.

When pilot evidence changes the estimate, revise the whole remaining ledger and
continuity boundaries before continuing. Do not append unrelated atmosphere or
duplicate variants merely until a duration counter looks closer to the target.
Every added unit must have a purpose and an intended place in the authoritative
sequence.

Keep render order explicit. Assemble from the ordered accepted-path list in the
production record, never from a directory glob, filename sort, artifact creation
time, or every successful tool return. Rejected retries and unused alternatives
remain evidence, not editorial inputs; titles and endings stay at their planned
positions regardless of when they were generated.

## Spend generation calls by risk

Generate early evidence for identity-critical close-ups, complex physical
actions, object-state changes, difficult boundaries, exact layout or product
form, and motion-matched transitions. Delay low-risk atmosphere, cutaways, and
montage until the core visual language works. Create alternatives only when
they resolve a known risk or editorial choice.

Before batching one generation configuration, produce one representative pilot
and probe the actual result. Confirm returned duration, dimensions, frame rate,
motion, schema limits, and suitability for the intended cut. Provider output is
the current fact even when it differs from a requested or assumed value. Adapt
the complete atomic-unit and duration plan before repeating the call so a wrong
frame count, unsupported resolution, or unsuitable motion mode is not
multiplied across the project.

Do not substitute local motion over still images for requested generated video
while a compatible video capability is available. Do not solve a long target
duration by making every shot the same maximum length. Let story beats, action,
speech, reaction, and editorial rhythm determine useful shot durations; trim,
intercut, or add purposeful coverage when fixed provider lengths do not fit.

## Control context growth

Load only the reference needed for the current decision. Avoid reloading
unchanged Skills or copying long tool contracts into every production turn.
Use a modest contact sheet for broad coverage and exact frames for material
boundaries. Once accepted, write a compact evidence summary and exact path into
the production record instead of repeatedly re-reading the same media.

When context pressure grows, preserve requirements, current status, accepted
paths, failures, and next actions. Do not preserve every progress narration or
raw review image at the expense of current production state.

## Resume without user-driven polling

Before a generation that may interrupt execution, persist the intended shot,
accepted reference, expected result, current status, and next inspection. After
success, return to the parent production loop, record the exact returned path as
`generated-uninspected`, inspect it, and continue automatically under an
autonomous interaction policy.

If the runtime truly requires a new user turn, preserve state and state that it
is a technical boundary. Do not pretend the user is approving a creative
decision by sending “继续”.

For an interrupted local Docker media operation, use the operation ID emitted
by `media_ops.py` to cancel only that owned operation and verify its absence
before resuming or retrying. If the ID was lost, inspect managed containers and
use only the helper's age- and parent-state-gated stale cleanup. Do not leave an
old encoder writing an output while a retry starts, and do not turn routine
cleanup of the production's own operation into a user checkpoint.

## Compose and repair from evidence

Build a rough sequence as soon as several shots are accepted. Hard cuts are the
default unless a transition has a clear purpose. Inspect generated starts and
tails; never trim a universal fixed amount from every clip.

Classify defects before repair:

- content, identity, or state: revise the reference or regenerate the shot;
- boundary mismatch: change the cut point, shorten, insert a cutaway, restore a
  planned boundary, or regenerate the segment;
- timing or order: trim, reorder, or change transition locally;
- subtitle: revise affected cues or style and burn again;
- narration: resynthesize, reposition, or remix affected audio;
- isolated visual defect: shorten, cover, reframe, or regenerate the smallest
  region that restores intent.

Reinspect the repaired layer and downstream boundaries it changes. Change
strategy when repeated evidence shows the same repair is not converging.

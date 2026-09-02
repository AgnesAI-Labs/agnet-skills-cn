# Local media tool contract

The Skill exposes two deterministic Python 3.9+ scripts. Use the resolved
absolute paths shown in the loaded Skill's supporting-file list.

All examples use placeholders:

```text
<python> <skill-dir>/scripts/media_ops.py ...
<python> <skill-dir>/scripts/tts.py ...
```

On Windows, `<python>` is normally `py -3` or `python`. On macOS/Linux it is
normally `python3` or `python`. Quote every path. The scripts invoke child
processes without a shell and support Windows, macOS, and Linux path semantics.
They do not install dependencies or call hosted image or video generation APIs.

## Check operation-level capabilities

`media_ops.py` supports `auto`, `docker`, and `native` runtimes. Top-level flags
must appear before the subcommand. `auto` prefers an already-cached, pinned,
multi-platform Docker FFmpeg image when the Docker engine is ready, then falls
back to already-installed native `ffmpeg` and `ffprobe`. Explicit `--ffmpeg`,
`--ffprobe`, `FFMPEG_BIN`, or `FFPROBE_BIN` values select native execution in
`auto` mode.

```text
<python> "<skill-dir>/scripts/media_ops.py" doctor
<python> "<skill-dir>/scripts/media_ops.py" --runtime docker doctor
```

The doctor reports native and Docker readiness, selected runtime, image identity,
and operation-level capabilities. Each operation reports `ready` and any missing
capability. Do not treat a missing subtitle or transition filter as a reason to
block probing, frame extraction, trimming, or hard-cut concatenation.

The script never installs host packages and never pulls an image implicitly.
Only after dependency acquisition is authorized may the agent prepare a missing
image explicitly:

```text
<python> "<skill-dir>/scripts/media_ops.py" --runtime docker --pull-docker-image doctor
```

Override selection with `AGNES_MEDIA_RUNTIME`, `AGNES_MEDIA_DOCKER_IMAGE`, or
`DOCKER_BIN`, or with the corresponding top-level flags. Normal container media
operations run without network access, without a shell, with dropped Linux
capabilities and minimal bind mounts. A custom image still has to satisfy the
doctor's relevant operation contract. Image download, local image storage, and
Docker engine startup remain host-visible resource operations.

## Recover managed Docker operations

Each Docker-backed media command owns one operation ID across all of its
sequential FFmpeg and ffprobe containers. Before the first container starts,
the script writes a compact `docker_operation_started` event with that ID to
stderr. Successful summarized operation results repeat it as `operation_id` in
the runtime metadata; direct `probe` output remains unmodified ffprobe JSON, so
retain its start event instead. Containers carry AgnesCode ownership,
operation, parent-process, start-time, and command labels; unlabelled containers
are outside this contract. While the command is active, a small user-owned
record in the platform temporary directory keeps the operation discoverable
even between sequential containers. It contains control metadata only, never
media, prompts, credentials, or project state.

Read the currently managed containers and active operation records without
changing them:

```text
<python> "<skill-dir>/scripts/media_ops.py" managed-containers
<python> "<skill-dir>/scripts/media_ops.py" managed-containers --operation-id "<operation-id>"
```

If the shell runner times out, is interrupted, or loses the child process after
the start event, cancel that exact operation and verify that it is absent before
retrying the media command:

```text
<python> "<skill-dir>/scripts/media_ops.py" cancel --operation-id "<operation-id>"
<python> "<skill-dir>/scripts/media_ops.py" managed-containers --operation-id "<operation-id>"
```

`cancel` is exact and idempotent: it marks only the supplied 32-character
operation ID as cancelled and removes only containers with both that ID and the
managed label. The running helper checks the marker before and during each
Docker stage, so a cancellation remains effective across gaps between
sequential containers. Under standing authorization for autonomous production,
cancelling the production's own interrupted operation is normal technical
recovery and does not require a new user checkpoint. Do not guess an ID, cancel
by name prefix, or use broad Docker stop/kill/prune commands.

Cancellation proves process termination, not output validity. The helper does
not automatically delete the requested output path because it may contain
useful diagnostic evidence or a previously existing user-authorized target.
Treat any file left by an interrupted command as untrusted, probe it only for
diagnosis, and resume into a fresh versioned path unless explicit replacement
is already authorized.

For orphan recovery when an operation ID was not retained, first inspect the
managed list. The bounded stale cleanup below considers only managed containers
at least ten minutes old and removes one only when its recorded parent process
is confirmed absent:

```text
<python> "<skill-dir>/scripts/media_ops.py" cleanup --stale-after 10m
<python> "<skill-dir>/scripts/media_ops.py" cleanup --stale-after 10m --operation-id "<operation-id>"
```

Malformed ownership metadata, an unknown parent state, a live parent, and a
container or operation younger than the threshold are all fail-closed skips.
Eligible orphan operation records are removed only after their managed
containers are absent. This lifecycle interface does not adopt or remove old,
user-created, unlabelled, or otherwise unowned containers. Image pulling,
Docker engine startup, and cleanup outside these ownership labels remain
separate host-visible actions.

The local TTS wrapper detects these already-installed backends:

- macOS `say`
- Windows PowerShell `System.Speech`
- Linux `espeak-ng` or `espeak`
- Optional online `edge-tts` CLI

```text
<python> "<skill-dir>/scripts/tts.py" doctor
```

Automatic selection uses only the platform's installed local backend. Select
`edge-tts` explicitly only after the user approves an online TTS backend. Do
not install any backend without permission. Voice names and speaking-rate
semantics differ by backend.

## Probe media

Print full ffprobe JSON:

```text
<python> "<skill-dir>/scripts/media_ops.py" probe "input.mp4"
```

Write it to a report:

```text
<python> "<skill-dir>/scripts/media_ops.py" probe "input.mp4" --output "probe.json"
```

## Sample video for model-visible inspection

Create a contact sheet across the whole video:

```text
<python> "<skill-dir>/scripts/media_ops.py" contact-sheet "input.mp4" --output "review.png" --frames 12 --columns 4
```

Restrict sampling to a time range:

```text
<python> "<skill-dir>/scripts/media_ops.py" contact-sheet "input.mp4" --output "middle.png" --start 2.0 --end 7.5 --frames 8 --columns 4
```

Create a one-frame sheet at the start or end of a range:

```text
<python> "<skill-dir>/scripts/media_ops.py" contact-sheet "input.mp4" --output "first.png" --mode first
<python> "<skill-dir>/scripts/media_ops.py" contact-sheet "input.mp4" --output "last.png" --mode last
```

Inspect each PNG with `read_image`. A contact sheet does not prove smooth
motion, exact dialogue, or audio quality.

Extract one exact reusable frame:

```text
<python> "<skill-dir>/scripts/media_ops.py" extract-frame "input.mp4" --output "first-frame.png" --position first
<python> "<skill-dir>/scripts/media_ops.py" extract-frame "input.mp4" --output "last-frame.png" --position last
<python> "<skill-dir>/scripts/media_ops.py" extract-frame "input.mp4" --output "frame-3s.png" --at 3.0
```

Inspect the output before using it as a reference. The script reports the
resolved extraction time; `last` seeks just before the decodable end rather than
requesting a frame beyond the duration.

## Trim without modifying the source

```text
<python> "<skill-dir>/scripts/media_ops.py" trim "shot.mp4" --output "shot-trimmed.mp4" --start 1.25 --end 4.8
```

Use either `--end` or `--duration`, not both. Choose trim points from evidence;
do not remove a universal fixed amount from every generated clip.

## Concatenate clips

Hard-cut clips after normalizing canvas, frame rate, codec, and audio layout:

```text
<python> "<skill-dir>/scripts/media_ops.py" concat "shot-01.mp4" "shot-02.mp4" --output "rough-cut.mp4" --width 1920 --height 1080 --fps 24
```

Add the same short transition between adjacent clips only when the edit
decision calls for it:

```text
<python> "<skill-dir>/scripts/media_ops.py" concat "shot-01.mp4" "shot-02.mp4" "shot-03.mp4" --output "rough-cut.mp4" --transition dissolve --transition-duration 0.5
```

Supported transitions are printed by `concat --help`. A transition duration of
`0` means hard cuts. The script letterboxes mismatched aspect ratios instead of
cropping and adds silence to clips without audio. If canvas or frame rate are
omitted, the first clip defines them.

The operation does not decide narrative, clip order, or transition meaning.

## Generate one local narration asset

From inline text:

```text
<python> "<skill-dir>/scripts/tts.py" synthesize --text "Narration text" --output "narration.wav"
```

From a UTF-8 text file:

```text
<python> "<skill-dir>/scripts/tts.py" synthesize --text-file "narration.txt" --output "narration.wav" --voice "VOICE_NAME"
```

Use `--backend` only when a particular installed backend is required. `auto`
never selects `edge-tts`. The `--rate` meaning is backend-specific:
words/minute for `say` and `espeak`, `-10..10` for PowerShell, and percentage
change for explicitly selected `edge-tts`.

After explicit approval, select the online backend with both flags:

```text
<python> "<skill-dir>/scripts/tts.py" synthesize --text "Narration text" --output "narration.mp3" --backend edge-tts --allow-online
```

This helper is a local fallback. Prefer a user-selected voice capability when
voice identity, acting, licensing, or production quality is material.
Synthesize and probe one representative semantic unit before producing a long
batch. Record the selected backend, voice, rate, exact text, and actual duration
so the remaining narration and picture timing use observed cadence rather than
an assumed reading speed.

## Add or mix audio

Replace the video's audio with narration:

```text
<python> "<skill-dir>/scripts/media_ops.py" add-audio "picture.mp4" "narration.wav" --output "narrated.mp4" --mode replace
```

Place narration at an exact picture time instead of assuming it starts at
zero:

```text
<python> "<skill-dir>/scripts/media_ops.py" add-audio "picture.mp4" "narration.wav" --output "narrated.mp4" --mode replace --start-at 15.5
```

Mix narration or music with existing audio:

```text
<python> "<skill-dir>/scripts/media_ops.py" add-audio "picture.mp4" "voice.wav" --output "mixed.mp4" --mode mix --original-volume 0.25 --overlay-volume 1.0
```

Use `--loop-audio` for short background music that should repeat to the video
duration. Do not use it for narration. `--start-at` is a non-negative timeline
position in seconds. The command inserts silence before the overlay, keeps the
output aligned to picture time zero, and reports `audio_start`,
`source_audio_duration`, `audio_end`, and `audio_truncated`.

Reject a start at or beyond the end of the picture. When `audio_truncated` is
true, reposition or shorten the source unless truncation is intentional. Build
subtitle cues from the same returned `audio_start` and actual source duration;
do not guess timing from a shot number or an approximate narration length. If
no phrase-level timestamps exist, use one cue for a short narration across its
audible interval rather than splitting it into invented consecutive ranges.

## Mix an explicit multi-track audio timeline

Use one JSON timeline when several narration, dialogue, ambience, effect, or
music assets need independent start times. Paths may be absolute or relative to
the timeline file. `role` and `label` are descriptive metadata; they do not
change mixing behavior.

```json
{
  "original_volume": 0.2,
  "tracks": [
    {
      "label": "opening narration",
      "role": "narration",
      "path": "audio/opening.wav",
      "start": 3.0,
      "volume": 1.0
    },
    {
      "label": "rain bed",
      "role": "ambience",
      "path": "audio/rain.wav",
      "start": 0.0,
      "volume": 0.25,
      "loop": true
    }
  ]
}
```

Mix it into the picture timeline:

```text
<python> "<skill-dir>/scripts/media_ops.py" mix-audio-timeline "picture.mp4" "audio-timeline.json" --output "mixed.mp4"
```

The command resolves and probes every source, refuses a track that starts after
the picture, preserves picture time zero with an explicit silent base, mixes
the tracks, limits peaks, and verifies the rendered duration and audio stream.
It reports each track's exact `start`, `source_duration`, `end`, `loop`, and
`truncated` values plus `track_count` and `mix_stem_count`. A non-zero
`original_volume` requires an existing input audio stream. Use `loop` only for
material intended to repeat, never to stretch narration or dialogue.

The operation writes to an operation-scoped temporary file, validates it, and
only then replaces the requested output. Short non-looping assets are not padded
individually to the full picture duration; the silent timeline base owns final
duration. Larger manifests are first reduced into bounded, temporary lossless
float-audio stems and then mixed into the picture. This avoids one unbounded
FFmpeg filter graph while preserving overlapping tracks without intermediate
clipping. It also prevents a killed render from leaving a corrupt file at the
requested output path.

Build subtitle cues and production-record timing from the returned values, not
from duplicated handwritten offsets. Treat `truncated: true` as a repair unless
the cut is intentional. This operation owns deterministic placement only; the
agent still decides track content, starts, roles, balance, and whether the mix
is editorially appropriate.

Treat the reported `track_count` and per-track paths as the inclusion contract.
On timeout or failure, do not replace this operation with a loop of successive
`add-audio` calls. Probe any reported output, diagnose the same manifest, and
retry or repair into a fresh path. `add-audio` remains appropriate for one
isolated overlay, not as an improvised multi-track mixer.

## Burn subtitles

The script accepts SRT, VTT, ASS, or SSA. By default it derives a safe font
size, outline, horizontal margin, and bottom margin from the probed video
canvas, and rejects cues estimated to need more than two rendered lines:

```text
<python> "<skill-dir>/scripts/media_ops.py" burn-subtitles "mixed.mp4" "captions.srt" --output "subtitled.mp4"
```

Optional `--font-size`, `--outline`, and `--margin-v` values are target output
pixels; the script converts them to the subtitle format's play resolution. For
example, `--font-size 42` means approximately 42 output pixels rather than 42
ASS style units. Use `--max-lines 3` only for an intentional three-line design.
Prefer splitting and retiming an overloaded cue at a semantic speech boundary.

Before rendering, the script parses the actual cue text, finds an existing font
on Windows, macOS, or Linux, reads its OpenType/TrueType character maps, and
requires one selected face to cover every visible subtitle character. It does
not install fonts. Supply a known font file or font directory when discovery is
insufficient:

```text
<python> "<skill-dir>/scripts/media_ops.py" burn-subtitles "mixed.mp4" "captions.srt" --output "subtitled.mp4" --font-file "/path/to/NotoSansCJK-Regular.ttc"
<python> "<skill-dir>/scripts/media_ops.py" burn-subtitles "mixed.mp4" "captions.srt" --output "subtitled.mp4" --fonts-dir "/path/to/project-fonts" --font "Noto Sans CJK SC"
```

Repeat `--font-file` or `--fonts-dir` for fallback sources. When either is
provided, the script limits selection to those sources. `--font` is a required
family-name hint, not permission to assume that a similarly named font exists.
`AGNES_SUBTITLE_FONTS_DIR` supplies one or more directories separated by the
platform path separator. Keep the subtitle source and any project-owned font
beside the editable project after producing a burned-in render.

For Docker, the script copies only the selected font into its operation-scoped
temporary directory and supplies a minimal temporary fontconfig file. It also
checks FFmpeg/libass diagnostics and fails instead of returning a render when
the verified font was not actually usable. A successful result reports
`font_family`, `font_file`, `glyph_coverage_verified`, timing containment, and
risk-selected cue midpoints in `subtitle_check_times`, plus the resolved
canvas-aware values in `subtitle_layout`. The first midpoint is
also retained as `subtitle_check_time` for compatibility.

Before burning, verify every cue is inside the final picture duration and that
dialogue or narration cues overlap the intended placed-audio interval. After
burning, extract a frame at every returned `subtitle_check_times[].time` and
inspect it with `read_image`, then reprobe the render. The selected cues include
the first, last, three longest-line, and most-lines risks when they are distinct.
The reported `max_line_columns` is a sampling hint, not proof that text fits.
These exact-frame checks are required to catch layout, clipping, wrong font,
encoding, and tofu-box failures. Stream presence and preflight metadata alone
do not prove correct rendering or synchronization.

## Output safety and portability

- Commands refuse to overwrite an existing output unless `--overwrite` is
  explicit.
- Inputs are never modified.
- Derived media is staged in a temporary directory next to the output where the
  operation requires replacement.
- Commands use argument arrays and `shell=False`; do not wrap paths in a
  platform-specific shell expression.
- Docker execution uses the same operation commands and output contracts as
  native execution; do not fork a separate production workflow around it.
- Docker media containers receive unique operation names and ownership labels.
  SIGINT or SIGTERM to the helper terminates the Docker client and forcibly
  removes the active named container. If a shell runner cannot deliver that
  signal, use the emitted operation ID with `cancel` and verify absence before
  retrying. A hard host or daemon crash can require bounded `cleanup` after the
  parent disappears.
- PowerShell runs under the user's normal execution policy. The helper does not
  bypass enterprise policy.
- Optional codecs and filters differ by FFmpeg build. Check the specific
  operation rather than assuming every feature exists.
- The compatibility contract is design- and code-reviewed for Windows, macOS,
  and Linux. A platform is not field-verified unless the current run actually
  executed there.

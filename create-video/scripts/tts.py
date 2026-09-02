#!/usr/bin/env python3
"""Cross-platform text-to-speech wrapper for AgnesCode video production."""

from __future__ import annotations

import argparse
import json
import math
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence


class TtsError(RuntimeError):
    pass


def which(candidates: Sequence[str]) -> Optional[str]:
    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found
    return None


def run_checked(command: Sequence[str], cwd: Optional[Path] = None) -> None:
    completed = subprocess.run(
        list(command),
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        if len(detail) > 6000:
            detail = detail[-6000:]
        raise TtsError(f"TTS command failed with exit code {completed.returncode}: {detail}")


def available_backends() -> dict[str, str]:
    backends: dict[str, str] = {}
    say = which(("say",))
    if say:
        backends["say"] = say
    powershell = which(("pwsh", "powershell.exe", "powershell"))
    if powershell:
        backends["powershell"] = powershell
    espeak = which(("espeak-ng", "espeak"))
    if espeak:
        backends["espeak"] = espeak
    edge = which(("edge-tts", "edge-tts.exe"))
    if edge:
        backends["edge-tts"] = edge
    return backends


def preferred_backend(backends: dict[str, str]) -> Optional[str]:
    system = platform.system()
    order = {
        "Darwin": ("say", "espeak", "powershell"),
        "Windows": ("powershell", "espeak", "say"),
        "Linux": ("espeak", "powershell", "say"),
    }.get(system, ("espeak", "powershell", "say"))
    return next((name for name in order if name in backends), None)


def doctor() -> None:
    backends = available_backends()
    print(
        json.dumps(
            {
                "platform": platform.system(),
                "python": sys.version.split()[0],
                "backends": backends,
                "local_backends": {
                    name: path for name, path in backends.items() if name != "edge-tts"
                },
                "online_backends": {
                    name: path for name, path in backends.items() if name == "edge-tts"
                },
                "default_backend": preferred_backend(backends),
                "ffmpeg": which(("ffmpeg", "ffmpeg.exe")),
                "ready": preferred_backend(backends) is not None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def input_text(args: argparse.Namespace) -> str:
    if bool(args.text) == bool(args.text_file):
        raise TtsError("provide exactly one of --text or --text-file")
    if args.text_file:
        path = Path(args.text_file).expanduser().resolve()
        if not path.is_file():
            raise TtsError(f"text file not found: {path}")
        value = path.read_text(encoding="utf-8")
    else:
        value = args.text
    if not value or not value.strip():
        raise TtsError("speech text is empty")
    return value


def speak_with_say(
    executable: str,
    text_path: Path,
    native_output: Path,
    voice: Optional[str],
    rate: Optional[int],
) -> None:
    command = [executable, "-f", str(text_path), "-o", str(native_output)]
    if voice:
        command.extend(["-v", voice])
    if rate is not None:
        command.extend(["-r", str(rate)])
    run_checked(command)


def speak_with_espeak(
    executable: str,
    text_path: Path,
    native_output: Path,
    voice: Optional[str],
    rate: Optional[int],
) -> None:
    command = [executable, "-f", str(text_path), "-w", str(native_output)]
    if voice:
        command.extend(["-v", voice])
    if rate is not None:
        command.extend(["-s", str(rate)])
    run_checked(command)


def speak_with_powershell(
    executable: str,
    text_path: Path,
    native_output: Path,
    voice: Optional[str],
    rate: Optional[int],
    temporary: Path,
) -> None:
    script = temporary / "synthesize.ps1"
    script.write_text(
        """
param(
  [Parameter(Mandatory=$true)][string]$TextPath,
  [Parameter(Mandatory=$true)][string]$OutputPath,
  [string]$Voice = "",
  [int]$Rate = 0
)
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
  if ($Voice) { $speaker.SelectVoice($Voice) }
  $speaker.Rate = [Math]::Max(-10, [Math]::Min(10, $Rate))
  $text = [System.IO.File]::ReadAllText($TextPath, [System.Text.Encoding]::UTF8)
  $speaker.SetOutputToWaveFile($OutputPath)
  $speaker.Speak($text)
} finally {
  $speaker.Dispose()
}
""".lstrip(),
        encoding="utf-8",
    )
    command = [
        executable,
        "-NoProfile",
        "-NonInteractive",
        "-File",
        str(script),
        "-TextPath",
        str(text_path),
        "-OutputPath",
        str(native_output),
        "-Rate",
        str(rate or 0),
    ]
    if voice:
        command.extend(["-Voice", voice])
    run_checked(command)


def speak_with_edge(
    executable: str,
    text_path: Path,
    native_output: Path,
    voice: Optional[str],
    rate: Optional[int],
) -> None:
    command = [
        executable,
        "--file",
        str(text_path),
        "--write-media",
        str(native_output),
    ]
    if voice:
        command.extend(["--voice", voice])
    if rate is not None:
        command.extend(["--rate", f"{rate:+d}%"])
    run_checked(command)


def normalize_audio(
    native_output: Path,
    output: Path,
    ffmpeg_argument: Optional[str],
) -> None:
    ffmpeg = shutil.which(ffmpeg_argument) if ffmpeg_argument else None
    if ffmpeg_argument and not ffmpeg:
        candidate = Path(ffmpeg_argument)
        ffmpeg = str(candidate.resolve()) if candidate.is_file() else None
    if not ffmpeg_argument:
        ffmpeg = which(("ffmpeg", "ffmpeg.exe"))
    if not ffmpeg:
        if native_output.suffix.lower() == output.suffix.lower():
            shutil.copyfile(native_output, output)
            return
        raise TtsError(
            "ffmpeg is required to convert the selected TTS backend output "
            f"from {native_output.suffix} to {output.suffix}"
        )
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(native_output),
        "-vn",
    ]
    extension = output.suffix.lower()
    if extension == ".wav":
        command.extend(["-c:a", "pcm_s16le"])
    elif extension == ".mp3":
        command.extend(["-c:a", "libmp3lame", "-q:a", "2"])
    elif extension in {".m4a", ".aac"}:
        command.extend(["-c:a", "aac", "-b:a", "192k"])
    command.append(str(output))
    run_checked(command)


def validate_audio(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size <= 128:
        raise TtsError(f"{label} contains no usable audio data")
    ffprobe = which(("ffprobe", "ffprobe.exe"))
    if not ffprobe:
        return
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    try:
        duration = float(completed.stdout.strip())
    except ValueError as error:
        raise TtsError(f"{label} duration could not be verified") from error
    if completed.returncode != 0 or not math.isfinite(duration) or duration <= 0:
        raise TtsError(f"{label} contains no positive-duration audio")


def validate_rate(backend: str, rate: Optional[int]) -> None:
    if rate is None:
        return
    if backend in {"say", "espeak"} and rate <= 0:
        raise TtsError(f"{backend} rate must be a positive words-per-minute value")
    if backend == "powershell" and not -10 <= rate <= 10:
        raise TtsError("PowerShell rate must be between -10 and 10")
    if backend == "edge-tts" and not -100 <= rate <= 500:
        raise TtsError("edge-tts rate must be between -100 and 500 percent")


def synthesize(args: argparse.Namespace) -> None:
    text = input_text(args)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise TtsError(f"output already exists (pass --overwrite to replace it): {output}")
    if not output.suffix:
        raise TtsError("output path must include an audio file extension")

    backends = available_backends()
    backend = args.backend
    if backend == "auto":
        backend = preferred_backend(backends)
    if not backend or backend not in backends:
        raise TtsError(
            f"TTS backend unavailable: {backend or 'none'}; "
            f"available backends: {sorted(backends)}"
        )
    if backend == "edge-tts" and not args.allow_online:
        raise TtsError(
            "edge-tts is an online backend; pass --allow-online only after "
            "the user explicitly approves network TTS"
        )
    validate_rate(backend, args.rate)

    with tempfile.TemporaryDirectory(prefix=".agnes-tts-", dir=output.parent) as raw:
        temporary = Path(raw)
        text_path = temporary / "speech.txt"
        text_path.write_text(text, encoding="utf-8")
        native_suffix = {
            "say": ".aiff",
            "powershell": ".wav",
            "espeak": ".wav",
            "edge-tts": ".mp3",
        }[backend]
        native_output = temporary / f"speech{native_suffix}"
        executable = backends[backend]

        if backend == "say":
            speak_with_say(executable, text_path, native_output, args.voice, args.rate)
        elif backend == "powershell":
            speak_with_powershell(
                executable,
                text_path,
                native_output,
                args.voice,
                args.rate,
                temporary,
            )
        elif backend == "espeak":
            speak_with_espeak(
                executable, text_path, native_output, args.voice, args.rate
            )
        else:
            speak_with_edge(
                executable, text_path, native_output, args.voice, args.rate
            )

        validate_audio(native_output, f"{backend} output")
        staged = temporary / f"final{output.suffix}"
        normalize_audio(native_output, staged, args.ffmpeg)
        validate_audio(staged, "normalized output")
        if output.exists():
            output.unlink()
        staged.replace(output)

    print(
        json.dumps(
            {
                "operation": "synthesize",
                "backend": backend,
                "output": str(output),
                "voice": args.voice,
                "rate": args.rate,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def bounded_rate(value: str) -> int:
    rate = int(value)
    if not math.isfinite(rate) or rate < -500 or rate > 500:
        raise argparse.ArgumentTypeError("rate must be between -500 and 500")
    return rate


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Portable wrapper around installed local TTS backends."
    )
    commands = root.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="list available local TTS backends")

    synth = commands.add_parser("synthesize", help="create one narration audio file")
    synth.add_argument("--text")
    synth.add_argument("--text-file")
    synth.add_argument("--output", required=True)
    synth.add_argument(
        "--backend",
        choices=("auto", "say", "powershell", "espeak", "edge-tts"),
        default="auto",
    )
    synth.add_argument("--voice")
    synth.add_argument(
        "--rate",
        type=bounded_rate,
        help=(
            "backend-specific speaking rate: words/minute for say/espeak, "
            "-10..10 for PowerShell, percentage delta for edge-tts"
        ),
    )
    synth.add_argument("--ffmpeg", help="ffmpeg executable path for format conversion")
    synth.add_argument(
        "--allow-online",
        action="store_true",
        help="allow an explicitly selected online backend such as edge-tts",
    )
    synth.add_argument("--overwrite", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "doctor":
        doctor()
    else:
        synthesize(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (TtsError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

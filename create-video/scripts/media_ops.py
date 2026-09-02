#!/usr/bin/env python3
"""Cross-platform FFmpeg helpers for AgnesCode video production."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import signal
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import unicodedata
import uuid
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence


class MediaError(RuntimeError):
    pass


DEFAULT_DOCKER_IMAGE = (
    "jrottenberg/ffmpeg@"
    "sha256:50171be54480baa9371be135493b034a9e08d2ff54eb873ce99963f12a24a187"
)
DOCKER_FFMPEG = "__agnes_docker_ffmpeg__"
DOCKER_FFPROBE = "__agnes_docker_ffprobe__"
FONT_EXTENSIONS = {".otf", ".ttf", ".ttc"}
DOCKER_MANAGED_LABEL = "com.agnescode.media.managed"
DOCKER_OPERATION_LABEL = "com.agnescode.media.operation"
DOCKER_PARENT_PID_LABEL = "com.agnescode.media.parent-pid"
DOCKER_STARTED_AT_LABEL = "com.agnescode.media.started-at"
DOCKER_COMMAND_LABEL = "com.agnescode.media.command"

_selected_runtime = "native"
_selected_docker_image: Optional[str] = None
_selected_docker_cli: Optional[str] = None
_operation_id: Optional[str] = None
_operation_command: Optional[str] = None
_operation_started_at: Optional[float] = None
_operation_announced = False
_container_sequence = 0
_operation_registered = False


def begin_operation(command: str) -> None:
    global _operation_id, _operation_command, _operation_started_at
    global _operation_announced, _container_sequence, _operation_registered

    _operation_id = uuid.uuid4().hex
    _operation_command = command
    _operation_started_at = time.time()
    _operation_announced = False
    _container_sequence = 0
    _operation_registered = False


def operation_container_name() -> str:
    global _container_sequence
    if not _operation_id:
        begin_operation("media")
    _container_sequence += 1
    return f"agnes-media-{_operation_id[:12]}-{_container_sequence}"


def operation_registry_directory(create: bool) -> Optional[Path]:
    suffix = str(os.getuid()) if hasattr(os, "getuid") else "user"
    directory = Path(tempfile.gettempdir()) / f"agnescode-media-operations-{suffix}"
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    elif not directory.exists():
        return None
    if directory.is_symlink() or not directory.is_dir():
        raise MediaError(f"unsafe media operation registry path: {directory}")
    if os.name != "nt" and hasattr(os, "getuid"):
        if directory.stat().st_uid != os.getuid():
            raise MediaError(f"media operation registry is not user-owned: {directory}")
        directory.chmod(0o700)
    return directory


def operation_registry_path(operation_id: str, create: bool) -> Optional[Path]:
    directory = operation_registry_directory(create)
    return directory / f"{operation_id}.json" if directory else None


def operation_cancel_path(operation_id: str, create: bool) -> Optional[Path]:
    directory = operation_registry_directory(create)
    return directory / f"{operation_id}.cancel" if directory else None


def write_operation_record(record: dict[str, Any]) -> None:
    operation_id = str(record.get("operation_id") or "")
    if not re.fullmatch(r"[0-9a-f]{32}", operation_id):
        raise MediaError("cannot register a media operation without a valid ID")
    destination = operation_registry_path(operation_id, True)
    if destination is None:
        raise MediaError("media operation registry is unavailable")
    descriptor, raw_temporary = tempfile.mkstemp(
        prefix=f".{operation_id}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(raw_temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def read_operation_record(operation_id: str) -> Optional[dict[str, Any]]:
    path = operation_registry_path(operation_id, False)
    if path is None or not path.is_file() or path.is_symlink():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(value, dict) or value.get("operation_id") != operation_id:
        return None
    return value


def register_docker_operation() -> None:
    global _operation_registered

    if _selected_runtime != "docker" or not _operation_id:
        return
    write_operation_record(
        {
            "operation_id": _operation_id,
            "command": _operation_command,
            "parent_pid": os.getpid(),
            "started_at": _operation_started_at,
        }
    )
    marker = operation_cancel_path(_operation_id, False)
    if marker and marker.is_file() and not marker.is_symlink():
        marker.unlink()
    _operation_registered = True


def create_operation_cancel_marker(operation_id: str) -> None:
    marker = operation_cancel_path(operation_id, True)
    if marker is None:
        raise MediaError("media operation cancellation registry is unavailable")
    if marker.is_symlink():
        raise MediaError(f"unsafe media operation cancellation marker: {marker}")
    flags = os.O_CREAT | os.O_WRONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(marker, flags, 0o600)
    os.close(descriptor)


def operation_cancel_requested(operation_id: Optional[str]) -> bool:
    if not operation_id:
        return False
    marker = operation_cancel_path(operation_id, False)
    return bool(marker and marker.is_file() and not marker.is_symlink())


def ensure_operation_not_cancelled() -> None:
    if operation_cancel_requested(_operation_id):
        raise MediaError(f"Docker media operation {_operation_id} was cancelled")


def remove_operation_registry(operation_id: str) -> None:
    for path in (
        operation_registry_path(operation_id, False),
        operation_cancel_path(operation_id, False),
    ):
        if path and path.is_file() and not path.is_symlink():
            path.unlink()


def unregister_docker_operation() -> None:
    global _operation_registered

    if _operation_registered and _operation_id:
        remove_operation_registry(_operation_id)
    _operation_registered = False


def native_executable(
    explicit: Optional[str], environment_name: str, candidates: Sequence[str]
) -> str:
    value = explicit or os.environ.get(environment_name)
    if value:
        resolved = shutil.which(value) or (value if Path(value).is_file() else None)
        if resolved:
            return str(Path(resolved).expanduser().absolute())
        raise MediaError(f"executable not found: {value}")
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise MediaError(
        f"required executable not found; set {environment_name} or add "
        f"{'/'.join(candidates)} to PATH"
    )


def executable(
    explicit: Optional[str], environment_name: str, candidates: Sequence[str]
) -> str:
    if _selected_runtime == "docker":
        return DOCKER_FFMPEG if environment_name == "FFMPEG_BIN" else DOCKER_FFPROBE
    return native_executable(explicit, environment_name, candidates)


def optional_executable(
    explicit: Optional[str], environment_name: str, candidates: Sequence[str]
) -> Optional[str]:
    value = explicit or os.environ.get(environment_name)
    if value:
        resolved = shutil.which(value)
        if resolved:
            return str(Path(resolved).expanduser().absolute())
        candidate = Path(value).expanduser()
        if candidate.is_file():
            return str(candidate.absolute())
        return None
    for candidate in candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return str(Path(resolved).absolute())
    return None


def process_checked(
    command: Sequence[str], cwd: Optional[Path] = None
) -> subprocess.CompletedProcess[str]:
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
        raise MediaError(f"command failed with exit code {completed.returncode}: {detail}")
    return completed


def docker_engine_ready(docker: Optional[str]) -> bool:
    if not docker:
        return False
    try:
        process_checked((docker, "version", "--format", "{{.Server.Version}}"))
    except MediaError:
        return False
    return True


def docker_image_present(docker: str, image: str) -> bool:
    try:
        process_checked((docker, "image", "inspect", image))
    except MediaError:
        return False
    return True


def docker_image_details(docker: str, image: str) -> dict[str, Any]:
    result = process_checked(
        (
            docker,
            "image",
            "inspect",
            image,
            "--format",
            "{{json .}}",
        )
    )
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"reference": image}
    return {
        "reference": image,
        "id": value.get("Id"),
        "repo_digests": value.get("RepoDigests") or [],
        "architecture": value.get("Architecture"),
        "os": value.get("Os"),
    }


def requested_runtime(args: argparse.Namespace) -> str:
    runtime = (args.runtime or os.environ.get("AGNES_MEDIA_RUNTIME") or "auto").strip()
    if runtime not in {"auto", "docker", "native"}:
        raise MediaError("media runtime must be auto, docker, or native")
    return runtime


def configured_docker_image(args: argparse.Namespace) -> str:
    image = (
        args.docker_image
        or os.environ.get("AGNES_MEDIA_DOCKER_IMAGE")
        or DEFAULT_DOCKER_IMAGE
    ).strip()
    if not image:
        raise MediaError("Docker image reference must not be empty")
    return image


def configure_runtime(args: argparse.Namespace) -> None:
    global _selected_runtime, _selected_docker_cli, _selected_docker_image

    runtime = requested_runtime(args)
    native_ffmpeg = optional_executable(
        args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe")
    )
    native_ffprobe = optional_executable(
        args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe")
    )
    native_ready = bool(native_ffmpeg and native_ffprobe)
    native_was_explicit = bool(
        args.ffmpeg
        or args.ffprobe
        or os.environ.get("FFMPEG_BIN")
        or os.environ.get("FFPROBE_BIN")
    )

    docker = optional_executable(args.docker, "DOCKER_BIN", ("docker", "docker.exe"))
    image = configured_docker_image(args)
    engine_ready = docker_engine_ready(docker)
    image_present = bool(engine_ready and docker and docker_image_present(docker, image))
    should_prepare_docker = runtime == "docker" or (
        runtime == "auto" and not native_was_explicit
    )
    if (
        should_prepare_docker
        and engine_ready
        and docker
        and not image_present
        and args.pull_docker_image
    ):
        process_checked((docker, "pull", image))
        image_present = docker_image_present(docker, image)
    docker_ready = bool(engine_ready and docker and image_present)

    if runtime == "native" or (runtime == "auto" and native_was_explicit):
        if not native_ready:
            raise MediaError("native runtime requested but ffmpeg and ffprobe are not both ready")
        _selected_runtime = "native"
        _selected_docker_cli = None
        _selected_docker_image = None
        return
    if runtime == "docker":
        if not engine_ready:
            raise MediaError("Docker runtime requested but the Docker engine is unavailable")
        if not image_present:
            raise MediaError(
                f"Docker image is not available locally: {image}; pull it explicitly or "
                "pass --pull-docker-image after dependency acquisition is authorized"
            )
        _selected_runtime = "docker"
        _selected_docker_cli = docker
        _selected_docker_image = image
        return
    if docker_ready:
        _selected_runtime = "docker"
        _selected_docker_cli = docker
        _selected_docker_image = image
        return
    if native_ready:
        _selected_runtime = "native"
        _selected_docker_cli = None
        _selected_docker_image = None
        return

    missing_image = (
        f"; Docker engine is ready but image is absent: {image}" if engine_ready else ""
    )
    raise MediaError(
        "no usable media runtime: Docker is unavailable or unprepared and native "
        f"ffmpeg/ffprobe are missing{missing_image}"
    )


def docker_mount_value(source: Path, target: str, read_only: bool) -> str:
    source_text = str(source)
    if "," in source_text:
        raise MediaError("Docker bind-mount paths containing commas are unsupported")
    value = f"type=bind,src={source_text},dst={target}"
    return f"{value},readonly" if read_only else value


def dockerized_command(
    tool: str,
    arguments: Sequence[str],
    cwd: Optional[Path],
    container_name: Optional[str] = None,
) -> list[str]:
    if not _selected_docker_cli or not _selected_docker_image:
        raise MediaError("Docker media runtime is not configured")

    resolved_cwd = cwd.resolve() if cwd else None
    path_tokens: dict[int, Path] = {}
    for index, token in enumerate(arguments):
        candidate = Path(token).expanduser()
        if candidate.is_absolute():
            path_tokens[index] = candidate.resolve(strict=False)

    output_index = len(arguments) - 1 if tool == "ffmpeg" else -1
    mount_modes: dict[Path, bool] = {}
    if resolved_cwd:
        mount_modes[resolved_cwd] = True
    for index, path in path_tokens.items():
        parent = path.parent
        writable = index == output_index
        mount_modes[parent] = mount_modes.get(parent, False) or writable

    mount_targets: dict[Path, str] = {}
    next_mount = 0
    for parent in mount_modes:
        if resolved_cwd and parent == resolved_cwd:
            mount_targets[parent] = "/work"
        else:
            mount_targets[parent] = f"/agnes/mount-{next_mount}"
            next_mount += 1

    mapped_arguments = list(arguments)
    for index, path in path_tokens.items():
        mapped_arguments[index] = f"{mount_targets[path.parent]}/{path.name}"

    command = [
        _selected_docker_cli,
        "run",
        "--rm",
        *(("--name", container_name) if container_name else ()),
        *(
            (
                "--label",
                f"{DOCKER_MANAGED_LABEL}=true",
                "--label",
                f"{DOCKER_OPERATION_LABEL}={_operation_id}",
                "--label",
                f"{DOCKER_PARENT_PID_LABEL}={os.getpid()}",
                "--label",
                f"{DOCKER_STARTED_AT_LABEL}={_operation_started_at}",
                "--label",
                f"{DOCKER_COMMAND_LABEL}={_operation_command}",
            )
            if container_name
            else ()
        ),
        "--network",
        "none",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
    ]
    if os.name != "nt" and hasattr(os, "getuid") and hasattr(os, "getgid"):
        command.extend(["--user", f"{os.getuid()}:{os.getgid()}"])
    if resolved_cwd and (resolved_cwd / "fonts.conf").is_file():
        command.extend(
            [
                "--env",
                "FONTCONFIG_FILE=/work/fonts.conf",
                "--env",
                "FONTCONFIG_PATH=/work",
            ]
        )
    for parent, writable in mount_modes.items():
        command.extend(
            [
                "--mount",
                docker_mount_value(parent, mount_targets[parent], not writable),
            ]
        )
    if resolved_cwd:
        command.extend(["--workdir", "/work"])
    command.extend(
        [
            "--entrypoint",
            tool,
            _selected_docker_image,
            *mapped_arguments,
        ]
    )
    return command


def remove_docker_container(container_name: str) -> None:
    if not _selected_docker_cli:
        return
    try:
        subprocess.run(
            [_selected_docker_cli, "rm", "-f", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        pass


def docker_process_checked(
    tool: str, arguments: Sequence[str], cwd: Optional[Path]
) -> subprocess.CompletedProcess[str]:
    global _operation_announced

    ensure_operation_not_cancelled()
    container_name = operation_container_name()
    if not _operation_announced:
        print(
            json.dumps(
                {
                    "event": "docker_operation_started",
                    "operation_id": _operation_id,
                    "command": _operation_command,
                },
                ensure_ascii=False,
            ),
            file=sys.stderr,
            flush=True,
        )
        _operation_announced = True
    process = subprocess.Popen(
        dockerized_command(tool, arguments, cwd, container_name),
        cwd=str(cwd) if cwd else None,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    previous_sigterm: Any = None

    def terminate_on_signal(_signum: int, _frame: Any) -> None:
        raise KeyboardInterrupt

    try:
        try:
            previous_sigterm = signal.signal(signal.SIGTERM, terminate_on_signal)
        except (AttributeError, ValueError):
            previous_sigterm = None
        while True:
            if operation_cancel_requested(_operation_id):
                raise MediaError(f"Docker media operation {_operation_id} was cancelled")
            try:
                stdout, stderr = process.communicate(timeout=0.25)
                break
            except subprocess.TimeoutExpired:
                continue
    except BaseException:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        remove_docker_container(container_name)
        raise
    finally:
        if previous_sigterm is not None:
            signal.signal(signal.SIGTERM, previous_sigterm)

    completed = subprocess.CompletedProcess(
        process.args,
        process.returncode,
        stdout,
        stderr,
    )
    if completed.returncode != 0:
        remove_docker_container(container_name)
        detail = completed.stderr.strip() or completed.stdout.strip()
        if len(detail) > 6000:
            detail = detail[-6000:]
        raise MediaError(
            f"command failed with exit code {completed.returncode}: {detail}"
        )
    return completed


def run_checked(
    command: Sequence[str], cwd: Optional[Path] = None
) -> subprocess.CompletedProcess[str]:
    if command and command[0] in {DOCKER_FFMPEG, DOCKER_FFPROBE}:
        tool = "ffmpeg" if command[0] == DOCKER_FFMPEG else "ffprobe"
        return docker_process_checked(tool, command[1:], cwd)
    return process_checked(command, cwd)


def managed_docker_cli(args: argparse.Namespace) -> str:
    docker = optional_executable(args.docker, "DOCKER_BIN", ("docker", "docker.exe"))
    if not docker or not docker_engine_ready(docker):
        raise MediaError("Docker container management requires a reachable Docker engine")
    return docker


def managed_container_ids(docker: str, operation_id: Optional[str]) -> list[str]:
    command = [
        docker,
        "ps",
        "-aq",
        "--filter",
        f"label={DOCKER_MANAGED_LABEL}=true",
    ]
    if operation_id:
        command.extend(
            ["--filter", f"label={DOCKER_OPERATION_LABEL}={operation_id}"]
        )
    result = process_checked(command)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def parent_process_state(raw_pid: Any) -> tuple[Optional[int], Optional[bool]]:
    try:
        pid = int(raw_pid)
    except (TypeError, ValueError):
        return None, None
    if pid <= 0:
        return None, None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return pid, False
    except PermissionError:
        return pid, True
    except OSError:
        return pid, None
    return pid, True


def registered_operation_summary(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    operation_id = record.get("operation_id")
    if not isinstance(operation_id, str) or not re.fullmatch(
        r"[0-9a-f]{32}", operation_id
    ):
        return None
    try:
        started_at = float(record.get("started_at"))
    except (TypeError, ValueError):
        started_at = None
    if started_at is not None and (not math.isfinite(started_at) or started_at <= 0):
        started_at = None
    parent_pid, parent_alive = parent_process_state(record.get("parent_pid"))
    return {
        "operation_id": operation_id,
        "command": record.get("command"),
        "started_at": started_at,
        "age_seconds": max(0.0, time.time() - started_at) if started_at else None,
        "parent_pid": parent_pid,
        "parent_alive": parent_alive,
        "cancel_requested": operation_cancel_requested(operation_id),
    }


def registered_operations(operation_id: Optional[str]) -> list[dict[str, Any]]:
    directory = operation_registry_directory(False)
    if directory is None:
        return []
    if operation_id:
        paths = [directory / f"{operation_id}.json"]
    else:
        paths = sorted(directory.glob("*.json"))
    operations = []
    for path in paths:
        if not path.is_file() or path.is_symlink():
            continue
        candidate_id = path.stem
        if not re.fullmatch(r"[0-9a-f]{32}", candidate_id):
            continue
        record = read_operation_record(candidate_id)
        if record is None:
            continue
        summary = registered_operation_summary(record)
        if summary is not None:
            operations.append(summary)
    operations.sort(
        key=lambda item: (
            item["started_at"] or 0.0,
            item["operation_id"],
        )
    )
    return operations


def inspect_managed_container(
    docker: str, container_id: str
) -> Optional[dict[str, Any]]:
    completed = subprocess.run(
        [docker, "inspect", container_id],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        if "No such" in detail or "not found" in detail.lower():
            return None
        raise MediaError(f"Docker inspect failed for {container_id}: {detail}")
    try:
        values = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise MediaError(f"Docker inspect returned invalid JSON: {error}") from error
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise MediaError(f"Docker inspect returned an unexpected record for {container_id}")

    value = values[0]
    config = value.get("Config") if isinstance(value.get("Config"), dict) else {}
    labels = config.get("Labels") if isinstance(config.get("Labels"), dict) else {}
    if labels.get(DOCKER_MANAGED_LABEL) != "true":
        return None
    state = value.get("State") if isinstance(value.get("State"), dict) else {}
    raw_started_at = labels.get(DOCKER_STARTED_AT_LABEL)
    try:
        started_at = float(raw_started_at)
    except (TypeError, ValueError):
        started_at = None
    if started_at is not None and (not math.isfinite(started_at) or started_at <= 0):
        started_at = None
    age_seconds = max(0.0, time.time() - started_at) if started_at else None
    parent_pid, parent_alive = parent_process_state(
        labels.get(DOCKER_PARENT_PID_LABEL)
    )
    return {
        "id": str(value.get("Id") or container_id),
        "name": str(value.get("Name") or "").lstrip("/"),
        "operation_id": labels.get(DOCKER_OPERATION_LABEL),
        "command": labels.get(DOCKER_COMMAND_LABEL),
        "image": config.get("Image"),
        "status": state.get("Status"),
        "running": bool(state.get("Running")),
        "started_at": started_at,
        "age_seconds": age_seconds,
        "parent_pid": parent_pid,
        "parent_alive": parent_alive,
    }


def inspect_managed_containers(
    docker: str, operation_id: Optional[str]
) -> list[dict[str, Any]]:
    containers = []
    for container_id in managed_container_ids(docker, operation_id):
        container = inspect_managed_container(docker, container_id)
        if container is None:
            continue
        if operation_id and container["operation_id"] != operation_id:
            continue
        containers.append(container)
    containers.sort(
        key=lambda item: (item["started_at"] or 0.0, item["name"], item["id"])
    )
    return containers


def remove_managed_container(
    docker: str, container_id: str, operation_id: str
) -> bool:
    current = inspect_managed_container(docker, container_id)
    if current is None:
        return False
    if current["operation_id"] != operation_id:
        raise MediaError(
            f"refusing to remove container {container_id}: operation ownership changed"
        )
    completed = subprocess.run(
        [docker, "rm", "-f", container_id],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    if completed.returncode == 0:
        return True
    detail = completed.stderr.strip() or completed.stdout.strip()
    if "No such" in detail or "not found" in detail.lower():
        return False
    raise MediaError(f"failed to remove managed container {container_id}: {detail}")


def managed_containers_command(args: argparse.Namespace) -> None:
    docker = managed_docker_cli(args)
    containers = inspect_managed_containers(docker, args.operation_id)
    operations = registered_operations(args.operation_id)
    print_result(
        {
            "operation": "managed-containers",
            "operation_id": args.operation_id,
            "managed_label": f"{DOCKER_MANAGED_LABEL}=true",
            "count": len(containers),
            "containers": containers,
            "registered_operation_count": len(operations),
            "registered_operations": operations,
        }
    )


def cancel_command(args: argparse.Namespace) -> None:
    docker = managed_docker_cli(args)
    operations = registered_operations(args.operation_id)
    containers = inspect_managed_containers(docker, args.operation_id)
    cancel_requested = bool(operations or containers)
    if cancel_requested:
        create_operation_cancel_marker(args.operation_id)

    matched: dict[str, dict[str, Any]] = {
        container["id"]: container for container in containers
    }
    cancelled = []
    for attempt in range(3):
        current = inspect_managed_containers(docker, args.operation_id)
        for container in current:
            matched[container["id"]] = container
            if remove_managed_container(docker, container["id"], args.operation_id):
                cancelled.append(
                    {
                        "id": container["id"],
                        "name": container["name"],
                    }
                )
        if attempt < 2:
            time.sleep(0.1)

    remaining = inspect_managed_containers(docker, args.operation_id)
    operation_still_registered = bool(read_operation_record(args.operation_id))
    if not remaining and not operation_still_registered:
        marker = operation_cancel_path(args.operation_id, False)
        if marker and marker.is_file() and not marker.is_symlink():
            marker.unlink()
    print_result(
        {
            "operation": "cancel",
            "operation_id": args.operation_id,
            "registered": bool(operations),
            "cancel_requested": cancel_requested,
            "matched_count": len(matched),
            "cancelled_count": len(cancelled),
            "cancelled": cancelled,
            "remaining_container_count": len(remaining),
            "operation_still_registered": operation_still_registered,
            "already_absent": not operations and not matched,
        }
    )


def cleanup_command(args: argparse.Namespace) -> None:
    docker = managed_docker_cli(args)
    containers = inspect_managed_containers(docker, args.operation_id)
    operations = registered_operations(args.operation_id)
    removed = []
    skipped = []
    for container in containers:
        age_seconds = container["age_seconds"]
        operation_id = container["operation_id"]
        if not isinstance(operation_id, str) or not re.fullmatch(
            r"[0-9a-f]{32}", operation_id
        ):
            reason = "invalid-operation-metadata"
        elif age_seconds is None:
            reason = "invalid-start-time-metadata"
        elif age_seconds < args.stale_after:
            reason = "younger-than-threshold"
        elif container["parent_alive"] is True:
            reason = "parent-alive"
        elif container["parent_alive"] is None:
            reason = "unknown-parent-state"
        else:
            reason = None
        if reason:
            skipped.append(
                {
                    "id": container["id"],
                    "name": container["name"],
                    "operation_id": operation_id,
                    "reason": reason,
                }
            )
            continue
        if remove_managed_container(docker, container["id"], operation_id):
            removed.append(
                {
                    "id": container["id"],
                    "name": container["name"],
                    "operation_id": operation_id,
                }
            )

    removed_operations = []
    skipped_operations = []
    for operation in operations:
        age_seconds = operation["age_seconds"]
        if age_seconds is None:
            reason = "invalid-start-time-metadata"
        elif age_seconds < args.stale_after:
            reason = "younger-than-threshold"
        elif operation["parent_alive"] is True:
            reason = "parent-alive"
        elif operation["parent_alive"] is None:
            reason = "unknown-parent-state"
        elif inspect_managed_containers(docker, operation["operation_id"]):
            reason = "managed-containers-remain"
        else:
            reason = None
        if reason:
            skipped_operations.append(
                {
                    "operation_id": operation["operation_id"],
                    "reason": reason,
                }
            )
            continue
        remove_operation_registry(operation["operation_id"])
        removed_operations.append(operation["operation_id"])
    print_result(
        {
            "operation": "cleanup",
            "operation_id": args.operation_id,
            "stale_after_seconds": args.stale_after,
            "matched_count": len(containers),
            "removed_count": len(removed),
            "removed": removed,
            "skipped": skipped,
            "registered_operation_count": len(operations),
            "removed_operation_count": len(removed_operations),
            "removed_operations": removed_operations,
            "skipped_operations": skipped_operations,
        }
    )


def ffmpeg_command(ffmpeg: str, arguments: Iterable[str]) -> list[str]:
    return [ffmpeg, "-hide_banner", "-loglevel", "error", *arguments]


def require_input(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        raise MediaError(f"input file not found: {path}")
    return path


def prepare_output(path_text: str, overwrite: bool) -> Path:
    output = Path(path_text).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not overwrite:
        raise MediaError(f"output already exists (pass --overwrite to replace it): {output}")
    return output


def probe_media(ffprobe: str, path: Path) -> dict[str, Any]:
    result = run_checked(
        [
            ffprobe,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(path),
        ]
    )
    try:
        details = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise MediaError(f"ffprobe returned invalid JSON: {error}") from error
    if isinstance(details.get("format"), dict):
        details["format"]["filename"] = str(path)
    return details


def duration_seconds(probe: dict[str, Any]) -> float:
    candidates: list[Any] = [probe.get("format", {}).get("duration")]
    candidates.extend(stream.get("duration") for stream in probe.get("streams", []))
    for candidate in candidates:
        try:
            duration = float(candidate)
        except (TypeError, ValueError):
            continue
        if math.isfinite(duration) and duration > 0:
            return duration
    raise MediaError("media duration could not be determined")


def stream_exists(probe: dict[str, Any], codec_type: str) -> bool:
    return any(
        stream.get("codec_type") == codec_type for stream in probe.get("streams", [])
    )


def video_stream(probe: dict[str, Any]) -> dict[str, Any]:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == "video":
            return stream
    raise MediaError("input has no video stream")


def video_frame_rate(probe: dict[str, Any]) -> float:
    stream = video_stream(probe)
    for key in ("avg_frame_rate", "r_frame_rate"):
        raw_rate = stream.get(key)
        try:
            fps = float(Fraction(str(raw_rate)))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if math.isfinite(fps) and fps > 0:
            return fps
    return 24.0


def frame_interval(probe: dict[str, Any]) -> float:
    return max(1.0 / video_frame_rate(probe), 0.04)


def target_video_settings(
    details: dict[str, Any],
    requested_width: Optional[int],
    requested_height: Optional[int],
    requested_fps: Optional[float],
) -> tuple[int, int, float]:
    if (requested_width is None) != (requested_height is None):
        raise MediaError("--width and --height must be provided together")
    stream = video_stream(details)
    if requested_width is None:
        width = int(stream.get("width") or 0)
        height = int(stream.get("height") or 0)
        if width <= 0 or height <= 0:
            raise MediaError("first clip dimensions could not be determined")
        width -= width % 2
        height -= height % 2
    else:
        width = requested_width
        height = requested_height
    if requested_fps is None:
        raw_rate = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
        try:
            fps = float(Fraction(str(raw_rate)))
        except (ValueError, ZeroDivisionError):
            fps = 24.0
        if not math.isfinite(fps) or fps <= 0:
            fps = 24.0
    else:
        fps = requested_fps
    return width, height, fps


def print_result(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def runtime_metadata() -> dict[str, Any]:
    metadata: dict[str, Any] = {"runtime": _selected_runtime}
    if _selected_runtime == "docker":
        metadata["docker_image"] = _selected_docker_image
        metadata["operation_id"] = _operation_id
    return metadata


def capability_report(ffmpeg: Optional[str], ffprobe: Optional[str]) -> dict[str, Any]:
    errors: list[str] = []
    filters = ""
    encoders = ""
    if ffmpeg:
        try:
            filters = run_checked(ffmpeg_command(ffmpeg, ("-filters",))).stdout
            encoders = run_checked(ffmpeg_command(ffmpeg, ("-encoders",))).stdout
        except MediaError as error:
            errors.append(str(error))
    features = {
        "ffmpeg": bool(ffmpeg),
        "ffprobe": bool(ffprobe),
        "subtitles": bool(re.search(r"\bsubtitles\b", filters)),
        "xfade": bool(re.search(r"\bxfade\b", filters)),
        "acrossfade": bool(re.search(r"\bacrossfade\b", filters)),
        "adelay": bool(re.search(r"\badelay\b", filters)),
        "alimiter": bool(re.search(r"\balimiter\b", filters)),
        "libx264": bool(re.search(r"\blibx264\b", encoders)),
        "aac": bool(re.search(r"\baac\b", encoders)),
    }

    def operation(*requirements: str) -> dict[str, Any]:
        missing = [name for name in requirements if not features[name]]
        return {"ready": not missing, "missing": missing}

    operations = {
        "probe": operation("ffprobe"),
        "contact_sheet": operation("ffmpeg", "ffprobe"),
        "extract_frame": operation("ffmpeg", "ffprobe"),
        "trim": operation("ffmpeg", "ffprobe", "libx264", "aac"),
        "concat_cut": operation("ffmpeg", "ffprobe", "libx264", "aac"),
        "concat_transition": operation(
            "ffmpeg", "ffprobe", "libx264", "aac", "xfade", "acrossfade"
        ),
        "add_audio": operation("ffmpeg", "ffprobe", "aac", "adelay"),
        "mix_audio_timeline": operation(
            "ffmpeg", "ffprobe", "aac", "adelay", "alimiter"
        ),
        "burn_subtitles": operation("ffmpeg", "subtitles", "libx264"),
    }
    report = {
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "filters": {
            "subtitles": bool(re.search(r"\bsubtitles\b", filters)),
            "xfade": bool(re.search(r"\bxfade\b", filters)),
            "acrossfade": bool(re.search(r"\bacrossfade\b", filters)),
            "adelay": bool(re.search(r"\badelay\b", filters)),
            "alimiter": bool(re.search(r"\balimiter\b", filters)),
        },
        "encoders": {
            "libx264": bool(re.search(r"\blibx264\b", encoders)),
            "aac": bool(re.search(r"\baac\b", encoders)),
        },
        "operations": operations,
    }
    report["ready"] = bool(ffmpeg and ffprobe and not errors)
    report["all_operations_ready"] = bool(not errors) and all(
        details["ready"] for details in operations.values()
    )
    if errors:
        report["errors"] = errors
    return report


def doctor(args: argparse.Namespace) -> None:
    global _selected_runtime, _selected_docker_cli, _selected_docker_image

    native_ffmpeg = optional_executable(
        args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe")
    )
    native_ffprobe = optional_executable(
        args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe")
    )
    native_report = capability_report(native_ffmpeg, native_ffprobe)

    docker = optional_executable(args.docker, "DOCKER_BIN", ("docker", "docker.exe"))
    image = configured_docker_image(args)
    engine_ready = docker_engine_ready(docker)
    image_present = bool(engine_ready and docker and docker_image_present(docker, image))
    runtime = requested_runtime(args)
    native_was_explicit = bool(
        args.ffmpeg
        or args.ffprobe
        or os.environ.get("FFMPEG_BIN")
        or os.environ.get("FFPROBE_BIN")
    )
    if (
        engine_ready
        and docker
        and not image_present
        and args.pull_docker_image
        and (runtime == "docker" or (runtime == "auto" and not native_was_explicit))
    ):
        process_checked((docker, "pull", image))
        image_present = docker_image_present(docker, image)

    previous = (_selected_runtime, _selected_docker_cli, _selected_docker_image)
    docker_report: dict[str, Any] = {
        "cli": docker,
        "engine_ready": engine_ready,
        "image_present": image_present,
        "image": {"reference": image},
        "capabilities": None,
    }
    if image_present and docker:
        docker_report["image"] = docker_image_details(docker, image)
        _selected_runtime = "docker"
        _selected_docker_cli = docker
        _selected_docker_image = image
        docker_report["capabilities"] = capability_report(
            DOCKER_FFMPEG, DOCKER_FFPROBE
        )
    _selected_runtime, _selected_docker_cli, _selected_docker_image = previous

    selection_error: Optional[str] = None
    try:
        configure_runtime(args)
        selected_runtime: Optional[str] = _selected_runtime
    except MediaError as error:
        selected_runtime = None
        selection_error = str(error)

    result: dict[str, Any] = {
        "requested_runtime": runtime,
        "selected_runtime": selected_runtime,
        "native": native_report,
        "docker": docker_report,
        "ready": selected_runtime is not None,
    }
    if selection_error:
        result["selection_error"] = selection_error
    print_result(result)


def probe_command(args: argparse.Namespace) -> None:
    path = require_input(args.input)
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    result = probe_media(ffprobe, path)
    if args.output:
        output = prepare_output(args.output, args.overwrite)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print_result(
            {
                "operation": "probe",
                "input": str(path),
                "report": str(output),
                **runtime_metadata(),
            }
        )
    else:
        print_result(result)


def normalize_clip(
    ffmpeg: str,
    ffprobe: str,
    source: Path,
    output: Path,
    width: int,
    height: int,
    fps: float,
    crf: int,
    preset: str,
) -> float:
    details = probe_media(ffprobe, source)
    video_stream(details)
    duration_seconds(details)
    scale = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"fps={fps},setsar=1,setpts=PTS-STARTPTS"
    )
    command = ["-y", "-i", str(source)]
    if stream_exists(details, "audio"):
        command.extend(
            [
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-vf",
                scale,
                "-af",
                "aresample=48000,asetpts=PTS-STARTPTS",
            ]
        )
    else:
        command.extend(
            [
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-vf",
                scale,
                "-shortest",
            ]
        )
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run_checked(ffmpeg_command(ffmpeg, command))
    return duration_seconds(probe_media(ffprobe, output))


def hard_cut_concat(ffmpeg: str, clips: Sequence[Path], output: Path) -> None:
    listing = output.parent / "concat.txt"
    listing.write_text(
        "".join(f"file '{clip.name}'\n" for clip in clips), encoding="utf-8"
    )
    run_checked(
        ffmpeg_command(
            ffmpeg,
            (
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                listing.name,
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output),
            ),
        ),
        cwd=output.parent,
    )


TRANSITIONS = {
    "fade",
    "fadeblack",
    "fadewhite",
    "dissolve",
    "wipeleft",
    "wiperight",
    "slideleft",
    "slideright",
    "smoothleft",
    "smoothright",
    "pixelize",
}


def transition_concat(
    ffmpeg: str,
    clips: Sequence[Path],
    durations: Sequence[float],
    output: Path,
    transition: str,
    transition_duration: float,
    crf: int,
    preset: str,
) -> None:
    if transition not in TRANSITIONS:
        raise MediaError(
            f"unsupported transition {transition!r}; choose one of {sorted(TRANSITIONS)}"
        )
    if any(duration <= transition_duration for duration in durations):
        raise MediaError("transition duration must be shorter than every input clip")

    command: list[str] = ["-y"]
    for clip in clips:
        command.extend(["-i", str(clip)])

    filters: list[str] = []
    current_video = "[0:v]"
    current_audio = "[0:a]"
    merged_duration = durations[0]
    for index in range(1, len(clips)):
        offset = merged_duration - transition_duration
        next_video = f"[v{index}]"
        next_audio = f"[a{index}]"
        filters.append(
            f"{current_video}[{index}:v]xfade=transition={transition}:"
            f"duration={transition_duration:.6f}:offset={offset:.6f}{next_video}"
        )
        filters.append(
            f"{current_audio}[{index}:a]acrossfade=d={transition_duration:.6f}:"
            f"c1=tri:c2=tri{next_audio}"
        )
        current_video = next_video
        current_audio = next_audio
        merged_duration += durations[index] - transition_duration

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            current_video,
            "-map",
            current_audio,
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run_checked(ffmpeg_command(ffmpeg, command))


def concat_command(args: argparse.Namespace) -> None:
    if len(args.inputs) < 2:
        raise MediaError("concat requires at least two input clips")
    inputs = [require_input(value) for value in args.inputs]
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    first_details = probe_media(ffprobe, inputs[0])
    width, height, fps = target_video_settings(
        first_details, args.width, args.height, args.fps
    )

    with tempfile.TemporaryDirectory(prefix=".agnes-video-", dir=output.parent) as raw:
        temporary = Path(raw)
        normalized: list[Path] = []
        durations: list[float] = []
        for index, source in enumerate(inputs):
            clip = temporary / f"{index:04d}.mp4"
            durations.append(
                normalize_clip(
                    ffmpeg,
                    ffprobe,
                    source,
                    clip,
                    width,
                    height,
                    fps,
                    args.crf,
                    args.preset,
                )
            )
            normalized.append(clip)

        staged = temporary / "render.mp4"
        if args.transition_duration > 0:
            transition_concat(
                ffmpeg,
                normalized,
                durations,
                staged,
                args.transition,
                args.transition_duration,
                args.crf,
                args.preset,
            )
        else:
            hard_cut_concat(ffmpeg, normalized, staged)
        if output.exists():
            output.unlink()
        staged.replace(output)

    final_probe = probe_media(ffprobe, output)
    print_result(
        {
            "operation": "concat",
            "output": str(output),
            **runtime_metadata(),
            "inputs": [str(path) for path in inputs],
            "duration": duration_seconds(final_probe),
            "width": width,
            "height": height,
            "fps": fps,
            "transition": args.transition if args.transition_duration > 0 else "cut",
            "transition_duration": args.transition_duration,
        }
    )


def trim_command(args: argparse.Namespace) -> None:
    source = require_input(args.input)
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    details = probe_media(ffprobe, source)
    source_duration = duration_seconds(details)
    if args.start >= source_duration:
        raise MediaError("--start must be before the end of the input")
    if args.end is not None and args.duration is not None:
        raise MediaError("use only one of --end or --duration")
    if args.end is not None:
        if args.end <= args.start:
            raise MediaError("--end must be greater than --start")
        clip_duration = args.end - args.start
    elif args.duration is not None:
        clip_duration = args.duration
    else:
        clip_duration = source_duration - args.start
    clip_duration = min(clip_duration, source_duration - args.start)

    command = [
        "-y",
        "-ss",
        f"{args.start:.6f}",
        "-i",
        str(source),
        "-t",
        f"{clip_duration:.6f}",
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-c:v",
        "libx264",
        "-preset",
        args.preset,
        "-crf",
        str(args.crf),
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    run_checked(ffmpeg_command(ffmpeg, command))
    final_duration = duration_seconds(probe_media(ffprobe, output))
    print_result(
        {
            "operation": "trim",
            "input": str(source),
            "output": str(output),
            **runtime_metadata(),
            "start": args.start,
            "duration": final_duration,
        }
    )


def contact_sheet_command(args: argparse.Namespace) -> None:
    source = require_input(args.input)
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    details = probe_media(ffprobe, source)
    duration = duration_seconds(details)
    video_stream(details)
    start = args.start
    end = args.end if args.end is not None else duration
    if start >= duration:
        raise MediaError("--start must be before the end of the input")
    if end <= start:
        raise MediaError("--end must be greater than --start")
    if end > duration + frame_interval(details):
        raise MediaError("--end must not exceed the input duration")
    end = min(end, duration)

    if args.mode == "first":
        seek = start
        frames = 1
        columns = 1
        video_filter = (
            f"scale={args.thumb_width}:-2:force_original_aspect_ratio=decrease"
        )
    elif args.mode == "last":
        seek = max(start, end - frame_interval(details))
        frames = 1
        columns = 1
        video_filter = (
            f"scale={args.thumb_width}:-2:force_original_aspect_ratio=decrease"
        )
    else:
        seek = start
        frames = args.frames
        columns = min(args.columns, frames)
        rows = math.ceil(frames / columns)
        sample_rate = max(frames / (end - start), 0.001)
        video_filter = (
            f"fps={sample_rate:.10f},"
            f"scale={args.thumb_width}:-2:force_original_aspect_ratio=decrease,"
            f"tile={columns}x{rows}:nb_frames={frames}:"
            "padding=4:margin=4:color=black"
        )

    with tempfile.TemporaryDirectory(
        prefix=".agnes-contact-sheet-", dir=output.parent
    ) as raw:
        temporary = Path(raw)
        staged = temporary / f"sheet{output.suffix or '.png'}"
        command = [
            "-y",
            "-ss",
            f"{seek:.6f}",
            "-i",
            str(source),
        ]
        if args.mode == "even":
            command.extend(["-t", f"{end - start:.6f}"])
        command.extend(
            [
                "-vf",
                video_filter,
                "-frames:v",
                "1",
                str(staged),
            ]
        )
        run_checked(ffmpeg_command(ffmpeg, command))
        if output.exists():
            output.unlink()
        staged.replace(output)

    print_result(
        {
            "operation": "contact-sheet",
            "input": str(source),
            "output": str(output),
            **runtime_metadata(),
            "frames": frames,
            "columns": columns,
            "start": start,
            "end": end,
            "mode": args.mode,
        }
    )


def extract_frame_command(args: argparse.Namespace) -> None:
    source = require_input(args.input)
    output = prepare_output(args.output, args.overwrite)
    if output.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise MediaError("frame output must be PNG, JPEG, or WebP")
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    details = probe_media(ffprobe, source)
    duration = duration_seconds(details)
    video_stream(details)

    if args.at is not None:
        if args.at >= duration:
            raise MediaError("--at must be before the end of the input")
        seek = args.at
        position = "time"
    elif args.position == "first":
        seek = 0.0
        position = "first"
    else:
        seek = max(0.0, duration - frame_interval(details))
        position = "last"

    with tempfile.TemporaryDirectory(
        prefix=".agnes-extract-frame-", dir=output.parent
    ) as raw:
        temporary = Path(raw)
        staged = temporary / f"frame{output.suffix}"
        run_checked(
            ffmpeg_command(
                ffmpeg,
                (
                    "-y",
                    "-i",
                    str(source),
                    "-ss",
                    f"{seek:.6f}",
                    "-map",
                    "0:v:0",
                    "-frames:v",
                    "1",
                    "-an",
                    str(staged),
                ),
            )
        )
        if output.exists():
            output.unlink()
        staged.replace(output)

    print_result(
        {
            "operation": "extract-frame",
            "input": str(source),
            "output": str(output),
            **runtime_metadata(),
            "position": position,
            "time_seconds": seek,
        }
    )


def parse_subtitle_timestamp(value: str) -> float:
    parts = value.strip().replace(",", ".").split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = "0"
        minutes, seconds = parts
    else:
        raise MediaError(f"invalid subtitle timestamp: {value}")
    try:
        result = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except ValueError as error:
        raise MediaError(f"invalid subtitle timestamp: {value}") from error
    if not math.isfinite(result) or result < 0:
        raise MediaError(f"invalid subtitle timestamp: {value}")
    return result


def decode_subtitle_file(path: Path) -> str:
    data = path.read_bytes()
    encodings = ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be")
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise MediaError(
        "subtitle encoding is unsupported; save the file as UTF-8 or UTF-16"
    )


def clean_subtitle_markup(value: str) -> str:
    value = value.replace(r"\N", "\n").replace(r"\n", "\n").replace(r"\h", " ")
    value = re.sub(r"\{[^}]*\}", "", value)
    value = re.sub(r"<[^>]*>", "", value)
    return html.unescape(value)


def subtitle_display_columns(value: str) -> int:
    columns = 0
    for character in value:
        if character == "\t":
            columns += 4
        elif unicodedata.combining(character):
            continue
        elif unicodedata.east_asian_width(character) in {"F", "W"}:
            columns += 2
        elif not unicodedata.category(character).startswith("C"):
            columns += 1
    return columns


def subtitle_payload(path: Path) -> dict[str, Any]:
    content = decode_subtitle_file(path)
    extension = path.suffix.lower()
    cues: list[dict[str, Any]] = []
    play_res_x = 384
    play_res_y = 288
    if extension in {".ass", ".ssa"}:
        match_x = re.search(r"(?im)^\s*PlayResX\s*:\s*(\d+)\s*$", content)
        match_y = re.search(r"(?im)^\s*PlayResY\s*:\s*(\d+)\s*$", content)
        if match_x:
            play_res_x = max(1, int(match_x.group(1)))
        if match_y:
            play_res_y = max(1, int(match_y.group(1)))

    def append_cue(start_text: str, end_text: str, cue_text: str) -> None:
        start = parse_subtitle_timestamp(start_text)
        end = parse_subtitle_timestamp(end_text)
        if end <= start:
            raise MediaError(
                f"subtitle cue must end after it starts: {start_text} --> {end_text}"
            )
        visible = clean_subtitle_markup(cue_text).strip()
        if not visible:
            return
        lines = visible.splitlines() or [visible]
        line_columns = [subtitle_display_columns(line) for line in lines]
        cues.append(
            {
                "start": start,
                "end": end,
                "text": visible,
                "line_count": len(lines),
                "line_columns": line_columns,
                "max_line_columns": max(line_columns),
            }
        )

    if extension in {".ass", ".ssa"}:
        for line in content.splitlines():
            if not line.lstrip().lower().startswith("dialogue:"):
                continue
            payload = line.split(":", 1)[1].lstrip()
            fields = payload.split(",", 9)
            if len(fields) != 10:
                continue
            append_cue(fields[1], fields[2], fields[9])
    else:
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        for block in re.split(r"\n\s*\n", normalized):
            lines = block.splitlines()
            timestamp_index: Optional[int] = None
            for index, line in enumerate(lines):
                if "-->" not in line:
                    continue
                timestamp_index = index
                left, right = line.split("-->", 1)
                right_timestamp = right.strip().split()[0]
                break
            if timestamp_index is None:
                continue
            append_cue(
                left,
                right_timestamp,
                "\n".join(
                    line for line in lines[timestamp_index + 1 :] if line.strip()
                ),
            )

    if not cues:
        raise MediaError("subtitle file contains no renderable cues")

    review_candidates = [
        (0, "first-cue"),
        (len(cues) - 1, "last-cue"),
        (
            max(range(len(cues)), key=lambda index: cues[index]["line_count"]),
            "most-lines",
        ),
    ]
    longest_cues = sorted(
        range(len(cues)),
        key=lambda index: (
            cues[index]["max_line_columns"],
            cues[index]["line_count"],
            -index,
        ),
        reverse=True,
    )[:3]
    review_candidates.extend(
        (cue_index, f"long-line-rank-{rank}")
        for rank, cue_index in enumerate(longest_cues, start=1)
    )
    review_by_index: dict[int, set[str]] = {}
    for cue_index, reason in review_candidates:
        review_by_index.setdefault(cue_index, set()).add(reason)
    check_times = []
    for cue_index in sorted(review_by_index):
        cue = cues[cue_index]
        check_times.append(
            {
                "time": cue["start"] + (cue["end"] - cue["start"]) / 2,
                "cue_index": cue_index + 1,
                "reasons": sorted(review_by_index[cue_index]),
                "start": cue["start"],
                "end": cue["end"],
                "line_count": cue["line_count"],
                "max_line_columns": cue["max_line_columns"],
            }
        )
    return {
        "visible_text": "\n".join(str(cue["text"]) for cue in cues),
        "cues": cues,
        "check_times": check_times,
        "play_res_x": play_res_x,
        "play_res_y": play_res_y,
    }


def required_codepoints(value: str) -> set[int]:
    return {
        ord(character)
        for character in value
        if not character.isspace()
        and not unicodedata.category(character).startswith("C")
    }


def read_u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise MediaError("font table is truncated")
    return struct.unpack_from(">H", data, offset)[0]


def read_i16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise MediaError("font table is truncated")
    return struct.unpack_from(">h", data, offset)[0]


def read_u32(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 4 > len(data):
        raise MediaError("font table is truncated")
    return struct.unpack_from(">I", data, offset)[0]


def sfnt_offsets(data: bytes) -> list[int]:
    if data[:4] != b"ttcf":
        return [0]
    count = read_u32(data, 8)
    if count <= 0 or count > 1024:
        raise MediaError("font collection has an invalid face count")
    return [read_u32(data, 12 + index * 4) for index in range(count)]


def font_tables(data: bytes, sfnt_offset: int) -> dict[str, tuple[int, int]]:
    table_count = read_u16(data, sfnt_offset + 4)
    tables: dict[str, tuple[int, int]] = {}
    for index in range(table_count):
        record = sfnt_offset + 12 + index * 16
        if record + 16 > len(data):
            raise MediaError("font table directory is truncated")
        tag = data[record : record + 4].decode("latin-1")
        offset = read_u32(data, record + 8)
        length = read_u32(data, record + 12)
        if offset + length > len(data):
            raise MediaError("font table points outside the font file")
        tables[tag] = (offset, length)
    return tables


def decode_font_name(platform: int, value: bytes) -> Optional[str]:
    try:
        if platform in {0, 3}:
            return value.decode("utf-16-be").strip("\x00 ")
        if platform == 1:
            return value.decode("mac_roman").strip("\x00 ")
    except UnicodeDecodeError:
        return None
    return None


def font_family(data: bytes, tables: dict[str, tuple[int, int]]) -> Optional[str]:
    if "name" not in tables:
        return None
    offset, length = tables["name"]
    if length < 6:
        return None
    count = read_u16(data, offset + 2)
    string_offset = offset + read_u16(data, offset + 4)
    candidates: list[tuple[int, str]] = []
    for index in range(count):
        record = offset + 6 + index * 12
        if record + 12 > offset + length:
            break
        platform = read_u16(data, record)
        language = read_u16(data, record + 4)
        name_id = read_u16(data, record + 6)
        if name_id not in {1, 16}:
            continue
        value_length = read_u16(data, record + 8)
        value_offset = string_offset + read_u16(data, record + 10)
        if value_offset + value_length > offset + length:
            continue
        decoded = decode_font_name(
            platform, data[value_offset : value_offset + value_length]
        )
        if not decoded:
            continue
        score = (20 if name_id == 16 else 10) + (2 if language == 0x0409 else 0)
        candidates.append((score, decoded))
    return max(candidates, default=(0, ""))[1] or None


def cmap_format_4_coverage(
    data: bytes, offset: int, table_end: int, required: set[int]
) -> set[int]:
    length = read_u16(data, offset + 2)
    end = min(offset + length, table_end)
    segment_count = read_u16(data, offset + 6) // 2
    end_codes = offset + 14
    start_codes = end_codes + segment_count * 2 + 2
    deltas = start_codes + segment_count * 2
    ranges = deltas + segment_count * 2
    if ranges + segment_count * 2 > end:
        return set()
    covered: set[int] = set()
    for codepoint in required:
        if codepoint > 0xFFFF:
            continue
        for index in range(segment_count):
            segment_end = read_u16(data, end_codes + index * 2)
            if codepoint > segment_end:
                continue
            segment_start = read_u16(data, start_codes + index * 2)
            if codepoint < segment_start:
                break
            delta = read_i16(data, deltas + index * 2)
            range_offset_address = ranges + index * 2
            range_offset = read_u16(data, range_offset_address)
            if range_offset == 0:
                glyph = (codepoint + delta) & 0xFFFF
            else:
                glyph_address = (
                    range_offset_address
                    + range_offset
                    + (codepoint - segment_start) * 2
                )
                if glyph_address + 2 > end:
                    glyph = 0
                else:
                    glyph = read_u16(data, glyph_address)
                    if glyph:
                        glyph = (glyph + delta) & 0xFFFF
            if glyph:
                covered.add(codepoint)
            break
    return covered


def cmap_group_coverage(
    data: bytes, offset: int, table_end: int, required: set[int]
) -> set[int]:
    length = read_u32(data, offset + 4)
    end = min(offset + length, table_end)
    group_count = read_u32(data, offset + 12)
    if offset + 16 + group_count * 12 > end:
        return set()
    remaining = set(required)
    covered: set[int] = set()
    for index in range(group_count):
        record = offset + 16 + index * 12
        first = read_u32(data, record)
        last = read_u32(data, record + 4)
        glyph_start = read_u32(data, record + 8)
        for codepoint in tuple(remaining):
            if first <= codepoint <= last:
                glyph = (
                    glyph_start
                    if read_u16(data, offset) == 13
                    else glyph_start + codepoint - first
                )
                if glyph:
                    covered.add(codepoint)
                remaining.remove(codepoint)
        if not remaining:
            break
    return covered


def cmap_coverage(
    data: bytes, tables: dict[str, tuple[int, int]], required: set[int]
) -> set[int]:
    if "cmap" not in tables:
        return set()
    offset, length = tables["cmap"]
    table_end = offset + length
    if length < 4:
        return set()
    subtable_count = read_u16(data, offset + 2)
    covered: set[int] = set()
    for index in range(subtable_count):
        record = offset + 4 + index * 8
        if record + 8 > table_end:
            break
        platform = read_u16(data, record)
        if platform not in {0, 3}:
            continue
        subtable = offset + read_u32(data, record + 4)
        if subtable + 2 > table_end:
            continue
        format_number = read_u16(data, subtable)
        remaining = required - covered
        if not remaining:
            break
        if format_number == 4:
            covered.update(
                cmap_format_4_coverage(data, subtable, table_end, remaining)
            )
        elif format_number in {12, 13}:
            covered.update(cmap_group_coverage(data, subtable, table_end, remaining))
        elif format_number == 0 and subtable + 262 <= table_end:
            covered.update(
                codepoint
                for codepoint in remaining
                if codepoint < 256 and data[subtable + 6 + codepoint] != 0
            )
        elif format_number == 6 and subtable + 10 <= table_end:
            count = read_u16(data, subtable + 8)
            end = subtable + 10 + count * 2
            if end > table_end:
                continue
            first = read_u16(data, subtable + 6)
            covered.update(
                codepoint
                for codepoint in remaining
                if first <= codepoint < first + count
                and read_u16(data, subtable + 10 + (codepoint - first) * 2) != 0
            )
    return covered


def inspect_font(path: Path, required: set[int]) -> list[dict[str, Any]]:
    data = path.read_bytes()
    faces: list[dict[str, Any]] = []
    for sfnt_offset in sfnt_offsets(data):
        tables = font_tables(data, sfnt_offset)
        faces.append(
            {
                "family": font_family(data, tables) or path.stem,
                "covered": cmap_coverage(data, tables, required),
            }
        )
    return faces


def font_files_in(path: Path) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() in FONT_EXTENSIONS:
            yield path
        return
    if not path.is_dir():
        return
    for root, directories, files in os.walk(path):
        directories.sort()
        for name in sorted(files):
            candidate = Path(root) / name
            if candidate.suffix.lower() in FONT_EXTENSIONS:
                yield candidate


def font_sources(args: argparse.Namespace) -> list[Path]:
    explicit_files = [Path(value).expanduser() for value in (args.font_file or [])]
    explicit_dirs = [Path(value).expanduser() for value in (args.fonts_dir or [])]
    if explicit_files or explicit_dirs:
        missing = [path for path in explicit_files + explicit_dirs if not path.exists()]
        if missing:
            raise MediaError(f"font source not found: {missing[0]}")
        return explicit_files + explicit_dirs

    environment_dirs = [
        Path(value).expanduser()
        for value in os.environ.get("AGNES_SUBTITLE_FONTS_DIR", "").split(os.pathsep)
        if value
    ]
    skill_fonts = Path(__file__).resolve().parent.parent / "assets" / "fonts"
    sources: list[Path] = [*environment_dirs]
    if skill_fonts.is_dir():
        sources.append(skill_fonts)

    if sys.platform == "darwin":
        sources.extend(
            Path(value)
            for value in (
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/STHeiti Light.ttc",
                "/Library/Fonts",
                "~/Library/Fonts",
                "/System/Library/Fonts",
            )
        )
    elif os.name == "nt":
        windows = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        sources.extend(
            [
                windows / "msyh.ttc",
                windows / "msyhbd.ttc",
                windows / "simhei.ttf",
                windows / "simsun.ttc",
                windows,
            ]
        )
    else:
        sources.extend(
            Path(value).expanduser()
            for value in (
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
                "/usr/share/fonts/opentype/adobe-source-han-sans/SourceHanSansCN-Regular.otf",
                "/usr/local/share/fonts",
                "/usr/share/fonts",
                "~/.local/share/fonts",
                "~/.fonts",
            )
        )
    return sources


def candidate_fonts(args: argparse.Namespace) -> Iterable[Path]:
    preferred = (
        "hiragino sans gb",
        "pingfang",
        "stheiti",
        "notosanscjk",
        "sourcehansans",
        "msyh",
        "simhei",
        "simsun",
    )
    seen: set[Path] = set()
    candidates: list[Path] = []
    for source in font_sources(args):
        source = source.expanduser()
        try:
            for candidate in font_files_in(source):
                resolved = candidate.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    candidates.append(resolved)
        except OSError:
            continue

    def priority(path: Path) -> tuple[int, str]:
        normalized = path.name.casefold().replace(" ", "")
        rank = next(
            (
                index
                for index, keyword in enumerate(preferred)
                if keyword.replace(" ", "") in normalized
            ),
            len(preferred),
        )
        return rank, str(path).casefold()

    yield from sorted(candidates, key=priority)


def describe_codepoints(codepoints: Iterable[int], limit: int = 20) -> str:
    values = sorted(set(codepoints))
    descriptions = [f"{chr(value)} (U+{value:04X})" for value in values[:limit]]
    if len(values) > limit:
        descriptions.append(f"... and {len(values) - limit} more")
    return ", ".join(descriptions)


def resolve_subtitle_font(
    args: argparse.Namespace, required: set[int]
) -> dict[str, Any]:
    if not required:
        raise MediaError("subtitle file contains no visible characters")
    hint = args.font.casefold() if args.font else None
    best: Optional[dict[str, Any]] = None
    inspected = 0
    matching_families = 0
    errors: list[str] = []
    for path in candidate_fonts(args):
        inspected += 1
        try:
            faces = inspect_font(path, required)
        except (MediaError, OSError, struct.error) as error:
            if len(errors) < 3:
                errors.append(f"{path}: {error}")
            continue
        for face in faces:
            family = str(face["family"])
            if hint and hint not in family.casefold() and family.casefold() not in hint:
                continue
            matching_families += 1
            covered = set(face["covered"])
            candidate = {
                "path": path,
                "family": family,
                "covered": covered,
            }
            if best is None or len(covered) > len(best["covered"]):
                best = candidate
            if required <= covered:
                return {
                    "path": path,
                    "family": family,
                    "checked_character_count": len(required),
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }

    if inspected == 0:
        raise MediaError(
            "no usable subtitle fonts were found; pass --font-file or --fonts-dir "
            "with a font already available on the host"
        )
    if hint and matching_families == 0:
        raise MediaError(
            f"no inspected font matched family {args.font!r}; pass its file with "
            "--font-file or choose an available family"
        )
    if best:
        missing = required - set(best["covered"])
        raise MediaError(
            f"font {best['family']!r} at {best['path']} lacks subtitle glyphs: "
            f"{describe_codepoints(missing)}"
        )
    detail = f"; first scan errors: {' | '.join(errors)}" if errors else ""
    raise MediaError(f"no readable OpenType or TrueType subtitle font was found{detail}")


def subtitle_filter(filename: str, style: str, fonts_dir: str) -> str:
    return (
        f"subtitles=filename={filename}:fontsdir={fonts_dir}:"
        f"force_style='{style}'"
    )


def fontconfig_document(family: str) -> str:
    escaped_family = html.escape(family, quote=True)
    return f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>/work/fonts</dir>
  <cachedir>/tmp/agnes-fontconfig-cache</cachedir>
  <alias>
    <family>sans-serif</family>
    <prefer><family>{escaped_family}</family></prefer>
  </alias>
</fontconfig>
"""


def validate_subtitle_render(stderr: str) -> None:
    failure_patterns = (
        r"Glyph 0x[0-9A-Fa-f]+ not found",
        r"fontselect: failed to find any fallback",
        r"No usable fontconfig configuration file found",
        r"Error opening font",
    )
    matches: list[str] = []
    for line in stderr.splitlines():
        if any(re.search(pattern, line) for pattern in failure_patterns):
            matches.append(line.strip())
            if len(matches) == 5:
                break
    if matches:
        raise MediaError(
            "subtitle renderer could not use the verified font: " + " | ".join(matches)
        )


def validate_style_value(value: str, label: str) -> str:
    if not re.fullmatch(r"[\w .&+-]+", value, flags=re.UNICODE):
        raise MediaError(f"{label} contains unsupported punctuation")
    return value


def subtitle_layout(
    details: dict[str, Any], subtitle_data: dict[str, Any], args: argparse.Namespace
) -> dict[str, Any]:
    stream = video_stream(details)
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)
    if width <= 0 or height <= 0:
        raise MediaError("subtitle canvas dimensions could not be determined")

    default_font_pixels = round(min(height * 0.04, width * 0.055))
    font_pixels = args.font_size or max(18, min(96, default_font_pixels))
    default_margin_pixels = round(min(height * 0.05, width * 0.08))
    margin_v_pixels = (
        args.margin_v
        if args.margin_v is not None
        else max(12, default_margin_pixels)
    )
    outline_pixels = (
        args.outline
        if args.outline is not None
        else max(1.0, font_pixels * 0.05)
    )
    margin_h_pixels = max(12, round(width * 0.05))

    play_res_x = int(subtitle_data["play_res_x"])
    play_res_y = int(subtitle_data["play_res_y"])
    ass_font_size = max(1.0, font_pixels * play_res_y / height)
    ass_outline = max(0.1, outline_pixels * play_res_y / height)
    ass_margin_v = max(1, round(margin_v_pixels * play_res_y / height))
    ass_margin_h = max(1, round(margin_h_pixels * play_res_x / width))

    safe_width = max(1, width - 2 * margin_h_pixels)
    columns_per_line = max(8, math.floor(safe_width / (font_pixels / 2)))
    overflow: list[dict[str, Any]] = []
    for cue_index, cue in enumerate(subtitle_data["cues"], start=1):
        estimated_lines = sum(
            max(1, math.ceil(int(columns) / columns_per_line))
            for columns in cue["line_columns"]
        )
        if estimated_lines > args.max_lines:
            overflow.append(
                {
                    "cue_index": cue_index,
                    "estimated_lines": estimated_lines,
                    "max_line_columns": cue["max_line_columns"],
                }
            )
    if overflow:
        examples = ", ".join(
            f"cue {item['cue_index']} needs about {item['estimated_lines']} lines"
            for item in overflow[:5]
        )
        suffix = f" and {len(overflow) - 5} more" if len(overflow) > 5 else ""
        raise MediaError(
            "subtitle layout exceeds the configured safe line count "
            f"({args.max_lines}): {examples}{suffix}; split and retime the cues, "
            "choose a smaller output-pixel --font-size, or explicitly raise --max-lines"
        )

    return {
        "canvas_width": width,
        "canvas_height": height,
        "font_size_pixels": font_pixels,
        "outline_pixels": outline_pixels,
        "margin_v_pixels": margin_v_pixels,
        "margin_h_pixels": margin_h_pixels,
        "max_lines": args.max_lines,
        "estimated_columns_per_line": columns_per_line,
        "ass_font_size": ass_font_size,
        "ass_outline": ass_outline,
        "ass_margin_v": ass_margin_v,
        "ass_margin_h": ass_margin_h,
        "play_res_x": play_res_x,
        "play_res_y": play_res_y,
    }


def burn_subtitles_command(args: argparse.Namespace) -> None:
    source = require_input(args.input)
    subtitles = require_input(args.subtitles)
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    extension = subtitles.suffix.lower()
    if extension not in {".srt", ".vtt", ".ass", ".ssa"}:
        raise MediaError("subtitles must be SRT, VTT, ASS, or SSA")

    subtitle_data = subtitle_payload(subtitles)
    video_details = probe_media(ffprobe, source)
    video_duration = duration_seconds(video_details)
    latest_end = max(float(cue["end"]) for cue in subtitle_data["cues"])
    if latest_end > video_duration + 0.05:
        raise MediaError(
            f"subtitle cue ends after the video: {latest_end:.3f}s > "
            f"{video_duration:.3f}s"
        )
    font = resolve_subtitle_font(
        args, required_codepoints(str(subtitle_data["visible_text"]))
    )
    layout = subtitle_layout(video_details, subtitle_data, args)

    style_values = [
        f"FontName={validate_style_value(str(font['family']), 'font family')}",
        f"FontSize={layout['ass_font_size']:.3f}",
        f"Outline={layout['ass_outline']:.3f}",
        f"MarginV={layout['ass_margin_v']}",
        f"MarginL={layout['ass_margin_h']}",
        f"MarginR={layout['ass_margin_h']}",
        "Alignment=2",
        "WrapStyle=0",
    ]

    with tempfile.TemporaryDirectory(prefix=".agnes-subs-", dir=output.parent) as raw:
        temporary = Path(raw)
        local_subtitles = temporary / f"captions{extension}"
        shutil.copyfile(subtitles, local_subtitles)
        local_fonts = temporary / "fonts"
        local_fonts.mkdir()
        local_font = local_fonts / f"subtitle-font{Path(font['path']).suffix.lower()}"
        shutil.copyfile(Path(font["path"]), local_font)
        if _selected_runtime == "docker":
            (temporary / "fonts.conf").write_text(
                fontconfig_document(str(font["family"])), encoding="utf-8"
            )
        staged = temporary / f"render{output.suffix or '.mp4'}"
        completed = run_checked(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "warning",
                *(
                    "-y",
                    "-i",
                    str(source),
                    "-vf",
                    subtitle_filter(
                        local_subtitles.name, ",".join(style_values), local_fonts.name
                    ),
                    "-c:v",
                    "libx264",
                    "-preset",
                    args.preset,
                    "-crf",
                    str(args.crf),
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "copy",
                    str(staged),
                ),
            ],
            cwd=temporary,
        )
        validate_subtitle_render(completed.stderr)
        if output.exists():
            output.unlink()
        staged.replace(output)
    print_result(
        {
            "operation": "burn-subtitles",
            "input": str(source),
            "subtitles": str(subtitles),
            "output": str(output),
            **runtime_metadata(),
            "font_family": font["family"],
            "font_file": str(font["path"]),
            "glyph_coverage_verified": True,
            "checked_character_count": font["checked_character_count"],
            "glyph_check_at": font["checked_at"],
            "subtitle_cue_count": len(subtitle_data["cues"]),
            "subtitle_latest_end": latest_end,
            "subtitle_timing_within_video": True,
            "subtitle_layout": layout,
            "subtitle_check_time": subtitle_data["check_times"][0]["time"],
            "subtitle_check_times": subtitle_data["check_times"],
        }
    )


def add_audio_command(args: argparse.Namespace) -> None:
    video = require_input(args.input)
    audio = require_input(args.audio)
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    details = probe_media(ffprobe, video)
    duration = duration_seconds(details)
    has_original_audio = stream_exists(details, "audio")
    audio_duration = duration_seconds(probe_media(ffprobe, audio))
    if args.start_at >= duration:
        raise MediaError("--start-at must be before the end of the input video")

    delay_milliseconds = round(args.start_at * 1000)
    overlay_filters = [f"volume={args.overlay_volume}"]
    if delay_milliseconds:
        overlay_filters.append(f"adelay={delay_milliseconds}:all=1")
    overlay_filters.append("apad")
    overlay_filter = ",".join(overlay_filters)

    command: list[str] = ["-y", "-i", str(video)]
    if args.loop_audio:
        command.extend(["-stream_loop", "-1"])
    command.extend(["-i", str(audio)])

    if args.mode == "mix" and has_original_audio:
        filter_complex = (
            f"[0:a]volume={args.original_volume},apad[original];"
            f"[1:a]{overlay_filter}[overlay];"
            "[original][overlay]amix=inputs=2:duration=longest:"
            "dropout_transition=2[mixed]"
        )
        command.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "0:v:0",
                "-map",
                "[mixed]",
            ]
        )
        actual_mode = "mix"
    else:
        command.extend(
            [
                "-filter_complex",
                f"[1:a]{overlay_filter}[replacement]",
                "-map",
                "0:v:0",
                "-map",
                "[replacement]",
            ]
        )
        actual_mode = "replace"

    command.extend(
        [
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{duration:.6f}",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run_checked(ffmpeg_command(ffmpeg, command))
    audio_end = duration if args.loop_audio else min(duration, args.start_at + audio_duration)
    audio_truncated = not args.loop_audio and args.start_at + audio_duration > duration
    print_result(
        {
            "operation": "add-audio",
            "input": str(video),
            "audio": str(audio),
            "output": str(output),
            **runtime_metadata(),
            "mode": actual_mode,
            "duration": duration,
            "audio_start": args.start_at,
            "source_audio_duration": audio_duration,
            "audio_end": audio_end,
            "audio_truncated": audio_truncated,
        }
    )


def manifest_number(
    value: Any, label: str, minimum: float = 0.0, maximum: Optional[float] = None
) -> float:
    if isinstance(value, bool):
        raise MediaError(f"{label} must be a number")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as error:
        raise MediaError(f"{label} must be a number") from error
    if not math.isfinite(parsed) or parsed < minimum:
        raise MediaError(f"{label} must be at least {minimum}")
    if maximum is not None and parsed > maximum:
        raise MediaError(f"{label} must be at most {maximum}")
    return parsed


def timeline_audio_path(manifest: Path, raw_path: Any, label: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise MediaError(f"{label}.path must be a non-empty string")
    candidate = Path(raw_path).expanduser()
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    resolved = candidate.resolve()
    if not resolved.is_file():
        raise MediaError(f"{label}.path does not exist: {resolved}")
    return resolved


def load_audio_timeline(
    manifest: Path, picture_duration: float, ffprobe: str
) -> tuple[float, list[dict[str, Any]]]:
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise MediaError(f"audio timeline is invalid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise MediaError("audio timeline must be a JSON object")

    original_volume = manifest_number(
        payload.get("original_volume", 0.0), "original_volume", maximum=10.0
    )
    raw_tracks = payload.get("tracks")
    if not isinstance(raw_tracks, list):
        raise MediaError("audio timeline tracks must be a JSON array")
    if len(raw_tracks) > 128:
        raise MediaError("audio timeline supports at most 128 tracks")

    tracks: list[dict[str, Any]] = []
    for index, raw_track in enumerate(raw_tracks, start=1):
        label = f"tracks[{index - 1}]"
        if not isinstance(raw_track, dict):
            raise MediaError(f"{label} must be a JSON object")
        start = manifest_number(raw_track.get("start", 0.0), f"{label}.start")
        if start >= picture_duration:
            raise MediaError(f"{label}.start must be before the end of the picture")
        track_volume = manifest_number(
            raw_track.get("volume", 1.0), f"{label}.volume", maximum=10.0
        )
        loop = raw_track.get("loop", False)
        if not isinstance(loop, bool):
            raise MediaError(f"{label}.loop must be true or false")
        path = timeline_audio_path(manifest, raw_track.get("path"), label)
        source_duration = duration_seconds(probe_media(ffprobe, path))
        end = picture_duration if loop else min(
            picture_duration, start + source_duration
        )
        display_label = raw_track.get("label", f"track-{index:02d}")
        role = raw_track.get("role")
        if not isinstance(display_label, str) or not display_label.strip():
            raise MediaError(f"{label}.label must be a non-empty string")
        if role is not None and not isinstance(role, str):
            raise MediaError(f"{label}.role must be a string when provided")
        tracks.append(
            {
                "label": display_label.strip(),
                "role": role.strip() if isinstance(role, str) else None,
                "path": path,
                "start": start,
                "volume": track_volume,
                "loop": loop,
                "source_duration": source_duration,
                "end": end,
                "truncated": not loop and start + source_duration > picture_duration,
            }
        )
    if not tracks and original_volume == 0:
        raise MediaError(
            "audio timeline must include a track or a non-zero original_volume"
        )
    return original_volume, tracks


def render_audio_stems(
    ffmpeg: str,
    tracks: list[dict[str, Any]],
    picture_duration: float,
    temporary: Path,
) -> list[Path]:
    duration_text = f"{picture_duration:.6f}"
    stems: list[Path] = []
    group_size = 8
    for group_index, group_start in enumerate(
        range(0, len(tracks), group_size), start=1
    ):
        group = tracks[group_start : group_start + group_size]
        command: list[str] = ["-y"]
        for track in group:
            if track["loop"]:
                command.extend(["-stream_loop", "-1"])
            command.extend(["-i", str(track["path"])])

        filters = [
            "anullsrc=r=48000:cl=stereo,"
            f"atrim=duration={duration_text},asetpts=PTS-STARTPTS[stem_zero]"
        ]
        mix_inputs = ["[stem_zero]"]
        for input_index, track in enumerate(group):
            delay_milliseconds = round(float(track["start"]) * 1000)
            filters.append(
                f"[{input_index}:a:0]aresample=48000,"
                "aformat=sample_rates=48000:channel_layouts=stereo,"
                "asetpts=PTS-STARTPTS,"
                f"volume={track['volume']},adelay={delay_milliseconds}:all=1,"
                f"atrim=duration={duration_text}[stem_track_{input_index}]"
            )
            mix_inputs.append(f"[stem_track_{input_index}]")
        filters.append(
            "".join(mix_inputs)
            + f"amix=inputs={len(mix_inputs)}:duration=longest:"
            "dropout_transition=0:normalize=0,"
            f"atrim=duration={duration_text},asetpts=N/SR/TB[stem]"
        )

        stem = temporary / f"audio-stem-{group_index:02d}.nut"
        command.extend(
            [
                "-filter_complex",
                ";".join(filters),
                "-map",
                "[stem]",
                "-vn",
                "-c:a",
                "pcm_f32le",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-t",
                duration_text,
                "-f",
                "nut",
                str(stem),
            ]
        )
        run_checked(ffmpeg_command(ffmpeg, command), cwd=temporary)
        stems.append(stem)
    return stems


def mix_audio_timeline_command(args: argparse.Namespace) -> None:
    video = require_input(args.input)
    manifest = require_input(args.timeline)
    output = prepare_output(args.output, args.overwrite)
    ffmpeg = executable(args.ffmpeg, "FFMPEG_BIN", ("ffmpeg", "ffmpeg.exe"))
    ffprobe = executable(args.ffprobe, "FFPROBE_BIN", ("ffprobe", "ffprobe.exe"))
    details = probe_media(ffprobe, video)
    picture_duration = duration_seconds(details)
    has_original_audio = stream_exists(details, "audio")
    original_volume, tracks = load_audio_timeline(
        manifest, picture_duration, ffprobe
    )
    if original_volume > 0 and not has_original_audio:
        raise MediaError(
            "audio timeline requests original audio but the input video has none"
        )

    duration_text = f"{picture_duration:.6f}"
    with tempfile.TemporaryDirectory(prefix=".agnes-audio-", dir=output.parent) as raw:
        temporary = Path(raw)
        stems = render_audio_stems(ffmpeg, tracks, picture_duration, temporary)
        command: list[str] = ["-y", "-i", str(video)]
        for stem in stems:
            command.extend(["-i", str(stem)])

        filters = [
            "anullsrc=r=48000:cl=stereo,"
            f"atrim=duration={duration_text},asetpts=PTS-STARTPTS[timeline_zero]"
        ]
        mix_inputs = ["[timeline_zero]"]
        if original_volume > 0:
            filters.append(
                "[0:a:0]aresample=48000,"
                "aformat=sample_rates=48000:channel_layouts=stereo,"
                "asetpts=PTS-STARTPTS,"
                f"volume={original_volume},atrim=duration={duration_text}[original]"
            )
            mix_inputs.append("[original]")
        for stem_index in range(1, len(stems) + 1):
            filters.append(
                f"[{stem_index}:a:0]aresample=48000,"
                "aformat=sample_rates=48000:channel_layouts=stereo,"
                f"asetpts=PTS-STARTPTS[stem_{stem_index}]"
            )
            mix_inputs.append(f"[stem_{stem_index}]")
        filters.append(
            "".join(mix_inputs)
            + f"amix=inputs={len(mix_inputs)}:duration=longest:"
            "dropout_transition=0:normalize=0,alimiter=limit=0.95,"
            f"atrim=duration={duration_text},asetpts=N/SR/TB[mixed]"
        )

        staged = Path(raw) / f"mixed{output.suffix or '.mp4'}"
        command.extend(
            [
                "-filter_complex",
                ";".join(filters),
                "-map",
                "0:v:0",
                "-map",
                "[mixed]",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-t",
                duration_text,
                "-movflags",
                "+faststart",
                str(staged),
            ]
        )
        run_checked(ffmpeg_command(ffmpeg, command))
        output_probe = probe_media(ffprobe, staged)
        if not stream_exists(output_probe, "audio"):
            raise MediaError("mixed output has no audio stream")
        output_duration = duration_seconds(output_probe)
        if abs(output_duration - picture_duration) > 0.1:
            raise MediaError(
                "mixed output duration does not match the picture timeline: "
                f"{output_duration:.3f}s != {picture_duration:.3f}s"
            )
        if output.exists():
            output.unlink()
        staged.replace(output)

    print_result(
        {
            "operation": "mix-audio-timeline",
            "input": str(video),
            "timeline": str(manifest),
            "output": str(output),
            **runtime_metadata(),
            "picture_duration": picture_duration,
            "output_duration": output_duration,
            "timeline_zero_anchored": True,
            "original_audio_included": original_volume > 0,
            "original_volume": original_volume,
            "track_count": len(tracks),
            "mix_stem_count": len(stems),
            "tracks": [
                {
                    key: str(value) if key == "path" else value
                    for key, value in track.items()
                }
                for track in tracks
            ],
        }
    )


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def volume(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed < 0 or parsed > 10:
        raise argparse.ArgumentTypeError("must be between 0 and 10")
    return parsed


def operation_id_value(value: str) -> str:
    normalized = value.strip().lower()
    if not re.fullmatch(r"[0-9a-f]{32}", normalized):
        raise argparse.ArgumentTypeError(
            "must be the 32-character operation ID emitted by media_ops.py"
        )
    return normalized


def duration_threshold(value: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([smhd]?)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError(
            "must be a positive duration such as 30s, 10m, 2h, or 1d"
        )
    amount = float(match.group(1))
    if not math.isfinite(amount) or amount <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    multiplier = {"": 1.0, "s": 1.0, "m": 60.0, "h": 3600.0, "d": 86400.0}
    return amount * multiplier[match.group(2)]


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Portable local video inspection and post-production helpers."
    )
    root.add_argument(
        "--runtime",
        choices=("auto", "docker", "native"),
        help="media runtime (default: AGNES_MEDIA_RUNTIME or auto)",
    )
    root.add_argument("--ffmpeg", help="ffmpeg executable path")
    root.add_argument("--ffprobe", help="ffprobe executable path")
    root.add_argument("--docker", help="Docker CLI executable path")
    root.add_argument(
        "--docker-image",
        help="prepared FFmpeg image reference (defaults to a pinned multi-platform image)",
    )
    root.add_argument(
        "--pull-docker-image",
        action="store_true",
        help="explicitly authorize pulling a missing Docker image",
    )
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("doctor", help="check native and Docker FFmpeg capabilities")

    managed_parser = commands.add_parser(
        "managed-containers",
        help="list Docker containers owned by media_ops.py",
    )
    managed_parser.add_argument("--operation-id", type=operation_id_value)

    cancel_parser = commands.add_parser(
        "cancel",
        help="idempotently stop one exact media_ops.py Docker operation",
    )
    cancel_parser.add_argument(
        "--operation-id", required=True, type=operation_id_value
    )

    cleanup_parser = commands.add_parser(
        "cleanup",
        help="remove stale managed containers whose parent process is gone",
    )
    cleanup_parser.add_argument(
        "--stale-after",
        required=True,
        type=duration_threshold,
        help="minimum orphan age, for example 10m or 2h",
    )
    cleanup_parser.add_argument("--operation-id", type=operation_id_value)

    probe_parser = commands.add_parser("probe", help="inspect media as JSON")
    probe_parser.add_argument("input")
    probe_parser.add_argument("--output")
    probe_parser.add_argument("--overwrite", action="store_true")

    concat_parser = commands.add_parser(
        "concat", help="normalize and concatenate video clips"
    )
    concat_parser.add_argument("inputs", nargs="+")
    concat_parser.add_argument("--output", required=True)
    concat_parser.add_argument("--width", type=positive_int)
    concat_parser.add_argument("--height", type=positive_int)
    concat_parser.add_argument("--fps", type=positive_float)
    concat_parser.add_argument("--transition", choices=sorted(TRANSITIONS), default="fade")
    concat_parser.add_argument(
        "--transition-duration", type=nonnegative_float, default=0.0
    )
    concat_parser.add_argument("--crf", type=int, choices=range(0, 52), default=18)
    concat_parser.add_argument(
        "--preset",
        choices=(
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
        ),
        default="medium",
    )
    concat_parser.add_argument("--overwrite", action="store_true")

    trim_parser = commands.add_parser("trim", help="cut a time range from one video")
    trim_parser.add_argument("input")
    trim_parser.add_argument("--output", required=True)
    trim_parser.add_argument("--start", type=nonnegative_float, default=0.0)
    trim_parser.add_argument("--end", type=positive_float)
    trim_parser.add_argument("--duration", type=positive_float)
    trim_parser.add_argument("--crf", type=int, choices=range(0, 52), default=18)
    trim_parser.add_argument(
        "--preset",
        choices=("veryfast", "faster", "fast", "medium", "slow"),
        default="medium",
    )
    trim_parser.add_argument("--overwrite", action="store_true")

    sheet_parser = commands.add_parser(
        "contact-sheet", help="sample a video into one PNG for visual review"
    )
    sheet_parser.add_argument("input")
    sheet_parser.add_argument("--output", required=True)
    sheet_parser.add_argument("--frames", type=positive_int, default=12)
    sheet_parser.add_argument("--columns", type=positive_int, default=4)
    sheet_parser.add_argument("--thumb-width", type=positive_int, default=320)
    sheet_parser.add_argument("--start", type=nonnegative_float, default=0.0)
    sheet_parser.add_argument("--end", type=positive_float)
    sheet_parser.add_argument(
        "--mode", choices=("even", "first", "last"), default="even"
    )
    sheet_parser.add_argument("--overwrite", action="store_true")

    frame_parser = commands.add_parser(
        "extract-frame", help="extract one exact video frame for visual inspection"
    )
    frame_parser.add_argument("input")
    frame_parser.add_argument("--output", required=True)
    frame_selector = frame_parser.add_mutually_exclusive_group(required=True)
    frame_selector.add_argument("--at", type=nonnegative_float)
    frame_selector.add_argument("--position", choices=("first", "last"))
    frame_parser.add_argument("--overwrite", action="store_true")

    subtitle_parser = commands.add_parser(
        "burn-subtitles", help="render SRT, VTT, ASS, or SSA subtitles into video"
    )
    subtitle_parser.add_argument("input")
    subtitle_parser.add_argument("subtitles")
    subtitle_parser.add_argument("--output", required=True)
    subtitle_parser.add_argument("--font", help="required font family name")
    subtitle_parser.add_argument(
        "--font-file",
        action="append",
        help="font file to inspect and mount; repeat to provide fallbacks",
    )
    subtitle_parser.add_argument(
        "--fonts-dir",
        action="append",
        help="font directory to inspect; repeat to provide multiple directories",
    )
    subtitle_parser.add_argument(
        "--font-size",
        type=positive_int,
        help="target font size in output pixels; defaults from the video canvas",
    )
    subtitle_parser.add_argument(
        "--outline",
        type=nonnegative_float,
        help="target outline thickness in output pixels; defaults from font size",
    )
    subtitle_parser.add_argument(
        "--margin-v",
        type=nonnegative_int,
        help="bottom safe margin in output pixels; defaults from the video canvas",
    )
    subtitle_parser.add_argument(
        "--max-lines",
        type=positive_int,
        default=2,
        help="maximum estimated rendered lines per cue before preflight fails",
    )
    subtitle_parser.add_argument("--crf", type=int, choices=range(0, 52), default=18)
    subtitle_parser.add_argument(
        "--preset",
        choices=("veryfast", "faster", "fast", "medium", "slow"),
        default="medium",
    )
    subtitle_parser.add_argument("--overwrite", action="store_true")

    audio_parser = commands.add_parser(
        "add-audio", help="replace or mix a video's audio track"
    )
    audio_parser.add_argument("input")
    audio_parser.add_argument("audio")
    audio_parser.add_argument("--output", required=True)
    audio_parser.add_argument("--mode", choices=("replace", "mix"), default="mix")
    audio_parser.add_argument("--original-volume", type=volume, default=0.35)
    audio_parser.add_argument("--overlay-volume", type=volume, default=1.0)
    audio_parser.add_argument("--start-at", type=nonnegative_float, default=0.0)
    audio_parser.add_argument("--loop-audio", action="store_true")
    audio_parser.add_argument("--overwrite", action="store_true")

    timeline_audio_parser = commands.add_parser(
        "mix-audio-timeline",
        help="mix multiple timed audio assets from a JSON timeline",
    )
    timeline_audio_parser.add_argument("input")
    timeline_audio_parser.add_argument("timeline")
    timeline_audio_parser.add_argument("--output", required=True)
    timeline_audio_parser.add_argument("--overwrite", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "doctor":
        doctor(args)
    elif args.command == "managed-containers":
        managed_containers_command(args)
    elif args.command == "cancel":
        cancel_command(args)
    elif args.command == "cleanup":
        cleanup_command(args)
    else:
        begin_operation(args.command)
        configure_runtime(args)
        register_docker_operation()
        try:
            if args.command == "probe":
                probe_command(args)
            elif args.command == "concat":
                concat_command(args)
            elif args.command == "trim":
                trim_command(args)
            elif args.command == "contact-sheet":
                contact_sheet_command(args)
            elif args.command == "extract-frame":
                extract_frame_command(args)
            elif args.command == "burn-subtitles":
                burn_subtitles_command(args)
            elif args.command == "add-audio":
                add_audio_command(args)
            elif args.command == "mix-audio-timeline":
                mix_audio_timeline_command(args)
        finally:
            unregister_docker_operation()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MediaError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Batch orchestration for whisper.cpp: transcription and audio extraction."""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("whisper_batch")

MODEL_DIR = Path(os.environ.get("WHISPER_MODEL_DIR", Path.cwd() / "models"))
MODEL_PREFIX = os.environ.get("WHISPER_MODEL_PREFIX", "ggml")
AUDIO_CODECS = {"mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le", "flac": "flac", "opus": "libopus"}


def _check_tool(name: str) -> None:
    if subprocess.call(["which", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        logger.error("%s not found in PATH", name)
        sys.exit(1)


def _model_path(model: str) -> Path:
    p = MODEL_DIR / f"{MODEL_PREFIX}-{model}.bin"
    if not p.exists():
        logger.error("Model file not found: %s", p)
        sys.exit(1)
    return p


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def transcribe_file(
    model: str,
    language: str,
    input_file: Path,
    output_file: Path,
    output_txt: bool = False,
) -> None:
    """Transcribe a single audio file with whisper-cli."""
    cmd = [
        "whisper-cli",
        "-m", str(_model_path(model)),
        "--language", language,
        "-f", str(input_file),
        "--output-file", str(output_file),
    ]
    if output_txt:
        cmd.insert(1, "--output-txt")

    logger.info("Transcribing: %s", input_file)
    subprocess.run(cmd, check=True)


def cmd_transcribe(args: argparse.Namespace) -> None:
    _check_tool("whisper-cli")

    input_path = Path(args.input)
    output_path = Path(args.output)

    if input_path.is_file():
        _ensure_dir(output_path.parent)
        transcribe_file(
            model=args.model,
            language=args.language,
            input_file=input_path,
            output_file=output_path,
            output_txt=args.output_txt,
        )
    elif input_path.is_dir():
        files = sorted(input_path.rglob("*"))
        if not files:
            logger.warning("No files found in: %s", input_path)
            return

        for in_file in files:
            if not in_file.is_file():
                continue
            relative = in_file.relative_to(input_path)
            out_file = output_path / relative.with_suffix("")
            _ensure_dir(out_file.parent)
            transcribe_file(
                model=args.model,
                language=args.language,
                input_file=in_file,
                output_file=out_file,
                output_txt=args.output_txt,
            )
    else:
        logger.error("Input not found: %s", input_path)
        sys.exit(1)


def cmd_extract_audio(args: argparse.Namespace) -> None:
    _check_tool("ffmpeg")

    codec = AUDIO_CODECS[args.format]
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.is_dir():
        logger.error("Input must be a directory: %s", input_path)
        sys.exit(1)

    files = sorted(input_path.rglob("*"))
    if not files:
        logger.warning("No files found in: %s", input_path)
        return

    for in_file in files:
        if not in_file.is_file():
            continue
        relative = in_file.relative_to(input_path)
        out_file = output_path / relative.with_suffix(f".{args.format}")
        _ensure_dir(out_file.parent)

        logger.info("Extracting audio: %s", in_file)
        subprocess.run(
            ["ffmpeg", "-i", str(in_file), "-map", "0:a", "-c:a", codec, str(out_file), "-y"],
            check=True,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Batch orchestration for whisper.cpp")
    sub = parser.add_subparsers(dest="command", required=True)

    # transcribe
    p_trans = sub.add_parser("transcribe", help="Transcribe audio files with whisper-cli")
    p_trans.add_argument("-m", "--model", required=True, help="Model name (e.g. tiny, base, large-v3-turbo)")
    p_trans.add_argument("-l", "--language", required=True, help="Language code (e.g. zh, en)")
    p_trans.add_argument("-i", "--input", required=True, help="Input audio file or directory")
    p_trans.add_argument("-o", "--output", required=True, help="Output file or directory")
    p_trans.add_argument("-t", "--output-txt", action="store_true", help="Also output plain text")

    # extract-audio
    p_ext = sub.add_parser("extract-audio", help="Extract audio from video files with ffmpeg")
    p_ext.add_argument("-i", "--input", required=True, help="Input directory containing video files")
    p_ext.add_argument("-o", "--output", required=True, help="Output directory for audio files")
    p_ext.add_argument(
        "-f", "--format", default="mp3", choices=list(AUDIO_CODECS),
        help="Output audio format (default: mp3)",
    )

    args = parser.parse_args()

    if args.command == "transcribe":
        cmd_transcribe(args)
    elif args.command == "extract-audio":
        cmd_extract_audio(args)


if __name__ == "__main__":
    main()

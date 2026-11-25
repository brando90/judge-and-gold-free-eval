#!/usr/bin/env python3
"""Launcher for models whose vLLM engine needs the spawn start method (Qwen3.5, multimodal arch): runs generate.py under a __main__ guard.
Same arguments as generate.py:  python3 generate_spawn.py --model <dir> --name Qwen/Qwen3.5-4B --n 16 --out gen --util 0.35"""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("generate.py")), run_name="__gen__")

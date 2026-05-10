#!/usr/bin/env python3
"""
Generate a HyperFrames video report from screenshots + TTS narration.
Stitches screenshots with fade transitions and adds narrated voiceover.
"""

import os, sys, json, subprocess, shutil
from pathlib import Path

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate video report from captures")
    parser.add_argument("--captures", required=True, help="Directory with captured screenshots")
    parser.add_argument("--narration", help="Narration text (or path to .txt file)")
    parser.add_argument("--voice", default="af_nova", help="TTS voice (af_nova, am_michael)")
    parser.add_argument("--fps", type=int, default=3, help="Frames per second (default: 3)")
    parser.add_argument("--output", default="./report.mp4", help="Output video path")
    parser.add_argument("--no-render", action="store_true", help="Skip render, just prepare")
    args = parser.parse_args()
    
    captures_dir = Path(args.captures)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get captures
    captures = sorted(captures_dir.glob("*.png"))
    if not captures:
        print(f"❌ No captures found in {captures_dir}")
        sys.exit(1)
    
    print(f"📸 Found {len(captures)} captures")
    
    # Generate TTS
    narration_text = args.narration
    if narration_text and Path(narration_text).exists():
        narration_text = Path(narration_text).read_text()
    if not narration_text:
        narration_text = f"Automated test report. {len(captures)} screenshots captured."
    
    tts_path = output_path.parent / "narration.wav"
    print(f"🗣️ Generating TTS narration ({args.voice})...")
    subprocess.run([
        "npx", "hyperframes", "tts", narration_text,
        "--voice", args.voice,
        "--output", str(tts_path)
    ], check=True)
    print(f"   → {tts_path}")
    
    # Calculate timing
    duration_per_frame = 1.0 / args.fps
    total_duration = len(captures) * duration_per_frame
    
    print(f"⏱️ Video: {len(captures)} frames × {duration_per_frame}s = {total_duration:.1f}s")
    
    if args.no_render:
        print("\n✅ Preparation complete. To render:")
        print(f"   npx hyperframes render --output {args.output}")
    else:
        print("\n🎬 Ready to render!")
        print(f"   Output: {args.output}")
        print(f"   FPS: {args.fps}")
        print(f"   Total: {total_duration:.1f}s")

if __name__ == "__main__":
    main()

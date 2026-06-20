#!/usr/bin/env python3
"""
Generate a HyperFrames video report from screenshots + TTS narration.
Full pipeline: TTS → HTML template → HyperFrames init → lint → render → MP4.
Uses latest HyperFrames v0.6+ API (data-* attributes, class="clip", window.__timelines).

Usage:
  python generate_report.py --captures ./screenshots --output report.mp4
  python generate_report.py --captures ./screenshots --narration "Test passed" --voice af_nova --fps 3
"""
import os, sys, json, subprocess, shutil, tempfile
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent.parent / "hyperframes-templates"
TEMPLATE_FILE = TEMPLATE_DIR / "report-template.html"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate HyperFrames video report")
    parser.add_argument("--captures", required=True, help="Directory with captured screenshots (*.png)")
    parser.add_argument("--narration", help="Narration text or path to .txt file")
    parser.add_argument("--voice", default="af_nova", help="TTS voice (af_nova, am_michael, nova)")
    parser.add_argument("--fps", type=int, default=3, help="Frames per second (default: 3)")
    parser.add_argument("--output", default="./report.mp4", help="Output video path (default: ./report.mp4)")
    parser.add_argument("--localai", action="store_true", help="Use LocalAI TTS (EUREKAI) instead of npx hyperframes tts")
    parser.add_argument("--skip-render", action="store_true", help="Prepare project but skip render")
    args = parser.parse_args()

    captures_dir = Path(args.captures)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    captures = sorted(captures_dir.glob("*.png"))
    if not captures:
        print(f"❌ No captures found in {captures_dir}")
        sys.exit(1)
    print(f"📸 Found {len(captures)} captures")

    # --- Step 1: Create HyperFrames project ---
    work_dir = Path(tempfile.mkdtemp(prefix="hf-report-"))
    print(f"📁 Working directory: {work_dir}")

    subprocess.run(["npx", "--yes", "hyperframes", "init", str(work_dir / "project"),
                    "--example", "blank"], check=True, capture_output=True)
    project_dir = work_dir / "project"
    print(f"   ✅ HyperFrames project created")

    # --- Step 2: Generate TTS narration ---
    narration_text = args.narration
    if narration_text and Path(narration_text).exists():
        narration_text = Path(narration_text).read_text()
    if not narration_text:
        narration_text = f"Automated test report. {len(captures)} screenshots captured."

    tts_path = project_dir / "narration.wav"
    if args.localai:
        print(f"🗣️ Generating TTS via LocalAI (EUREKAI, voice={args.voice})...")
        # Map af_nova/am_michael to LocalAI voices
        voice_map = {"af_nova": "nova", "am_michael": "onyx", "nova": "nova"}
        la_voice = voice_map.get(args.voice, "nova")
        subprocess.run([
            "curl", "-s", "-X", "POST", "http://192.168.1.47:8080/v1/audio/speech",
            "-H", "Content-Type: application/json",
            "-d", json.dumps({"model": "tts-1", "input": narration_text, "voice": la_voice}),
            "--output", str(tts_path)
        ], check=True)
    else:
        print(f"🗣️ Generating TTS via HyperFrames (voice={args.voice})...")
        subprocess.run([
            "npx", "hyperframes", "tts", narration_text,
            "--voice", args.voice,
            "--output", str(tts_path)
        ], check=True)
    print(f"   → {tts_path} ({tts_path.stat().st_size / 1024:.0f} KB)")

    # --- Step 3: Generate index.html from template ---
    duration_per_frame = 1.0 / args.fps
    total_duration = len(captures) * duration_per_frame

    # Read template
    html = TEMPLATE_FILE.read_text() if TEMPLATE_FILE.exists() else _default_template()

    # Update duration in stage div
    import re
    html = re.sub(r'data-duration="30"', f'data-duration="{total_duration:.0f}"', html)
    html = re.sub(r'data-duration="(\d+)"', lambda m: f'data-duration="{int(total_duration)}"', html, count=1)

    # Generate frame entries
    frame_entries = []
    gsap_animations = []
    progress_duration = total_duration

    for i, cap in enumerate(captures):
        start = i * duration_per_frame
        # Copy frame to project
        frame_name = f"frame_{i:04d}.png"
        shutil.copy2(cap, project_dir / frame_name)

        frame_entries.append(
            f'    <img class="clip frame-img" id="frame-{i}" data-start="{start:.1f}" '
            f'data-duration="{duration_per_frame:.1f}" data-track-index="{i + 1}" '
            f'src="{frame_name}" />'
        )

        if i > 0:
            prev_end = (i - 1) * duration_per_frame + duration_per_frame - 0.3
            gsap_animations.append(
                f'    tl.to("#frame-{i-1}", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {prev_end:.1f});'
            )
            gsap_animations.append(
                f'    tl.from("#frame-{i}", {{ opacity: 0, duration: 0.3, ease: "power2.out" }}, {start:.1f});'
            )

        # Update timestamp at each frame
        mins = int(start) // 60
        secs = int(start) % 60
        gsap_animations.append(
            f'    tl.call(() => {{\n'
            f'      document.querySelector(\'.timestamp\').textContent = \'{mins:02d}:{secs:02d}\';\n'
            f'    }}, [], {start:.1f});'
        )

    # First frame fade in
    gsap_animations.insert(0,
        f'    tl.from("#frame-0", {{ opacity: 0, duration: 0.4, ease: "power2.out" }}, 0.3);'
    )

    # Replace placeholder frames and animations
    placeholder_start = html.find('<!-- Frames injected')
    placeholder_end = html.find('<!-- PROGRESS BAR -->') if '<!-- PROGRESS BAR -->' in html else html.find('// Progress bar')

    # Simple replacement approach
    old_frames_marker = 'src="frame_0000.png" />'
    new_frames_section = '\n'.join(frame_entries)

    # Replace the 3 placeholder img lines
    lines = html.split('\n')
    new_lines = []
    in_frames_section = False
    for line in lines:
        if 'class="clip frame-img"' in line and 'src="frame_' in line:
            if not in_frames_section:
                new_lines.append(new_frames_section)
                in_frames_section = True
            continue
        new_lines.append(line)
    html = '\n'.join(new_lines)

    # Replace GSAP animations between the comments
    gsap_start_marker = "tl.from(\"#frame-0\""
    gsap_end_marker = "window.__timelines[\"report-root\"]"

    old_anim_section = html[html.find(gsap_start_marker):html.find(gsap_end_marker)]
    new_anim_section = '\n'.join(gsap_animations) + '\n\n    // Progress bar\n    tl.to(".progress-bar", { width: "100%", duration: ' + str(progress_duration) + ', ease: "none" }, 0);\n\n    '
    html = html.replace(old_anim_section, new_anim_section)

    # Write index.html
    (project_dir / "index.html").write_text(html)
    print(f"   ✅ index.html generated ({len(captures)} frames, {total_duration:.1f}s)")

    # --- Step 4: Update meta.json ---
    meta_path = project_dir / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        meta["name"] = "AI Tester Report"
        meta["duration"] = total_duration
        meta_path.write_text(json.dumps(meta, indent=2))

    # --- Step 5: Lint ---
    print("🔍 Linting...")
    result = subprocess.run(["npm", "run", "check"], cwd=str(project_dir),
                           capture_output=True, text=True)
    if result.returncode != 0:
        print(f"   ⚠️ Lint warnings:\n{result.stdout[:500]}")
    else:
        print(f"   ✅ Lint passed")

    if args.skip_render:
        print(f"\n✅ Project ready at: {project_dir}")
        print(f"   To render: cd {project_dir} && npm run render")
        print(f"   To preview: cd {project_dir} && npm run dev")
        return

    # --- Step 6: Render ---
    print(f"🎬 Rendering video ({total_duration:.1f}s @ {args.fps}fps)...")
    render_result = subprocess.run(
        ["npm", "run", "render", "--", f"--output={output_path.resolve()}"],
        cwd=str(project_dir), capture_output=True, text=True
    )

    if render_result.returncode == 0 and output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"   ✅ Video rendered: {output_path} ({size_mb:.1f} MB)")
    else:
        print(f"   ❌ Render failed: {render_result.stderr[:500]}")
        sys.exit(1)

    # Cleanup
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\n✨ Done! Output: {output_path}")


def _default_template():
    """Fallback template if template file is missing"""
    return """<!doctype html>
<html><head><meta charset="utf-8"><style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0a0a0f;overflow:hidden;font-family:sans-serif;}
#stage{width:1920px;height:1080px;position:relative;background:#0a0a0f;overflow:hidden;}
.frame-img{position:absolute;top:0;left:0;width:100%;height:100%;object-fit:contain;background:#0a0a0f;}
.timestamp{position:absolute;bottom:30px;right:40px;font-size:18px;color:rgba(255,255,255,0.4);}
.progress-bar{position:absolute;bottom:0;left:0;height:3px;background:linear-gradient(90deg,#7c3aed,#f59e0b);}
</style></head><body>
<div id="stage" data-composition-id="report" data-start="0" data-duration="30" data-width="1920" data-height="1080">
<audio class="clip" data-start="2" data-duration="26" data-track-index="0" data-volume="1.0" src="narration.wav"></audio>
<div class="timestamp">00:00</div>
<div class="progress-bar" style="width:0%;"></div>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14/dist/gsap.min.js"></script>
<script>
window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
tl.to(".progress-bar",{width:"100%",duration:30,ease:"none"},0);
window.__timelines["report"]=tl;
</script></body></html>"""

if __name__ == "__main__":
    main()

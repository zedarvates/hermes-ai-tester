#!/usr/bin/env python3
"""
Capture Windows desktop screenshots from WSL using PyAutoGUI.
Run on Windows or from WSL with X-server.
"""

import os, sys, time, argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Screen capture utility for AI Tester")
    parser.add_argument("--output", default="./captures", help="Output directory")
    parser.add_argument("--duration", type=int, default=30, help="Capture duration (seconds)")
    parser.add_argument("--interval", type=float, default=0.3, help="Interval between captures")
    parser.add_argument("--count", type=int, help="Number of captures (overrides duration)")
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.count:
        frames = args.count
    else:
        frames = int(args.duration / args.interval)
    
    print(f"📸 Capturing {frames} screenshots...")
    print(f"   Output: {output_dir}")
    print(f"   Interval: {args.interval}s")
    print(f"   Press Ctrl+C to stop early")
    print()
    
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        
        for i in range(frames):
            path = output_dir / f"frame_{i:04d}.png"
            pyautogui.screenshot(str(path))
            elapsed = i * args.interval
            if i % 10 == 0:
                print(f"   [{elapsed:.1f}s] Captured {path.name}")
            time.sleep(args.interval)
        
        print(f"\n✅ Done! {frames} screenshots saved to {output_dir}")
        
    except ImportError:
        print("❌ PyAutoGUI not installed.")
        print("   Install: pip install pyautogui")
        print("   Or on Windows: py -m pip install pyautogui")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopped. {i+1} screenshots captured.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

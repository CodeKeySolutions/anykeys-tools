# mp4_to_gif.py
import subprocess
import os
import sys

def convert_mp4_to_gif(input_file, output_file=None, scale=None, fps=10):
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.gif'

    scale_filter = f",scale={scale}" if scale else ""

    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'fps={fps}{scale_filter}',
        '-loop', '0',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Converted to: {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mp4_to_gif.py input.mp4 [scale_width:scale_height] [fps]")
    else:
        input_file = sys.argv[1]
        scale = sys.argv[2] if len(sys.argv) > 2 else None
        fps = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        convert_mp4_to_gif(input_file, scale=scale, fps=fps)
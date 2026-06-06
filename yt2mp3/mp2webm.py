# mp4_to_webm.py
import subprocess
import os

def convert_mp4_to_webm(input_file, output_file=None):
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.webm'

    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libvpx-vp9',
        '-b:v', '1M',
        '-c:a', 'libopus',
        output_file
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Converted to: {output_file}")
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mp4_to_webm.py input.mp4")
    else:
        convert_mp4_to_webm(sys.argv[1])
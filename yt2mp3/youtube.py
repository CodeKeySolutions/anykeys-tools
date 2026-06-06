import yt_dlp
import os
import sys


def download_with_yt_dlp(url, output_path='./', format='best'):
    """
    Downloads and optionally converts YouTube videos using yt-dlp
    :param url: YouTube video URL
    :param output_path: Output directory
    :param format: Format code or 'best' for best quality
    """
    ydl_opts = {
        'format': format,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        # To extract audio only and convert to mp3:
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"\nDownloaded: {info.get('title', 'unknown title')}")
            print(f"Saved to: {ydl.prepare_filename(info)}")
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"\nError: {e}")
        return None

def main():
    print("YouTube Video Downloader")
    print("-----------------------")

# sys.argv is a list containing all command line arguments
# The first element (index 0) is the script name itself

    video_url = sys.argv[1]
    if not video_url:
        return
        # Get URL from user input
        # video_url = input("\nEnter YouTube URL (or 'q' to quit): ")
    if video_url.lower() == 'q':
        print("Exiting program...")


    if not video_url:
        print("Please enter a valid URL")


        # Download the video
    download_with_yt_dlp(video_url)


        # Ask if user wants to download another


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mp4_to_webm.py input.mp4")
    else:
        download_with_yt_dlp(sys.argv[1])
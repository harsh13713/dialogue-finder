import subprocess
import tempfile
from pathlib import Path


def is_okru(url):
    return (
        "ok.ru" in url.lower()
        or "odnoklassniki.ru" in url.lower()
    )


def download_okru(url, video_path):

    # OK.ru exposes named formats rather than
    # normal 360p/480p resolutions.

    formats = [
        "low",
        "lowest",
        "mobile"
    ]

    last_error = None

    for video_format in formats:

        print(
            f"\nTrying OK.ru format: {video_format}"
        )

        try:

            subprocess.run(
                [
                    "yt-dlp",

                    "--no-check-certificates",

                    "--socket-timeout", "60",
                    "--retries", "5",
                    "--fragment-retries", "5",

                    "-f",
                    video_format,

                    "-o",
                    str(video_path),

                    url
                ],
                check=True
            )

            print(
                f"Successfully downloaded "
                f"format: {video_format}"
            )

            return

        except subprocess.CalledProcessError as e:

            last_error = e

            print(
                f"Format {video_format} failed."
            )

    raise RuntimeError(
        "Could not download the OK.ru video.\n"
        "The server may be blocking the media request "
        "with HTTP 403."
    ) from last_error


def download_other_video(url, video_path):

    print("\nChecking available video formats...")

    # Prefer a small video format.
    #
    # 360p is sufficient for extracting frames.
    # If unavailable, yt-dlp falls back to the
    # smallest available format.

    format_selector = (
        "worst[height<=360]/"
        "worst"
    )

    print(
        "Downloading suitable low-resolution video..."
    )

    subprocess.run(
        [
            "yt-dlp",

            "--no-check-certificates",

            "--socket-timeout", "60",
            "--retries", "5",
            "--fragment-retries", "5",

            "-f",
            format_selector,

            "-o",
            str(video_path),

            url
        ],
        check=True
    )


def extract_audio_from_url(url):

   

    # -----------------------------------------
    # Download video
    # -----------------------------------------

    print("\nDownloading suitable low-resolution video...")

    if is_okru(url):

        download_okru(
            url,
            video_path
        )

    else:

        download_other_video(
            url,
            video_path
        )

    # -----------------------------------------
    # Extract audio
    # -----------------------------------------

    print("\nExtracting audio...")

    subprocess.run(
        [
            "ffmpeg",
            "-y",

            "-i",
            str(video_path),

            "-vn",

            "-ac", "1",

            "-ar", "16000",

            str(audio_path)
        ],
        check=True
    )

    print(
        "Audio extraction completed."
    )

    return (
        str(audio_path),
        str(video_path)
    )


if __name__ == "__main__":

    url = input(
        "Enter video URL: "
    ).strip()

    audio_path, video_path = (
        extract_audio_from_url(url)
    )

    print("\nAudio:", audio_path)
    print("Video:", video_path)
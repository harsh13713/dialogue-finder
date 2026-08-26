from flask import Flask, render_template, request

import os
import json
import hashlib
import shutil

from video_processor import extract_audio_from_url
from transcribe import transcribe_audio
from search_dialogue import search_dialogue


app = Flask(__name__)

CACHE_DIR = "cache"


# ==================================================
# CACHE UTILITIES
# ==================================================

def get_video_id(url):
    """
    Create a unique ID from the video URL.
    """

    return hashlib.md5(
        url.encode("utf-8")
    ).hexdigest()


def get_cache_paths(url):

    video_id = get_video_id(url)

    cache_dir = os.path.join(
        CACHE_DIR,
        video_id
    )

    os.makedirs(
        cache_dir,
        exist_ok=True
    )

    return {
        "dir": cache_dir,

        "video": os.path.join(
            cache_dir,
            "video.mp4"
        ),

        "audio": os.path.join(
            cache_dir,
            "audio.wav"
        ),

        "transcript": os.path.join(
            cache_dir,
            "transcript.json"
        )
    }


def load_cached_transcript(path):

    if not os.path.exists(path):
        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return None


def save_cached_transcript(path, transcript):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            transcript,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    error = None

    if request.method == "POST":

        video_url = request.form.get(
            "video_url",
            ""
        ).strip()

        dialogue = request.form.get(
            "dialogue",
            ""
        ).strip()

        # ------------------------------------------
        # Validate input
        # ------------------------------------------

        if not video_url:

            error = "Please enter a video URL."

            return render_template(
                "index.html",
                result=result,
                error=error
            )

        if not dialogue:

            error = "Please enter a dialogue."

            return render_template(
                "index.html",
                result=result,
                error=error
            )

        try:

            # ======================================
            # GET CACHE PATHS
            # ======================================

            paths = get_cache_paths(video_url)

            video_path = paths["video"]
            audio_path = paths["audio"]
            transcript_path = paths["transcript"]

            # ======================================
            # CHECK WHAT IS ALREADY CACHED
            # ======================================

            video_exists = os.path.isfile(
                video_path
            )

            audio_exists = os.path.isfile(
                audio_path
            )

            transcript_exists = os.path.isfile(
                transcript_path
            )

            # ======================================
            # CASE 1:
            # VIDEO + TRANSCRIPT ALREADY EXIST
            # ======================================

            if video_exists and transcript_exists:

                print(
                    "\n========================================"
                )

                print("CACHE FOUND")

                print(
                    "Using cached video."
                )

                print(
                    "Using cached transcript."
                )

                print(
                    "Skipping download."
                )

                print(
                    "Skipping transcription."
                )

                print(
                    "========================================"
                )

                transcript = load_cached_transcript(
                    transcript_path
                )

                if transcript is None:

                    error = (
                        "Cached transcript could not "
                        "be loaded."
                    )

                    return render_template(
                        "index.html",
                        result=result,
                        error=error
                    )

            # ======================================
            # CASE 2:
            # VIDEO EXISTS BUT TRANSCRIPT MISSING
            # ======================================

            elif video_exists:

                print(
                    "\n========================================"
                )

                print(
                    "VIDEO FOUND IN CACHE"
                )

                print(
                    "Skipping video download."
                )

                print(
                    "Transcript not found."
                )

                print(
                    "Transcribing cached video..."
                )

                print(
                    "========================================"
                )

                # If audio exists, use it.
                # Otherwise extract audio from
                # the cached video.

                if not audio_exists:

                    import subprocess

                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-i",
                            video_path,
                            "-vn",
                            "-ac",
                            "1",
                            "-ar",
                            "16000",
                            audio_path
                        ],
                        check=True
                    )

                transcript = transcribe_audio(
                    audio_path
                )

                if transcript is None:

                    error = (
                        "Transcription failed."
                    )

                    return render_template(
                        "index.html",
                        result=result,
                        error=error
                    )

                save_cached_transcript(
                    transcript_path,
                    transcript
                )

            # ======================================
            # CASE 3:
            # NOTHING CACHED
            # ======================================

            else:

                print(
                    "\n========================================"
                )

                print(
                    "NO CACHE FOUND"
                )

                print(
                    "Downloading video..."
                )

                print(
                    "========================================"
                )

                # ----------------------------------
                # Download video + extract audio
                # ----------------------------------

                downloaded_audio, downloaded_video = (
                    extract_audio_from_url(
                        video_url
                    )
                )

                # ----------------------------------
                # Copy video into permanent cache
                # ----------------------------------

                print(
                    "\nSaving video to cache..."
                )

                shutil.copy2(
                    downloaded_video,
                    video_path
                )

                # ----------------------------------
                # Copy audio into permanent cache
                # ----------------------------------

                shutil.copy2(
                    downloaded_audio,
                    audio_path
                )

                # ----------------------------------
                # Transcribe
                # ----------------------------------

                print(
                    "\nTranscribing audio..."
                )

                transcript = transcribe_audio(
                    audio_path
                )

                if transcript is None:

                    error = (
                        "Transcription failed."
                    )

                    return render_template(
                        "index.html",
                        result=result,
                        error=error
                    )

                # ----------------------------------
                # Save transcript
                # ----------------------------------

                save_cached_transcript(
                    transcript_path,
                    transcript
                )

                print(
                    "\n========================================"
                )

                print(
                    "CACHE CREATED"
                )

                print(
                    "Video saved."
                )

                print(
                    "Audio saved."
                )

                print(
                    "Transcript saved."
                )

                print(
                    "========================================"
                )

            # ======================================
            # SEARCH DIALOGUE
            # ======================================

            print(
                "\nSearching dialogue..."
            )

            result = search_dialogue(
                transcript,
                dialogue,
                video_path
            )

            if result is None:

                error = (
                    "No sufficiently similar "
                    "dialogue was found."
                )

        except Exception as e:

            print(
                "\n========================================"
            )

            print("ERROR:")
            print(e)

            print(
                "========================================"
            )

            error = str(e)

    return render_template(
        "index.html",
        result=result,
        error=error
    )


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
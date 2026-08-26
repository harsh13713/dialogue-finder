from flask import Flask, render_template, request

import os
import json
import hashlib

from video_processor import extract_audio_from_url
from transcribe import transcribe_audio
from search_dialogue import search_dialogue


app = Flask(__name__)

CACHE_DIR = os.environ.get(
    "CACHE_DIR",
    "cache"
)


# ==================================================
# CACHE FUNCTIONS
# ==================================================

def get_video_id(url):
    """
    Create the same unique ID used by main.py.
    """

    return hashlib.md5(
        url.encode("utf-8")
    ).hexdigest()


def get_cached_data(url):

    video_id = get_video_id(url)

    cache_path = os.path.join(
        CACHE_DIR,
        video_id
    )

    transcript_path = os.path.join(
        cache_path,
        "transcript.json"
    )

    video_path = os.path.join(
        cache_path,
        "video.mp4"
    )

    # ----------------------------------------------
    # Check whether transcript exists
    # ----------------------------------------------

    if os.path.exists(transcript_path):

        with open(
            transcript_path,
            "r",
            encoding="utf-8"
        ) as file:

            transcript = json.load(file)

        return transcript, video_path

    return None, None


def save_transcript(url, transcript):

    video_id = get_video_id(url)

    video_cache_dir = os.path.join(
        CACHE_DIR,
        video_id
    )

    os.makedirs(
        video_cache_dir,
        exist_ok=True
    )

    transcript_path = os.path.join(
        video_cache_dir,
        "transcript.json"
    )

    with open(
        transcript_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            transcript,
            file,
            indent=4,
            ensure_ascii=False
        )


def save_video(url, downloaded_video_path):

    video_id = get_video_id(url)

    video_cache_dir = os.path.join(
        CACHE_DIR,
        video_id
    )

    os.makedirs(
        video_cache_dir,
        exist_ok=True
    )

    cached_video_path = os.path.join(
        video_cache_dir,
        "video.mp4"
    )

    # Copy video into permanent cache

    with open(
        downloaded_video_path,
        "rb"
    ) as source:

        with open(
            cached_video_path,
            "wb"
        ) as destination:

            destination.write(
                source.read()
            )

    return cached_video_path


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
        # Validate URL
        # ------------------------------------------

        if not video_url:

            error = "Please enter a video URL."

            return render_template(
                "index.html",
                result=result,
                error=error
            )

        # ------------------------------------------
        # Validate dialogue
        # ------------------------------------------

        if not dialogue:

            error = "Please enter a dialogue."

            return render_template(
                "index.html",
                result=result,
                error=error
            )

        try:

            # ======================================
            # CHECK CACHE
            # ======================================

            print(
                "\nChecking existing video and "
                "transcript..."
            )

            transcript, video_path = (
                get_cached_data(video_url)
            )

            # ======================================
            # CACHE EXISTS
            # ======================================

            if (
                transcript is not None
                and os.path.exists(video_path)
            ):

                print(
                    "\n================================"
                )

                print(
                    "CACHE FOUND"
                )

                print(
                    "Skipping video download."
                )

                print(
                    "Skipping transcription."
                )

                print(
                    "================================"
                )

            # ======================================
            # CACHE DOES NOT EXIST
            # ======================================

            else:

                print(
                    "\n================================"
                )

                print(
                    "NO CACHE FOUND"
                )

                print(
                    "Downloading video..."
                )

                print(
                    "================================"
                )

                # ----------------------------------
                # Download video + extract audio
                # ----------------------------------

                audio_path, downloaded_video_path = (
                    extract_audio_from_url(
                        video_url
                    )
                )

                # ----------------------------------
                # Save video permanently
                # ----------------------------------

                print(
                    "\nSaving video to cache..."
                )

                video_path = save_video(
                    video_url,
                    downloaded_video_path
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

                save_transcript(
                    video_url,
                    transcript
                )

                print(
                    "\nVideo saved to cache."
                )

                print(
                    "Transcript saved to cache."
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
                "\nERROR:"
            )

            print(e)

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

    app.run(
        debug=True
    )
import whisper
import json
import os


# ==================================================
# LOAD WHISPER MODEL ONCE
# ==================================================

print("\nLoading Whisper model...")

model = whisper.load_model("base")

print("Whisper model loaded successfully.\n")


# ==================================================
# TRANSCRIPTION
# ==================================================

def transcribe_audio(audio_path):

    if not os.path.exists(audio_path):

        print("Audio file not found!")

        return None

    print("\nTranscribing...")

    result = model.transcribe(
        audio_path,
        fp16=False,
        word_timestamps=True
    )

    print("\nTRANSCRIPTION COMPLETE\n")

    segments = []

    for segment in result["segments"]:

        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        # ------------------------------------------
        # Word-level timestamps
        # ------------------------------------------

        words = []

        for word in segment.get("words", []):

            words.append({
                "word": word["word"].strip(),
                "start": word["start"],
                "end": word["end"]
            })

        # ------------------------------------------
        # Store segment
        # ------------------------------------------

        segments.append({
            "start": start,
            "end": end,
            "text": text,
            "words": words
        })

        print(
            f"[{start:.2f} --> {end:.2f}] {text}"
        )

    return segments


# ==================================================
# TESTING
# ==================================================

if __name__ == "__main__":

    audio_path = input(
        "Enter audio path: "
    ).strip()

    transcript = transcribe_audio(
        audio_path
    )

    if transcript is not None:

        with open(
            "transcript.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                transcript,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            "\nTranscript saved to transcript.json"
        )
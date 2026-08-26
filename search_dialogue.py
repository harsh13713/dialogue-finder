import json
import re
import os

from rapidfuzz import fuzz
import cv2


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower()

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Remove extra spaces
    text = " ".join(text.split())

    return text


# ============================================================
# FIND FIRST MATCHING WORD TIMESTAMP
# ============================================================

def get_dialogue_start_time(segment, query):

    words = segment.get("words", [])

    # If word timestamps are unavailable,
    # fall back to segment start
    if not words:
        return float(segment["start"])

    query_words = normalize_text(query).split()

    if not query_words:
        return float(segment["start"])

    # --------------------------------------------------------
    # Find the earliest matching query word
    # --------------------------------------------------------

    best_match = None
    best_position = None

    for query_word in query_words:

        best_score = 0
        best_word = None
        best_index = None

        for index, word_info in enumerate(words):

            transcript_word = normalize_text(
                word_info.get("word", "")
            )

            if not transcript_word:
                continue

            score = fuzz.ratio(
                query_word,
                transcript_word
            )

            if score > best_score:

                best_score = score
                best_word = word_info
                best_index = index

        # ----------------------------------------------------
        # Accept sufficiently similar word
        # ----------------------------------------------------

        if (
            best_word is not None
            and best_score >= 65
        ):

            if (
                best_position is None
                or best_index < best_position
            ):

                best_position = best_index
                best_match = best_word

    # --------------------------------------------------------
    # Return timestamp of earliest matching word
    # --------------------------------------------------------

    if best_match is not None:

        return float(
            best_match["start"]
        )

    # Fallback
    return float(
        segment["start"]
    )


# ============================================================
# GET VIDEO FRAME
# ============================================================

def get_frame_from_video(
    video_path,
    timestamp,
    output_path
):

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():

        print("Could not open video.")

        return None, None

    # --------------------------------------------------------
    # Get FPS
    # --------------------------------------------------------

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:

        print(
            "Could not determine video FPS."
        )

        cap.release()

        return None, None

    # --------------------------------------------------------
    # Calculate frame number
    # --------------------------------------------------------

    frame_number = int(
        timestamp * fps
    )

    # --------------------------------------------------------
    # Move to required frame
    # --------------------------------------------------------

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number
    )

    success, frame = cap.read()

    if not success:

        print(
            "Could not extract video frame."
        )

        cap.release()

        return None, None

    # --------------------------------------------------------
    # Save frame
    # --------------------------------------------------------

    success = cv2.imwrite(
        output_path,
        frame
    )

    if not success:

        print(
            "Could not save video frame."
        )

        cap.release()

        return None, None

    cap.release()

    return frame_number, fps


# ============================================================
# SEARCH DIALOGUE
# ============================================================

def search_dialogue(
    transcript,
    query,
    video_path
):

    query_normalized = normalize_text(
        query
    )

    query_words = query_normalized.split()

    if not query_words:

        print(
            "Please enter some dialogue."
        )

        return None

    matches = []

    # ========================================================
    # SEARCH EVERY TRANSCRIPT SEGMENT
    # ========================================================

    for segment in transcript:

        text = segment.get(
            "text",
            ""
        )

        text_normalized = normalize_text(
            text
        )

        text_words = text_normalized.split()

        if not text_words:
            continue

        # ----------------------------------------------------
        # 1. Overall fuzzy similarity
        # ----------------------------------------------------

        overall_score = fuzz.ratio(
            query_normalized,
            text_normalized
        )

        # ----------------------------------------------------
        # 2. Match every query word
        # ----------------------------------------------------

        matching_words = 0

        word_scores = []

        for query_word in query_words:

            best_word_score = max(
                (
                    fuzz.ratio(
                        query_word,
                        text_word
                    )
                    for text_word in text_words
                ),
                default=0
            )

            word_scores.append(
                best_word_score
            )

            if best_word_score >= 65:

                matching_words += 1

        # ----------------------------------------------------
        # 3. Word coverage
        # ----------------------------------------------------

        word_coverage = (
            matching_words /
            len(query_words)
        ) * 100

        # ----------------------------------------------------
        # 4. Average word similarity
        # ----------------------------------------------------

        average_word_score = (
            sum(word_scores) /
            len(word_scores)
        )

        # ----------------------------------------------------
        # 5. Combined score
        # ----------------------------------------------------

        final_score = (
            0.7 * average_word_score
            + 0.3 * overall_score
        )

        # ----------------------------------------------------
        # 6. Accept fuzzy matches
        # ----------------------------------------------------

        if (
            word_coverage >= 50
            and final_score >= 60
        ):

            matches.append({

                "segment": segment,

                "score": final_score,

                "coverage": word_coverage,

                "average_word_score":
                    average_word_score
            })

    # ========================================================
    # SORT BEST MATCHES
    # ========================================================

    matches.sort(
        key=lambda x: (
            x["coverage"],
            x["score"]
        ),
        reverse=True
    )

    if not matches:

        print(
            "\nNo sufficiently similar dialogue found."
        )

        return None

    # ========================================================
    # BEST MATCH
    # ========================================================

    best = matches[0]

    segment = best["segment"]

    # --------------------------------------------------------
    # Find FIRST WORD timestamp
    # --------------------------------------------------------

    start = get_dialogue_start_time(
        segment,
        query
    )

    end = float(
        segment.get(
            "end",
            start
        )
    )

    # ========================================================
    # CREATE FLASK STATIC FRAME DIRECTORY
    # ========================================================

    frame_dir = os.path.join(
        "static",
        "frames"
    )

    os.makedirs(
        frame_dir,
        exist_ok=True
    )

    # ========================================================
    # FRAME FILE
    # ========================================================

    frame_filename = os.path.join(
        frame_dir,
        f"frame_{start:.3f}.jpg"
    )

    # ========================================================
    # EXTRACT FRAME
    # ========================================================

    frame_number, fps = get_frame_from_video(
        video_path,
        start,
        frame_filename
    )

    if frame_number is None:

        return None

    # ========================================================
    # TIMESTAMP HH:MM:SS.sss
    # ========================================================

    hours = int(
        start // 3600
    )

    minutes = int(
        (start % 3600) // 60
    )

    seconds = start % 60

    timestamp = (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{seconds:06.3f}"
    )

    # ========================================================
    # WEB PATH
    # ========================================================

    # Do NOT return "static/frames/..."
    # because index.html already uses url_for('static', ...)
    #
    # We return only the path INSIDE static/

    web_frame_path = (
        f"frames/frame_{start:.3f}.jpg"
    )

    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print()

    print(
        f"Timestamp : {timestamp}"
    )

    print(
        f"Frame : {frame_number}"
    )

    print(
        f'Text : "{segment["text"]}"'
    )

    print(
        f"Frame image : {web_frame_path}"
    )

    print()

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "segment": segment,

        "timestamp": timestamp,

        "frame_number": frame_number,

        "frame_image": web_frame_path,

        "fps": fps,

        "score": best["score"],

        "coverage": best["coverage"],

        "average_word_score":
            best["average_word_score"]
    }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    with open(
        "transcript.json",
        "r",
        encoding="utf-8"
    ) as file:

        transcript = json.load(file)

    query = input(
        "Enter dialogue to find: "
    ).strip()

    video_path = input(
        "Enter video path: "
    ).strip()

    search_dialogue(
        transcript,
        query,
        video_path
    )

# Dialogue Finder

> **Dialogue Finder** is a Flask web application that finds a dialogue inside a video using speech-to-text transcription and fuzzy text matching. It takes a video URL and a dialogue as input, processes the video, generates a transcript using Whisper, and searches the transcript for the closest match.

## Problem

Finding a particular dialogue in a long video manually can take a lot of time.

The idea behind this project is to make the process simpler:

**Give the video URL + enter the dialogue → find where that dialogue occurs.**

The application handles the video processing, transcription and dialogue matching automatically.

---

## How It Works

The application follows this basic pipeline:

1. User provides a video URL.
2. The video is downloaded using `yt-dlp`.
3. Audio is extracted from the video using `ffmpeg`.
4. The extracted audio is converted into a suitable format for transcription.
5. Whisper generates the transcript.
6. The requested dialogue is compared against the transcript.
7. Fuzzy matching is used so that small differences between the searched dialogue and the actual transcript do not immediately result in a failure.
8. The matching result is displayed through the Flask web interface.

### Overall Flow


<img width="1376" height="768" alt="Gemini_Generated_Image_xyqrhxxyqrhxxyqr" src="https://github.com/user-attachments/assets/1e3dc31a-49d6-44e0-93d2-b133915c0a1c" />


---

## Tech Stack

### Backend

* Python
* Flask

### Video / Audio Processing

* `yt-dlp` - downloading videos from supported URLs
* `ffmpeg` - extracting and processing audio

### Speech Recognition

* OpenAI Whisper
* Whisper `base` model

### Dialogue Matching

* RapidFuzz
* Regular expressions for text processing

### Video Processing

* OpenCV

### Frontend

* HTML
* CSS


---

## Project Structure

```text
dialogue_finder/
│
├── app.py
├── main.py
├── video_processor.py
├── transcribe.py
├── search_dialogue.py
│
├── templates/
│   └── ...
│
├── static/
│   └── ...
│
├── cache/
│   └── ...
│
├── requirements.txt
├── prompts.txt
├── approach.md
├── README.md
├── Dockerfile
└── .gitignore
```

### Important Files

| File                 | Purpose                                                   |
| -------------------- | --------------------------------------------------------- |
| `app.py`             | Flask application and request handling                    |
| `video_processor.py` | Video downloading and audio extraction                    |
| `transcribe.py`      | Loads Whisper and performs transcription                  |
| `search_dialogue.py` | Searches the transcript for the requested dialogue        |
| `templates/`         | HTML templates used by the application                    |
| `static/`            | CSS and other frontend assets                             |
| `requirements.txt`   | Python dependencies                                       |
| `approach.md`        | Detailed explanation of the approach and design decisions |
| `prompts.txt`        | AI prompts used during development                        |
| `Dockerfile`         | Container configuration                                   |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/harsh13713/dialogue-finder.git
cd dialogue_finder
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

FFmpeg is required for extracting audio from videos.

Make sure `ffmpeg` is available in the system PATH.

You can verify the installation using:

```bash
ffmpeg -version
```

---

## Running the Application

Start the Flask application:

```bash
python app.py
```

The application will start locally.

Open:

```text
http://127.0.0.1:5000
```

---

## Example Usage

1. Open the application.
2. Enter the URL of the video.
3. Enter the dialogue or phrase to search for.
4. Submit the request.
5. The application processes the video and searches the generated transcript.
6. The matching dialogue/result is displayed.

---

## Dialogue Matching

Exact string matching is not always reliable for speech transcripts.

For example, the searched dialogue might be:

```text
I don't want to go there
```

while Whisper could produce something slightly different such as:

```text
I do not want to go there
```

or contain small transcription differences.

Because of this, the project uses fuzzy string matching instead of relying only on exact equality.

The matching process also involves text preprocessing before comparing the query with transcript content.

This makes the search more tolerant of minor transcription differences.

---

## Caching

Video and processing results can be cached so that the same video does not have to be processed from scratch unnecessarily.

This is useful because transcription is one of the more computationally expensive parts of the application.

The project therefore separates the processing stages and reuses previously generated data where possible.

---

## Design Decisions

### Why Whisper?

The main requirement is to convert spoken dialogue into searchable text.

Whisper provides a practical way of performing speech-to-text transcription locally without requiring an external transcription API.

The `base` model was selected as a balance between transcription quality and computational requirements.

### Why RapidFuzz?

A transcript generated from speech recognition may not exactly match the text entered by the user.

RapidFuzz provides efficient fuzzy string matching, making it suitable for finding approximate matches in the transcript.

### Why FFmpeg?

The input video may contain audio in different formats.

FFmpeg provides a reliable way to extract the audio and convert it into a format suitable for transcription.

### Why Flask?

The application mainly requires a lightweight web interface around the processing pipeline.

Flask provides the routing and request-handling functionality needed without introducing unnecessary framework complexity.

---

## Limitations

There are a few practical limitations to the current implementation:

* Transcription time depends on the length of the video and available hardware.
* Whisper transcription may contain errors, especially with unclear audio, background noise, accents or overlapping speech.
* Fuzzy matching improves tolerance to transcription differences but cannot guarantee a correct match in every case.
* Video availability depends on whether `yt-dlp` supports the provided URL.
* Processing longer videos requires more time and computational resources.

---

## Future Improvements

Some possible improvements include:

* Showing timestamps for matched dialogues.
* Supporting multiple matching results instead of only the best match.
* Improving transcript preprocessing and matching.
* Allowing users to upload local video files.
* Using a faster transcription backend such as `faster-whisper`.
* Adding asynchronous/background processing for longer videos.
* Improving the UI with processing progress indicators.
* Adding more robust error handling for unsupported or unavailable video URLs.

---

## Development Notes

The reasoning behind the implementation, important design choices and development process are documented separately in:

```text
approach.md
```

The AI prompts used during development are documented in:

```text
prompts.txt
```

These files are included to make the development process and problem-solving approach transparent.

---

## AI Usage

AI tools were used during development as a supporting tool for:

* Exploring possible approaches to the problem.
* Understanding unfamiliar libraries and APIs.
* Debugging implementation issues.
* Discussing alternative solutions.
* Improving and reviewing parts of the implementation.

The final implementation was tested and integrated into the project based on the requirements of the problem.

The prompts used during development are available in `prompts.txt`.

---

## Author

**Harshini Ganga TS**

Built as part of the Quest1 placement problem-solving round.



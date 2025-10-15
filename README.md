# MetaScribe

MetaScribe is a modular, accessibility-first tool for building metadata from audio files using subtitle input. It was originally developed to generate `metadata.csv` files for associating transcriptions of `.wav` files in voice cloning AI workflows. However, its structured design makes it suitable for most simple `.wav` transcription tasks where audio needs to be paired with text.

## Features

- 🎧 Audio playback and file tracking
- 📄 Subtitle-assisted text entry from `.srt` files
- 💾 Metadata export to `metadata.csv`
- 🔁 Session resume with undo-safe editing
- 🧠 Dyslexia-friendly Verdana font and fatigue-free layout
- 🔄 Batch renaming of `.wav` files with undo support
- 📋 Live preview of metadata and session state
- 🧹 Automatic cleanup of session data when complete

## How It Works

MetaScribe loads a folder of `.wav` files and a `transcript.srt` file. For each audio file, it presents a user-friendly interface to:

1. Play the audio
2. View the corresponding subtitle line
3. Add or refine the text
4. Accept the entry to bind it to the filename
5. Save progress and resume later if needed

The resulting metadata is saved in `metadata.csv` using the format:

filename|text

## Folder Structure

Place your files in the following structure:

MetaScribe/
├── metascribe.py         # Main application script  
├── transcript.srt        # Subtitle input file  
├── metadata.csv          # Output metadata file  
├── session.json          # Session persistence  
├── wavs/                 # Folder for audio files  

## Dependencies

- Python 3.8 or higher  
- Tkinter (included with standard Python)  
- Windows OS (uses `winsound` for audio playback)  

## Installation

1. Clone the repository:

   git clone https://github.com/yourusername/MetaScribe.git

2. Navigate to the project folder:

   cd MetaScribe

3. Ensure your `.wav` files are placed in the `wavs/` directory.

4. Include a `transcript.srt` file in the root directory.

5. Run the application:

   python metascribe.py

## Usage Notes

- The interface is optimized for 1500x1000 resolution and launches centered on screen.
- All fonts use Verdana for dyslexia-friendly readability.
- Metadata is saved in `metadata.csv` using the format: `filename|text`.
- Session progress is saved in `session.json` and automatically resumed on next launch.
- The “Audio Renamer” tool allows batch renaming of `.wav` files with undo support.
- The “Accept” button finalizes the current transcription and moves to the next file.
- The “Skip” button preserves manual edits and advances without finalizing.

## License

Specify your license here (e.g., MIT, GPL-3.0). Include a LICENSE file in the repository.

## Author

James Starling — Freelance broadcast and systems integration engineer, accessibility advocate, and creator of Echoes & Encounters.

---

MetaScribe is built for clarity, precision, and accessibility. It streamlines the process of aligning audio files with subtitle-based metadata for voice model training and other audio-text workflows.
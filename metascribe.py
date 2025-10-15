import re
import json
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import winsound

# === CONFIG ===
PROJECT_DIR = r"D:\Programs\Vocie Model Training"
SRT_FILE = os.path.join(PROJECT_DIR, "transcript.srt")
METADATA_FILE = os.path.join(PROJECT_DIR, "metadata.csv")
SESSION_FILE = os.path.join(PROJECT_DIR, "session.json")
WAV_DIR = os.path.join(PROJECT_DIR, "wavs")
PREFIX = "AI_A1-"

def parse_srt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    blocks = re.split(r'\n\s*\n', content.strip())
    return [' '.join(block.strip().split('\n')[2:]).strip() for block in blocks if len(block.strip().split('\n')) >= 3]

class MetadataBuilder:
    def __init__(self, master, lines):
        self.master = master
        self.lines = lines
        self.index = 1
        self.line_index = 0
        self.current_text = ""
        self.history = []
        self.line_count = 0

        self.load_wav_files()
        self.load_session()

        self.master.title("Metadata Builder")
        # Set size and center the window
        width, height = 1500, 1000
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")


        self.build_gui()
        self.update_display()

    def build_gui(self):
        # === Audio Renamer Button ===
        tk.Button(self.master, text="Audio Renamer", command=self.open_renamer_window, width=20).pack(anchor="nw", padx=20, pady=(10, 0))

        # === Metadata Preview ===
        self.frame_preview_container = tk.Frame(self.master)
        self.frame_preview_container.pack(padx=20, pady=10, fill="both", expand=True)

        self.frame_preview = tk.Frame(self.frame_preview_container)
        self.frame_preview.pack(fill="both", expand=True)

        self.frame_preview_button = tk.Frame(self.frame_preview_container)
        self.frame_preview_button.pack(fill="x", pady=(8, 0))

        tk.Label(self.frame_preview, text="📄 Current metadata.csv content:", font=("Verdana", 12, "bold")).pack(anchor="w")
        self.scrollbar = tk.Scrollbar(self.frame_preview)
        self.scrollbar.pack(side="right", fill="y")

        self.text_log = tk.Text(self.frame_preview, height=10, wrap="word", font=("Verdana", 12),
                                yscrollcommand=self.scrollbar.set, padx=10, pady=10)
        self.text_log.pack(side="left", fill="both", expand=True)
        self.scrollbar.config(command=self.text_log.yview)

        tk.Button(self.frame_preview_button, text="💾 Save Metadata", command=self.save_metadata_file, width=20).pack(anchor="e", padx=10, pady=5)

        # === Sentence Builder ===
        self.label_filename = tk.Label(self.master, text="", font=("Verdana", 12, "bold"))
        self.label_filename.pack(pady=5)

        self.btn_play = tk.Button(self.master, text="Play Audio", command=self.play_audio, width=15)
        self.btn_play.pack(pady=(0, 10))

        self.frame_added = tk.LabelFrame(self.master, text="📝 Current Audio File Text", font=("Verdana", 12, "bold"),
                                        padx=10, pady=10, relief="groove", bd=2)
        self.frame_added.pack(fill="x", padx=20, pady=(10, 5))

        self.text_current = tk.Text(self.frame_added, height=2, wrap="word", font=("Verdana", 12), fg="blue")
        self.text_current.pack(fill="x")

        tk.Button(self.frame_added, text="Accept", command=self.finalise_file, width=15).pack(anchor="e", pady=(10, 0))

        self.frame_next = tk.LabelFrame(self.master, text="📥 Text To Process", font=("Verdana", 12, "bold"),
                                        padx=10, pady=10, relief="groove", bd=2)
        self.frame_next.pack(fill="x", padx=20, pady=(5, 10))

        self.text_next = tk.Text(self.frame_next, height=2, wrap="word", font=("Verdana", 12), fg="green")
        self.text_next.pack(fill="x")

        # Unified row for progress label (left) and buttons (right)
        self.frame_next_buttons = tk.Frame(self.frame_next)
        self.frame_next_buttons.pack(fill="x", pady=(10, 0))

        # Left-aligned progress label
        self.frame_progress = tk.Frame(self.frame_next_buttons)
        self.frame_progress.pack(side="left", anchor="w", padx=(5, 0))

        self.label_progress = tk.Label(self.frame_progress, text="", font=("Verdana", 10), anchor="w", justify="left")
        self.label_progress.pack()

        # Right-aligned buttons
        self.frame_actions = tk.Frame(self.frame_next_buttons)
        self.frame_actions.pack(side="right", anchor="e", padx=(0, 10))

        tk.Button(self.frame_actions, text="Skip", command=self.skip_line, width=15).pack(side="left", padx=(0, 5))
        tk.Button(self.frame_actions, text="Add->Current Text", command=self.add_line, width=15).pack(side="left")

        # Save & Exit section remains unchanged
        self.frame_buttons = tk.Frame(self.master)
        self.frame_buttons.pack(pady=10)

        tk.Button(self.frame_buttons, text="Save & Exit", command=self.finish, width=15).grid(row=0, column=0, padx=5)

        self.master.protocol("WM_DELETE_WINDOW", self.finish)
    
    def save_metadata_file(self):
        try:
            content = self.text_log.get("1.0", "end").strip()
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            messagebox.showinfo("Saved", "✅ metadata.csv updated successfully.")
            print("💾 metadata.csv manually updated.")
            self.refresh_metadata_preview()
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save metadata:\n{e}")

    def get_current_filename(self):
        try:
            if self.history:
                return self.history[-1]["filename"]
            elif 0 <= self.index - 1 < len(self.wav_files):
                return self.wav_files[self.index - 1]
        except Exception:
            pass
        return f"{PREFIX}{self.index:04d}.wav"

    def update_display(self):
        current_filename = self.get_current_filename()
        self.label_filename.config(text=f"🎧 Current audio file:\n\n{current_filename}\n")

        if self.line_index >= len(self.lines):
            self.label_progress.config(text="✅ All lines processed.")
            self.text_current.delete(1.0, tk.END)
            self.text_current.insert(tk.END, self.current_text.strip())
            self.text_next.delete(1.0, tk.END)
            self.text_next.insert(tk.END, "(No more lines)")
            return

        line = self.lines[self.line_index]
        percent = int((self.line_index + 1) / len(self.lines) * 100)
        self.label_progress.config(text=f"📄 Line {self.line_index+1} of {len(self.lines)} ({percent}%)")

        self.text_current.delete(1.0, tk.END)
        self.text_current.insert(tk.END, self.current_text.strip())
        self.text_next.delete(1.0, tk.END)
        self.text_next.insert(tk.END, line.strip())

        self.refresh_metadata_preview()
        self.save_session()

    def add_line(self):
        new_text = self.text_next.get("1.0", "end").strip()
        if not new_text:
            messagebox.showwarning("Empty Text", "No text to add.")
            return

        filename = self.get_current_filename()

        # Always read the current visible text from the widget
        existing_text = self.text_current.get("1.0", "end").strip()

        # Append the new line to the visible text
        combined_text = existing_text + " " + new_text if existing_text else new_text
        self.text_current.delete("1.0", "end")
        self.text_current.insert("1.0", combined_text.strip())

        # Sync to internal buffer
        self.current_text = combined_text.strip()

        self.line_count += 1
        self.history.append({"filename": filename, "text": new_text})
        self.line_index += 1
        self.update_display()

    def finalise_file(self):
        manual_text = self.text_current.get("1.0", "end").strip()
        if not manual_text:
            messagebox.showwarning("Empty Text", "No text has been added to this file.")
            return

        filename = self.get_current_filename()
        self.update_metadata_file(filename, manual_text)
        print(f"✅ Accepted: {filename}")

        self.index += 1
        self.current_text = ""
        self.history = []
        self.line_count = 0
        self.update_display()

    def play_audio(self):
        try:
            filename = self.get_current_filename()
            filepath = os.path.join(WAV_DIR, filename)

            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")

            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        except Exception as e:
            messagebox.showerror("Playback Error", f"Could not play audio:\n{e}")

    def update_metadata_file(self, filename, text):
        lines = []
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        updated = False
        for i, line in enumerate(lines):
            if line.startswith(filename + "|"):
                lines[i] = f"{filename}|{text}\n"
                updated = True
                break
        if not updated:
            lines.append(f"{filename}|{text}\n")

        with open(METADATA_FILE, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def save_session(self):
        session = {
            "index": self.index,
            "line_index": self.line_index,
            "current_text": self.current_text,
            "history": self.history,
            "line_count": self.line_count
        }
        with open(SESSION_FILE, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2)

    def load_session(self):
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                session = json.load(f)

            self.index = session.get("index", self.index)
            self.line_index = session.get("line_index", self.line_index)
            self.current_text = session.get("current_text", "")
            self.history = session.get("history", [])
            self.line_count = session.get("line_count", 0)

            print(f"🔁 Resuming from line {self.line_index+1}, record {self.get_current_filename()}")

    def finish(self):
        if self.current_text.strip():
            filename = self.get_current_filename()
            self.update_metadata_file(filename, self.current_text.strip())
            print(f"✅ Final saved: {filename}")

        if self.line_index >= len(self.lines):
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            print("🧹 Session complete — session.json removed.")
        else:
            print("💾 Session saved — resume will be available next time.")

        self.refresh_metadata_preview()
        messagebox.showinfo("Done", f"🎉 Metadata saved to: {METADATA_FILE}")
        self.master.quit()

    def refresh_metadata_preview(self):
        try:
            if not os.path.exists(METADATA_FILE):
                with open(METADATA_FILE, 'w', encoding='utf-8') as f:
                    f.write("")

            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            self.text_log.delete("1.0", "end")
            self.text_log.insert("1.0", content if content else "(metadata.csv is empty)")
            self.text_log.update_idletasks()
            self.text_log.see("end")

        except Exception as e:
            messagebox.showerror("Metadata Error", f"Could not load metadata:\n{e}")

    def load_wav_files(self):
        self.wav_files = sorted([
            f for f in os.listdir(WAV_DIR)
            if f.lower().endswith(".wav")
        ])

    def skip_line(self):
        if self.line_index >= len(self.lines):
            messagebox.showinfo("Done", "No more lines to skip.")
            return

        # Preserve manually entered text before skipping
        self.current_text = self.text_current.get("1.0", "end").strip()

        self.line_index += 1
        self.update_display()

    def open_renamer_window(self):
        renamer = tk.Toplevel(self.master)
        renamer.title("Batch Audio Renamer")
        renamer.geometry("400x250")

        tk.Label(renamer, text="Target Directory:", font=("Verdana", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        dir_var = tk.StringVar(value=WAV_DIR)
        tk.Entry(renamer, textvariable=dir_var, width=40).pack(padx=10)
        tk.Button(renamer, text="Browse", command=lambda: dir_var.set(filedialog.askdirectory())).pack(pady=(0, 10))

        tk.Label(renamer, text="Prefix:", font=("Verdana", 12, "bold")).pack(anchor="w", padx=10)
        prefix_var = tk.StringVar(value="audio_")
        tk.Entry(renamer, textvariable=prefix_var, width=20).pack(padx=10)

        tk.Label(renamer, text="Preview:", font=("Verdana", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        preview_var = tk.StringVar()
        preview = tk.Entry(renamer, state="readonly", width=20, textvariable=preview_var)
        preview.pack(padx=10)

        def update_preview(*_):
            preview_var.set(f"{prefix_var.get()}00001")
        prefix_var.trace_add("write", update_preview)
        update_preview()

        tk.Label(renamer, text="⚠ All files in this directory will be renamed", fg="red", font=("Verdana", 12, "bold")).pack(pady=10)
        tk.Button(renamer, text="Rename All", command=lambda: self.rename_all_audio(dir_var.get(), prefix_var.get())).pack(pady=(0, 10))

    def rename_all_audio(self, directory, prefix):
        files = sorted([f for f in os.listdir(directory) if f.lower().endswith(".wav")])
        rename_map = {}

        for i, filename in enumerate(files, start=1):
            new_name = f"{prefix}{i:05d}.wav"
            src = os.path.join(directory, filename)
            dst = os.path.join(directory, new_name)
            os.rename(src, dst)
            rename_map[filename] = new_name
            print(f"🔄 Renamed: {filename} → {new_name}")

        self.update_metadata_after_rename(rename_map)
        self.update_session_after_rename(rename_map)
        self.load_wav_files()
        self.refresh_metadata_preview()
        self.show_rename_summary(rename_map)
        self.update_display()

    def update_metadata_after_rename(self, rename_map):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            updated_lines = []
            for line in lines:
                if "|" in line:
                    filename, text = line.strip().split("|", 1)
                    new_filename = rename_map.get(filename, filename)
                    updated_lines.append(f"{new_filename}|{text}\n")
                else:
                    updated_lines.append(line)

            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                f.writelines(updated_lines)

            print("✅ metadata.csv updated with new filenames")

        except Exception as e:
            print(f"⚠ Failed to update metadata.csv: {e}")

    def update_session_after_rename(self, rename_map):
        try:
            if not os.path.exists(SESSION_FILE):
                print("⚠ No session file found to update.")
                return

            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                session = json.load(f)

            updated = False
            for entry in session.get("history", []):
                old = entry.get("filename")
                if old and old in rename_map:
                    entry["filename"] = rename_map[old]
                    updated = True

            if updated:
                with open(SESSION_FILE, "w", encoding="utf-8") as f:
                    json.dump(session, f, indent=2)
                print("✅ Session file updated with new filenames")
            else:
                print("ℹ No matching filenames found in session history")

        except Exception as e:
            print(f"⚠ Failed to update session file: {e}")

    def show_rename_summary(self, rename_map):
        popup = tk.Toplevel(self.master)
        popup.title("Rename Complete")
        popup.geometry("350x180")
        popup.resizable(False, False)

        tk.Label(popup, text=f"✅ Renamed {len(rename_map)} files.", font=("Verdana", 11)).pack(pady=(20, 10))
        tk.Label(popup, text="⚠ Undo will restore original filenames", fg="red", font=("Verdana", 12, "bold")).pack()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Undo Rename", command=lambda: self.undo_rename(rename_map), width=15).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Close", command=popup.destroy, width=15).grid(row=0, column=1, padx=10)

    def undo_rename(self, rename_map):
        for old, new in rename_map.items():
            src = os.path.join(WAV_DIR, new)
            dst = os.path.join(WAV_DIR, old)
            if os.path.exists(src):
                os.rename(src, dst)
                print(f"↩ Restored: {new} → {old}")

        self.update_metadata_after_rename({v: k for k, v in rename_map.items()})
        messagebox.showinfo("Undo Complete", "All filenames restored.")
        self.load_wav_files()
        self.update_display()

if __name__ == "__main__":
    subtitle_lines = parse_srt(SRT_FILE)
    root = tk.Tk()
    app = MetadataBuilder(root, subtitle_lines)
    root.mainloop()
#!/usr/bin/env python3
"""
consent_keystroke_logger.py

A safe, consent-first keystroke logger for learning:
- Requires explicit consent phrase "I CONSENT" to start.
- Logs keystrokes only while the app window is open and focused.
- Shows a visible UI with live log.
- Saves to a local file (keystrokes_log.txt) on demand or on exit.

Do NOT use this on machines you don't own or without written permission.
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import os

LOG_FILENAME = "keystrokes_log.txt"
CONSENT_PHRASE = "I CONSENT"

class ConsentLoggerApp:
    def __init__(self, root):
        self.root = root
        root.title("Consent Keystroke Logger (Foreground only)")
        root.geometry("700x420")

        # Consent area
        consent_frame = tk.Frame(root)
        consent_frame.pack(fill="x", padx=8, pady=(8,4))

        tk.Label(consent_frame, text="Type the phrase below to give consent and enable logging:").pack(anchor="w")
        tk.Label(consent_frame, text=f'Consent phrase: "{CONSENT_PHRASE}"', font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.consent_entry = tk.Entry(consent_frame, width=30)
        self.consent_entry.pack(anchor="w", pady=(4,8))
        self.consent_btn = tk.Button(consent_frame, text="Grant Consent", command=self.try_grant_consent)
        self.consent_btn.pack(anchor="w")

        # Info
        self.status_var = tk.StringVar(value="Waiting for consent...")
        tk.Label(root, textvariable=self.status_var, fg="blue").pack(anchor="w", padx=8)

        # Live log display
        self.text = scrolledtext.ScrolledText(root, wrap="word", height=15, state="disabled")
        self.text.pack(fill="both", expand=True, padx=8, pady=6)

        # Controls
        ctrl_frame = tk.Frame(root)
        ctrl_frame.pack(fill="x", padx=8, pady=6)

        self.save_btn = tk.Button(ctrl_frame, text="Save Log to File", command=self.save_log, state="disabled")
        self.save_btn.pack(side="left")
        clear_btn = tk.Button(ctrl_frame, text="Clear Display", command=self.clear_display)
        clear_btn.pack(side="left", padx=(6,0))
        exit_btn = tk.Button(ctrl_frame, text="Exit", command=self.on_exit)
        exit_btn.pack(side="right")

        # State
        self.consent_given = False
        self.log_entries = []

        # Bind only after consent is given (we'll enable binding after)
        root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def try_grant_consent(self):
        text = self.consent_entry.get().strip()
        if text == CONSENT_PHRASE:
            self.give_consent()
        else:
            messagebox.showwarning("Consent required", "You must type the exact consent phrase to enable logging.")

    def give_consent(self):
        self.consent_given = True
        self.status_var.set("Consent given. App will log keystrokes while this window is focused.")
        self.save_btn.config(state="normal")
        self.consent_entry.config(state="disabled")
        self.consent_btn.config(state="disabled")
        # Bind keystrokes to the root window (only active when the window has focus)
        self.root.bind("<Key>", self._on_key)
        self._append_display(f"[{self._now()}] --- Consent granted. Start typing in this window to record keystrokes ---\n")

    def _now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _format_key(self, event):
        # event.char is the printable character (if any)
        # event.keysym is symbolic name (e.g., Return, BackSpace)
        char = event.char
        if char and ord(char) >= 32:  # printable
            return char
        else:
            # Represent control keys in brackets
            return f"[{event.keysym}]"

    def _on_key(self, event):
        if not self.consent_given:
            return  # safety
        key_repr = self._format_key(event)
        entry = f"{self._now()}  {key_repr}"
        self.log_entries.append(entry)
        self._append_display(entry + "\n")

    def _append_display(self, text):
        self.text.config(state="normal")
        self.text.insert("end", text)
        self.text.see("end")
        self.text.config(state="disabled")

    def save_log(self):
        if not self.log_entries:
            messagebox.showinfo("No data", "No keystrokes recorded yet.")
            return
        try:
            with open(LOG_FILENAME, "a", encoding="utf-8") as f:
                f.write("\n".join(self.log_entries) + "\n")
            messagebox.showinfo("Saved", f"Log appended to {os.path.abspath(LOG_FILENAME)}")
            # clear in-memory buffer after save (display remains)
            self.log_entries.clear()
        except Exception as e:
            messagebox.showerror("Error saving", str(e))

    def clear_display(self):
        if messagebox.askyesno("Clear display", "Clear the visible log display? This does not delete saved files."):
            self.text.config(state="normal")
            self.text.delete("1.0", "end")
            self.text.config(state="disabled")

    def on_exit(self):
        if self.log_entries:
            if messagebox.askyesno("Unsaved data", "There are unsaved keystrokes in memory. Save them before exit?"):
                self.save_log()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConsentLoggerApp(root)
    root.mainloop()
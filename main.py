import tkinter as tk
from tkinter import ttk, messagebox
import database
import quiz
import romaji

class NihongoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nihongo JLPT N3 Study App")
        self.root.geometry("600x350")
        database.init_db()
        self.create_widgets()
        self.update_progress()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Input Kata")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Indonesia:").grid(row=0, column=0, padx=5, pady=5)
        self.indonesia_entry = ttk.Entry(input_frame)
        self.indonesia_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Jepang (Hiragana):").grid(row=1, column=0, padx=5, pady=5)
        self.jepang_entry = ttk.Entry(input_frame)
        self.jepang_entry.grid(row=1, column=1, padx=5, pady=5)
        self.jepang_entry.bind("<KeyRelease>", self.generate_romaji)

        ttk.Label(input_frame, text="Kanji (Opsional):").grid(row=2, column=0, padx=5, pady=5)
        self.kanji_entry = ttk.Entry(input_frame)
        self.kanji_entry.grid(row=2, column=1, padx=5, pady=5)
        self.kanji_entry.bind("<KeyRelease>", self.generate_romaji)

        ttk.Label(input_frame, text="Romaji:").grid(row=3, column=0, padx=5, pady=5)
        self.romaji_entry = ttk.Entry(input_frame, state="readonly")
        self.romaji_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(input_frame, text="Simpan", command=self.save_word).grid(row=4, column=1, padx=5, pady=5)

        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Progres JLPT N3 (Target: 3750 Kata)")
        progress_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_label = ttk.Label(progress_frame, text="Progres: 0% (0/3750 kata)")
        self.progress_label.grid(row=0, column=0, padx=5, pady=5)

        # Update Frame
        update_frame = ttk.LabelFrame(self.root, text="Update Kata")
        update_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(update_frame, text="Cari Indonesia:").grid(row=0, column=0, padx=5, pady=5)
        self.update_indonesia_entry = ttk.Entry(update_frame)
        self.update_indonesia_entry.grid(row=0, column=1, padx=5, pady=5)
        self.update_indonesia_entry.bind("<Return>", lambda event: self.search_word())

        ttk.Button(update_frame, text="Cari", command=self.search_word).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(update_frame, text="Clear", command=self.clear_update_entries).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(update_frame, text="Jepang (Hiragana):").grid(row=1, column=0, padx=5, pady=5)
        self.update_jepang_entry = ttk.Entry(update_frame)
        self.update_jepang_entry.grid(row=1, column=1, padx=5, pady=5)
        self.update_jepang_entry.bind("<KeyRelease>", self.update_generate_romaji)

        ttk.Label(update_frame, text="Kanji (Opsional):").grid(row=2, column=0, padx=5, pady=5)
        self.update_kanji_entry = ttk.Entry(update_frame)
        self.update_kanji_entry.grid(row=2, column=1, padx=5, pady=5)
        self.update_kanji_entry.bind("<KeyRelease>", self.update_generate_romaji)

        ttk.Label(update_frame, text="Romaji:").grid(row=3, column=0, padx=5, pady=5)
        self.update_romaji_entry = ttk.Entry(update_frame, state="readonly")
        self.update_romaji_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(update_frame, text="Update", command=self.update_word).grid(row=4, column=1, padx=5, pady=5)

        # Quiz Frame
        quiz_frame = ttk.LabelFrame(self.root, text="Kuis")
        quiz_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(quiz_frame, text="Pilih Kuis:").grid(row=0, column=0, padx=5, pady=5)
        self.quiz_combo = ttk.Combobox(quiz_frame, values=self.get_quiz_options())
        self.quiz_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(quiz_frame, text="Mulai Kuis", command=self.start_quiz).grid(row=0, column=2, padx=5, pady=5)

    def generate_romaji(self, event=None):
        jepang = self.jepang_entry.get()
        kanji = self.kanji_entry.get()
        text_to_convert = kanji if kanji else jepang
        if text_to_convert:
            romaji_text = romaji.convert_to_romaji(text_to_convert)
            self.romaji_entry.config(state="normal")
            self.romaji_entry.delete(0, tk.END)
            self.romaji_entry.insert(0, romaji_text)
            self.romaji_entry.config(state="readonly")

    def update_generate_romaji(self, event=None):
        jepang = self.update_jepang_entry.get()
        kanji = self.update_kanji_entry.get()
        text_to_convert = kanji if kanji else jepang
        if text_to_convert:
            romaji_text = romaji.convert_to_romaji(text_to_convert)
            self.update_romaji_entry.config(state="normal")
            self.update_romaji_entry.delete(0, tk.END)
            self.update_romaji_entry.insert(0, romaji_text)
            self.update_romaji_entry.config(state="readonly")

    def save_word(self):
        indonesia = self.indonesia_entry.get()
        jepang = self.jepang_entry.get()
        kanji = self.kanji_entry.get() or None
        romaji = self.romaji_entry.get()
        if indonesia and jepang and romaji:
            database.add_word(indonesia, jepang, kanji, romaji)
            messagebox.showinfo("Sukses", "Kata berhasil disimpan!")
            self.clear_entries()
            self.update_progress()
            self.quiz_combo.config(values=self.get_quiz_options())
        else:
            messagebox.showerror("Error", "Kolom Indonesia, Jepang, dan Romaji harus diisi!")

    def search_word(self):
        indonesia = self.update_indonesia_entry.get()
        if indonesia:
            word = database.get_word(indonesia)
            if word:
                self.update_jepang_entry.delete(0, tk.END)
                self.update_jepang_entry.insert(0, word[2])
                self.update_kanji_entry.delete(0, tk.END)
                if word[3]:
                    self.update_kanji_entry.insert(0, word[3])
                self.update_romaji_entry.config(state="normal")
                self.update_romaji_entry.delete(0, tk.END)
                self.update_romaji_entry.insert(0, word[4])
                self.update_romaji_entry.config(state="readonly")
            else:
                messagebox.showerror("Error", "Kata tidak ditemukan!")
        else:
            messagebox.showerror("Error", "Masukkan kata Indonesia untuk dicari!")

    def update_word(self):
        indonesia = self.update_indonesia_entry.get()
        jepang = self.update_jepang_entry.get()
        kanji = self.update_kanji_entry.get() or None
        romaji = self.update_romaji_entry.get()
        if indonesia and jepang and romaji:
            database.update_word(indonesia, jepang, kanji, romaji)
            messagebox.showinfo("Sukses", "Kata berhasil diupdate!")
            self.clear_update_entries()
            self.update_progress()
            self.quiz_combo.config(values=self.get_quiz_options())
        else:
            messagebox.showerror("Error", "Kolom Indonesia, Jepang, dan Romaji harus diisi!")

    def clear_entries(self):
        self.indonesia_entry.delete(0, tk.END)
        self.jepang_entry.delete(0, tk.END)
        self.kanji_entry.delete(0, tk.END)
        self.romaji_entry.config(state="normal")
        self.romaji_entry.delete(0, tk.END)
        self.romaji_entry.config(state="readonly")

    def clear_update_entries(self):
        self.update_indonesia_entry.delete(0, tk.END)
        self.update_jepang_entry.delete(0, tk.END)
        self.update_kanji_entry.delete(0, tk.END)
        self.update_romaji_entry.config(state="normal")
        self.update_romaji_entry.delete(0, tk.END)
        self.update_romaji_entry.config(state="readonly")

    def update_progress(self):
        word_count = database.get_word_count()
        progress = (word_count / 3750) * 100
        self.progress_label.config(text=f"Progres: {progress:.2f}% ({word_count}/3750 kata)")

    def get_quiz_options(self):
        word_count = database.get_word_count()
        quiz_count = (word_count // 50) + (1 if word_count % 50 > 0 else 0)
        return [f"Kuis {i+1} ({i*50+1}-{(i+1)*50})" for i in range(quiz_count)]

    def start_quiz(self):
        quiz_selection = self.quiz_combo.get()
        if quiz_selection:
            quiz_number = int(quiz_selection.split()[1])
            quiz.start_quiz(quiz_number)
        else:
            messagebox.showerror("Error", "Pilih kuis terlebih dahulu!")

if __name__ == "__main__":
    root = tk.Tk()
    app = NihongoApp(root)
    root.mainloop()
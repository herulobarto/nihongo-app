import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import database
import quiz
import romaji
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NihongoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nihongo JLPT N3 Study App")
        self.root.geometry("800x600")
        database.init_db()
        self.current_page = 1
        self.csv_file_path = None
        self.create_widgets()
        self.update_progress()

    def create_widgets(self):
        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="Main")

        input_frame = ttk.LabelFrame(main_tab, text="Input Kata")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

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

        csv_frame = ttk.LabelFrame(main_tab, text="Impor dari CSV")
        csv_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        ttk.Label(csv_frame, text="File CSV:").grid(row=0, column=0, padx=5, pady=5)
        self.csv_path_label = ttk.Label(csv_frame, text="Belum ada file dipilih", wraplength=200)
        self.csv_path_label.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        ttk.Button(csv_frame, text="Pilih File CSV", command=self.choose_csv_file).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(csv_frame, text="Contoh Format CSV", command=self.show_csv_format).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(csv_frame, text="Impor", command=self.import_csv).grid(row=2, column=0, padx=5, pady=5)

        progress_frame = ttk.LabelFrame(main_tab, text="Progres JLPT N3 (Target: 3750 Kata)")
        progress_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.progress_label = ttk.Label(progress_frame, text="Progres: 0% (0/3750 kata)")
        self.progress_label.grid(row=0, column=0, padx=5, pady=5)

        update_frame = ttk.LabelFrame(main_tab, text="Update Kata")
        update_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

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
        self.delete_button = ttk.Button(update_frame, text="Hapus", command=self.delete_word, state="disabled")
        self.delete_button.grid(row=4, column=2, padx=5, pady=5)

        view_tab = ttk.Frame(notebook)
        notebook.add(view_tab, text="Lihat Kata")

        view_frame = ttk.LabelFrame(view_tab, text="Lihat Kata (25 per Halaman)")
        view_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(view_frame, columns=("Indonesia", "Jepang", "Kanji", "Romaji"), show="headings", height=25)
        self.tree.heading("Indonesia", text="Indonesia")
        self.tree.heading("Jepang", text="Jepang")
        self.tree.heading("Kanji", text="Kanji")
        self.tree.heading("Romaji", text="Romaji")
        self.tree.column("Indonesia", width=200)
        self.tree.column("Jepang", width=150)
        self.tree.column("Kanji", width=150)
        self.tree.column("Romaji", width=200)
        self.tree.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        self.page_label = ttk.Label(view_frame, text="Page 1 of 1")
        self.page_label.grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(view_frame, text="Previous", command=self.prev_page).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(view_frame, text="Next", command=self.next_page).grid(row=1, column=2, padx=5, pady=5)

        self.refresh_words()

        quiz_tab = ttk.Frame(notebook)
        notebook.add(quiz_tab, text="Kuis")

        quiz_frame = ttk.LabelFrame(quiz_tab, text="Kuis (25 Kata per Kuis)")
        quiz_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(quiz_frame, text="Pilih Kuis:").grid(row=0, column=0, padx=5, pady=5)
        self.quiz_combo = ttk.Combobox(quiz_frame, values=self.get_quiz_options())
        self.quiz_combo.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(quiz_frame, text="Mulai Kuis", command=self.start_quiz).grid(row=0, column=2, padx=5, pady=5)

    def show_csv_format(self):
        example = (
            "Format CSV yang diharapkan:\n\n"
            "indonesia,jepang,kanji,romaji\n"
            "rumah,うち,家,uchi\n"
            "mobil,くるま,車,kuruma\n"
            "buku,ほん,,hon\n"
            "air,みず,,mizu\n\n"
            "Catatan:\n"
            "- Kolom wajib: indonesia, jepang, romaji\n"
            "- Kolom kanji opsional (kosongkan jika tidak ada)\n"
            "- Romaji akan diisi otomatis jika kosong"
        )
        messagebox.showinfo("Contoh Format CSV", example)

    def choose_csv_file(self):
        self.csv_file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if self.csv_file_path:
            self.csv_path_label.config(text=self.csv_file_path.split("/")[-1])
            logging.debug(f"File CSV dipilih: {self.csv_file_path}")
        else:
            self.csv_path_label.config(text="Belum ada file dipilih")

    def import_csv(self):
        if not self.csv_file_path:
            messagebox.showerror("Error", "Pilih file CSV terlebih dahulu!")
            return
        logging.debug(f"Mengimpor file CSV: {self.csv_file_path}")
        try:
            df = pd.read_csv(self.csv_file_path, encoding='utf-8')
            logging.debug(f"CSV dibaca: {df.shape[0]} baris, kolom: {df.columns.tolist()}")
            required_columns = ["indonesia", "jepang", "romaji"]
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Error", "File CSV harus memiliki kolom: indonesia, jepang, romaji!")
                return
            words = []
            for index, row in df.iterrows():
                indonesia = str(row["indonesia"]).strip() if not pd.isna(row["indonesia"]) else ""
                jepang = str(row["jepang"]).strip() if not pd.isna(row["jepang"]) else ""
                kanji = str(row.get("kanji", "")).strip() if not pd.isna(row.get("kanji", "")) else None
                romaji_text = str(row["romaji"]).strip() if not pd.isna(row["romaji"]) else ""
                logging.debug(f"Baris {index}: indonesia={indonesia}, jepang={jepang}, kanji={kanji}, romaji={romaji_text}")
                if not romaji_text:
                    text_to_convert = kanji if kanji else jepang
                    if text_to_convert:
                        romaji_text = romaji.convert_to_romaji(text_to_convert)
                        logging.debug(f"Romaji dihasilkan: {romaji_text}")
                if indonesia and jepang and romaji_text:
                    words.append((indonesia, jepang, kanji, romaji_text))
                else:
                    messagebox.showwarning("Peringatan", f"Baris {index+2} dengan indonesia '{indonesia}' diabaikan karena data tidak lengkap!")
            if words:
                try:
                    database.add_words_batch(words)
                    messagebox.showinfo("Sukses", f"{len(words)} kata berhasil diimpor!")
                    self.csv_file_path = None
                    self.csv_path_label.config(text="Belum ada file dipilih")
                    self.update_progress()
                    self.refresh_words()
                    self.quiz_combo.config(values=self.get_quiz_options())
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mengimpor: {str(e)}")
            else:
                messagebox.showerror("Error", "Tidak ada data valid untuk diimpor!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file CSV: {str(e)}")
            logging.error(f"Error membaca CSV: {str(e)}")

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
            try:
                database.add_word(indonesia, jepang, kanji, romaji)
                messagebox.showinfo("Sukses", "Kata berhasil disimpan!")
                self.clear_entries()
                self.update_progress()
                self.refresh_words()
                self.quiz_combo.config(values=self.get_quiz_options())
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Kata Indonesia sudah ada di database!")
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
                self.delete_button.config(state="normal")
            else:
                messagebox.showerror("Error", "Kata tidak ditemukan!")
                self.delete_button.config(state="disabled")
        else:
            messagebox.showerror("Error", "Masukkan kata Indonesia untuk dicari!")
            self.delete_button.config(state="disabled")

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
            self.refresh_words()
            self.quiz_combo.config(values=self.get_quiz_options())
            self.delete_button.config(state="disabled")
        else:
            messagebox.showerror("Error", "Kolom Indonesia, Jepang, dan Romaji harus diisi!")

    def delete_word(self):
        indonesia = self.update_indonesia_entry.get()
        if indonesia and messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus kata '{indonesia}'?"):
            database.delete_word(indonesia)
            messagebox.showinfo("Sukses", "Kata berhasil dihapus!")
            self.clear_update_entries()
            self.update_progress()
            self.refresh_words()
            self.quiz_combo.config(values=self.get_quiz_options())
            self.delete_button.config(state="disabled")

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
        self.delete_button.config(state="disabled")

    def update_progress(self):
        word_count = database.get_word_count()
        progress = (word_count / 3750) * 100
        self.progress_label.config(text=f"Progres: {progress:.2f}% ({word_count}/3750 kata)")

    def get_quiz_options(self):
        word_count = database.get_word_count()
        quiz_count = (word_count // 25) + (1 if word_count % 25 > 0 else 0)
        return [f"Kuis {i+1} ({i*25+1}-{(i+1)*25})" for i in range(quiz_count)]

    def start_quiz(self):
        quiz_selection = self.quiz_combo.get()
        if quiz_selection:
            quiz_number = int(quiz_selection.split()[1])
            quiz.start_quiz(quiz_number)
        else:
            messagebox.showerror("Error", "Pilih kuis terlebih dahulu!")

    def refresh_words(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        words = database.get_words_by_oldest(self.current_page)
        for word in words:
            self.tree.insert("", "end", values=(word[1], word[2], word[3] or "", word[4]))
        total_pages = database.get_total_pages()
        self.page_label.config(text=f"Page {self.current_page} of {total_pages}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_words()

    def next_page(self):
        total_pages = database.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_words()

if __name__ == "__main__":
    root = tk.Tk()
    app = NihongoApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox
import random
import database

class QuizWindow:
    def __init__(self, quiz_number):
        self.quiz_number = quiz_number
        self.words = database.get_words_for_quiz(quiz_number)
        random.shuffle(self.words)
        self.current_question = 0
        self.score = 0
        self.correct_answer = None

        self.window = tk.Toplevel()
        self.window.title(f"Kuis {quiz_number}")
        self.window.geometry("400x300")

        self.question_label = ttk.Label(self.window, text="")
        self.question_label.pack(pady=10)

        self.radio_var = tk.StringVar()
        self.options = []
        for i in range(4):
            rb = ttk.Radiobutton(self.window, text="", variable=self.radio_var, value="")
            rb.pack(anchor="w", padx=20)
            self.options.append(rb)

        ttk.Button(self.window, text="Submit", command=self.check_answer).pack(pady=10)
        self.next_question()

    def next_question(self):
        if self.current_question < len(self.words):
            self.correct_answer = self.words[self.current_question][1]
            self.question_label.config(text=f"Apa arti dari '{self.words[self.current_question][0]}'?")
            options = [self.correct_answer]
            while len(options) < 4:
                random_word = random.choice(self.words)[1]
                if random_word not in options:
                    options.append(random_word)
            random.shuffle(options)
            for i, option in enumerate(options):
                self.options[i].config(text=option, value=option)
            self.radio_var.set("")
        else:
            messagebox.showinfo("Selesai", f"Skor Anda: {self.score}/{len(self.words)}")
            self.window.destroy()

    def check_answer(self):
        if self.radio_var.get() == self.correct_answer:
            self.score += 1
        self.current_question += 1
        self.next_question()

def start_quiz(quiz_number):
    if not database.get_words_for_quiz(quiz_number):
        messagebox.showerror("Error", "Tidak ada kata untuk kuis ini!")
    else:
        QuizWindow(quiz_number)
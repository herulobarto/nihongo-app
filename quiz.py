import tkinter as tk
from tkinter import ttk, messagebox
import database
import random

class QuizWindow:
    def __init__(self, quiz_number):
        self.quiz_window = tk.Toplevel()
        self.quiz_window.title(f"Kuis {quiz_number}")
        # Set window size
        window_width = 600
        window_height = 400
        # Get screen dimensions
        screen_width = self.quiz_window.winfo_screenwidth()
        screen_height = self.quiz_window.winfo_screenheight()
        # Calculate center position
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        # Set window geometry
        self.quiz_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.quiz_number = quiz_number
        self.words = database.get_words_for_quiz(quiz_number)
        # Randomize the order of questions
        random.shuffle(self.words)
        self.current_question = 0
        self.score = 0
        self.wrong_answers = []
        self.correct_answers = [word[2] for word in self.words]  # Jepang (hiragana) as correct answers
        self.create_widgets()
        self.show_question()
        self.quiz_window.bind('<Key>', self.handle_key)
        self.quiz_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.question_label = ttk.Label(self.quiz_window, text="", font=("Arial", 14), wraplength=500, anchor="center")
        self.question_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.option_buttons = []
        for i in range(4):
            btn = ttk.Button(self.quiz_window, text="", command=lambda x=i: self.check_answer(x))
            btn.grid(row=i+1, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
            self.option_buttons.append(btn)

        self.feedback_label = ttk.Label(self.quiz_window, text="", font=("Arial", 12))
        self.feedback_label.grid(row=5, column=0, columnspan=4, padx=10, pady=10)

        ttk.Button(self.quiz_window, text="Previous", command=self.prev_question).grid(row=6, column=0, padx=10, pady=10)
        ttk.Button(self.quiz_window, text="Next", command=self.next_question).grid(row=6, column=3, padx=10, pady=10)

    def show_question(self):
        if self.current_question < len(self.words):
            word = self.words[self.current_question]
            self.question_label.config(text=f"Apa terjemahan dari '{word[1]}'?")
            options = [word[2]]  # Correct answer (jepang/hiragana)
            other_words = [w[2] for w in self.words if w[2] != word[2]]
            options.extend(random.sample(other_words, min(3, len(other_words))))
            random.shuffle(options)
            self.current_options = options
            for i, opt in enumerate(options):
                self.option_buttons[i].config(text=f"{chr(97+i)}. {opt}")
            self.feedback_label.config(text="")
        else:
            self.end_quiz()

    def check_answer(self, option_index):
        selected_answer = self.current_options[option_index]
        correct_answer = self.correct_answers[self.current_question]
        if selected_answer == correct_answer:
            self.feedback_label.config(text="Benar!")
            if self.current_question not in [wa[0] for wa in self.wrong_answers]:
                self.score += 1
        else:
            self.feedback_label.config(text=f"Salah! Jawaban benar adalah: {chr(97 + self.current_options.index(correct_answer))}")
            if self.current_question not in [wa[0] for wa in self.wrong_answers]:
                self.wrong_answers.append((self.current_question, option_index, self.current_options.index(correct_answer)))
        self.quiz_window.focus_set()

    def handle_key(self, event):
        if event.char in ['a', 'b', 'c', 'd']:
            option_index = ord(event.char) - ord('a')
            if option_index < len(self.current_options):
                self.check_answer(option_index)
        elif event.keysym == 'Left':
            self.prev_question()
        elif event.keysym == 'Right':
            self.next_question()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def next_question(self):
        if self.current_question < len(self.words) - 1:
            self.current_question += 1
            self.show_question()
        else:
            self.end_quiz()

    def end_quiz(self):
        self.quiz_window.unbind('<Key>')
        self.question_label.config(text=f"Kuis Selesai! Skor Anda: {self.score}/{len(self.words)}")
        for btn in self.option_buttons:
            btn.config(state="disabled")
        if self.wrong_answers:
            self.show_wrong_answers()
        else:
            self.feedback_label.config(text="Semua jawaban benar!")

    def show_wrong_answers(self):
        wrong_window = tk.Toplevel(self.quiz_window)
        wrong_window.title("Jawaban Salah")
        # Center the wrong answers window
        window_width = 600
        window_height = 400
        screen_width = wrong_window.winfo_screenwidth()
        screen_height = wrong_window.winfo_screenheight()
        x = int((screen_width - window_width) / 2)
        y = int((screen_height - window_height) / 2)
        wrong_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Frame to hold text and scrollbar
        frame = ttk.Frame(wrong_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        # Text widget with scrollbar
        text = tk.Text(frame, height=20, width=60, yscrollcommand=scrollbar.set, wrap="word")
        text.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=text.yview)

        for q_idx, selected, correct in self.wrong_answers:
            word = self.words[q_idx]
            text.insert(tk.END, f"Kata: {word[1]}\n")
            text.insert(tk.END, f"Jawaban Anda: {chr(97+selected)}. {self.current_options[selected]}\n")
            text.insert(tk.END, f"Jawaban Benar: {chr(97+correct)}. {self.correct_answers[q_idx]}\n\n")
        text.config(state="disabled")


    def on_closing(self):
        self.quiz_window.destroy()

def start_quiz(quiz_number):
    QuizWindow(quiz_number)
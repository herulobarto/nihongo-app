import sqlite3

def init_db():
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indonesia TEXT NOT NULL UNIQUE,
            jepang TEXT NOT NULL,
            kanji TEXT,
            romaji TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_word(indonesia, jepang, kanji, romaji):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO words (indonesia, jepang, kanji, romaji) VALUES (?, ?, ?, ?)',
                   (indonesia, jepang, kanji, romaji))
    conn.commit()
    conn.close()

def add_words_batch(words):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.executemany('INSERT INTO words (indonesia, jepang, kanji, romaji) VALUES (?, ?, ?, ?)', words)
    conn.commit()
    conn.close()

def get_word(indonesia):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM words WHERE indonesia = ?', (indonesia,))
    word = cursor.fetchone()
    conn.close()
    return word

def update_word(indonesia, jepang, kanji, romaji):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE words SET jepang = ?, kanji = ?, romaji = ? WHERE indonesia = ?',
                   (jepang, kanji, romaji, indonesia))
    conn.commit()
    conn.close()

def delete_word(indonesia):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM words WHERE indonesia = ?', (indonesia,))
    conn.commit()
    conn.close()

def get_words_by_oldest(page):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words ORDER BY id ASC LIMIT 25 OFFSET ?", ((page - 1) * 25,))
    words = cursor.fetchall()
    conn.close()
    return words

def get_total_pages():
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    conn.close()
    return (count // 25) + (1 if count % 25 > 0 else 0)

def get_word_count():
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM words")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_words_for_quiz(quiz_number):
    conn = sqlite3.connect('nihongo.db')
    cursor = conn.cursor()
    offset = (quiz_number - 1) * 25
    cursor.execute("SELECT * FROM words LIMIT 25 OFFSET ?", (offset,))
    words = cursor.fetchall()
    conn.close()
    return words
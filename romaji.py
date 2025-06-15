from pykakasi import kakasi

def convert_to_romaji(jepang):
    kks = kakasi()
    kks.setMode("H", "a")  # Hiragana to ascii
    kks.setMode("K", "a")  # Katakana to ascii
    kks.setMode("J", "a")  # Kanji to ascii
    conv = kks.getConverter()
    return conv.do(jepang)
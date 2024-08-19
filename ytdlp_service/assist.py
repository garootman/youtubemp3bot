import uuid


def new_id(l=20, first_letter=True):
    # l must me int betweel 8 and 32
    l = int(l)
    l = max(8, min(32, l))
    s = str(uuid.uuid4())
    s = s.replace("-", "")
    if first_letter:
        random_letter = chr(65 + (ord(s[0]) % 26))
        s = random_letter + s[1:]
    s = s.lower()
    return s[:l]

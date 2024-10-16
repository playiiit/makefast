import os


def table_name_generator(word):
    # Special cases
    irregular_nouns = {
        'child': 'children',
        'goose': 'geese',
        'man': 'men',
        'woman': 'women',
        'tooth': 'teeth',
        'foot': 'feet',
        'mouse': 'mice',
        'person': 'people'
    }

    # Check for irregular nouns
    if word.lower() in irregular_nouns:
        return irregular_nouns[word.lower()]

    # Rules for converting singular to plural
    if word.endswith('y'):
        # If word ends with 'y' preceded by a consonant, change 'y' to 'ies'
        if word[-2] not in 'aeiou':
            return word[:-1] + 'ies'
    elif word.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return word + 'es'
    elif word.endswith('f'):
        return word[:-1] + 'ves'
    elif word.endswith('fe'):
        return word[:-2] + 'ves'
    elif word.endswith('o'):
        # Some words ending in 'o' add 'es', but it's not a universal rule
        if word.lower() in ['hero', 'potato', 'tomato']:
            return word + 'es'

    # Default case: add 's'
    return word + 's'


def update_init_file(file_path, statement):
    if os.path.exists(file_path):
        with open(file_path, "r+") as f:
            content = f.read()
            if statement not in content:
                f.seek(0, 0)
                f.write(statement + content)
    else:
        with open(file_path, "w") as f:
            f.write(statement)

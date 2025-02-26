import os
import re


def table_name_generator(word):
    """
    Generates a pluralized version of the given word based on English pluralization rules.

    Parameters:
        word (str): The singular word to be converted to its plural form.

    Returns:
        str: The plural form of the input word, accounting for irregular and regular pluralization rules.
    """
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
    """
    Updates the specified file by adding a statement at the beginning if it does not already exist in the file.

    Parameters:
        file_path (str): The path to the file to be updated.
        statement (str): The statement to be added at the beginning of the file.

    Returns:
        None
    """
    if os.path.exists(file_path):
        with open(file_path, "r+") as f:
            content = f.read()
            if statement not in content:
                f.seek(0, 0)
                f.write(statement + content)
    else:
        with open(file_path, "w") as f:
            f.write(statement)


def generate_class_name(input_string):
    """
    Converts a user-provided string into a 'UserList' format.

    Parameters:
    input_string (str): The input string to be converted.

    Returns:
    str: The input string converted to 'UserList' format.
    """
    # Split the input by space, underscore, or dash and capitalize each part
    words = re.split(r'[ _-]+', input_string)
    # Capitalize the first letter of each word and join them
    return ''.join(word.capitalize() for word in words)


def convert_to_snake_case(input_string):
    """
    Converts a string to snake case, handling camelCase, PascalCase, spaces, and hyphens.

    Parameters:
    input_string (str): The string to be converted.

    Returns:
    str: The string in snake case.
    """
    # Add underscore before any uppercase letter
    result = ""
    for i, char in enumerate(input_string):
        if char.isupper() and i > 0:
            result += "_" + char.lower()
        else:
            result += char.lower()

    # Replace spaces and hyphens with underscores
    result = result.replace(" ", "_").replace("-", "_")

    # Remove any consecutive underscores and trim
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip("_")

    return result


def convert_to_hyphen(input_str):
    """
    Converts a string with spaces or underscores to a hyphen-separated format.

    Parameters:
        input_str (str): The input string to be converted.

    Returns:
        str: The converted string with spaces and underscores replaced by hyphens.
    """
    return input_str.replace(" ", "-").replace("_", "-")

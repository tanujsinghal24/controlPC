from Utitlities.ocr.ocr import do_processing, initOcr
import multiprocessing
from nltk.corpus import wordnet
import nltk
from spellchecker import SpellChecker
import re
nltk.download('wordnet')
print(nltk.data.path)

def get_top_definitions(word, num_definitions=3):
    synsets = wordnet.synsets(word)
    if not synsets:
        return None

    meanings = []
    for synset in synsets[:num_definitions]:
        meanings.append(synset.definition())
    print("\n".join(meanings))
    return "\n".join(meanings)


def get_conversational_definition(word):
    synsets = wordnet.synsets(word)
    if not synsets:
        return None

    definitions = []
    for synset in synsets[:3]:  # Limit to top 3 definitions
        definition = synset.definition()
        examples = synset.examples()
        synonyms = [lemma.name() for lemma in synset.lemmas()][:5]  # Limit to top 5 synonyms

        formatted_definition = f"{definition.capitalize()}."
        if examples:
            formatted_definition += f" For instance, '{examples[0]}'."
        if synonyms:
            formatted_definition += f" Similar words include: {', '.join(synonyms)}."

        definitions.append(formatted_definition)

    return definitions


def getSymanticMeaning(text):
    word = text
    definitions = get_conversational_definition(word)

    if definitions:
        print(f"Here are some definitions for the word '{word}':")
        for i, definition in enumerate(definitions, 1):
            print(f"{i}. {definition}")
    else:
        print(f"Sorry, I couldn't understand the word '{word}'....looks like i need to read more.")


# Initialize spell checker
spell = SpellChecker()


def correct_spelling(word):
    # Correct the word if it's misspelled
    corrected = spell.correction(word)
    return corrected

def clean_input(input_string):
    # Remove unwanted characters and split words
    cleaned_words = re.findall(r'\b\w+\b', input_string)
    return cleaned_words

def get_conversational_definition(word):
    synsets = wordnet.synsets(word)
    if not synsets:
        return None

    definitions = []
    for synset in synsets[:3]:  # Limit to top 3 definitions
        definition = synset.definition()
        examples = synset.examples()
        synonyms = [lemma.name() for lemma in synset.lemmas()][:5]  # Limit to top 5 synonyms

        formatted_definition = f"{definition.capitalize()}."
        if examples:
            formatted_definition += f" For instance, '{examples[0]}'."
        if synonyms:
            formatted_definition += f" Similar words include: {', '.join(synonyms)}."

        definitions.append(formatted_definition)

    return definitions


def gestbest(text):
    # words = text.split(" ")
    words = clean_input(text)
    all_definitions = []
    print(words)
    for word in words:
        if not word:
            continue
        corrected_word = correct_spelling(word)
        print(corrected_word)
        # print(word)
        if not corrected_word or corrected_word == 'None':
            continue
        if corrected_word != word:
            print(f"Did you mean '{corrected_word}' instead of '{word}'?")

        definitions = get_conversational_definition(corrected_word)
        if definitions:
            if corrected_word != word:
                all_definitions.append(f"Did you mean '{corrected_word}' instead of '{word}'?")
            for i, definition in enumerate(definitions, 1):
                all_definitions.append(f"{corrected_word}: {definition}")
        else:
            print(f"Sorry, I couldn't find any definitions for the word '{corrected_word}'.")
    if all_definitions:
    #     for definition in all_definitions:
    #         print(definition)
        return "\n".join(all_definitions)
    else:
        return f"Sorry, I couldn't find any robust to explain for the word '{corrected_word}'."


def ocr_thread_func(ocrQueue, ui_queue):
    print("OCR Thread begin")
    initOcr()
    print("OCR init done")
    while True:
        event = ocrQueue.get_event()
        eventType, arg = event
        print(event)
        if eventType == "QUIT":
            break
        elif eventType == "POS":
            word, center = do_processing(arg)
            print("meaning:")
            if word:
                text, prob, bbox = word
                print("meaning:")
                meaning = gestbest(text)
                print(meaning)
                print(f"got word {word} in thread")
                ui_queue.put(("OCR_RES", (meaning, center)))
# initOcr()
# print(gestbest("bloody hellp"))

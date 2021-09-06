import re
import os
import json
import nltk.data

import modules.my_classes as my_class
import modules.my_functions as my_function


def import_fct(INPUT_FILE):
    directory = os.getcwd()
    input_path = directory + "\\Input\\" + INPUT_FILE
    with open(input_path, 'r') as f:
        raw_text = f.read().strip()
        f.close()
    return raw_text


def clean_text(raw_text):                               # turning all apostrophes into "
    apostrophe1 = " `"
    apostrophe2 = "' "
    apostrophe3 = "'\n"
    temp_text = re.sub(apostrophe1, ' "', raw_text)
    temp2_text = re.sub(apostrophe2, '" ', temp_text)
    temp3_text = re.sub(apostrophe3, '"\n', temp2_text)
    clean_text = temp3_text.strip()
    return clean_text


def text2list(text_string):                             # text string gets split at every position of "
    voices_list = []
    num1 = text_string.find('"')
    if num1 == -1:                                      # no " found
        voices_list.append(text_string)
    else:
        counter = 1
        voices_list.append(text_string[:num1])          # if text appears before "
        finished = False
        while not finished:
            if text_string[num1 + 1:].find('"') == -1:
                num2 = len(text_string)
            else:
                num2 = num1 + text_string[num1 + 1:].find('"')
            voices_list.append(text_string[num1 + (counter + 1) % 2: num2 + 2 * (counter % 2)])         # depending on counter if " is included to sentence (which is wanted every odd ")
            if num2 >= len(text_string):
                finished = True
            num1 = num2 + 1
            counter += 1
    # clean voice_parts
    for i, voice_part in enumerate(voices_list):
        if len(voice_part) <= 1:
            voices_list.remove(voices_list[i])
    for i, voice_part in enumerate(voices_list):
        temp_text = re.sub(r'\n\n', '<p-end-stop>', voice_part)
        temp2_text = re.sub(r'\n', ' ', temp_text)
        temp3_text = re.sub('<p-end-stop>', ' \n\n ', temp2_text)
        voices_list[i] = temp3_text.strip()
    return voices_list


def voices2objs(voice_parts_list):
    # transform strings to Voice-objects
    voices_objs = []
    for i, voice_string in enumerate(voice_parts_list):
        voices_objs.append(my_class.Voice(i, voice_string))
    # add sentences_list to Voice-objects
    sentence_id_counter = 0
    for i, voice in enumerate(voices_objs):
        temp1_sentences = voice.text.split("\n\n")
        temp2_sentences = []
        for paragraph in temp1_sentences:
            temp2_sentences.append(nltk.sent_tokenize(paragraph))            # very helpful module for splitting sentences (but sadly doesnt split \n\n)
        temp_sentence_objects = []
        for sentence in temp2_sentences:
            temp_sentence_objects.append(my_class.Sentence(sentence_id_counter, sentence))
            sentence_id_counter += 1
        voice.sentences_list.append(temp_sentence_objects)
    return voices_objs


def output_voices_JSON(voice_objs, file_name):
    json_list = []
    for voice_part in voice_objs:
        for sentence_list in voice_part.sentences_list:
            temp_sentence_list = []
            temp_emotions_list = []
            for sentence in sentence_list:
                temp_sentence_list.append(sentence.text)
                temp_emotions_list.append(sentence.emotion)
            json_list.append({
                'Voice-Part ID': voice_part.id,
                'Chapter': voice_part.chapter,
                'Character': voice_part.character,
                'Sentences': temp_sentence_list,
                'Emotion per Sentence': temp_emotions_list                  # speed might be another useful attribute?
            })
    output_path = os.getcwd() + r"\Output\\"
    output_name = output_path + file_name[:-4] + ".json"
    with open(output_name, 'w') as json_file:
        json.dump(json_list, json_file, indent=4)

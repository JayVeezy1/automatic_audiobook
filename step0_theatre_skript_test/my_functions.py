import re
import os
import json
import nltk.data
import io
import re
import sys
import shutil
import itertools
import functools
import operator

import my_classes
import PRIVATE.my_authentification as my_authentification               # You need to set up your own authentification-details

from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def import_fct(input_file):
    directory = os.getcwd()
    input_path = directory + "\\Input\\" + input_file
    with open(input_path, 'r', encoding="utf-8") as f:
        raw_text = f.read().strip()
        f.close()
    return raw_text


def output_script_JSON(final_voice_objs, file_name):
    json_list = []
    for v in final_voice_objs:
        for i in range(0, len(v.sentences_list)):
            json_list.append({
                'chapter': v.sentences_list[i].chapter,
                'voice_part_id': v.id,
                'sentence_id': v.sentences_list[i].id,
                'character': v.sentences_list[i].character,
                'finalVoice': v.sentences_list[i].finalVoice,
                'text': v.sentences_list[i].text,
                'emotion_per_sentence': v.sentences_list[i].emotion,
                'speed': v.sentences_list[i].speed
            })
    output_path = os.getcwd() + r"\Output\\"
    output_name = output_path + file_name[:-4] + ".json"
    with open(output_name, 'w') as json_file:
        json.dump(json_list, json_file, indent=4)


def lines2objs(input_lines):
    voice_objs = []
    counter = 0
    for i, line in enumerate(input_lines):
        if len(line) > 1:
            voice_objs.append(my_classes.InitVoicePart(voice_id=counter, text=line))
            counter += 1
    for voice in voice_objs:
        line = voice.text
        if line[0] == "[" and line[-1] == "]":
            voice.initCharacter = "0_scene_change"
        elif line[0] == "(" and line[-1] == ")":
            voice.initCharacter = "0_direction"
        else:
            voice.initCharacter = "0_Narrator"
        if "date:" in line:
            pass
        elif ":" in line:
            temp_line = line.split(": ")
            voice.initCharacter = temp_line[0]
            voice.text = temp_line[1]
    return voice_objs


def add_sentences2voices(voice_objs):
    temp_sentences = []
    for voice in voice_objs:
        if "." or "?" or "!" in voice.text:
            temp_sentences.extend(nltk.sent_tokenize(voice.text))
        else:
            temp_sentences.extend(voice.text)
        temp_sentences.append("# end of voice-part #")
    # transform sentences into objects, split at (), and add metaVoice depending on content
    sentence_objects = []
    sentence_id_counter = 0
    for sentence in temp_sentences:
        if "(" in sentence and ")" in sentence:
            temp_s1 = sentence[sentence.index("("):sentence.index(")") + 1]
            if not "unintelligible" in sentence:
                sentence_objects.append(my_classes.Sentence(sentence_id=sentence_id_counter,
                                                            text=temp_s1, metaVoice="direction"))
            else:
                sentence_objects.append(my_classes.Sentence(sentence_id=sentence_id_counter,
                                                            text=temp_s1, metaVoice="unintelligible"))
            if len(sentence[sentence.index(")") + 1:]) > 1:
                temp_s2 = sentence[sentence.index(")") + 1:]
                sentence_id_counter += 1
                sentence_objects.append(
                    my_classes.Sentence(sentence_id=sentence_id_counter, text=temp_s2, metaVoice="-"))
        elif "# end of voice-part #" in sentence:
            sentence_objects.append("# end of voice-part #")
        else:
            sentence_objects.append(my_classes.Sentence(sentence_id=sentence_id_counter, text=sentence, metaVoice="-"))
        sentence_id_counter += 1
    # fill v.sentence_list with correct sentence objs
    old_pos = 0
    for v in voice_objs:
        new_pos = old_pos + sentence_objects[old_pos:].index("# end of voice-part #")
        distance = new_pos - old_pos
        for i in range(0, distance):
            v.sentences_list.append(sentence_objects[old_pos + i])
        old_pos = new_pos + 1
    for sentence in sentence_objects:
        if sentence == "# end of voice-part #":
            sentence_objects.remove(sentence)
    # Give each sentence its correct character
    for v in voice_objs:
        for i in range(0, len(v.sentences_list)):
            if v.sentences_list[i].metaVoice == "-":
                v.sentences_list[i].character = v.initCharacter
            elif "unintelligible" in v.sentences_list[i].metaVoice:
                v.sentences_list[i].character = v.initCharacter + " " + "(unintelligible)"
            else:
                v.sentences_list[i].character = v.sentences_list[i].metaVoice
    # Give Sentences responding Chapters - only if chapter is identified by [ ]
    chapter_counter = 0
    for s in sentence_objects:
        if s.text[0] == "[" and s.text[-1] == "]":
            chapter_counter += 1
        s.chapter = chapter_counter
    return voice_objs


def createDictPersonae(voice_objs):
    temp_personae = []
    for v in voice_objs:
        for i in range(0, len(v.sentences_list)):
            temp_personae.append(v.sentences_list[i].character)
    return sorted(set(temp_personae))


def createMainCast(nicknames):
    main_cast_list = []
    for person in nicknames:
        main_cast_list.append(my_classes.Character(person))
    return main_cast_list


def reduceSentences2mainCast(voice_objs, mainCast):
    temp_names = []
    for person in mainCast:
        temp_names.append(person.name)
    for v in voice_objs:
        for i in range(0, len(v.sentences_list)):
            pos = v.sentences_list[i].character.find(" ")
            if pos == -1:
                pos = len(v.sentences_list[i].character)
            if any(v.sentences_list[i].character[:pos] in string for string in temp_names):
                v.sentences_list[i].finalVoice = v.sentences_list[i].character[:pos]
            else:
                v.sentences_list[i].finalVoice = "Narrator"
    # for v in voice_objs:
    #     for i in range(0, len(v.sentences_list)):
    #         print(v.id, v.initCharacter, v.sentences_list[i].id, v.sentences_list[i].finalVoice, v.sentences_list[i].text)


def createFinalVoiceParts(init_voice_objs):
    final_voice_objs = []
    temp_new_list = []
    temp_sentences_list = []
    id_counter = 0
    for v in init_voice_objs:
        for i in range(0, len(v.sentences_list)):
            temp_sentences_list.append(v.sentences_list[i])
    i = 0
    try:
        while i <= len(temp_sentences_list):
            counter = 0
            while temp_sentences_list[i].finalVoice == temp_sentences_list[i + counter].finalVoice:
                temp_new_list.append(temp_sentences_list[i + counter])
                counter += 1
            temp_text = ""
            for s in temp_new_list:
                temp_text += s.text + " "  # if sentence only one line add '# \n'
            final_voice_objs.append(my_classes.VoicePart(voice_id=id_counter, text=temp_text, initCharacter="n.a.",
                                                         finalVoice=temp_sentences_list[i].finalVoice))
            for sentence in temp_new_list:
                final_voice_objs[-1].sentences_list.append(sentence)
            temp_new_list.clear()
            id_counter += 1
            i += counter
    except IndexError:
        if len(temp_new_list) > 0:
            temp_text = ""
            for elem in temp_new_list:
                temp_text += elem.text
            final_voice_objs.append(my_classes.VoicePart(voice_id=id_counter, text=temp_text, initCharacter="n.a.",
                                                         finalVoice=temp_sentences_list[i].finalVoice))
            for sentence in temp_new_list:
                final_voice_objs[-1].sentences_list.append(sentence)
            temp_new_list.clear()
            id_counter += 1
    return final_voice_objs


def createBucket(mainCast, voice_objs):
    for character in mainCast:
        for v in voice_objs:
            for i in range(0, len(v.sentences_list)):
                if v.sentences_list[i].finalVoice == character.name:
                    character.complete_text.append(v.sentences_list[i].text)
# send Buckets # but makes no sense to only let one person speak?
# def send2TTS(tts, person):
#     temp_path = os.getcwd() + r"\Output\temp\\"
#     temp_output = temp_path + "audio_temp" + str(person.name) + ".mp3"
#     voice = getVoice(person)
#     text = ""
#     for sentence in person.complete_text:
#         text += str(sentence)
#     print(voice, temp_output, text)
#     with open(temp_output, 'wb') as audio_file:
#         result = tts.synthesize(text, accept='audio/mp3', voice=voice).get_result()
#         audio_file.write(result.content)
#         audio_file.close()


def getVoice(finalVoice):
    if finalVoice == "Aang":
        voice = 'en-US_KevinV3Voice'
    elif finalVoice == "Katara":
        voice = 'en-US_AllisonV3Voice'
    elif finalVoice == "Sokka":
        voice = 'en-US_HenryV3Voice'
    elif finalVoice == "Zuko":
        voice = 'en-GB_JamesV3Voice'
    elif finalVoice == "Narrator":
        voice = 'en-GB_JamesV3Voice'
    else:
        voice = 'en-GB_JamesV3Voice'
    return voice


def testAndCosts(final_voice_objs):
    intended_parts = 20
    counter_char = 0
    counter_words = 0
    total_char = 0
    total_words = 0
    for v in final_voice_objs[:intended_parts]:
        print(v.id, v.finalVoice, ":", v.text)
    for v in final_voice_objs[:intended_parts]:
        counter_char += len(v.text)
        for char in v.text:
            if char == " ":
                counter_words += 1
    for v2 in final_voice_objs:
        total_char += len(v2.text)
        for char in v2.text:
            if char == " ":
                total_words += 1
    relative_parts = intended_parts / len(final_voice_objs) * 100
    print("\n The intended parts makes up", intended_parts, "of", len(final_voice_objs), " total voice-parts (",
          "%.2f" % relative_parts, "%).")
    print("Total word count:", total_words, "- with only intended parts word count:", counter_words)
    print("Total characters count:", total_char, "- with only intended parts char count:", counter_char,
          "(below 10000 characters per month is free)\n")
    print("Estimated Costs(intended) at IBM TTS:", intended_parts * 0.02 / 1000, "$ (0.02$ per 1000 characters).")
    print("Estimated Costs(total) at IBM TTS:", len(final_voice_objs) * 0.02 / 1000, "$ (0.02$ per 1000 characters).")


def voiceParts2TTS(final_voice_objs):                   # Reminder: TTS Services might cost!
    # intended_parts = len(final_voice_objs)
    intended_parts = 20
    authenticator = IAMAuthenticator(my_authentification.getApiKey())
    tts = TextToSpeechV1(authenticator)
    tts.set_service_url(my_authentification.getURL())

    for v in final_voice_objs[:intended_parts]:
        temp_path = os.getcwd() + r"\Output\temp\\"
        temp_output = temp_path + "audio_temp" + str(v.id) + ".mp3"
        # TTS Service might cost!
        with open(temp_output, 'wb') as audio_file:
            temp_voice = getVoice(v.finalVoice)
            result = tts.synthesize(v.text, accept='audio/mp3', voice=temp_voice).get_result()
            audio_file.write(result.content)
            audio_file.close()


def sortAlphanumeric(data):                                                 # sort temp_output_files
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(data, key=alphanum_key)


def mergeTempFiles(input_file):
    input_file = input_file
    temp_path = os.getcwd() + r"\Output\temp\\"
    # merge all temp parts into one file
    filelist = sortAlphanumeric(os.listdir(temp_path))
    total_file = bytes()
    for file in filelist:  # does not automatically take the correct order!
        with open(temp_path + file, 'rb') as f:
            part = f.read()
            f.close()
        total_file += part
    # create total_file
    file_name = input_file[:-4]
    output_name = './Output/audio_%s.mp3' % file_name
    with open(output_name, 'wb') as audio_file:
        audio_file.write(total_file)
        audio_file.close()
    # delete all temp files
    for root, dirs, files in os.walk(temp_path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

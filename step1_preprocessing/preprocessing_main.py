import modules.my_classes as my_class
import modules.my_functions as my_function

INPUT_FILE = 'wonderland_raw.txt'


# 1. import text
raw_text = my_function.import_fct(INPUT_FILE)
# 2. transform apostrophes & clean - maybe "choose" apostrophes outside of function
clean_text = my_function.clean_text(raw_text)
# 3. transform text string to list of voice_parts
voice_parts_list = my_function.text2list(clean_text)
# 4. transform voice_parts_strings into voice-objects (with sentences etc. for NN)
voice_objs = my_function.voices2objs(voice_parts_list)

# test print voices on sentence-level
# for voice in voice_objs[0:10]:
#     temp_sentence_list = []
#     for sentence in voice.sentences_list:
#         temp_list = sentence
#         for i in temp_list:
#             print(voice.id, i.text, i.id)

# 5. output voice-objects as JSON
my_function.output_voices_JSON(voice_objs, INPUT_FILE)

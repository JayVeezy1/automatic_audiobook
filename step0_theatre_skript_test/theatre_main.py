import my_functions

input_file = 'Avatar_ep01_raw.txt'                      # https://www.simplyscripts.com/tv_all.html

# 1. import text
raw_text = my_functions.import_fct(input_file)
script_lines = raw_text.split("\n")
temp_voice_objs = my_functions.lines2objs(script_lines)
init_voice_objs = my_functions.add_sentences2voices(temp_voice_objs)

# 2. create dictionary of personae
dictPersonae = my_functions.createDictPersonae(init_voice_objs)

# 3. Reduce to known personae, all others = narrator                            # TODO there must be a better solution smh
nicknames = ["Narrator", "Aang", "Children", "Iroh", "Katara", "Sokka", "Villagers", "Zuko"]         # known main-cast gets 'nicknames'
main_cast = my_functions.createMainCast(nicknames)
my_functions.reduceSentences2mainCast(init_voice_objs, main_cast)

# 4. create final voice-objects (split narrator-sentences from dialogue)
final_voice_objs = my_functions.createFinalVoiceParts(init_voice_objs)

# 5. output voice-objects as JSON
my_functions.output_script_JSON(final_voice_objs, input_file)

# 6. Send sentences to TTS & file-cleanup
my_functions.testAndCosts(final_voice_objs)
my_functions.voiceParts2TTS(final_voice_objs)                       # Reminder: TTS Services might cost! Also authentication file needed.
my_functions.mergeTempFiles(input_file)


# # OPTIONAL create text-buckets per character (useful for character-analysis)
# my_functions.createBucket(main_cast, final_voice_objs)
# for person in main_cast:
#     print(person.name, ":", person.complete_text)

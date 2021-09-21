class InitVoicePart(object):                        # used for initial import, to fill sentences with info
    def __init__(self, voice_id, text):
        self.id = voice_id
        self.initCharacter = "-"
        self.finalVoice = "-"
        self.sentences_list = []
        self.text = text


class VoicePart(object):                             # used for final TTS export
    def __init__(self, voice_id, text, initCharacter, finalVoice):
        self.id = voice_id
        self.initCharacter = initCharacter
        self.finalVoice = finalVoice
        self.sentences_list = []
        self.text = text


class Sentence(object):
    def __init__(self, sentence_id, text, metaVoice):
        self.chapter = "-"
        self.id = sentence_id
        self.character = "-"                 # true character (might be different than voice.initCharacter)
        self.metaVoice = metaVoice          # meta info about voice (directions, unintelligible, ...)
        self.finalVoice = "-"
        self.text = text
        self.emotion = "-"
        self.speed = "-"

    def toJson(self):  # to make sentences serializable
        return json.dumps(self, default=lambda o: o.__dict__)


class Character(object):  # for dictionary of personae
    def __init__(self, name):
        self.name = name
        self.voice = ""  # Useful? male/female, old/young, angry/kind
        self.complete_text = []

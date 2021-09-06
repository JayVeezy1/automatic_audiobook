class Voice(object):
    def __init__(self, voice_id, text_string):
        self.id = voice_id
        self.chapter = "-"
        self.text = text_string
        self.sentences_list = []
        self.character = "Narrator"


class Sentence(object):
    def __init__(self, sentence_id, text):
        self.id = sentence_id
        self.text = text
        self.emotion = "normal"                                         # TODO
        self.speed = "-"                                                # TODO

    def toJson(self):                                                   # to make sentences serializable
        return json.dumps(self, default=lambda o: o.__dict__)


class Character(object):                                                # for dictionary of personae
    def __init__(self, name):
        self.name = name
        self.attributes = []                                            # e.g. male/female, old/young, angry/kind

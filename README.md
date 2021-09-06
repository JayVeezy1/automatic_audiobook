# automatic_audiobook
The goal of this project is to transform any text (.txt format) into a qualitative audiobook (.mp3). Nowadays, the results of common text-to-speech (TTS) are getting better constantly. However, the idea of this program is to automatically detect which character (in a story) is saying which sentence based on natural language processing (NLP). This should enable different voices/pronounciations for different characters.

Step 1: Splitting .txt file into voice_parts (paragraphs of continous speech of one character). These voice_parts are then saved as objects in a JSON file. Each object contains the sentences and the respective attributes like the character (speaker/narrator), emotion, speed, ID.

Step 2: These attributes need to be filled. For this a neural network approach will be proposed in step 3.
- However the first step, which is currently under way, is to manually fill out these attributes. This strenuous work has to be done once, to obtain a basis for training data.
- At this step also a "dictionary of personae" has to be created (which will be the Outputs of the neural network).
- Editing the objects in the JSON file is not useful. Therefore, a web-editor is currently being developed in which the JSON file can be edited more easily. (like a drop-down list of characters so you don't have to type it every time, etc.)

Step 3: Now every sentence is connected to its respective character. Different machine learning methods shall be tested to automate this process.
- A useful first step might be to analyse which character appears in which chapter (making the dictionary of personae focus on each chapter, less output options)
- A recurrent network with a certain "memory" might be useful to remember who is part of a dialoge/scene. Based on that the sentences can be "tagged"/categorised/allocated to the characters (biggest task yet!)
- It is not clear yet if results soley based on syntactical aspects are reliable enough. The model probably needs to be based on semantical aspects which means word-level instead of sentence-level. With this, also speaking-patterns of certain characters can be used (one character talking more child-like than another, also emotions could then be analysed).

Step 3.2: This complete workflow needs to be generalised. At the moment I am working with Alice in Wonderland, as it is a license free book. Applying the mechanisms on other books will probably need a lot more training data (which needs to be obtained manually again). 

Step 4: Sending the sentences to a TTS-Engine and choosing a different voice depending on the character-attribute of the sentence is possible. This can be tested with a theatre-script, where a person is always mentioned before each line.
- At some point it would be nice not to be reliant on the commercial TTS providers as a whole audiobook might get quite costly (for example Amazon Polly Neural costed about 6€ for 200.000 words). However, their neural voices are have quite promising quality.
- Another great extension would be for users to configure the voices per character in detail. (giving a villain a malicious sounding voice, old people vs. young etc.). Even better would be an automated character-analysis which then sets up the voices for every character.
- Finally, it might even be possible to use one's own (or a certain actors) voice for the audiobook.

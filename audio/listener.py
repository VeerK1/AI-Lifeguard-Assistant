#!/usr/bin/env python3

import argparse
import queue
import sys
import sounddevice as sd
import json
import webrtcvad

from vosk import Model, KaldiRecognizer

KEYWORDS = [
    "help",
    "breathe",
    "drown",
    "breathing",
    "drowning",
    "save",
    "emergency"
]

q = queue.Queue()

#vosk
model = Model(model_name="vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

#vad
vad = webrtcvad.Vad(1) # 0-3, 3 is the most aggressive about filtering out non-speech

#general config
sample_rate = 16000
FRAME_DURATION = 20 #ms
FRAME_SIZE = int(sample_rate * FRAME_DURATION / 1000)
BLOCK_SIZE = FRAME_SIZE

def callback(indata, frames, time, status):
    q.put(bytes(indata))


def contains_keyword(text: str) -> bool:

    '''Checks if any keywords are found in text'''

    for keyword in KEYWORDS:
        if keyword in text:
            return True
    return False

def has_voice_activity(data: bytes) -> bool:

    '''Checks if the audio data contains speech like audio using VAD'''
    return vad.is_speech(data, sample_rate)


# creates chunk of audio
with sd.RawInputStream(
    samplerate = sample_rate,
    blocksize = BLOCK_SIZE,
    dtype="int16",
    channels = 1,
    callback = callback
):
    
    while True:

        data = q.get()

        # VAD (Voice Activity Detection) to check if speech exists -> otherwise no need to spend resources on processing the audio

        if has_voice_activity(data):

            # if done listening to chunk
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())

                text = result.get("text", "")
                print("FINAL: " + text)

                if contains_keyword(text):
                    print("KEYWORD DETECTED")

            else:
                # still listening

                partial = json.loads(recognizer.PartialResult())

                text = partial.get("partial", "")
                #print("PARTIAL: " + text)
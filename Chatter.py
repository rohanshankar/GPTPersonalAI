from slyme import SlymeDriver
import speech_recognition as sr
from google.cloud import speech
from gtts import gTTS
import os
import json
import pyttsx3 
import pyaudio
import wave
import numpy as np
import time 
import librosa



def record_speech():
    form_1 = pyaudio.paInt16
    chans = 1
    samp_rate = 96000
    chunk = 1024
    record_secs = 5
    dev_index = 1
    wav_output_filename = 'input.wav'

    audio = pyaudio.PyAudio()

    # Create pyaudio stream.
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")
    frames = []

    # Loop through stream and append audio chunks to frame array.
    for i in range(0,int((samp_rate/chunk)*record_secs)):
        data = stream.read(1024)
        frames.append(data)

    print("finished recording")

    # Stop the stream, close it, and terminate the pyaudio instantiation.
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the audio frames as .wav file.
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    resample_audio("input.wav")
    
def resample_audio(input_file, target_sample_rate=48000):
    # Load the audio using librosa
    audio, sr = librosa.load(input_file, sr=None, mono=True)

    # Resample the audio to the target sample rate
    resampled_audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sample_rate)

    # Save the resampled audio as a WAV file
    wavefile = wave.open(input_file, 'wb')
    wavefile.setnchannels(1)  # Set to 1 channel (mono)
    wavefile.setsampwidth(2)  # 2 bytes per sample
    wavefile.setframerate(target_sample_rate)
    wavefile.writeframes((resampled_audio * 32767).astype(np.int16).tobytes())
    wavefile.close()

def speech_to_text() :
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'OAuthGoogle.json'
    speechClient = speech.SpeechClient()
    mediaFileWav = 'input.wav'
    with open(mediaFileWav, 'rb') as f :
        byteData = f.read()
    audioWav = speech.RecognitionAudio(content = byteData)
    
    configWav = speech.RecognitionConfig(
        sample_rate_hertz = 48000,
        enable_automatic_punctuation = True,
        language_code = 'en-US',
        audio_channel_count = 1
    )
    
    response = speechClient.recognize(
        config=configWav,
        audio=audioWav
    )
    
    for result in response.results:
        return format(result.alternatives[0].transcript)

def SpeakText(command):
    engine = pyttsx3.init('nsss')
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.say(command)
    engine.runAndWait

def recognize_local_wav(wav_file, language="en-US"):
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as source:
        audio = r.record(source)

    try:
        recognized_text = r.recognize_sphinx(audio, language=language)
        print("Recognized text:", recognized_text)
        return recognized_text
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Sphinx; {e}")

def speak(text_to_speak):
    # Create a gTTS object with the text to be spoken
    tts = gTTS(text=text_to_speak, lang='en')

    # Save the speech as an audio file
    tts.save('output.mp3')
    audio_file = 'output.mp3'

    # Play the audio file
    os.system(f'open {audio_file}')

def ask_chat_gpt(prompt, slyme) :
    if prompt == '':
        return ""                           #throw error
    output = slyme.completion(prompt)
    slyme.end_session()
    return output

def main():
    slyme = SlymeDriver(pfname='~/Library/Application Support/Google/Chrome/')  #for now leave it like this --> later on change to make it instantiate a new chat at the beginning of a prompt and every 2 hours create a new one?
    time.sleep(5)
    slyme.new_chat()
    time.sleep(10)

    #record speech
    record_speech()
    #speech to text
    question = speech_to_text()
    # Send text to ChatGPT.
    print("Asking: {0}".format(question))
    gpt_response = ask_chat_gpt(question, slyme)
    print("Response: {0}".format(gpt_response))
    # Convert ChatGPT response into audio file and play it.
    speak(gpt_response)


if __name__ == "__main__":
    main()



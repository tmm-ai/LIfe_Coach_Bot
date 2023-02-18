from pydub import AudioSegment as am
import speech_recognition as sr
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import openai
import json
import wave
import load_G_sheets
from time import sleep
import camera_expression
import datetime
import polly_text_to_speech
import requests

from API_keys import empath_api_key, empath_API, openai_AP

def start_interaction():
    """""
    This function is the main driver of the module and calls all other functions listed below.
    The process is to turn on the microphone and then for a predetermined set number of responses, the
    function loops over these steps:
    1) Greets the user with a question about how they are doing and then asks about goals for the day
    2) Records the audio response and take a photo of the users face to capture facial expressions
    3) Transcribes the audio to text using sppech_recognizer and google_voice API
    4) Measures text sentiment from the text using Vadersentiment
    5) Predicts emotional facial expressions with luxand API
    6) Evaluates vocal intonations for emotional expression with Empath API
    7) Condenses all affective data and user response into a easily readable prompt for Chat_GPT
    8) Send the prompt to ChatGPT to get advice
    9) Turns ChatGPT advice into a human sounding audio file
    10) Uploads user response, all affective data, and ChatGPT response into a Google Sheet along with
    and invitation in the Google sheet for the user to reflect and journal on all this information. 
    
    Input: None
    Output: Audio of initial user statement, all affective data listed above and ChatGPT response on a Google Sheet
        Audio file of ChatGPT providing advice. 
    
    """""
    # Initialize the speech recognition
    speech_recognizer = sr.Recognizer()
    # for text sentiment
    text_sentiment = SentimentIntensityAnalyzer()
    responses = 1
    while responses < 3:
        response_list = []
        try:
            # using the microphone as source for input.
            with sr.Microphone() as audio_source:
                # wait for a second to let the recognizer adjust the energy threshold based on
                # the surrounding noise level
                speech_recognizer.adjust_for_ambient_noise(audio_source, duration=0.2)
                if responses == 1:
                    print("\n\nGood morning!! How are you feeling today?\n")
                if responses == 2:
                    print("Now, please share your top goal of the day", "\n")
                if responses > 2:
                    print("What is goal #", responses, " for the day?\n")

                audio_file = speech_recognizer.listen(audio_source, phrase_time_limit=8.8)

                # Now take a photo of the user to capture emotional facial expression
                facial_expression_keys, facial_expression_values = camera_expression.take_photo()
                print("\nGot it...hang on for a second while I process this...\n")

                # Using Google speech to text API to convert audio
                text_from_speech = speech_recognizer.recognize_google(audio_file)
                text_from_speech = text_from_speech.lower()

                # getting sentiment scores from Vader sentiment.
                text_sentiment_results = text_sentiment.polarity_scores(text_from_speech)

                # getting vocal intonation analysis
                vocal_emotion_results = get_vocal_emotions(responses,audio_file)

                # Putting user response and all affective data in an optimal prompt for GPT
                prompt = prep_data_for_GPT(responses, text_from_speech, text_sentiment_results,
                                        vocal_emotion_results, facial_expression_keys, facial_expression_values)

                # Getting response/advice from chat-gpt and trimming otu quotation marks
                gpt_response_raw = gpt_3_chat(prompt)
                gpt_response = gpt_response_raw["choices"][0]["text"]
                gpt_response = gpt_response[2:-1]

                # creating the mp3 file for the chat response
                polly_text_to_speech.polly_speak(gpt_response, responses)

                # adding affective data to a list for easier use
                response_list.append((text_from_speech, text_sentiment_results, vocal_emotion_results, gpt_response))

                # preparing all data to load into sheets
                sheets_values = sheets_data_prep(response_list, facial_expression_keys, facial_expression_values)

                # loading all data into Google sheets
                load_G_sheets.load_into_google_sheets(sheets_values, responses)
                responses += 1

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

        except sr.UnknownValueError:
            print("unknown error occurred")


def get_vocal_emotions(responses, audio_file):
    """""
    This function uses the webempath API to provide emotional analysis of vocal intonations. It opens the audio file
    down-samples it to 11025 rate as required by webempath, if the file is over 5MB it is too long and is then cut 
    down by 50% and resent to webempath. Once emotional readings are returned from the API, results are returned
    
    input: # of responses and an audio file of the user speaking
    output: a dictionary with emotions and values/levels. 
    """""
    # Empath API stuff
    vocal_empath_api_url = 'https://api.webempath.net/v2/analyzeWav'
    empath_payload = {'apikey': empath_api_key}

    with open("response" + str(responses) + "T.wav", "wb") as f:
        f.write(audio_file.get_wav_data())

    # downsampling for empath API as it must be 11025 rate
    sound = am.from_file("response" + str(responses) + "T.wav", format='wav', frame_rate=44100)
    down_sampled_sound = sound.set_frame_rate(11025)
    down_sampled_sound.export("response" + str(responses) + "T.wav", format='wav')
    # sending wave file to empath API
    wav = "response" + str(responses) + "T.wav"
    data = open(wav, 'rb')
    vocal_wav_file = {'wav': data}
    res = requests.post(vocal_empath_api_url, params=empath_payload, files=vocal_wav_file)
    vocal_emotions = res.json()

    # the following loop is done only if the size of the audio file is too large for Empath API.
    # This loop cuts the file by 50% and resends the file to the Empath API
    while vocal_emotions['error']:
        print(vocal_emotions)
        with wave.open("response" + str(responses) + "T.wav", "rb") as wav_in:
            # Read the audio data and metadata from the input file
            frames = wav_in.readframes(-1)
            params = wav_in.getparams()
            # Trim the audio data by 50%
            start = 0
            end = params.nframes
            new_end = int(end * 0.50) * params.sampwidth
            frames = frames[start * params.sampwidth: new_end]
            # Open the output WAV file
            with wave.open("response" + str(responses) + "T.wav", "wb") as wav_out:
                # Set the metadata for the output file
                wav_out.setparams(params)
                # Write the trimmed audio data to the output file
                wav_out.writeframes(frames)
            wav = "response" + str(responses) + "T.wav"
            data = open(wav, 'rb')
            vocal_wav_file = {'wav': data}
            # Get Empath results
            res = requests.post(vocal_empath_api_url, params=empath_payload, files=vocal_wav_file)
            vocal_emotions = res.json()

    return vocal_emotions


def prep_data_for_GPT(responses, text_from_speech, text_sentiment_results, vocal_emotion_results,
                      facial_expression_keys, facial_expression_values):
    """""
    This function takes in the user statement and all the various affective data in their initial array and dictionary 
    data structures and puts together a single string that sounds like a human explaining their test results, 
    Additionally, a specific advice type/style is added at the end. This single string prompt is then returned
    
    Inputs: user response, all affective data, response number
    Output: A single string prompt for ChatGPT 
    """""
    if responses == 0:
        initial = "Today "
    if responses > 0:
        initial = "One of my top goals today is: "
    prompt_answer = "".join([initial, text_from_speech])
    text_sent_formatted = "".join(
        [". The sentiment analysis of this response is ", str(round(text_sentiment_results["neg"],
                                                                    1)) + "% negative, ",
         str(round(text_sentiment_results["neu"], 1)) + "% neutral, ",
         str(round(text_sentiment_results["pos"], 1)) + "% positive, and ",
         str(round(text_sentiment_results["compound"], 1)) + "% is the compound. "])
    vocals = "".join(
        ["The empahtic analysis of my vocal intonations as I spoke, on a scale from 0 to 50, are ",
         str(vocal_emotion_results['calm']), " for calm, ", str(vocal_emotion_results['anger']),
         " for angry, ",
         str(vocal_emotion_results['joy']), " for joy ,",
         str(vocal_emotion_results['sorrow']), " for sorrow, and ", str(vocal_emotion_results['energy']),
         " for energy. "])
    face_results = ["The results of facial expression analysis done on my face as I said this are:"]
    for value in range(1, len(facial_expression_keys)):
        face_results.append(" ".join(
            [" ", str(facial_expression_values[value]), "for", str(facial_expression_keys[value])]))

    if len(face_results) == 1:
        face_results = ""
    else:
        face_results.append(". ")
        face_results = "".join(face_results)
    GPT_advice_type = " constructive, detailed, positive, and uplifting "
    question = "".join(
        ["Given this information about me, what advice do you have for me? Also, the kind of "
         "advice I want is ", GPT_advice_type])

    prompt = str("".join([prompt_answer, text_sent_formatted, vocals, face_results, question]))
    print("CHECK PROMPT")
    print(prompt)

    return prompt


def gpt_3_chat(fresh_prompt):
    """""
    This function utilizes the ChatGPT API to get detailed advice after sending each prompt
    
    Input: A prompt in the form of a single string
    Output: A string from ChatGPT
    """""
    openai.api_key = openai_API
    response_GPT = openai.Completion.create(
        engine="text-davinci-003",
        prompt=fresh_prompt,
        max_tokens=1500,
        temperature=0.5,
        top_p=1.0,
        frequency_penalty=.5,
        presence_penalty=.5
    )
    return response_GPT


def sheets_data_prep(response_list, face_keys, face_values):
    """""
    This function breaks out all responses and data into a dictionary for uploading to Google sheets in 
    an easy to read format
    
    Input: All user input, affectve data, GPT response
    Output: A dictionary of all values to upload to Google Sheets
    """""
    for idx, response in enumerate(response_list):
        now = datetime.datetime.now()

        # preparation of data for Google SHeets
        time_format = now.strftime("%B %d, %Y %I:%M:%S %p")

        initial_greeting = ["Feelings today:", response[0]]
        sent_1 = response[1]
        sentiment1 = ["Text Sentiments:", "Negative", "Neutral", "Positive", "Compound"]
        sentiment2 = ["  ", str(round(sent_1["neg"], 1)), str(round(sent_1["neu"], 1)),
                      str(round(sent_1["pos"], 1)),
                      str(round(sent_1["compound"], 1))]
        emotions = response[2]
        vocal_emotions1 = ["Vocal Emotions:", "Calm", "Angry", "Joy", "Sorrow", "Energy"]
        vocal_emotions2 = ["(scale: 0-50) ", str(emotions['calm']), str(emotions['anger']),
                           str(emotions['joy']),
                           str(emotions['sorrow']), str(emotions['energy'])]

        Chat_response1 = ["Advice from OpenAi GPT-Chat"]
        Chat_response2 = [response[3]]
        Journal_entry = [
            "Within 24 hours, write about how this goal setting and GPT-Chat advice impacted your day"
            " in the cell below."]

        sheets_values = {"values": [[" "], [time_format], initial_greeting, sentiment1, sentiment2,
                                            vocal_emotions1,
                                            vocal_emotions2,
                                            face_keys, face_values, Chat_response1, Chat_response2,
                                            Journal_entry, ["Add"
                                                            "notes here:"]]}
        return sheets_values


if __name__ == '__main__':
    start_interaction()

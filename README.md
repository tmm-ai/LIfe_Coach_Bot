# Life_Coach_Bot
Affective AI bot that helps users address emotional blocks and achieve goals

## Introduction

The Life-Coach Bot is my final semester project for CS437 Internet of Things at the University of Illinois Urbana-Champaign (UIUC) as part of my Masters in Computer Science.

The objective was to create a raspberry pi based, emotionally intelligent chat robot with which the user could interact daily. The bot would give users helpful advice in each interaction to help them achieve their goals and get the most out of the day. A basic premise for creating this is that an individual's productivity and success depend on their self-perspective and emotional state. For instance, if a person is sad and frustrated and thinks there is no use in trying, they will most likely fare poorly compared to an optimistic person who believes they can achieve anything they set their mind to.

An imagined use case is that the user is greeted by the bot each morning. The bot asks them how they are doing and then asks them what their main goals are for the day. The bot then does the following
1) Records each response in an audio file
2) Turns the text into speech using speech recognizer API
3) Determines the sentiment of the text using the Vader sentiment API
4) Evaluates emotions in the vocal intonations via WebEmpath API
5) Takes a photo of the user with a Pi Camera just after their response and predicts emotions based on facial expressions through the Luxand API   
6) Condenses all affective data and user responses into an easily readable prompt for Chat_GPT
7) Send the prompt to ChatGPT to get advice via the ChatGPT API
8) Turns ChatGPT advice into a human-sounding audio file with Amazon AWS Polly API
10) Uploads the user response, all affective data, and ChatGPT advice into a Google Sheet via a Google Cloud/Sheets API. The user then has a record of this interaction and is invited to review and reflect on how to implement the advice during the day.


## Modules Provided
life_coach_bot.py - main program driver
camera_expression.py - takes photos and gets facial expressions
polly_textTOspeech.py - turn ChatGPT advice text into an audio file
load_sheets.py = - creates google sheet and continuously loads all interactions into the sheet


## Requirements

You will need a raspberry pi loaded with Raspberrian, a high-quality microphone, and a camera connected to the pi.

How to connect and get started with the pi-camera version 2 is here: https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0

I used a four-mic linear array from seeed studio. The link to this product:
https://www.seeedstudio.com/ReSpeaker-4-Mic-Linear-Array-Kit-for-Raspberry-Pi.html

## Installation
Once your raspberry pi is set up with the OS and has a working camera and microphone, you can start running the provided code on the pi.

## Configuration
This program uses seven different APIs, many of which are associated with the user's specific account. I have removed my account's specific keys and replaced them with "Add your API key here." The personal accounts and new API keys needed are for WebEmpath, Luxand, ChatGPT, Amazon AWS, and Google Cloud/Sheets.

Aside from API account-specific keys, this program was not designed with different configurations in mind. However, if you imagine other use cases of this process, editing the initial prompts to the user can be easily edited within the life_coach_bot.py file.


## Maintainers
@TomMcOO1 on Twitter

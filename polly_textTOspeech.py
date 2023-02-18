import boto3
from API_keys import aws_access_API, aws_secret_API
# Create a Polly client with your access key ID and secret access key

def polly_speak(chat_response, response_number):
    """""
    This utilizes Amazon AWS Polly, a text to speech service. 
    
    Input: text and response #
    Output: a mp3 file of speech
    """""
    polly = boto3.client('polly',
                         aws_access_key_id= aws_access_API,
                         aws_secret_access_key= aws_secret_API,
                         region_name='us-east-1')

    # Use the Polly client to synthesize speech from the provided text
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        VoiceId='Joanna',
        Text= chat_response
    )

    # Save the generated audio to a file
    with open('GPT_Chat_response'+str(response_number)+'.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
        f.close()


if __name__ == '__main__':
    polly_speak("Just called function from module directly, there was no text sent",999)
from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from pprint import pprint

from API_keys import spreadsheet_id

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
temp_values_for_sheet_creation = {"values": [["John2", "Smith", "123 Main Street"],
                                             ["Jane", "Doe2", "456 Park Avenue"], [" .", " ", ""]]}


def load_into_google_sheets(sheets_values=temp_values_for_sheet_creation, response_num=0):
    """""
    This function both creates a new google sheet for the user and updates that google sheet with new values.
    The first time it is run, it needs to create the sheet. A token.js file is created as well as a spreadsheet
    ID. The current code is more designed for updating a previously created sheet as the token.js file is assumed
    to exist as well as the spreadsheet ID.

    Inputs: all data to upload to the google sheet and # of responses
    Outputs: An updated google sheet with all data after each responses provided. 
    """""

    def create(title, service):
        """""
        This function only creates the initial Google Sheet if it does not already exist. Overall, th program is
        designed to create this once, and then over many days/years update the google sheet with data from 
        each interaction. If this file is being used for the first time, you will need to comment out the
        spreadsheet = "ID_string" line.

        Input: title to Google Sheet, service function to create sheet
        Output: A new google sheet ready to be loaded with data. 
        """""
        try:
            print("Creds:", creds)
            spreadsheet = {
                'properties': {
                    'title': title
                }
            }
            print("Title")
            spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                        fields='spreadsheetId') \
                .execute()
            print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
            return spreadsheet.get('spreadsheetId')

        except HttpError as err:
            print(err)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # This id was created from a previous run of the create function above.
    # if running the first time, comment out the line below

    if not spreadsheet_id:
        spreadsheet_id = create("Mental State, Daily Goals and ChatGPT Advice", service)

    # The A1 notation of the values to update.
    response_num -= 1
    range_start = response_num * 14 +1
    range_ = 'Sheet1!A' + str(range_start) + ':J' + str(range_start + 1)  # TODO: Update placeholder value.
    # How the input data should be interpreted.
    value_input_option = 'USER_ENTERED'

    # Prepares data to load into sheets in specific format
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option, body=sheets_values)
    # Loads data into Google Sheets
    response = request.execute()

    pprint(response)


if __name__ == '__main__':
    load_into_google_sheets()
from __future__ import print_function

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil.parser import parse as dtparse
from datetime import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

preco_hora = 20

start_string = '2021-01-01T01:00:00'
end_string = '2021-01-31T23:00:00'

iso_format = '%Y-%m-%dT%H:%M:%SZ'
START_DATE = dt.strftime(dtparse(start_string), format=iso_format)
END_DATE = dt.strftime(dtparse(end_string), format=iso_format)

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary',
                                        timeMin=START_DATE, timeMax=END_DATE,
                                        maxResults=100000, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    monings_total = 0
    peoples = {}
    if not events:
        print('No events found.')
    for event in events:
        if event['summary'].startswith('Explica'):
            start = event['start'].get('dateTime', event['start'].get('date'))
            end =  event['end'].get('dateTime', event['end'].get('date'))
            if(len(start)>11):
                start_time = int(start[11:13]) + int(start[14:16])/60

                end_hour = int(end[11:13]) if int(end[11:13])!=0 else 24
                end_minutes = int(end[14:16])/60
                end_time = end_hour + end_minutes
                monings = (end_time-start_time)*preco_hora
                monings_total += monings

                tokens = event['summary'].split()
                explicando = tokens[1] if len(tokens)==2 else tokens[1] + ' ' + tokens[2]
                if explicando in peoples.keys():
                    peoples[explicando] += monings
                else:
                    peoples[explicando] = monings

    pretty_format = '%d %B %Y'
    start_pretty = dt.strftime(dtparse(start_string), format=pretty_format)
    end_pretty = dt.strftime(dtparse(end_string), format=pretty_format)

    peoples = dict(sorted(peoples.items(), key=lambda item: item[1]))
    print(peoples)

    explode = np.zeros(len(peoples))
    explode[-1] = 0.05

    plt.pie([v for v in peoples.values()], labels = [k for k in peoples.keys()], autopct='%1.0f%%', explode = explode)
    text= 'Monings entre ' + start_pretty + ' e ' + end_pretty + ': ' + str(int(monings_total))+'€'
    plt.xlabel(text)
    plt.show()


if __name__ == '__main__':
    main()

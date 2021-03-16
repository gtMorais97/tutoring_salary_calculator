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
import sys
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



def main():
    args = sys.argv
    if len(args) < 4:
        raise Exception('Please provide start and end date (dd/mm/yyyy) and price per hour')
    start_arg = '/'.join(args[1].split('/'))
    end_arg = '/'.join(args[2].split('/'))

    date_regex = re.compile('(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|04|08|12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)')
    match_start = bool(date_regex.match(start_arg))
    match_end = bool(date_regex.match(end_arg))
    print(match_start)
    print(match_end)
    if not match_start or not match_end:
        raise Exception('Invalid date. Format is dd/mm/yyyy.')
    start_arg = '-'.join(start_arg.split('/')[::-1])
    end_arg = '-'.join(end_arg.split('/')[::-1])
                       
    preco_hora = int(args[3])

    start_string = start_arg + 'T01:00:00' if start_arg else '2021-01-01T01:00:00'
    end_string = end_arg + 'T23:00:00' if end_arg else '2021-01-31T23:00:00'

    iso_format = '%Y-%m-%dT%H:%M:%SZ'
    START_DATE = dt.strftime(dtparse(start_string), format=iso_format)
    END_DATE = dt.strftime(dtparse(end_string), format=iso_format)
    
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
    exit()


if __name__ == '__main__':
    main()

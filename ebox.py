from bs4 import BeautifulSoup
import boto3
import sys
import logging
import requests
from datetime import datetime

ses = boto3.client('ses')

email_from = 'ebox@patate.xyz'
email_subject = 'Your available usage is down to '
email_body = 'Your available usage is down to '

def getEboxUsage(event, context):
    success = False
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        success = False
        code = event['code']
        password = event['password']
        email_to = event['email']
        logger.info('Starting script for account \'%s\' and email \'%s\'.', code, email_to)

        session = requests.session()
        response = session.get('https://client.ebox.ca/')
        soup = BeautifulSoup(response.content, 'html.parser')
        form = soup.find('form', id='formLogin')
        hidden_parameters = form.find_all('input', type='hidden')

        login_form_params = {'usrname': code, 'pwd':password}
        for param in hidden_parameters:
            login_form_params[param.attrs['name']] = param.attrs['value']

        session.post('https://client.ebox.ca/login', login_form_params)

        now = datetime.now()
        month = now.month
        year = now.year
        session.get(f'https://client.ebox.ca/ajax/usages?action=getMonth&m={month}&y={year}', headers={'X-Requested-With':'XMLHttpRequest'})
        
        response = session.get('https://client.ebox.ca/home')
        soup = BeautifulSoup(response.content, 'html.parser')
        used_ratio_list = ''.join(soup.find('span', {'class':'text_summary3'}).text.split()).split('Go')
        remaining = float(used_ratio_list[1].replace('/','')) - float(used_ratio_list[0])
        logger.info('%s GB remaining for account \'%s\'.', remaining, code)
        success = True
        if remaining < 30:
            ses.send_email(ReturnPath = email_from, Source = email_from, Destination={'ToAddresses': [email_to]}, Message={'Subject': {'Data': email_subject + str(remaining) + 'GB for account ' + code},'Body': {'Text': {'Data': email_body + str(remaining) + 'GB for account ' + code + '. https://client.ebox.ca'}}})
    except Exception:
        logger.exception('Something went terribly wrong!')
    return success
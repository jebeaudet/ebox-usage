from bs4 import BeautifulSoup
import httplib, urllib
import boto3
import sys
import logging

ses = boto3.client('ses')

email_from = 'ebox@patate.xyz'
email_subject = 'Your available usage is down to '
email_body = 'Your available usage is down to '

def getEboxUsage(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    success = False
    code = event["code"]
    email_to = event["email"]
    logger.info('Starting script for account "%s" and email "%s".', code, email_to)
    params = urllib.urlencode({'actions': 'list', 'DELETE_lng': 'en', 'lng': 'en','code': code})
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    conn = httplib.HTTPConnection("conso.ebox.ca")
    conn.request("POST", "/index.php", params, headers)
    response=conn.getresponse()
    data = response.read()

    soup = BeautifulSoup(data, 'html.parser')
    for div in soup.find_all('div'):
        if div.b and "Available" in div.b.string:
            remaining_str = div.contents[1][:-1]
            remaining = float(remaining_str)
            logger.info('%s GB remaining for account "%s".', remaining, code)
            success = True
            if remaining < 30:
                try:
                    ses.send_email(ReturnPath = email_from, Source = email_from, Destination={'ToAddresses': [email_to]}, Message={'Subject': {'Data': email_subject + remaining_str + 'GB for account ' + code},'Body': {'Text': {'Data': email_body + remaining_str + 'GB for account ' + code + '. http://conso.ebox.ca/'}}})
                except Exception, e:
                    print repr(e)
    return success

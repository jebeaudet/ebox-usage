# [Ebox](https://www.ebox.ca) usage script
A barebone python script to fetch the number of GB available on your ebox account. It can be used as standalone with minor modifications or in AWS lambda with SES for email notifications.

## How to use
### SES
You first need to configure your SES account. Chances are that your AWS account is sandboxed for SES so you need to confirm the sender and the receiver email. This can be done easily in the SES console so do this beforehand.

### Lambda
This script uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/download/) library to scrape the html returned by ebox as the usage page is php. It is included in this repo so you don't need to package it yourself. Clone the repo, zip the content of the root directory (with ebox.py at the root level), this will be uploaded to the Lambda console.

Open up the Lambda console and add a new python function. Configure the handler as `ebox.getEboxUsage` and create a role that can use SES. I suggest a timeout of 10sec as the website can be slow sometimes. 128MB ram is more than enough. Upload the zip you previously created.

In the trigger part, you can select anything you want but if you want to keep it simple, just create a cron in Cloudwatch events `cron(0 12 * * ? *)`, this will run every day at noon UTC.

After you created the function, edit the ebox.py file directly in the console. Change the `email_from` at the top with the email you confirmed. I used a threshold of 30GB which means a notification will be sent if my available usage is less than that. 

### Input
Now you can run the function with this payload : 
```json
{
  "code": "insert your ebox code here",
  "email": "the destination email the notification should be sent to"
}
```
That's it!

## Limitations
As of now, there is no state kept between runs so it will send you an email every day if you get lower than the threshold. This could easily be improved by using dynamodb but I have yet to find the time to implement it.

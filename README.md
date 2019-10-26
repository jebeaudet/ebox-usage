# [Ebox](https://www.ebox.ca) usage script
A barebone python3 script to fetch the number of GB available on your ebox account. It can be used as standalone with minor modifications or in AWS lambda with SES for email notifications.

This script uses [Requests](https://pypi.org/project/requests/) to simulate the login using the username and password combo. After, it uses [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup) library to scrape the html returned by ebox and calculate the amount of GB remaining on your cycle.

## How to setup on AWS
### SES
You first need to configure your SES account. Chances are that your AWS account is sandboxed for SES so you need to confirm the sender and the receiver email. This can be done easily in the SES console so do this beforehand.

### Lambda
Open up the Lambda console and add a new python 3.7 function. Configure the handler as `ebox.getEboxUsage` and create a role that can use SES. I suggest a timeout of 30sec as the website can be slow sometimes. 128MB ram is more than enough.

Since we're using some third party library, we'll need to package them up with the function so it works in lambda. To do this, we'll use a virtualenv like suggested on [AWS website](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) : 
```
virtualenv v-env
source v-env/bin/activate
pip install beautifulsoup4
pip install requests
deactivate
```
After this, go to the `v-env/lib/site-packages` and zip everything in there. You can skip the `pip` and `setuptools` to save up some space and enable the inline code editing in AWS Lambda console (it disables itself if the zip file is too big). Add the `ebox.py` in this zip file at the root level.

Upload the zip and edit the ebox.py file directly in the console. Change the `email_from` at the top with the email you confirmed. I used a threshold of 30GB which means a notification will be sent if the available usage is less than that. 

### Triggers
In the trigger part, you can select anything you want but if you want to keep it simple, just create a cron in Cloudwatch events `cron(0 12 * * ? *)`, this will run every day at noon UTC.

### Input
Now you can run the function with this payload : 
```json
{
  "code": "insert your ebox code here",
  "email": "the destination email the notification should be sent to",
  "password": "your ebox password"
}
```
That's it!

## Limitations
As of now, there is no state kept between runs so it will send you an email every day if you get lower than the threshold. Also, the login flow could change anytime so with no official API, this is not the most robust way to do things but it's unfortunately the only way.

from twocaptcha import TwoCaptcha
import requests
 
# Instance of TwoCaptcha
captcha_solver = TwoCaptcha('a4108fc3e9124230352738ca68575e6a')
 
# Target website URL
site_url = "https://patrickhlauke.github.io/recaptcha/"
 
# Getting the token
try:
    # For solving reCAPTCHA
    token = captcha_solver.recaptcha(
        sitekey='6Ld2sf4SAAAAAKSgzs0Q13IZhY02Pyo31S2jgOB5',
        url=site_url
    )
 
# Handling the exceptions
except Exception as e:
    raise SystemExit('Error: CAPTCHA token not recieved.')
 
# Sending the token to the website
else:
    # Sending spoof user-agent
    headers = {'user-agent': 'Mozilla/5.0 Chrome/52.0.2743.116 Safari/537.36'}
 
    # Sending recieved token
    data = {'recaptcha-token': str(token)}
 
    # Making POST request to the target site
    token_response = requests.post(site_url, headers=headers, data=data)
 
    print('Token sent')
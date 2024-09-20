Google FAQ Scrapper
-------------------

This tool can be used by seo professionals for scraping google faqs against any keyword.
Python is used to build the tool and the package used for this purpose is selenium.
Following are detail of how to execute this project

`pip install -r requirements.txt`

Following are the options/switches which can be used during command execution

    "-keyword" : "Keyword is required for initiating google search"
    "-d", "--domain" : Google regional domain like google.ca, google.us, default is google.com",default="google.com"
    "-m", "--maximum_faqs" : "Provide a count, how many faqs you want to extract from google SERP, default is 50 when flag inital faq is false", default=50
    "-i", "--initial_faqs" : "Only initial faqs are required from SERP results which are usually 4, default is True", default=True
    "-hl", "--hl" : "To change the prefered language", default="en"
    "-lang", "--lang" : "To change the prefered language", default="lang_en"  

So the command can be used like this as below

`python main.py -keyword "What is C#" -d "https://google.ca" -m 20 -i False -hl "en" -lang "lang_en"`

For it only outputs FAQs as a list of question,answer object array in the console
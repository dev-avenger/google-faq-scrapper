import json

import argparse
import re

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json







from QuestionAnswer import QuestionAnswer

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
global ids_handled,question_answer_array,maximum_faqs,only_initial_faqs,domain_name,hl,lang,supported_languages

ids_handled = []
question_answer_array = []
maximum_faqs = 50
only_initial_faqs = True
domain_name = "https://www.google.com"
hl = "en"
lang = "lang_en"

# Load the JSON file
with open('languages.json', 'r') as file:
    supported_languages = json.load(file)

def extract_domain(url):
    """Adds "https://www." to the URL if it doesn't already contain it.

    Args:
        url: The URL to check and modify.

    Returns:
        The modified URL with "https://www." added if necessary.
    """

    parsed_url = requests.head(url, allow_redirects=False)
    print(parsed_url)
    scheme = parsed_url.url.split("://")[0]
    print(scheme)
    netloc = parsed_url.url.split("://")[1]
    print(netloc)

    if not scheme:
        scheme = "https"
    if not netloc.startswith("www."):
        netloc = "www." + netloc

    return f"{scheme}://{netloc}"

def extract_domain_with_verification(url):
    """Extracts the domain name from a URL and verifies if it contains "google".

    Args:
        url: The URL to extract the domain from.

    Returns:
        The extracted domain name if it contains "google", otherwise None.
    """

    domain = extract_domain(url)  # Use the previous function to extract the domain

    if "google" in domain:
        return domain
    else:
        print("Error: Domain name does not contain 'google'")
        return None



def loop_through_faqs(question_containers):
    initial_question_count = len(question_containers)
    for index, question_container in enumerate(question_containers):
        # Extract the question text (adjust XPath if needed)'
        try:
            current_id = question_container.find_element(By.XPATH, ".//div").get_attribute("id")
            if current_id in ids_handled:
                print(f"Skipping question {index + 1} (ID already handled)")
                continue

            # Add the ID to the list
            ids_handled.append(current_id)
            question_element = question_container.find_element(By.XPATH,".//div/div/div/div[2]/div/div[1]/span/span")
            question = question_element.text.strip()
            # Locate the arrow element (if it exists)
            try:
                arrow_element = question_container.find_element(By.XPATH, ".//div/div/div/div[2]/div/div[3]")
                time.sleep(2)
                driver.execute_script("arguments[0].click();", arrow_element)
                time.sleep(2)
                try:
                    # answer_element = WebDriverWait(question_container, 10).until(
                    #     EC.visibility_of_element_located((By.XPATH, ".//div/div/div/span[1]/span"))
                    # )
                    new_answer = question_container.find_element(By.XPATH,".//div/div/div")
                    # new_answer = question_container.find_element(By.CSS_SELECTOR,f"//*[@id='{current_id}']/div/div/span[1]/span")
                    # new_answer = question_container.find_element(By.CSS_SELECTOR,f"#{current_id}>div>div>span:first-child>span")

                    pattern = re.escape(question)
                    modified_answer = re.sub(pattern, "", new_answer.text)


                    print(modified_answer)
                    answer = modified_answer
                    if answer:
                        print(f"Question: {question}")
                        print(f"Answer: {answer}")
                        QuestionAnswer(question, answer),

                        question_answer_array.append(QuestionAnswer(question,answer))
                        print("-" * 20)
                except TimeoutException:
                    print(f"Answer for question '{question}' timed out!")
                    continue
            except NoSuchElementException:
                # Skip if no arrow element found (not all results have accordions)
                continue
        except NoSuchElementException:
            continue
    if not only_initial_faqs:
        question_containers = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@jsname='yEVEwb']")))
        if len(question_containers) <= maximum_faqs:
            if len(question_containers) > initial_question_count:
                loop_through_faqs(question_containers)

def scrape_people_also_ask():
    # Set up the Chrome WebDriver
    parser = argparse.ArgumentParser(description="This script will extract faqs from google search results against a specific keyword")

    # Define required and optional arguments
    parser.add_argument("keyword", help="Keyword is required for initiating google search")
    parser.add_argument("-d", "--domain", help="Google regional domain like google.ca, google.us, default is google.com",default="google.com")
    parser.add_argument("-m", "--maximum_faqs", help="Provide a count, how many faqs you want to extract from google SERP, default is 50 when flag inital faq is false", default=50)
    parser.add_argument("-i", "--initial_faqs", help="Only initial faqs are required from SERP results which are usually 4, default is True", default=True)  # Set default value
    parser.add_argument("-hl", "--hl", help="To change the prefered language", default="en")  # Set default value
    parser.add_argument("-lang", "--lang", help="To change the prefered language", default="lang_en")  # Set default value


    # Parse arguments
    args = parser.parse_args()

    # Access arguments
    print(f"Required argument 1: {args.keyword}")

    if not args.keyword:
        print("Keyword argument is required, Please enter it")
        print("Searching results against keyword:", args.keyword)
        return
    else:
        print("Searching results against keyword:", args.keyword)

    # Check for optional arguments
    if args.domain:
        domain_name = extract_domain_with_verification(args.domain)
        if domain_name:
            print("Domain name selected:", domain_name)
        else:
            print("Invalid domain name")

    if args.maximum_faqs:
        try:
            maximum_faqs = int(args.maximum_faqs)
            print(f"Maximum FAQs you chosen: {maximum_faqs}")
        except ValueError:
            print("Error: maximum_faqs must be a number")

    if args.initial_faqs:
        try:
            only_initial_faqs = bool(args.initial_faqs)
            print(f"You have initial faqs to : {only_initial_faqs}")
        except ValueError:
            print("Error: initial_faqs must be a boolean value (True or False)")

    if args.hl:
        try:
            hl_value = str(args.hl)
            hl_exists = any(item['language_code'] == hl_value for item in supported_languages)
            print(f"The prefered language is  : {hl_value}")
            if not hl_exists:
              print(f"Not a valid language code: {hl_value}")
            else:
                hl = hl_value
        except ValueError:
            print("Error: Not a value string")

    if args.lang:
        try:
            lang_value = str(args.lang)
            print(lang_value)
            split_text = re.split('_+', lang_value)
            lang_exists = any(item['language_code'] == split_text[1] for item in supported_languages)
            print(lang_exists)
            print(f"The prefered language is  : {lang_value}")
            if not lang_exists:
              print(f"Not a valid language code: {lang_value}")
            else:
                lang = lang_value
        except ValueError:
            print("Error: Not a value string")
    print(hl)
    print(lang)
    url = f"{domain_name}search?hl={hl}&lr={lang}&"
    print(url)
    driver.get(url)
    # Perform a search for the query
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(args.keyword)
    search_box.submit()

    # Wait for the initial search results to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "search")))
    except TimeoutException:
        print("Search results loading timed out!")


    question_containers = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@jsname='yEVEwb']")))
    loop_through_faqs(question_containers)

    qa_dict_list = [qa.__dict__ for qa in question_answer_array]

    # Convert the list of dictionaries to a JSON string
    json_str = json.dumps(qa_dict_list, indent=4)

    print(json_str)

    print("exiting")
    driver.quit()



def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    scrape_people_also_ask()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
import time
import socket
import threading
import os

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import random
import csv
import sys

class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.path_to_csv = "1400-questions.csv"
        self.url = r"https://chat.openai.com/g/g-cy3cGFjNo-gpt-4-rag"
        self.free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(self.free_port, self.url)
        self.wait_for_human_verification()
        self.driver = self.setup_webdriver(self.free_port)
        self.input_box = self.driver.find_element(By.ID, "prompt-textarea")
        self.data = self.read_csv(self.path_to_csv)

    def setup_driver(self):
        self.free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(self.free_port, self.url)
        self.driver = self.setup_webdriver(self.free_port)

    def read_csv(self, path_to_csv):
        """ Reads content of .csv into list of lists """
        with open(path_to_csv, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            # next(csv_reader, None)
            data = list(csv_reader)
        return data
    
    def write_csv(self, path_to_csv):
        """ Writes content of self.data to .csv file """
        with open(path_to_csv, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(self.data)

    def return_chat_elements(self):
        """ Returns a list of elements that are the conversations from on left panel side of ChatGPT (exclude)"""
        return self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/g/g-cy3']")[2:]
    
    def test(self):
        for i in range(10):
            chat_elements = self.return_chat_elements()
            chat_elements[i].click()
            print("CLICKED!")
            time.sleep(45)

    def test_1(self):
        return self.data[152][3]
        

    def is_csv_full(self):
        """ Checks if .csv file has responses & citations filled in for every prompt """
        for row in self.data:
            if row[4] == 'GPT 4 RAG' or not row[4].strip() or row[5] == '[]':
                return False
        return True
    
    def populate_conversations(self, queries_per_conversation, max_num_conversations):

        # Counts how many queries get messed up
        cur_queries = 0
        num_conversations = 1

        while self.is_csv_full() == False:
            for row in self.data:
                if cur_queries == queries_per_conversation:
                    print("Max count reached for this conversation. Opening new conversation.")
                    self.open_new_conversation()
                    num_conversations += 1
                    print("Done.")
                    cur_queries = 0

                if num_conversations == max_num_conversations:
                    for i in reversed(range(1, max_num_conversations)):
                        chat_elements = self.return_chat_elements()
                        chat_elements[i].click()
                        print("Loading chat to read into .csv file. Index: ", i)
                        time.sleep(20)
                        conversation = self.return_chatgpt_conversation()
                        self.process_conversation(conversation)
                        # self.open_new_conversation()
                    self.open_new_conversation()
                    num_conversations = 1
                    cur_queries = 0

                if len(row) > 4 and (row[4] == 'GPT 4 RAG' or not row[4].strip() or row[5] == '[]'):
                    cur_prompt = row[3]
                    print("Sending prompt to GPT: ", cur_prompt)

                    # Preprocess Python strings for Javascript
                    cur_prompt = cur_prompt.replace("'", "\\'")
                    cur_prompt = cur_prompt.replace("\n", "\\n")

                    # Send to GPT-4
                    self.send_prompt_to_chatgpt(cur_prompt)

                    while self.is_button_present("//button[@aria-label='Stop generating']"):
                        time.sleep(20)
                    time.sleep(20)

                    if "There was an error generating a response" in self.driver.page_source or "network error" in self.driver.page_source or "Error in message stream" in self.driver.page_source:
                        print("Loading error. Will generate new conversation")
                        self.open_new_conversation()
                        num_conversations += 1
                    else:
                        print("No errors, next prompt")
                        cur_queries += 1
            self.end_session()

    def open_new_conversation(self):
        link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/g/g-cy3cGFjNo-gpt-4-rag']")
        link.click()
        time.sleep(30)
        self.input_box = self.driver.find_element(By.ID, "prompt-textarea")


    def loop_through_prompts(self):
        try:
            # TO-DO: count, .csv_file as a hyperparameter
            full_csv = self.is_csv_full()
            count = 0
            while full_csv == False:
                for row in self.data:

                    # Checks if current row does not have a response or citation
                    if len(row) > 4 and (row[4] == 'GPT 4 RAG' or not row[4].strip() or row[5] == '[]') and count < 7:
                        count += 1
                        cur_prompt = row[3]
                        
                        # Processes str of prompt and sends to GPT
                        print("Entering prompt to GPT: ", cur_prompt)
                        cur_prompt = cur_prompt.replace("'", "\\'")
                        self.send_prompt_to_chatgpt(str(cur_prompt))
                        time.sleep(30)

                        # TO-DO: Create time-out (max of 150 seconds before opening new browser?)

                        # Lets response load until "Stop generating" button disappears
                        while self.is_button_present("//button[@aria-label='Stop generating']"):
                            time.sleep(20)

                        time.sleep(30)
                        # TO-DO: Handle entries where the only url is openai
                        # If GPT-4 raises an error, writes current conversation into .csv file and opens new chat
                        if "There was an error generating a response" in self.driver.page_source or "network error" in self.driver.page_source or "Error in message stream" in self.driver.page_source:
                            print("Loading error. Will read current conversation into csv, then generate new page")
                            time.sleep(45)
                            conversation = self.return_chatgpt_conversation()
                            self.process_conversation(conversation)
                            self.data = self.read_csv(self.path_to_csv)


                            print("Read items into csv. Loading new page...")
                            link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/g/g-cy3cGFjNo-gpt-4-rag']")
                            link.click()
                            time.sleep(60)
                            self.input_box = self.driver.find_element(By.ID, "prompt-textarea")
                        else:
                            print("No errors, next response")
                    elif count == 7:
                        print("Max count reached")
                        time.sleep(45)
                        conversation = self.return_chatgpt_conversation()
                        self.process_conversation(conversation)
                        self.data = self.read_csv(self.path_to_csv)

                        print("Read items into csv. Loading new page...")
                        link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/g/g-cy3cGFjNo-gpt-4-rag']")
                        link.click()
                        time.sleep(60)
                        self.input_box = self.driver.find_element(By.ID, "prompt-textarea")
                        count = 0
                        

                # Once all queries are made, fills out .csv with data
                print("Filling in .csv")
                conversation = self.return_chatgpt_conversation()
                self.process_conversation(conversation)
                self.data = self.read_csv(self.path_to_csv)

                full_csv = self.is_csv_full()
            self.end_session()
        
        # Opens new chat in case of any miscellaneous behavior
        except:
            print("Except condition")
            conversation = self.return_chatgpt_conversation()
            self.process_conversation(conversation)
            self.data = self.read_csv(self.path_to_csv)

            full_csv = self.is_csv_full()
            self.end_session()  

    def find_available_port(self):
        """ This function finds and returns an available port number on the local machine by creating a temporary
            socket, binding it to an ephemeral port, and then closing the socket. """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
        

    def launch_chrome_with_remote_debugging(self, port, url):
        """ Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
            provided url """

        def open_chrome():
            chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {url}"
            os.system(chrome_cmd)

        chrome_thread = threading.Thread(target=open_chrome)
        chrome_thread.start()


    def setup_webdriver(self, port):
        """  Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
             with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        # driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=chrome_options)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                  options=chrome_options)
        return driver
    

    def is_button_present(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
            return True
        except:
            return False

    def send_prompt_to_chatgpt(self, prompt):
        """ Sends a message to ChatGPT and waits for 20 seconds for the response """
        try:
            self.input_box.click()
            self.driver.execute_script(f"arguments[0].value = '{prompt}';", self.input_box)
            self.input_box.send_keys(Keys.RETURN)
            self.input_box.submit()
        except:
            print("Error loading screen.. Will open new one")
            time.sleep(45)
            conversation = self.return_chatgpt_conversation()
            self.process_conversation(conversation)
            self.data = self.read_csv(self.path_to_csv)

            print("Read items into csv. Loading new page...")

            link = self.driver.find_element(By.CSS_SELECTOR, "a[href='/g/g-cy3cGFjNo-gpt-4-rag']")
            link.click()

            time.sleep(90)
            self.input_box = self.driver.find_element(By.ID, "prompt-textarea")
            self.send_prompt_to_chatgpt(prompt)


    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, every even pair are the submitted questions (prompts) and odd pair of items are chatgpt response
        Ex: [question1, question1, response1, response1, question2, question2, response2, response2]
        """
        conversation = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
        for item in conversation:
            print(item.text)
        return conversation
    

    def process_conversation(self, conversation):
        """
        Writes responses and URLs from conversation to .csv ifile
        """
        for i in range(0, len(conversation), 4):  
            prompt = conversation[i].text
            for sublist in self.data:
                if len(sublist) >= 4 and sublist[3] in prompt:
                    print("Entering data into .csv row")
                    print("Question:", prompt)
                    response_element = conversation[i+2]
                    print("Response:", response_element.text)
                    sublist[4] = response_element.text
                    print(sublist[4])
                    print("URLs:")
                    urls = self.return_url_citations(response_element)
                    print(urls)
                    sublist[5] = urls

        self.write_csv(self.path_to_csv)
 

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n")


    def return_last_response(self):
        """ :return: the text of the last chatgpt response """

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value='div.text-base')
        return response_elements[-1]
    
    
    def return_url_citations(self, response_element):
        """Retrieves URLs from response"""
        html_content = response_element.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, 'html.parser')
        a_tags = soup.find_all('a')
        url_links = [a.get('href') for a in a_tags if a.has_attr('href')]
        return(url_links)
    

    def wait_for_human_verification(self):
        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            user_input = input(
                "Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again. Make sure page is fully loaded before entering: ").lower()

            if user_input == 'y':
                print("Continuing with the automation process...")
                break
            elif user_input == 'n':
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")


    def end_session(self):
        while True:
            print("Saving current data, ending session")
            time.sleep(10)
            conversation = self.return_chatgpt_conversation()
            self.process_conversation(conversation)
            self.quit()
            sys.exit(0)

    def quit(self):
        """ Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        self.driver.close()
        self.driver.quit()





from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from handler.chatgpt_selenium_automation import ChatGPTAutomation
import time
import csv
import threading



def get_prompts_from_csv(path):
    import csv

    prompts = []

    # Open the CSV file and read it
    with open(path, newline='') as csvfile:

        csv_reader = csv.reader(csvfile)

        # Skip the header if your CSV has one
        next(csv_reader)

        # Iterate over the rows in the CSV
        for row in csv_reader:
            if row:  # Check if row is not empty
                # Assuming question is in fourth column
                prompts.append(row[3])  # Append the second column data
    return prompts

options = Options()
options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
#                          options=options)
chrome_driver_path = r"/Users/allisoncasasola/medical-ai/chromedriver-mac-arm64/chromedriver"
chrome_path = r'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"'
csv_path = "data/test.csv"
# prompts = get_prompts_from_csv(csv_path)
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path)

test = chatgpt.test_1()
print("test: ", test)
test = test.replace("'", "\\'")
test = test.replace("\n", "\\n")

chatgpt.populate_conversations(5, 5)

# chatgpt.loop_through_prompts()

# thread1 = threading.Thread(target=chatgpt.loop_through_prompts())
# thread2 = threading.Thread(target=chatgpt.end_session())

# Start threads
# thread2.start()
# thread1.start()

# Join threads to wait for them to finish (optional, if you want the main program to wait for these threads)
# thread1.join()
# thread2.join()
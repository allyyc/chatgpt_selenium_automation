# Automating GPT-4's RAG with Selenium

This is a Python project forked from [https://github.com/Michelangelo27/chatgpt_selenium_automation] that aims to automate interactions with OpenAI's ChatGPT using Selenium WebDriver. Currently, it requires human interaction for log-in and human verification. It handles launching Chrome, connecting to ChatGPT, sending prompts, and retrieving responses. This tool can be useful for experimenting with ChatGPT or building similar web automation tools.


## Prerequisites

1. Make sure you have installed the required libraries, as specified in the `requirements.txt` file.
2. Download the appropriate version of `chromedriver.exe` and save it to a known location on your system.
3. This project only accepts data in the form of a .csv file. In your .csv file, make sure that prompts are in the fourth column, and there is a fifth and sixth column that are empty. These columns will be filled by GPT-4 responses and citations, respectively.
4. The path to the .csv is currently hard-coded as data/questions.csv in the handler/chatgpt_selenium_automation.py file. Make sure to change this to fit your data.

##  How to run

 ```python main.py```
   
   
## Notes

After instantiating the ChatGPTAutomation class, chrome will open up ChatGPT, and it will require you to manually complete the register/ log-in / Human-verification. **Log-in AND make sure that you are using appropriate GPT-4 (in this case, we are using the custom GPT 4 RAG).**  _Before_ you tell the program to continue by typing 'y,' make sure that the page fully loads. After Those steps, the program will be able to continue autonomously.

## Note on Changing Tabs or Conversations

Please be aware that changing tabs or switching to another conversation while the script is running might cause errors or lead to the methods being applied to unintended chats. For optimal results and to avoid unintended consequences, it is recommended to avoid to manually interact with the browser (after the log-in/human verification) while the automation script is running.


   
## Note on Errors and Warnings

While running the script, you may see some error messages or warnings in the console, such as:
- DevTools listening on ws://...
- INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
- ERROR: Couldn't read tbsCertificate as SEQUENCE
- ERROR: Failed parsing Certificate
   

These messages are related to the underlying libraries or the browser, and you can safely ignore them if the script works as expected. If you encounter any issues with the script, please ensure that you have installed the correct dependencies and are using the correct ChromeDriver version compatible with your Chrome browser.

   
   


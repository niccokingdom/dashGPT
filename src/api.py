import openai
import logging
import re
from time import sleep
from subprocess import check_call, check_output, STDOUT, CalledProcessError
from utils import *
from text import *

class API:
    def __init__(self, open_ai_key, model= "gpt-3.5-turbo", temperature=0):
        self.logger = logging.getLogger("log")
        self.open_ai_key = open_ai_key
        self.model = model
        self.temperature = temperature
        self.history = ""
        self.generated_code = ""

        logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def chat_completion(self, temperature):
        '''
        Call to gpt API for chat completion
        '''
        response =  openai.ChatCompletion.create(
                        model=self.model,
                        messages=self.history,
                        temperature=self.temperature,
                        api_key=self.open_ai_key
                    )
        return response.choices[0].message["content"]



    def generate_goals_code(self, goals):
        '''
        Function to generate final code based on input list of goals. Calls gpt API
        '''
        goalStr = ",".join(goals)
        self.history = [
            {"role": "system", "content": "You are a python program that: " + goalStr},
            {"role": "user", "content": "Do not return anything so far, wait for further instruction"},
            {"role": "assistant", "content": "I am waiting for the next instruction"}
        ]
        for i,goal in enumerate(goals):

            self.history.append({"role": "user", "content": f"Generate python code for: {goal}. Only respond with your Python code. Do not include any other explanatory text in your response."})
            
            self.logger.info(f"Generating code for goal {i+1}...")

            response = self.chat_completion(self.temperature) # API CALL

            self.history.append({"role": "assistant", "content": response})
            self.generated_code += "\n\n" + response

        #Strips undesired chars
        self.generated_code = self.generated_code.replace("`","").lstrip("\n").lstrip("python")

        self.logger.info("Code generation completed")

        #Save generate code
        self.logger.info("generating file generated_code.py...")
        with open('generated_code.py', 'w') as file:
            file.write(self.generated_code)
        self.logger.info("generated_code.py created successfully!")

        #Save history
        with open('history.txt', 'w') as file:
            for message in self.history:
                file.write(str(message) + '\n')

        return self.generated_code
    


    def optimise(self):
        '''
        Function to Optimise generated code
        '''
        self.history.append(
            {"role": "user", "content": f"Taking in account the goals mentioned so far optimise the below Python code\nOnly respond with your Python code and do not include any other explanatory text in your response.\nCode:\n{self.generated_code}"}
        )
        self.logger.info(f"Optimising code...")
        self.generated_code = self.chat_completion(self.temperature) # API CALL
        self.generated_code = self.generated_code.replace("`","").lstrip("\n").lstrip("python")
        self.logger.info(f"Optimisation completed")

        self.history.append({"role": "assistant", "content": self.generated_code})

        #Update history
        with open('history.txt', 'w') as file:
            for message in self.history:
                file.write(str(message) + '\n')

        #Update generated code with the opt version
        self.logger.info("generating file code.py...")
        with open('generated_code.py', 'w') as file:
            file.write(self.generated_code)
        self.logger.info("generated_code.py updated successfully!")

        return self.generated_code



    def check_execution_debug(self):
        '''
        Function to Verify execution of the code and to auto debug if not working correctly using the API
        ''' 
        Done = False
        i=0
        while Done==False: 
            try:
                i+=1
                self.logger.info(f"Verifying correct execution of the code, iteration {i}...")
                check_output(['python', 'generated_code.py'], stderr=STDOUT)
                Done=True
                if Done == True:
                    break
            except CalledProcessError as e:
                self.logger.info(f"Script failed with error code {e.output}")

                # In case of fail debug with API
                self.history.append(
                    {"role": "user", "content": f"I found the below error when executing the Python code\nProvide the corrected python code that will work\nOnly respond with your Python code. Do not include any other explanatory text in your response.\nError:\n{e.output}"}
                )
                self.logger.info(f"Debugging code, iteration {i}...")

                self.generated_code = self.chat_completion(self.temperature) # API CALL
                self.generated_code = self.generated_code.replace("`","").lstrip("\n").lstrip("python")

                self.history.append({"role": "assistant", "content": self.generated_code})

                #Update history
                with open('history.txt', 'w') as file:
                    for message in self.history:
                        file.write(str(message) + '\n')

                #Update generating code after debugging
                with open('generated_code.py', 'w') as file:
                    file.write(self.generated_code)



    def best_google_searches(self,purpose):
        """
        Function that takes a objective, calls the API and returns a list with the associated best 3 google searches
        """

        self.history = [
                    {"role": "system", "content": "You are a helpul assistant that provide only numeric bullet points in output"},
                    {"role": "user", "content": f"provide the 3 best google searches for the following objective: {purpose}"}
                ]
        searches = self.chat_completion(temperature=0.7)
        searches = [search for search in searches.split("\n") if "1." in search or "2." in search or "3." in search]

        for i in range(len(searches)):
            if '"' in searches[i]:
                searches[i] = searches[i].replace('"','')
                searches[i] = searches[i].split(".")[1].lstrip(" ")
        return searches




    def summarise_texts(self, texts, purpose, max_tokens=3000):
        """
        Function that takes a list of texts, calls the API and returns a summary
        """
        summaries = []

        for k,text in enumerate(texts): # Each body of websites

            tot_tokens, pieces = split_text_gpt(text, max_tokens=max_tokens)

            self.logger.info(f"Splitted body {k+1}/{len(texts)} of {tot_tokens} tokens in {len(pieces)} chunks")
            #speak(f"Text {k+1} of {len(texts)} has been splitted in {len(pieces)} chunks to start the summarisation")

            for j,piece in enumerate(pieces): # Each piece of body
                self.history = [
                    {"role": "system", "content": "You are a helpul assistant that extracts main informations from a text based on a specific objective"},
                    {"role": "user", "content": f"I need you to extract the main informations from the text that I will provide knowing that my goal is: {purpose}. Phrase in a clear and readable way"},
                    {"role": "assistant", "content": "Please provide the text to summarise"}
                ]
                self.history.append({"role": "user", "content": piece})

                self.logger.info(f'    Summary for chunk {j+1}/{len(pieces)}')

                while True:
                    try:
                        summary = self.chat_completion(temperature=0.7)
                        break
                    except:
                        self.logger.info("An error occurred. Retrying last summary in 30 seconds...")
                        sleep(5)  # Wait for 5 seconds before retrying
                summaries.append(summary)

        return " ".join(summaries)


        



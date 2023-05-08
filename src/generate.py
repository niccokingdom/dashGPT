from api import API
import logging

logger = logging.getLogger("log")
logging.basicConfig(level = logging.INFO)
gptAPI = API()

goals = [
    "Sends a google search with the following query : 'Best laptop for data scientists in 2023' and returns the first 5 website urls",
    "webscrapes the body content from the webistes for the input urls and saves it in a list of strings in output",
    "Creates a txt report where the best laptops are listed with their specs and makes a recommendation on which one to choose"
]
# Code generation
code = gptAPI.generate_goals_code(goals)

# Code optimisation
code_opt = gptAPI.optimise()
# Code verification and debugging if necessary
gptAPI.check_execution_debug()

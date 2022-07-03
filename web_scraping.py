from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from initialization import initialize
import json


# dictionary to keep all token - username, password key value pairs in memory
user_storage = {}


def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def login(driver, username, password):
    login_url = "https://app.comet.co/freelancer/signin?to=%2Ffreelancer%2Fdashboard"
    driver.get(login_url)

    # login with provided credentials
    elmnt = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[1]/div[1]/div/div[2]/div/form/div[1]/div[1]/input')))

    elmnt1 = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div[2]/div/form/div[2]/div[1]/input')))

    c_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[1]/div[1]/div/div[2]/div/form/div[3]/a[1]/button/span'))
    )

    elmnt.send_keys(username)
    elmnt1.send_keys(password)
    c_button.click()
    time.sleep(3)

    # check if valid login
    rendered_navbar_class = "freelancer-nav-bar"
    timeout = 2
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, rendered_navbar_class))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        return False

    return True


def LoginUser(username, password):
    global user_storage
    # need to login and grab the session cookie after successful authentication
    # then, return the session cookie token to the user. this way, the server manages the security
    # for us and we dont have to store any sensitive user data

    driver = initialize()
    if not login(driver, username, password):
        return ""

    # get session cookie and send that to user
    token = driver.get_cookie("session")["value"]
    if [username, password] in user_storage.values():
        user_storage = {key:val for key, val in user_storage.items() if val != [username, password]}
    user_storage[token] = [username, password]
    driver.quit()

    return token

def UserInfo(token):
    # login with saved credentials and get all of user's data
    profile_url = "https://app.comet.co/freelancer/profile"

    # initialize driver
    driver = initialize()

    # if user has not logged in before
    if not token in user_storage.keys():
        return {}
    # grab username and password from memory
    username, password = user_storage[token]

    if not login(driver, username, password):
        return ""
    # logged in

    driver.get(profile_url)
    time.sleep(3)

    browser_log = driver.get_log('performance')
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method']]

    result = {}
    # need:

    # name
    # email
    # title
    # image url
    # phone number
    # biography

    # skills array
    # for every skill name and years of exp

    # experience title
    # experience array
    # for every experience name of company, title, time and skills used there

    for event in events:
        try:
            req_type = event["params"]["type"]
            req_url = event["params"]["response"]["url"]

            if req_type == "Fetch" and req_url == "https://app.comet.co/api/graphql":
                operation_name = json.loads(driver.execute_cdp_cmd('Network.getRequestPostData', {'requestId': event["params"]["requestId"]})["postData"])["operationName"]
                data = json.loads(driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': event["params"]["requestId"]})["body"])["data"]
                # valid request, process data here

                # from AppUser operation can get name, title, image url and experience title (biography)
                if operation_name == "AppUser":
                    name = data["me"]["fullName"]
                    email = data["me"]["email"]
                    job_title = data["me"]["jobTitle"]
                    phone_number = data["me"]["phoneNumber"]
                    image_url = data["me"]["profilePictureUrl"]
                    biography = data["me"]["freelance"]["biography"]
                    result["name"] = name
                    result["email"] = email
                    result["job_title"] = job_title
                    result["phone_number"] = phone_number
                    result["image_url"] = image_url
                    result["biography"] = biography

                # from FreelancerProfileSkills operation can get skills
                if operation_name == "FreelancerProfileSkills":
                    skills_arr = []
                    for skill in data["freelance"]["skills"]:
                        skill_obj = {}
                        skill_name = skill["name"] 
                        skill_years = skill["duration"]
                        skill_obj["name"] = skill_name
                        skill_obj["years"] = skill_years
                        skills_arr.append(skill_obj)
                    result["skills"] = skills_arr

                # from FreelancerExperiences operation can get experiences
                if operation_name == "FreelancerExperiences":
                    exp_arr = []
                    for exp in data["freelance"]["experiences"]:
                        exp_obj = {}
                        exp_company_name = exp["companyName"] 
                        exp_work_period = f"From {exp['startDate'].split('T')[0]} to {exp['endDate'].split('T')[0]}"
                        exp_description = exp["description"]
                        exp_skills = []
                        for exp_skill in exp["skills"]:
                            exp_skills.append(exp_skill["name"])
                        exp_obj["company_name"] = exp_company_name
                        exp_obj["work_period"] = exp_work_period
                        exp_obj["description"] = exp_description
                        exp_obj["skills"] = exp_skills
                        exp_arr.append(exp_obj)
                    result["experiences"] = exp_arr

        except:
            pass

    return result

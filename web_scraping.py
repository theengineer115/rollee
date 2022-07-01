from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from initialization import initialize

# dictionary to keep all token - username, password key value pairs in memory
user_storage = {}

# get text attribute from element
def get_txt_attr(var, var_name):
    text = None
    try:
        text = var.text
    except Exception as e:
        print(f'failed to get {var_name}')
        print(f'error code {e}')
        print(f'{var_name} received {var}')
        pass

    return text

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

    # get the required information
    name = 'Empty or Error'

    title = 'Empty or Error'

    profile_pic = 'Empty or Error'

    experience_title = 'Empty or Error'

    s_name = 'Empty or Error'

    years = 'Empty or Error'

    infos = []

    skills = []

    time.sleep(3)

    dict_info = {}

    # grab the html for parsing
    html = driver.page_source
    # close the page
    driver.quit()
    # begin parsing
    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find('div', {'class': 'd-flex flex-column MeView_main_rWiQ9'})

    profile = main_div.find('div', {'class': 'flex'})
    #####################################################################

    profile_pic = main_div.find('div', {'class': 'v-image__image v-image__image--cover'})
    profile_pic = profile_pic.get('style')
    profile_pic = profile_pic.replace('background-image: url("', '')

    profile_pic = profile_pic.replace('"); background-position: center center;', '')
    #####################################################################

    name = profile.find('div', {'class': 'v-card__title headline font-weight-bold pa-0 pt-1 FreelancerDetails_fullName_1BIGR'})

    name = get_txt_attr(name, 'name')

    title = profile.find('div', {'class': 'v-card__subtitle black--text pt-0 pb-2 FreelancerDetails_subtitle_2yLrJ'})

    title = get_txt_attr(title, 'title')
    #####################################################################

    divs = profile.find_all('div', {'class': 'FreelancerDetails_infos_2weto'})

    for div in divs:

        info = None
        info = get_txt_attr(div, 'info')

        infos.append(info)
    #####################################################################

    dict_info['name'] = name
    dict_info['title'] = title
    dict_info['image'] = profile_pic
    dict_info['general_info'] = infos
    #####################################################################

    div_skills = main_div.find('div', {'class': 'mb-6 v-card v-sheet theme--light FreelancerProfileSkills_freelancerProfileSkills_3L4js'})
    inside_div = div_skills.find('div', {'class': 'd-flex flex-row flex-wrap align-center mt-1 FreelancerSkillsField_skills_-bj0l'})
    spans = inside_div.find_all('span', {'class': 'body-3 v-chip v-chip--no-color v-chip--outlined theme--light v-size--default CChipTalent_root_3Xor7 FreelancerSkillsField_chip_63cvk'})

    for span in spans:

        skills_2 = []
        skill_name = span.find('span', {'class': 'v-chip__content'})
        skill_name = skill_name.find_all('span')

        try:
            s_name = get_txt_attr(skill_name[0], 'Skill Name')
        except Exception as e:
            print(f'error code {e}')
            pass

        try:
            years = get_txt_attr(skill_name[3], 'Years of experience')
        except Exception as e:
            print(f'error code {e}')
            pass

        skills_2.append(s_name)
        skills_2.append(years)
        skills.append(skills_2)

    dict_info['skills'] = skills
    #####################################################################

    experience = main_div.find('div', {'class': 'pa-4 pt-3 mb-6 v-card v-sheet theme--light FreelancerFullResume_freelancerExperiences_35IPk'})

    experience_titles = experience.find_all('div')

    temp_exp_title = None

    for experience_title in experience_titles:
        try:
            if experience_title.has_attr('data-cy-freelancer-biography'):
                temp_exp_title = get_txt_attr(experience_title, "experience title")
        except Exception as e:
            print(f'error code {e}')
            pass

    dict_info['Exp_Title'] = temp_exp_title

    experiences = experience.find('div', {'id': 'freelancerProfileExperiences'})

    temp_list = []

    try:
        list_experiences = experiences.select("div[id^=experience-]")

        for l_exp in list_experiences:

            div_exp = None
            work_category = None

            div_exp = l_exp.find('div', {'class': 'd-flex body-2 mb-2 FreelancerExperiences_header_1jR2S'})

            work_category = div_exp.find('div', {'class': 'd-flex align-center overline secondary--text'})
            work_category = get_txt_attr(work_category, 'Work Category')

            work_title = div_exp.find('span', {'class': 'font-weight-semi-bold pr-1 title'})
            work_title = get_txt_attr(work_title, 'Work Title')

            work_years = div_exp.find('div', {'class': 'body-2 secondary--text text--pre-line caption'})
            work_years = get_txt_attr(work_years, 'Work Years')

            work_skills = l_exp.find('div', {'class': 'FreelancerExperiences_skills_1N6ZB'})

            work_skills_ = []
            try:
                work_skills_ = work_skills.select("span[class^=Tag_name]")
            except Exception as e:
                print(e)


            work_skills__ = []

            try:
                if len(work_skills_) > 0:
                    for w_s in work_skills_:
                        temp_var = None
                        temp_var = w_s
                        temp_var = get_txt_attr(temp_var, 'work skill')
                        work_skills__.append(temp_var)
            except Exception as e:
                print(e)
            

            temp_list.append(work_category)
            temp_list.append(work_title)
            temp_list.append(work_years)
            temp_list.append(work_skills__)
    except:
        pass

    dict_info['experiences'] = temp_list

    # return final user info
    return dict_info

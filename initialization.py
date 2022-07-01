from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
import json

def send(driver, cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    return response.get('value')

def add_script(driver, script):
    send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})

def initialize():
    opts = Options()

    # various options and security features
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36")
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument("--incognito")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    prefs = {'profile.default_content_setting_values.notifications': 2}
    opts.add_experimental_option('prefs', prefs)
    opts.add_argument('--no-sandbox')
    opts.add_argument('--single-process')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument("--headless")
    opts.add_argument('--disable-blink-features=AutomationControlled')

    # specify path to the chromedriver executable here
    driver = webdriver.Chrome("/path/to/chromedriver",  chrome_options=opts)

    WebDriver.add_script = add_script

    # security scripts to keep browser undetected
    driver.add_script("Object.defineProperty(navigator, 'webdriver', {get: () => false,});")
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("window.chrome = { runtime: {} };")
    driver.execute_script(
        "window.navigator.permissions.query = (parameters) => ( parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters) );")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {  get: () => [1, 2, 3, 4, 5], });")
    driver.execute_script(
        "WebGLRenderingContext.prototype.getParameter = function(parameter) { if (parameter === 37445) { return 'Intel Open Source Technology Center'; } if (parameter === 37446) { return 'ANGLE (Intel(R) HD Graphics 630 Direct3D11 vs_5_0 ps_5_0)'; }};")

    return driver

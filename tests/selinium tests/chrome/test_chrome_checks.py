import pytest
from selenium.webdriver import Chrome
import socket
# requires snappy to be running


@pytest.fixture
def browser():
    # Initialize ChromeDriver
    driver = Chrome()
    # Wait implicitly for elements to be ready before attempting interactions
    driver.implicitly_wait(10)

    yield driver

    # For cleanup, quit the driver
    driver.quit()


def test_successful_login(browser):
    # test the login page works with default user
    user_name = 'tom'

    browser.get("192.168.1.70:5000")
    username = browser.find_element_by_name("q")
    submit = browser.find_element_by_name("submit")
    username.send_keys(user_name)
    submit.click()
    wait = browser.implicitly_wait(10)
    title = browser.title
    assert title == 'Snappy'


def test_unsuccessful_login(browser):
    # test the login page works with default user
    user_name = 'tom1'

    browser.get("192.168.1.70:5000")
    username = browser.find_element_by_name("q")
    submit = browser.find_element_by_name("submit")
    username.send_keys(user_name)
    submit.click()
    wait = browser.implicitly_wait(10)
    title = browser.title
    # check for error messages
    assert title != 'Snappy'



def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

print(get_ip())
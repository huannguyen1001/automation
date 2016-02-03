import FrameworkLibrary
import unittest, time, sys, os
from Environment.PyDriver import *
from Common import *
from selenium.webdriver.common.keys import Keys
from flaky import flaky

@flaky(max_runs=3, min_passes=1)
class TestCase(unittest.TestCase):

    def setUp(self):
        self.scriptname = os.path.abspath(__file__)
        log('Executing ' + self.scriptname)
        configfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Config', 'config.ini')
        self.driver = PyDriver(configfile)
        self.driver.implicitly_wait(30)
        log('Loaded webdriver successfully...')
    
    def test_google_search_with_python(self):
        log('Start test execution with script: ' + self.scriptname)
        driver = self.driver
        driver.get("http://www.google.com")
        search = driver.find_element_by_name('q')
        search.send_keys('sauce labs')
        search.send_keys(Keys.RETURN)
        time.sleep(5)
        self.assertIn("sauce labs", driver.title)
        driver.get_screenshot_as_file(screen_shot_folder + 'google_search.png')
        log('Finished test execution with script: ' + self.scriptname)

    def tearDown(self):
        if sys.exc_info()[0]:
            path = self.driver.logfolder + os.path.splitext(os.path.basename(__file__))[0] + '/'
            if not os.path.isdir(path): os.mkdirs(path, 0755)
            test_method_name = self._testMethodName
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.driver.save_screenshot(path + test_method_name + "-" + now + ".png")
        self.driver.quit()
        log('Exit browser')

if __name__ == '__main__':
    test = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    result = unittest.TextTestRunner(stream=sys.stdout).run(test)

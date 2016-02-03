import os, time
import configparser
from testconfig import config
from selenium import webdriver as Wd
from appium import webdriver as Md
from datetime import datetime
from Common import *
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.events import AbstractEventListener
from selenium.webdriver.support.events import EventFiringWebDriver

configTest = None

class ScreenshotListener(AbstractEventListener):
    def on_exception(self, exception, driver):
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_name = screen_shot_folder + "screenshot_" + now + '.png'
        driver.get_screenshot_as_file(screenshot_name)
        log("Exception screenshot saved as '%s'" % screenshot_name)


class TestConfig(object):
    def __init__(self, configfile=None):
        self.nose_config = True
        try: bw = config['config']['browser'] 
        except: self.nose_config = False
        if self.nose_config == False:
            if (not configfile) or (not os.path.isfile(configfile)):          
                configfile = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../Config/', 'config.ini')
            self.settings = configparser.ConfigParser()
            self.settings._interpolation = configparser.ExtendedInterpolation()
            self.settings.read(configfile)

    def getConfig(self, section, configtype):
        if self.nose_config: 
            try: tmp=config[section][configtype]
            except: tmp=''
        else:
            try: tmp=self.settings.get(section, configtype)
            except: tmp =''
        return tmp

def PyDriver(configfile=None):
    global configTest
    configTest = TestConfig(configfile)
    browser=configTest.getConfig('config', 'browser').lower()
    if (browser=='iphone') or (browser=='android'):
        d = MDriver(browser)
        driver = EventFiringWebDriver(d, ScreenshotListener())
    else:
        d = WDriver(browser)
        driver = EventFiringWebDriver(d, ScreenshotListener())
    return driver

def ProxySetting(browser, dc):
    try:
        myProxy = configTest.getConfig('config', 'webproxy')
    except: 
        myProxy = None
    if myProxy:
        if browser=='firefox':
            FirefoxProxy = Proxy({
               'proxyType': ProxyType.MANUAL,
               'httpProxy': myProxy,
               'ftpProxy': myProxy,
               'sslProxy': myProxy,
               'noProxy': '127.0.0.1' # set this value as desired
               })
            FirefoxProxy.add_to_capabilities(dc)
        elif browser=='chrome':
            ChromeProxy = ['--proxy-server ' + myProxy]
            dc['chrome.switches'] = ChromeProxy
        elif browser=='ie':
            IEProxy = {
                "httpProxy":myProxy,
                "ftpProxy":myProxy,
                "sslProxy":myProxy,
                "noProxy":None,
                "proxyType":"MANUAL",
                "class":"org.openqa.selenium.Proxy",
                "autodetect":False
                }
            dc['proxy'] = IEProxy
    return dc

def set_browser_profile(browser):
    if browser=='firefox':
        profile = Wd.FirefoxProfile();
        profile.set_preference("browser.startup.homepage", "about:blank");
        profile.set_preference("startup.homepage_welcome_url", "about:blank");
        profile.set_preference("startup.homepage_welcome_url.additional", "about:blank");
    return profile

def desired_cap(browser):
    platform = configTest.getConfig('config', 'platform')
    version = configTest.getConfig('config', 'version')
    device = configTest.getConfig('config', 'device')
    desired_capabilities = {}
    if platform.lower() == "ios":
        desired_capabilities['browserName'] = 'Safari'
        desired_capabilities['deviceName'] = device
        desired_capabilities['platformName'] = platform
        desired_capabilities['platformVersion'] = version
    elif platform.lower() == "android":
        desired_capabilities['platformName'] = platform
        desired_capabilities['platformVersion'] = version
        desired_capabilities['browserName'] = browser
        desired_capabilities['deviceName'] = device
    elif browser == "ie":
        desired_capabilities=DesiredCapabilities.INTERNETEXPLORER.copy()
        desired_capabilities['platform'] = platform
    elif browser == "chrome":
        desired_capabilities=DesiredCapabilities.CHROME.copy()
        desired_capabilities['platform'] = platform
    elif browser == "firefox":
        desired_capabilities=DesiredCapabilities.FIREFOX.copy()
        desired_capabilities['platform'] = platform
    elif browser == "phantomjs":
        desired_capabilities=DesiredCapabilities.PHANTOMJS.copy()
        desired_capabilities['platform'] = platform
    elif browser == "htmlunit":
        desired_capabilities=DesiredCapabilities.HTMLUNIT.copy()
        desired_capabilities['platform'] = platform
    elif browser == "safari":
        desired_capabilities=DesiredCapabilities.SAFARI.copy()
        desired_capabilities['platform'] = platform
    elif browser == "iphone_iosdriver":
        desired_capabilities=DesiredCapabilities.IPHONE.copy()
        desired_capabilities['platform'] = platform
    elif browser == "android_iosdriver":
        desired_capabilities=DesiredCapabilities.ANDROID.copy()
        desired_capabilities['platform'] = platform
        #desired_capabilities['appPackage'] = 'com.android.chrome'
        #desired_capabilities['appActivity'] = 'com.google.android.apps.chrome.Main'
    desired_capabilities['version'] = version
        #desired_caps['udid'] = udid
        #desired_caps['udid'] = 'emulator-5554'
    dc = ProxySetting(browser, desired_capabilities)
    return dc

class WDriver(Wd.Remote):
    def __init__(self, browser):
        testenv = configTest.getConfig('config', 'testenv').lower()
        if testenv=='local':
            hub = configTest.getConfig('config', 'hubip') + ':' + configTest.getConfig('config', 'hubport')
            command_executor = 'http://'+hub+'/wd/hub'
        elif testenv=='saucelab':
            username = configTest.getConfig('saucelab', 'sauce_username')
            access_key = configTest.getConfig('saucelab', 'sauce_accesskey')
            command_executor='http://'+username+':'+access_key+'@ondemand.saucelabs.com:80/wd/hub'
        browser_profile=None
        keep_alive=False
        desired_capabilities = desired_cap(browser)
        webdriver_success = 0
        numRetry = 0
        driverTimeout = configTest.getConfig('config', 'drivertimeout')
        driverRetry = configTest.getConfig('config', 'driverretry')
        self.logfolder = configTest.getConfig('system', 'logfolder')
        self.drivername = 'Selenium'
        while (webdriver_success==0) and (numRetry<driverRetry):
            webdriver_success = 1
            numRetry+=1
            try:
                super(WDriver, self).__init__(command_executor, desired_capabilities)
            except:
                print "webdriver is busy, retry..." + str(numRetry) + " times after " + driverTimeout + " secs"
                webdriver_success = 0
            time.sleep(int(driverTimeout))


class MDriver(Md.Remote):
    def __init__(self, browser):
        testenv = configTest.getConfig('config', 'testenv').lower()
        if testenv=='local':
            hub = configTest.getConfig('config', 'hubip') + ':' + configTest.getConfig('config', 'hubport')
            command_executor = 'http://'+hub+'/wd/hub'
        elif testenv=='saucelab':
            username = configTest.getConfig('saucelab', 'sauce_username')
            access_key = configTest.getConfig('saucelab', 'sauce_accesskey')
            command_executor='http://'+username+':'+access_key+'@ondemand.saucelabs.com:80/wd/hub'
        browser_profile=None
        proxy=None
        keep_alive=False
        desired_capabilities=desired_cap(browser)
        webdriver_success = 0
        numRetry = 0
        driverTimeout = configTest.getConfig('config', 'drivertimeout')
        driverRetry = configTest.getConfig('config', 'driverretry')
        self.logfolder = configTest.getConfig('system', 'logfolder')
        self.drivername = 'Appium'
        while (webdriver_success==0) and (numRetry<driverRetry):
            webdriver_success = 1
            numRetry+=1
            try:
                super(MDriver, self).__init__(command_executor, desired_capabilities, browser_profile, proxy, keep_alive)
            except:
                print "webdriver is busy, retry..." + str(numRetry) + " times after "+driverTimeout+" secs"
                webdriver_success = 0
            time.sleep(int(driverTimeout))

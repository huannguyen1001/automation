import time, os
import configparser
import urllib2, json
from testconfig import config
from urlparse import urlparse, urljoin


screen_shot_folder = '/var/screenshot/python/' #os.path.dirname(__file__) + '/../screenshot/'

def log(msg):
    print(time.strftime("%H:%M:%S") + ": " + msg)

def get_node_hostname(session_id, configfile):
    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read(configfile)
    hub = settings.get('config', 'hubIP') + ':' + settings.get('config', 'hubPort')
    hub_url = 'http://' + hub
    fragment = '/grid/api/testsession?session=%s' % session_id
    query_url = urljoin(hub_url, fragment)
    req = urllib2.Request(url=query_url)
    resp = urllib2.urlopen(req).read()
    json_blob = json.loads(resp)
    if 'proxyId' in json_blob:
        proxy_id = json_blob['proxyId']
        parse_result = urlparse(proxy_id)
        print parse_result.port
        return parse_result.hostname
    else:
        raise Exception('Failed to get hostname. Is Selenium running locally? hub response: %s' % resp)

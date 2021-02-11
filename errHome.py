import configparser
import os
import pysonofflanr3.cli
import requests

from bs4 import BeautifulSoup

from errbot import BotPlugin, botcmd, arg_botcmd, webhook


class ErrHome(BotPlugin):
    """
    Controlling some home devices
    """

    def activate(self):
        """ 
        Loading config information
        """
        super().activate() 
        
        HOME = os.path.expanduser("~") 
        CONFIGDIR = f'{HOME}/.mySocial/config' 
        section = 'Estudio' 
        config = configparser.ConfigParser() 
        config.read(f'{CONFIGDIR}/.rssSonoff') 
        api_key = config.get(section,'api_key') 
        device_id = config.get(section,'device_id') 
        host = config.get(section,'host') 
        
        self.config = {'host':host, 'device_id':device_id, 'api_key':api_key}


    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def on(self, message, args):
        """A command to send the switch on command to the sonnoff""" 
        pysonofflanr3.cli.switch_device(self.config, None, "on")


    @botcmd(split_args_with=None)
    def off(self, message, args):
        """A command to send the switch off command to the sonnoff""" 
        pysonofflanr3.cli.switch_device(self.config, None, "off")


    @botcmd(split_args_with=None)
    def listIPs(self, message, args):
        """A command to list the IPs connected to the router Mistrastar""" 
        import base64
        import keyring 

        ip='192.168.1.1' 
        host = f'http://{ip}/'
        user = '1234' 
        password = keyring.get_password(ip, user)
        auth = user + ':' + password 
        sessionKey = base64.b64encode(auth.encode()) 
        data = {'sessionKey': sessionKey, 'pass':''} 
        r = requests.post(host + 'login-login.cgi', data=data) 
        
        # Get cookies (interested in SESSION) 
        session = r.cookies 
        result = requests.get(host + 'networkmap.html',  cookies=session) 
        soup = BeautifulSoup(result.content, features="lxml") 
        imgs = soup.find_all('img') 
        listIPs = {} 
        # We are using a dict because there were some duplicates
    
        for img in imgs:
            oc = img.get('onclick')
            if oc and (oc.find('showElement')>=0): 
                data = eval(oc[11:-1])
                listIPs[data[2]] = data
        
        for ip in listIPs:
            yield(f"Name: {listIPs[ip][0]}. IP: {listIPs[ip][2]}")
 

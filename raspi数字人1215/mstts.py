'''
After you've set your subscription key, run this application from your working
directory with this command: python TTSSample.py
'''
import os, requests, time
from xml.etree import ElementTree
from config import SPEECH_SERVICE_KEY, SPEECH_SERVICE_REGION, TTS_VOICE

subscription_key = SPEECH_SERVICE_KEY

class TextToSpeech(object):
    def __init__(self, subscription_key):
        self.subscription_key = subscription_key
        self.timestr = time.strftime("%Y%m%d-%H%M")
        self.access_token = None
        self.token_expiry = 0

    '''
    The TTS endpoint requires an access token. This method exchanges your
    subscription key for an access token that is valid for ten minutes.
    '''
    def get_token(self):
        # if token is still valid, do nothing
        if self.token_expiry > time.time():
            return

        fetch_token_url = f"https://{SPEECH_SERVICE_REGION}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key
        }
        try:
            response = requests.post(fetch_token_url, headers=headers, timeout=5)
            response.raise_for_status()
            self.access_token = str(response.text)
            self.token_expiry = time.time() + 9 * 60 # 9 minutes
        except requests.exceptions.RequestException as e:
            print(f"Error getting token: {e}")
            self.access_token = None
            self.token_expiry = 0

    def save_audio(self,input_text, voice_name=None):
        self.get_token() # Ensure we have a valid token
        if not self.access_token:
            print("Could not get access token, aborting TTS.")
            return None

        base_url = f'https://{SPEECH_SERVICE_REGION}.tts.speech.microsoft.com/'
        path = 'cognitiveservices/v1'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-16khz-16bit-mono-pcm',
            'User-Agent': 'YOUR_RESOURCE_NAME'
        }
        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-CN')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-CN')
        current_voice = voice_name if voice_name else TTS_VOICE
        voice.set('name', current_voice)
        voice.text = input_text
        body = ElementTree.tostring(xml_body)

        response = requests.post(constructed_url, headers=headers, data=body)
        '''
        If a success response is returned, then the binary audio is written
        to file in your working directory. It is prefaced by sample and
        includes the date.
        '''
        if response.status_code == 200:
            print("\nStatus code: " + str(response.status_code) + "\nYour TTS is ready for playback.\n")
            return response.content
            
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")
            print("Reason: " + str(response.reason) + "\n")
            return None

    def get_voices_list(self):
        # japaneast 换成自己的区域节点        
        base_url = 'https://eastus.tts.speech.microsoft.com/'
        path = 'cognitiveservices/voices/list'
        constructed_url = base_url + path
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
        }
        response = requests.get(constructed_url, headers=headers)
        if response.status_code == 200:
            print("\nAvailable voices: \n" + response.text)
        else:
            print("\nStatus code: " + str(response.status_code) + "\nSomething went wrong. Check your subscription key and headers.\n")

if __name__ == "__main__":
    app = TextToSpeech(subscription_key)
    app.get_token()
    app.save_audio("你好呀，明天有什么打算呢？")
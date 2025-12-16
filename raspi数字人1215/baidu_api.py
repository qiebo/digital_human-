from aip import AipSpeech
import time
import json
import pygame


def login():
        from config import BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY
        #根据登录信息创建百度云语音接口，以实现语音识别和语音合成
        client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)     
        print("语音api登录成功")  
        return client

def listening(client, audio_data):
    result_text = client.asr(audio_data,'wav',16000, {'dev_pid': '1537',})
    if 'result' in result_text.keys():
        info = result_text["result"][0][:-1]
        print('音识别结果：'+"|"+info+"|")
        if len(info)==0:
            return None
        return info
    else:
        print('识别失败')
        return None

def run_tts(client, text: str, vol=5, speed=5, per=0, pit=5):
    result  =  client.synthesis(text, 'zh', 1,
                                        {'vol':vol,
                                        'spd':speed,
                                        'per':per,
                                        'pit':pit})

    if not isinstance(result, dict):
        return result



if __name__ == "__main__":
    client = login()
    listening(client,"audio/man.mp3")
    # run_tts("清明时节雨纷纷！")

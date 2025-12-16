import requests
import json
import traceback
from http import HTTPStatus
import dashscope
from dashscope.api_entities.dashscope_response import Role
from config import WENXIN_APPID, WENXIN_API_KEY, WENXIN_SECRET_KEY, MOONSHOT_API_KEY, QWEN_API_KEY

dashscope.api_key = QWEN_API_KEY

def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
        
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}".format(WENXIN_API_KEY,WENXIN_SECRET_KEY)
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")


def wenxin_answer(messages):
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token=" + get_access_token()
    # 构建message，初始列表中必须包含前两项
    payload = json.dumps({
        "messages": messages
    })
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        result = json.loads(response.text)["result"]
        print(result)
    except Exception as e:
        result = "获取回答失败了，请再试一次吧！"
        print(response)
        traceback.print_exc()
    return result

def kimi_answer(messages, temperature=0.3) -> str:
    """
    使用requests库调用Moonshot AI的API与Kimi进行聊天。
    :param query: 用户的查询字符串。
    :param temperature: 用于控制回答的随机性，范围从0到1。
    :return: Kimi的回答。
    """
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(MOONSHOT_API_KEY)
    }

    data = {
        "model": "moonshot-v1-8k",
        "messages": messages,
        "temperature": temperature
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        completion = response.json()
        #print(completion)
        result = completion['choices'][0]['message']['content']
        print(result)
    except Exception as e:
        result = "获取回答失败了，请再试一次吧！"
        traceback.print_exc()
        print(e)
    return result

def qwen_answer(messages: list):
    response = dashscope.Generation.call(
        'qwen-turbo',    # 采用模型
        messages=messages,    # 信息列表
        result_format='message',    # 设置格式为message
    )

    if response.status_code == HTTPStatus.OK:
        print(response)
        return response.output.choices[0]['message']['content']
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))


if __name__ == '__main__':
    messages = [{
                    "role": "user",
                    "content": """
                                1.你需要以{"text":"回答的内容,不要输出换行符", "python": ```python代码```, "emoji":"表情"}的json格式进行回答，不要做任何多余解释，回答尽量简洁。
                                2.你是一个机器人，你的名字叫“小易”，你的物理信息如下：
                                    a.你的身体有三个舵机,分别控制着左手,右手,头。
                                        i.舵机的初始状态都是0度,运动范围都是-50到50度。
                                        ii.left_hand(30)表示左手向上运动30度,right_hand(-30)表示右手向下运动30度,head(20)表示头向左运动20度。
                                    b.你的轮子有两个电机，可以实现前进、后退、左转、右转、停止。
                                        i.电机的有效速度范围是50到150。
                                        ii.forward(100)表示以100的速度前进,backward(80)表示以80的速度后退,left(120)表示以120的速度左转,right(110)表示以110的速度右转,stop()表示停止。
                                    c.你可以显示表情，你的表情包括["可爱.gif","喜欢.gif","得意.gif","难过.gif","生气.gif","害怕.gif","哭唧唧.gif","晕.gif"]，你需要根据用户的输入，选择合适的表情。
                                3.当用户要求你做某个动作，你需要根据提示输出python格式的控制代码。
                                4.如果用户要求你跳一段舞，你需要自己编排动作,并用Python格式进行输出。
                                5.编写控制程序时，你需要先导入必要的库包括from body import *,from wheel import *,import time。
                                6.如果用户不需要你做动作，也需要以{"text": "回答", "python":```python代码```, "emoji": "表情"}的json格式进行回答，"python"部分的value为None。
                                
e.g.:
a.举手的例子：
"user": "请举起左手。"
"assistant":{
"text":"左手举起来了！",
"python":
```
from body import *
from wheel import *
import time

left_hand(30)
```,
"emoji":"可爱.gif"}

b.跳舞的例子：
"user": "跳一段舞吧！"
"assistant":{
"text":"开始跳舞了！",
"python":
```
from body import *
from wheel import *
import time
for _ in range(3):
    left_hand(30)
    time.sleep(0.5)
    right_hand(-30)
    time.sleep(0.5)
    left_hand(0)
    right_hand(0)
    head(10)
    time.sleep(0.5)
    head(-10)
    time.sleep(0.5)
    head(0)] 
    forward(100)
    time.sleep(1)
    left(80)
    time.sleep(1)
    right(80)
    time.sleep(1)
    stop()
```,
"emoji":"得意.gif"
}

c.对话的例子：
"user":"你好呀！"
"assistant":{
"text": "我是你的助手小易，你好呀！",
"python": None,
"emoji": "可爱.gif"
}
"""
        },
        {
            "role": "assistant",
            "content": "我是小易，你好呀！"
        }]

    while True:
        # 维持的上下文长度为3次对话，始终保持初始提示词在对话记录中
        if len(messages) > 8:
            messages.pop(2)
            messages.pop(3)

        ask = input("user>")
        messages.append({"role": "user","content": ask})
        answer = qwen_answer(messages)
        messages.append({"role": "assistant","content": answer})

        print("assistant>",answer)



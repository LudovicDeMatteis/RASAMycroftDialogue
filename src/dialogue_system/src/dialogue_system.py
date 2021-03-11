#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.agent import Agent
from rasa_core.utils import EndpointConfig
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.policies.keras_policy import KerasPolicy
import json
import re

import rospy
import rospkg
from std_msgs.msg import String
from boole_msgs.srv import SetPlatformStateSrv



voice_pub = rospy.Publisher('/speak', String, queue_size=2)
set_emotion_service = rospy.ServiceProxy('/set_emotion_service', SetPlatformStateSrv)
res_path = rospy.get_param('dialogue_res_path')


interpreter = RasaNLUInterpreter(res_path+"/models/default/nlu")
agent = Agent.load(res_path+"/models/default/dialogue",
    interpreter=interpreter,
    action_endpoint=EndpointConfig(url=rospy.get_param('action_server_url')))
# interpreter = RasaNLUInterpreter(rospkg.RosPack().get_path('dialogue_system')+"/res/models/default/nlu")
# agent = Agent.load(rospkg.RosPack().get_path('dialogue_system')+"/res/models/default/dialogue",
    # interpreter=interpreter,
    # action_endpoint=EndpointConfig(url=rospy.get_param('action_server_url')))



def utteranceCallback(data):
    print("[RECEIVED]: " + data.data)

    result = interpreter.parse(unicode(data.data,encoding="utf-8"))

    print("[INTENT]: " + json.dumps(result['intent'], indent=2))


    message = agent.handle_text(unicode(data.data, encoding="utf-8"))
    if(message):
        text = message[0]['text']
        print(text)
        if("[" in text):
            action = text[text.find("[")+1:text.find("]")]
            print(action)
            if("EXPR" in action):
                expression = action.replace("EXPR: ", "")
                set_emotion_service(state=expression, timeout=4500, restore=False)
                voice = re.sub('\s?\[.*?\]', '', text).strip()
                print(voice)
                voice_pub.publish(voice)

        else:
            print("[SAY]: " + text)
            voice_pub.publish(text)
    else:
        print("no message")




def Dialogue():
    rospy.init_node('dialogue_system')
    rospy.Subscriber("/perception/raw_utterances", String, utteranceCallback)
    rospy.spin()


if __name__ == '__main__':
    try:
        Dialogue()
    except rospy.ROSInterruptException:
        pass

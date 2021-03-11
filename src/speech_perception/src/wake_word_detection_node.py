#!/usr/bin/env python3

import rospy
from std_msgs.msg import String
from boole_msgs.srv import ControlSpeechPercepSrv
from boole_msgs.srv import SetPlatformStateSrv

from precise.network_runner import Listener
from precise.util import buffer_to_audio
from precise_runner import PreciseRunner
from precise_runner.runner import ListenerEngine

import numpy as np
from playsound import playsound
import requests


chunk_size = 2048
res_path = rospy.get_param('speech_res_path')
print(res_path)
stop_speech_perception_service = rospy.ServiceProxy('stop_speech_perception_service', ControlSpeechPercepSrv)
set_emotion_service = rospy.ServiceProxy('/set_emotion_service', SetPlatformStateSrv)
speak_pub = rospy.Publisher('/speak', String, queue_size=2)



def main():
    rospy.init_node('wake_word_detection_node')
    print("node is up")


    def on_activation():
        print("activate")
        playsound(res_path+"/attention.wav")
        try:
           requests.get('http://www.google.com')
           try:
               response = stop_speech_perception_service(True)
               print(response)
           except rospy.ServiceException as exc:
               print("Service did not process request: " + str(exc))
        except requests.ConnectionError:
            print("no internet")
            speak_pub.publish("I'm sorry. I am not connected to the internet now and cannot answer")
            set_emotion_service(state="SADNESS", timeout=5500, restore=True)


    def on_prediction(conf):
        print(".")


    listener = Listener(res_path+"/stevie_10_06.pb", chunk_size)
    audio_buffer = np.zeros(listener.pr.buffer_samples, dtype=float)

    def get_prediction(chunk):
        nonlocal audio_buffer
        audio = buffer_to_audio(chunk)
        audio_buffer = np.concatenate((audio_buffer[len(audio):], audio))
        return listener.update(chunk)

    engine = ListenerEngine(listener, chunk_size)
    engine.get_prediction = get_prediction
    runner = PreciseRunner(engine, trigger_level=3, sensitivity=0.5,
        on_activation=on_activation, on_prediction=on_prediction)
    runner.start()
    print("spinning")
    rospy.spin()

if __name__ == '__main__':
    main()

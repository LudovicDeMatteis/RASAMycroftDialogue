#!/usr/bin/env python

import random
import time
import speech_recognition as sr
import pyaudio

import rospy
import rospkg
from std_msgs.msg import String
from speech_perception.srv import *

interperate_flag=True

def handle_pause(req):
    print("handling pause", req.interpret)
    interperate_flag = req.interpret
    #sprint "Returning [%s + %s = %s]"%(req.a, req.b, (req.a + req.b))
    return True


def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech from recorded from `microphone`.

    Returns a dictionary with three keys:
    "success": a boolean indicating whether or not the API request was
               successful
    "error":   `None` if no error occured, otherwise a string containing
               an error message if the API could not be reached or
               speech was unrecognizable
    "transcription": `None` if speech could not be transcribed,
               otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    print "called function"



    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    WIT_AI_KEY = "ZE7KU24JZX3XPYMOPZQEIB2HBBPCALL3"  # Wit.ai keys are 32-character uppercase alphanumeric strings

    try:
        print("interperate_flag", interperate_flag)
        if interperate_flag:
            print "fetching"
            # response["transcription"] = recognizer.recognize_google(audio)
            response["transcription"] = recognizer.recognize_wit(audio, key=WIT_AI_KEY)
        else:
            print "not interpreting"
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response



if __name__ == "__main__":
    myPyAudio=pyaudio.PyAudio()
    #print(myPyAudio.get_device_count())
    dev_index=2 #seems to pop up on 2 a good bit
    #try:
        #result = []
    for i in range(myPyAudio.get_device_count()):
        device_info = myPyAudio.get_device_info_by_index(i)
        #result.append(device_info.get("name"))
        print("device: ", device_info.get("name"))
        if(device_info.get("name") =="CD04: USB Audio (hw:1,0)"):
            dev_index=i
    #finally:
        #myPyAudio.terminate()
    #print("device: ", result)
    # create recognizer and mic instances
    print("Using device index: ", dev_index)
    recognizer = sr.Recognizer()
    microphone = sr.Microphone(device_index=dev_index)



    rospy.init_node('speech_perception')
    pub = rospy.Publisher('/perception/raw_utterances', String, queue_size=10)
    s = rospy.Service('pause_speech_perception_service', pauseSpeechPerception, handle_pause)



    while not rospy.is_shutdown():
        print "in loop"
        guess = recognize_speech_from_mic(recognizer, microphone)
        if guess["transcription"]:
            print("You said: {}".format(guess["transcription"]))
            pub.publish(guess["transcription"])

        if not guess["success"]:
            print("I didn't catch that. What did you say?\n")

        # if there was an error, stop the game
        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))

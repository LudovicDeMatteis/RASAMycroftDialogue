#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from playsound import playsound
from boole_msgs.srv import SetPlatformStateSrv

from rasa_core_sdk import Action, Tracker
from flask import Flask, jsonify, request
import requests
import json
import datetime
import numpy as np

QUEUE_SIZE=1

App = Flask(__name__)
cmd_vel_pub = rospy.Publisher("cmd_vel", Twist, queue_size=QUEUE_SIZE)
joint_state_pub = rospy.Publisher("/joints/goal", JointState, queue_size=QUEUE_SIZE)
set_emotion_service = rospy.ServiceProxy('/set_emotion_service', SetPlatformStateSrv)
res_path = rospy.get_param('dialogue_res_path')


class CollectingDispatcher(object):
    """Send messages back to user"""

    def __init__(self):
        self.messages = []

    def utter_custom_message(self, *elements):
        # type: (*Dict[Text, Any]) -> None
        """Sends a message with custom elements to the output channel."""

        message = {"text": None, "elements": elements}

        self.messages.append(message)

    def utter_message(self, text):
        # type: (Text) -> None
        """"Send a text to the output channel"""
        message = {"text": text}

        self.messages.append(message)

    def utter_button_message(self, text, buttons, **kwargs):
        # type: (Text, List[Dict[Text, Any]], Any) -> None
        """Sends a message with buttons to the output channel."""

        message = {"text": text, "buttons": buttons}
        message.update(kwargs)

        self.messages.append(message)

    def utter_attachment(self, attachment):
        # type: (Text) -> None
        """Send a message to the client with attachments."""

        message = {"text": None, "attachment": attachment}

        self.messages.append(message)

    # TODO: deprecate this function?
    # noinspection PyUnusedLocal
    def utter_button_template(self,
                              template,  # type: Text
                              buttons,  # type: List[Dict[Text, Any]]
                              tracker,  # type: Tracker
                              silent_fail=False,  # type: bool
                              **kwargs  # type: Any
                              ):
        # type: (...) -> None
        """Sends a message template with buttons to the output channel."""

        message = {"template": template, "buttons": buttons}
        message.update(kwargs)

        self.messages.append(message)

    # noinspection PyUnusedLocal
    def utter_template(self,
                       template,  # type: Text
                       tracker,  # type: Tracker
                       silent_fail=False,  # type: bool
                       **kwargs  # type: Any
                       ):
        # type: (...) -> None
        """"Send a message to the client based on a template."""

        message = {"template": template}
        message.update(kwargs)

        self.messages.append(message)




"""
ACTIONS
"""

## elicitation
def action_battery(dispatcher, tracker, domain):

    print("action_battery action")
    #dispatcher.utter_template("utter_weather", tracker, weather="placeholder weather")
    dispatcher.utter_message("the battery is at some level")
    return []



## INFORMATION RETRIEVAL
def action_weather(dispatcher, tracker, domain):
    #53.350551318399916 lat
    #-6.284179687500001 long
    print("weather action")
    #dispatcher.utter_template("utter_weather", tracker, weather="placeholder weather")
    dispatcher.utter_message("the weather is always nice")
    return []


def action_activities(dispatcher, tracker, domain):
    dispatcher.utter_message("there are always great activities on")
    return []


def action_time(dispatcher, tracker, domain):
    print("time action")
    time = datetime.datetime.now().strftime('%I %M %p')
    print(time)
    dispatcher.utter_template("utter_time", tracker, time=time)
    return []

def action_date(dispatcher, tracker, domain):
    date = datetime.datetime.now().strftime('%b %d, %Y')
    print(date)
    dispatcher.utter_template("utter_date", tracker, date=date)
    return []

def action_menu(dispatcher, tracker, domain):
    dispatcher.utter_message("there are delicious things on the menu today")
    return []

def action_post_arrived(dispatcher, tracker, domain):
    dispatcher.utter_message("the post has not yet arrived")
    return []



## COMMANDS
def action_dance(dispatcher, tracker, domain):
    print("action_dance")
    dispatcher.utter_message("dancing now")
    return []

def action_be_silent(dispatcher, tracker, domain):
    print("action_be_silent")
    dispatcher.utter_message("being silent")
    return []

def action_play_music(dispatcher, tracker, domain):
    print("action_play_music")

    dispatcher.utter_message("playing music")
    return []

def action_tell_a_story(dispatcher, tracker, domain):
    print("action_tell_a_story")

    dispatcher.utter_message("telling a story")
    return []

def action_tell_a_riddle(dispatcher, tracker, domain):
    print("action_tell_a_riddle")
    dispatcher.utter_message("telling a riddle")
    return []

def action_recite_a_poem(dispatcher, tracker, domain):
    print("action_recite_a_poem")
    dispatcher.utter_message("reciting a poem")
    return []

def action_sing_a_song(dispatcher, tracker, domain):
    print("action_sing_a_song")
    dispatcher.utter_message("singing a song")
    return []

def action_play_an_audiobook(dispatcher, tracker, domain):
    print("action_play_an_audiobook")
    dispatcher.utter_message("playing an audiobook")
    return []

def action_play_a_game(dispatcher, tracker, domain):
    print("action_play_a_game")
    dispatcher.utter_message("playing a game")
    return []

def action_play_game(dispatcher, tracker, domain):
    print("action_play_game")
    dispatcher.utter_message("playing game")
    return []

def action_stop_game(dispatcher, tracker, domain):
    print("action_stop_game")
    dispatcher.utter_message("stopping game")
    return []





##
def action_twist_left(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("HIP_YAW")
    msg.position.append(np.deg2rad(-90))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("twisting now")
    return []

def action_twist_right(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("HIP_YAW")
    msg.position.append(np.deg2rad(90))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("twisting now")
    return []

def action_look_left(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("NECK_YAW")
    msg.position.append(np.deg2rad(-80))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("looking now")
    return []

def action_look_right(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("NECK_YAW")
    msg.position.append(np.deg2rad(80))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("looking now")
    return []

def action_look_down(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("NECK_PITCH")
    msg.position.append(np.deg2rad(-25))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("looking now")
    return []

def action_look_up(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("NECK_PITCH")
    msg.position.append(np.deg2rad(25))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("looking now")
    return []

def action_both_arms_up(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("LEFT_ARM_PITCH")
    msg.position.append(np.deg2rad(180))
    msg.name.append("RIGHT_ARM_PITCH")
    msg.position.append(np.deg2rad(180))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("executing now")
    return []

def action_both_arms_down(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("LEFT_ARM_PITCH")
    msg.position.append(np.deg2rad(0))
    msg.name.append("RIGHT_ARM_PITCH")
    msg.position.append(np.deg2rad(0))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("executing now")
    return []

def action_zero_position(dispatcher, tracker, domain):
    msg = JointState()
    msg.name.append("NECK_PITCH")
    msg.position.append(np.deg2rad(0))
    msg.name.append("NECK_ROLL")
    msg.position.append(np.deg2rad(0))
    msg.name.append("NECK_YAW")
    msg.position.append(np.deg2rad(0))
    msg.name.append("HIP_YAW")
    msg.position.append(np.deg2rad(0))
    msg.name.append("HIP_PITCH")
    msg.position.append(np.deg2rad(0))
    msg.name.append("LEFT_ARM_PITCH")
    msg.position.append(np.deg2rad(0))
    msg.name.append("LEFT_ARM_ROLL")
    msg.position.append(np.deg2rad(0))
    msg.name.append("RIGHT_ARM_PITCH")
    msg.position.append(np.deg2rad(0))
    msg.name.append("RIGHT_ARM_ROLL")
    msg.position.append(np.deg2rad(0))
    joint_state_pub.publish(msg)
    dispatcher.utter_message("executing now")
    return []

def action_do_a_spin(dispatcher, tracker, domain):
    print("action_do_a_spin")
    dispatcher.utter_message("doing a spin now")
    return []

def action_wave(dispatcher, tracker, domain):
    print("action_wave")
    dispatcher.utter_message("waving now")
    return []

def action_be_happy(dispatcher, tracker, domain):
    print("action_be_happy")
    set_emotion_service(state="HAPPINESS", timeout=6000, restore=False)

    dispatcher.utter_message("being happy now")
    return []

def action_repeat_after_me(dispatcher, tracker, domain):
    print("action_repeat_after_me")
    dispatcher.utter_message("repeating after you")
    return []

def action_say_profanity(dispatcher, tracker, domain):
    print("action_say_profanity")
    dispatcher.utter_message("not saying profanity")
    return []

def action_volume_up(dispatcher, tracker, domain):
    print("action_volume_up")
    dispatcher.utter_message("volume up")
    return []

def action_volume_down(dispatcher, tracker, domain):
    print("action_volume_down")
    dispatcher.utter_message("volume down")
    return []

def action_show_cameras(dispatcher, tracker, domain):
    print("action_show_cameras")
    dispatcher.utter_message("showing you cameras")
    return []

def action_follow_me_start(dispatcher, tracker, domain):
    print("action_follow_me_start")
    dispatcher.utter_message("starting to follow you")
    return []

def action_follow_me_stop(dispatcher, tracker, domain):
    print("action_follow_me_stop")
    dispatcher.utter_message("stopping following you")
    return []

##

def action_set_a_timer(dispatcher, tracker, domain):
    print("action_set_a_timer")
    dispatcher.utter_message("setting a timer")
    return []

def action_start_stopwatch(dispatcher, tracker, domain):
    print("action_start_stopwatch")
    dispatcher.utter_message("starting stopwatch")
    return []

def action_stop_stopwatch(dispatcher, tracker, domain):
    print("action_stop_stopwatch")
    dispatcher.utter_message("stopping stopwatch")
    return []

def action_flip_a_coin(dispatcher, tracker, domain):
    print("action_flip_a_coin")
    dispatcher.utter_message("flipping a coin")
    return []

def action_roll_a_dice(dispatcher, tracker, domain):
    print("action_roll_a_dice")
    dispatcher.utter_message("rolling a dice")
    return []

def action_pick_a_number(dispatcher, tracker, domain):
    print("action_pick_a_number")
    dispatcher.utter_message("picking a number")
    return []

def action_do_maths(dispatcher, tracker, domain):
    print("action_do_maths")
    dispatcher.utter_message("doing maths")
    return []


##


def action_call_teleoperator(dispatcher, tracker, domain):
    print("action_call_teleoperator")
    dispatcher.utter_message("calling teleoperator")
    return []

def action_call_staff(dispatcher, tracker, domain):
    print("action_call_staff")
    dispatcher.utter_message("calling staff")
    return []

def action_call_acquietance(dispatcher, tracker, domain):
    print("action_call_acquietance")
    dispatcher.utter_message("calling acquietance")
    return []


# misc
# def action_cancel(dispatcher, tracker, domain):
    # print("cancelling now")
    # playsound(res_path+"/cancel.wav")
    # return []

def action_fallback(dispatcher, tracker, domain):
    print("fallback action")
    #TODO handle and log here
    dispatcher.utter_message("I'm sorry, I don't understand that")
    return []


def create_api_response(events, messages):
    return {
        "events": events if events else [],
        "responses": messages
    }


@App.route("/health", methods=['GET', 'OPTIONS'])
def health():
    return jsonify({"status": "ok"})


@App.route("/webhook", methods=['POST', 'OPTIONS'])
def webhook():
    action_name = request.json.get("next_action")
    tracker_json = request.json.get("tracker")
    domain = request.json.get("domain", {})
    tracker = Tracker.from_dict(tracker_json)
    dispatcher = CollectingDispatcher()
    print("action: ", action_name)
    events = eval(str(action_name) + '(dispatcher, tracker, domain)')
    return jsonify(create_api_response(events, dispatcher.messages))



if __name__ == '__main__':
    rospy.init_node('dialogue_action_server')
    print("running on: ",rospy.get_param('action_server_port'))
    App.run(port=rospy.get_param('action_server_port'))

#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu import config
from rasa_core.agent import Agent
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy

import rospy


def trainNLU():
    print("training NLU")
    training_data = load_data(rospy.get_param('intents_data'))
    trainer = Trainer(config.load(rospy.get_param('nlu_config')))
    trainer.train(training_data)
    trainer.persist(rospy.get_param('nlu_output'), fixed_model_name="nlu")

def trainDialogue():

    print("training Dialogue")


    # fallback = FallbackPolicy(fallback_action_name="action_fallback",
                              # core_threshold=0.03,
                              # nlu_threshold=0.03)
    # print("core fallback thresho  ld ", 0.015)
    # fallback = FallbackPolicy(fallback_action_name="action_fallback", core_threshold=0.015, nlu_threshold=0.015)

    # agent = Agent(rospy.get_param('domain_file'), policies=[MemoizationPolicy(max_history=3), KerasPolicy(), fallback])

    agent = Agent(rospy.get_param('domain_file'), policies=[MemoizationPolicy(max_history=3), KerasPolicy()])
    training_data = agent.load_data(rospy.get_param('stories'))
    agent.train(training_data,epochs=200,batch_size=100,validation_split=0.2)
    agent.persist(rospy.get_param('dialogue_output'))

if __name__ == '__main__':
    try:
        trainNLU()
        trainDialogue()
    except rospy.ROSInterruptException:
        pass

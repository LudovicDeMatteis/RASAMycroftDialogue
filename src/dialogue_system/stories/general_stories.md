<!-- GREETINGS AND VALEDICTIONS-->
## story_hello_1
* hello OR goodmorning OR goodevening
- utter_hello

## story_hello_2
* hello OR goodmorning OR goodevening
- utter_hello
- utter_ask_how_are_you

## story_hello_3
* nice_to_meet OR nice_to_see OR nice_to_talk
- utter_hello

## story_hello_4
* nice_to_meet OR nice_to_see OR nice_to_talk
- utter_hello
- utter_ask_how_are_you

## story_how_are_you_1
* user_lonely OR user_warm OR user_excited OR user_happy
- utter_respond_to_user_state_good

## story_how_are_you_1
* user_lonely OR user_cold OR user_sad OR user_tired OR user_sleepy OR user_bored OR user_busy OR user_angry
- utter_respond_to_user_state_bad

## story_remark_1
* remark_smart OR remark_beautiful OR remark_funny OR remark_good OR remark_like_robot
- utter_respond_to_compliment

## story_remark_2
* remark_annoying OR remark_unhelpful OR remark_boring OR remark_crazy
- utter_respond_to_insult


## story_goodbye_1
* goodnight
- utter_goodbye

## story_goodbye_2
* goodbye
- utter_goodbye

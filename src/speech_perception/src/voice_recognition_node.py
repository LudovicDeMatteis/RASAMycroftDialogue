#!/usr/bin/env python


from __future__ import division

import time
import re
import sys

from google.cloud import speech

import pyaudio
from six.moves import queue
from playsound import playsound

import rospy
import rospkg
from std_msgs.msg import String
# from system_manager.msg import System
from boole_msgs.srv import ControlSpeechPercepSrv
from boole_msgs.srv import SetLedSrv
from boole_msgs.srv import SetPlatformStateSrv

# Audio recording parameters
STREAMING_LIMIT = 55000
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE/10)
raw_pub = rospy.Publisher('/perception/raw_utterances', String)
chest_led_service = rospy.ServiceProxy('chest_led_service', SetLedSrv)
set_emotion_service = rospy.ServiceProxy('/set_emotion_service', SetPlatformStateSrv)
res_path = rospy.get_param('speech_res_path')
# system_pub = rospy.Publisher('/system', System)

stopped=True

def get_current_time():
    return int(round(time.time()*1000))


def duration_to_secs(duration):
    return duration.seconds + (duration.nanos / float(1e9))


def indicateListening(listening):
    print("indicate listening ", listening)
    if listening:
        # set_emotion_service(emotion="JOY", timeout=-1)
        # msg = System()
        # msg.interpreting_speech = True
        # system_pub.publish(msg)
        try:
            response = chest_led_service(6, [255,255,255], 220)
            print(response)
        except rospy.ServiceException as exc:
            print("Service did not process request: " + str(exc))
    else:
        set_emotion_service(state="NEUTRAL", timeout=-1, restore=False)
        # msg = System()
        # msg.interpreting_speech = False
        # system_pub.publish(msg)
        try:
            response = chest_led_service(2, [255,255,255], 85)
            print(response)
        except rospy.ServiceException as exc:
            print("Service did not process request: " + str(exc))



class ResumableMicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk_size):
        self._rate = rate
        self._chunk_size = chunk_size
        self._num_channels = 1
        self._max_replay_secs = 5

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()

        # 2 bytes in 16 bit samples
        self._bytes_per_sample = 2 * self._num_channels
        self._bytes_per_second = self._rate * self._bytes_per_sample

        self._bytes_per_chunk = (self._chunk_size * self._bytes_per_sample)
        self._chunks_per_second = (
                self._bytes_per_second // self._bytes_per_chunk)



    def __enter__(self):
        self.closed = False

        self._audio_interface = pyaudio.PyAudio()

        """
        dev_index=2
        for i in range(self._audio_interface.get_device_count()):
            device_info = self._audio_interface.get_device_info_by_index(i)
            print("device: ", device_info.get("name"))
            if(device_info.get("name") =="CD04: USB Audio (hw:1,0)"):
                print("device info: ", device_info)
                dev_index=i

        print("Using device index: ", dev_index)
        """

        self._audio_stream = self._audio_interface.open(
            #input_device_index=dev_index,
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue


    def generator(self):
        while not self.closed:
            if get_current_time() - self.start_time > STREAMING_LIMIT:
                self.start_time = get_current_time()
                break
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses, stream):
    responses = (r for r in responses if (
            r.results and r.results[0].alternatives))

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        top_alternative = result.alternatives[0]
        transcript = top_alternative.transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            #sys.stdout.write(transcript + overwrite_chars + '\r')
            #sys.stdout.flush()

            num_chars_printed = len(transcript)
        else:
            print("[FINAL] "+transcript + overwrite_chars)
            if(transcript=="cancel"):
                playsound(res_path+"/cancel.wav")
            else:
                raw_pub.publish(transcript)
            global stopped
            global mic_manager
            mic_manager._buff.put(None)
            mic_manager.closed = True
            stopped = True
            num_chars_printed = 0
            indicateListening(False)



mic_manager = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)


def handle_pause(req):
    global stopped
    global mic_manager
    print("handling pause", req.interpret)
    print(stopped)
    if(stopped):
        print("sp stopped, will not change")
        return False
    else:
        print("sp interpreting, will pause")
        # msg = System()
        # msg.interpreting_speech = req.interpret
        # system_pub.publish(msg)
        mic_manager._buff.put(None)
        if req.interpret:
            indicateListening(True)
            mic_manager.closed = False
        else:
            indicateListening(False)
            # mic_manager._buff.put(None)
            mic_manager.closed = True
        # indicateListening(req.interpret)
        # mic_manager._buff.put(None)
        # mic_manager.closed = not req.interpret
        return True


def handle_stop(req):
    global stopped
    global mic_manager
    print("handling stop", req.interpret)
    if(req.interpret):
        #print("interpreting now")
        mic_manager._buff.put(None)
        mic_manager.closed = False
        stopped = False
    else:
        #print("stopping")
        mic_manager._buff.put(None)
        mic_manager.closed = True
        stopped = True
    # msg = System()
    # msg.interpreting_speech = req.interpret
    # system_pub.publish(msg)
    indicateListening(req.interpret)
    return True


if __name__ == '__main__':

    rospy.init_node('voice_recognition')
    s = rospy.Service('pause_speech_perception_service', ControlSpeechPercepSrv, handle_pause)
    s1 = rospy.Service('stop_speech_perception_service', ControlSpeechPercepSrv, handle_stop)
    client = speech.SpeechClient()
    config = speech.types.RecognitionConfig(
        encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SAMPLE_RATE,
        language_code='en-US',
        max_alternatives=1,
        enable_word_time_offsets=True)
    streaming_config = speech.types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    print("node is up")


    with mic_manager as stream:
        stream.closed = True

        while True:
            if not stream.closed:
                print "interpreting"
                audio_generator = stream.generator()
                requests = (speech.types.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
                responses = client.streaming_recognize(streaming_config, requests)
                try:
                    listen_print_loop(responses, stream)
                    continue
                except Exception as e:
                    indicateListening(False)
                    time.sleep(0.1)
                    print(e)
                    continue
            else:
                time.sleep(0.1)
                print "."

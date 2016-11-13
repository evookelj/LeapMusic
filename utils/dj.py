################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################

import Leap, sys, thread, time, wave, pyaudio
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from random import randint
from time import time

pos = 0
rate = -1

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def getRate(self, frame, toSet):
        global rate
        for gest in frame.gestures():
            found = False
            if gest.type == Leap.Gesture.TYPE_KEY_TAP:
                tap = KeyTapGesture(gest)
                found = True
            if gest.type == Leap.Gesture.TYPE_SCREEN_TAP:
                tap = ScreenTapGesture(gest)
                found = True
            if found:
                print "DIRECTION: "
                print tap.direction
        #if toSet:
            #set Rate to help
        return 0

    def spin(self, frame, toSet):
        global pos
        ret = -1
        for gest in frame.gestures():
            if gest.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gest)
                if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                    ret = pos*.8
                else:
                    ret = pos*1.2
        if toSet:
            pos = ret
        return ret

    def play(self):
        global rate
        global pos
        f = wave.open("Optimistic.wav","rb")
        if pos == 0:
            f.rewind()
        else:
            f.setpos(rate)
        pos = f.tell()
        p = pyaudio.PyAudio()
        if rate == 0:
            rRate = f.getframerate()
        else:
            rRate = rate
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                        channels = f.getnchannels(),
                        rate = rRate,
                        output = True)
        data = f.readframes(1024)
        start2 = time()
        while data != "":
            stream.write(data)
            data = f.readframes(1024)
        pos = f.tell()
        stream.stop_stream()
        stream.close()
        p.terminate()

    def on_frame(self, controller):
        global pos
        frame = controller.frame()
        self.getRate(frame,False)
        self.spin(frame,False)

        """
        if gesture.type == Leap.Gesture.TYPE_CIRCLE:
            circle = CircleGesture(gesture)
            
            # Determine clock direction using the angle between the pointable and the circle normal
            if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                clockwiseness = "clockwise"
            else:
                clockwiseness = "counterclockwise"
                
                # Calculate the angle swept since the last frame
                swept_angle = 0
            if circle.state != Leap.Gesture.STATE_START:
                previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI
                    
                print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                    gesture.id, self.state_names[gesture.state],
                    circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)
                
            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                    gesture.id, self.state_names[gesture.state],
                    swipe.position, swipe.direction, swipe.speed)
                    
            if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                keytap = KeyTapGesture(gesture)
                print "  Key Tap id: %d, %s, position: %s, direction: %s" % (
                    gesture.id, self.state_names[gesture.state],
                    keytap.position, keytap.direction )
                
            if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                screentap = ScreenTapGesture(gesture)
                print "  Screen Tap id: %d, %s, position: %s, direction: %s" % (
                    gesture.id, self.state_names[gesture.state],
                    screentap.position, screentap.direction )
"""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    while (True):
        listener.play()
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()

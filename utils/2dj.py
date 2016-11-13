import Leap, sys, thread, time, wave, pyaudio
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from random import randint
from time import time, sleep
from math import ceil

global pos
global prevFrame

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        global prevFrame
        prevFrame = 0
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def posMult(self, controller):
        frame = controller.frame()
        for gest in frame.gestures():
            if gest.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gest)
                clockwise= (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2)
                if clockwise:
                    print "SPEED UP"
                    return 1.01
                else:
                    print "SLOW DOWN"
                    return .99
            else:
                print gest.type
        return 1

    def rateMult(self, controller):
        global rate
        frame = controller.frame()
        for gest in frame.gestures():
            if gest.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gest)
                print swipe.direction
        return 1

    def play(self, controller):
        ctr = 0
        global pos
        while ctr < 10000:
            f = wave.open("Optimistic.wav","rb")
            p = pyaudio.PyAudio()
            stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                            channels = f.getnchannels(),
                            rate = int(f.getframerate()*self.rateMult(controller)),
                            output = True)
            data = f.readframes(1024)
            start = time()
            try:
                f.setpos(pos)
            except:
                f.rewind()
            while (time() - start) < 5:
                stream.write(data)
                data = f.readframes(1024)
                try:
                    f.setpos(int(f.tell()*self.posMult(controller)))
                except:
                    f.rewind()
            pos = f.tell()
            stream.stop_stream()
            stream.close()
            p.terminate()
        print "SWITCH"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    #on frame not being run?
    def on_frame(self, controller):
        global prevFrame
        frame = controller.frame()
        while (frame.id == prevFrame):
            print "curr: %d, prev: %d"%(frame.id, prevFrame.id)
            frame = controller.frame()
        prevFrame = frame.id

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()

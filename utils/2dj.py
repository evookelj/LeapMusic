import Leap, sys, thread, time, wave, pyaudio
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from random import randint
from time import time

global pos

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
        self.play(controller)

    def posMult(self, controller):
        frame = controller.frame()
        for gest in frame.gestures():
            if gest.type == Leap.Gesture.TYPE_CIRCLE:
                circle = CircleGesture(gest)
                clockwise= (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2)
                if clockwise:
                    print "SPEED UP"
                    return 1.1
                else:
                    print "SLOW DOWN"
                    return .9
            else:
                print gest.type
        print "SAME"
        return 1

    def play(self, controller):
        f = wave.open("Optimistic.wav","rb")
        p = pyaudio.PyAudio()
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                        channels = f.getnchannels(),
                        rate = f.getframerate(),
                        output = True)
        data = f.readframes(1024)
        start = time()
        while True:
            while (time() - start) < 5:
                stream.write(data)
                data = f.readframes(1024)
                f.setpos(f.tell()*self.posMult(controller))
        stream.stop_stream()
        stream.close()
        p.terminate()

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        frame = controller.frame()
        print "HELLO"

def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.add_listener(listener)
    try:
        sys.stdin.readline()
    except:
        exit()
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()

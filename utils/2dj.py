import Leap, sys, thread, time, wave, pyaudio
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
from multiprocessing import Process
from time import time, sleep

pos = 0
posMul = 1
rateMul = 1
prevCirc = 0

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']

    def on_init(self, controller):
        global posMul
        global rateMul
        posMul = 1
        rateMul = 1
        p1 = Process(target = self.play(controller))
        p1.start()
        p2 = Process(target = self.on_frame(controller))
        p2.start()

    def on_connect(self, controller):
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def posMult(self, gest):
        global posMul
        if gest is None:
            posMul = 1
            return
        if gest.type == Leap.Gesture.TYPE_CIRCLE:
            print "Circle!"
            circle = CircleGesture(gest)
            clockwise= (circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2)
            if clockwise:
                print "SKIP FORWARD"
                posMul = 1.1
            else:
                print "REWIND"
                posMul = .9
        posMul = 1
            
    def rateMult(self, gest):
        global rateMul
        if gest is None:
            rateMul = 1
            return
        if gest.type == Leap.Gesture.TYPE_SWIPE:
            swipe = SwipeGesture(gest)
            print swipe.direction
            return 1.2
        rateMul = 1

    def play(self, controller):
        while True:
            global pos
            global posMul
            global rateMul
            f = wave.open("Optimistic.wav","rb")
            p = pyaudio.PyAudio()
            stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                            channels = f.getnchannels(),
                            rate = int(f.getframerate()*rateMul),
                            output = True)
            data = f.readframes(1024)
            try:
                f.setpos(pos)
            except:
                f.rewind()
            start = time()
            while time() - start < 2:
                stream.write(data)
                data = f.readframes(1024)
                try:
                    f.setpos(f.tell()*posMul)
                except:
                    f.rewind()
            pos = f.tell()
            stream.stop_stream()
            stream.close()
            p.terminate()
            
    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def getGest(self, controller):
        global prevCirc
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        # Get gestures
        for gesture in frame.gestures():
            if gesture.type == Leap.Gesture.TYPE_CIRCLE \
            or gesture.type == Leap.Gesture.TYPE_SWIPE \
            or gesture.type == Leap.Gesture.TYPE_KEY_TAP \
            or gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)
                    if int(circle.progress) == 1 and time()-prevCirc > 4:
                        prevCirc = time()
                        return gesture
                    else:
                        return None
                return gesture
        return None


    #on frame not being run?
    def on_frame(self, controller):
        gest = self.getGest(controller)
        self.posMult(gest)
        self.rateMult(gest)
        
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

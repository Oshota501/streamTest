# from gpiozero import OutputDevice
from time import sleep
class OutputDevice :
    def __init__(self,pin):
        self.pin = pin
        
    def on () :
        print("ON")

    def off () :
        print("OFF")

class L_chika (OutputDevice ) :
    def __init__(self,pin) :
        super().__init__(pin)
    def clock_start(self,repeat_size,interval_size):
        for i in range(repeat_size) :
            self.on()
            sleep(interval_size/2)
            self.off()
            sleep(interval_size/2)

if __name__ == "__main__" :
    p23 = L_chika(23) 
    p23.clock_start(12,0.4)

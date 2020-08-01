import serial, time, sys
import matplotlib.pyplot as plt
import os
import numpy as np

from subprocess import call
import cv2

class P_measurement:
    """
    This class controls the pressure measurements.
    """
    def __init__(self):
        self.channels = [5,10] #channel 5 = PS2, channel 10 = PS3
        self.camera_interval = 5
        self.path='/media/flow-lab/E6944FFA944FCBAD/monem/experiment1_45angle/'
        self.pathimages=self.path + 'im/'
        
        if not os.path.exists(self.pathimages):
            os.makedirs(self.pathimages)

        self.pressure_file = open(self.path + time.ctime() + '_pressure.txt', 'a')
        self.image_file = open(self.path + time.ctime() + '_image.txt', 'a')
        self.time_step = 0.5
        self.p_temp = 0
        self.init_time = 0
        self.calibrationfactor1 = 4.3868*10**5 #pressure sensor 2 (port.5)
        self.calibrationfactor2 = 4.3758*10**5 #pressure sensor 3 (port.10)
        
        
        
    def load_port(self):
        port = '/dev/ttyUSB0' #+ str(self.pressure_port)
        g = serial.Serial(port,9600,timeout=5,xonxoff=True) # constructs a serial object
        g.write(b'*RST\n')
        g.write(b':DISP:ENAB ON\n')
        g.write(b':SYST:BEEP:STAT OFF\n')
        g.write(b':FUNC ''VOLT:DC'' \n') # measure type
        print('Connected to serial port ' + port)
        self.init_time = time.time() # save the time
        return g
        
        
    
    def get_and_save_pressure(self,p,init_time):
        
        p_save = np.zeros(len(self.channels)) #allocating an array
        for i in range(len(self.channels)):
        
            p.flush() # clear the serial connection
            temp = b':ROUT:CLOS (@'+str(self.channels[i])+')\n'
            p.write(temp)
            p.write(b':INIT\n')
            p.write(b':FETCH?\n')
            M_praw = p.readline()
            p_save[i] = M_p = float(M_praw) # changing the pressure data format
                
        self.p_temp = p_save
        self.save_pressure(p_save) #saving the pressure measurement
        print p_save
        
         
        
    def save_pressure(self,p_save):
        to_save = (str(time.time() - self.init_time))
        count = 1;
        for i in p_save:
            tmp = 'self.calibrationfactor' + str(count)
            to_save = to_save + (' ' + str(i) + ' ' +  str(eval(tmp)*i))
            count += 1
        to_save = to_save + ('\n')

        self.pressure_file.write(to_save)
  


   
    def save_photo(self,pic_number):
        call(['gphoto2', '--capture-image-and-download',
                      '--force-overwrite'])
        call(['mv', 'capt0000.jpg', self.pathimages + str(pic_number).zfill(5) + '.jpg'])
        print 'Image ' + str(pic_number)
   


    def realtimeplotting(self,pic_number):
        """
        under construction
        """
        plt.ion()
        print self.p_temp[0]
        ax = plt.scatter(pic_number,self.p_temp[0])
        plt.draw()
        plt.pause(0.1)
        

def main():

    P=P_measurement()
    portobject = P.load_port()
    init_time = time.time() #initial time
    pic_number = 0 # photo counter
    init_time = time.time() # save the time
    count = 0;
    while True:
        P.get_and_save_pressure(portobject,init_time)
        if count == 50:
            P.save_photo(pic_number)
            time.sleep(P.time_step)
            count = 0
            pic_number  += 1
        #P.realtimeplotting(pic_number)
        count += 1
        
    
if __name__=='__main__':
    main()
    
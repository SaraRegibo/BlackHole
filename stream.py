# -*- coding: utf-8 -*-
"""
Capturing images with camera mounted on Raspberry Pi and show them on screen as 
if a black hole was standing in the way.

Based on: https://picamera.readthedocs.org/en/release-1.9/recipes2.html#unencoded-image-capture-rgb-format
"""

#########
# Imports
#########

import io
import time
import threading
import picamera
import numpy as np

##################
# Global variables
##################

lock = threading.Lock() # Low-level synchronisation primitive
pool = []               # Pool of image processors            

#################
# Image processor
#################

class ImageProcessor(threading.Thread):
    
    def __init__(self):
        
        super(ImageProcessor, self).__init__()
        
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.start()

    def run(self):  # In a separate thread
        
        # Take action as long as the image processor has not been shut down
                
        while not self.terminated:
            
            # Wait for an image to be written to the stream
            
            if self.event.wait(1):
                
                try:
                    
                    self.stream.seek(0)
                    
                    # Read the image and do some processing on it
                    #Image.open(self.stream)
                    data = np.fromstring(self.stream.getvalue(), dtype = np.uint8)
                    data = np.flipud(data)
                    print "Flipped"
                    np.savetxt(self.stream, data)
                    print "Done"
                    #image = cv2.imdecode(data, 1)
                    #...
                    #...
                    # Set done to True if you want the script to terminate
                    # at some point
                    #done=True
                    
                finally:
                    
                    # Reset the stream and event
                    
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    
                    # Add this image processor to the pool
                    
                    with lock:
                        
                        pool.append(self)  

def streams():
    
    while True:#not done:
        
        with lock:
            
            if pool:

                # If there are still items left in the pool, go to the next image processor
                processor = pool.pop()
                
            else:
                
                # No more image processors left
                
                processor = None
        
        if processor:
            
            yield processor.stream
            processor.event.set()
            
        else:
            
            # When the pool is starved, wait a while for it to re-fill
            
            time.sleep(0.1)

###########
# Streaming
###########

with picamera.PiCamera() as camera:
    
    # Create a pool of image processors
    
    pool = [ImageProcessor() for i in range(4)]
    
    # Camera configuration    
    
    camera.resolution = (640, 480)  # Resolution (width [pixels], height [pixels])
    camera.framerate = 10           # Frame rate [1/s]
    camera.start_preview()
    time.sleep(2)
    
    try:
        
        # Keep on capturing images, apply the influence of the black hole and display them        
        print "Start capturing sequence"
        camera.capture_sequence(streams(), use_video_port=True)

    except KeyboardInterrupt:
        
        # Once the process gets interrupted (Ctrl + C), shut down the processors in an orderly fashion
        
        while pool:
            
            with lock:
                
                processor = pool.pop()
                
            processor.terminated = True
            processor.join()
            camera.stop_preview()

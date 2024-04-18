import seriallib.armcontroller
import seriallib.exceptions
import torch
from resnet.classifier import classify_waste
from detection.detection import get_waste_image
import seriallib
from time import sleep

GUI = True

if GUI:
      try:
            import tkinter as tk
      except ImportError:
            print("forcing gui to false, tk not avalible")
            GUI = False

model = torch.load("resnet/model/trash.pth")
model.eval()

armcontroller = seriallib.ArmController("mock") # dont connect to arm over serial, just say it is successful instantly
## ensure arduino ide/anything else using the serial port is closed.
# armcontroller = seriallib.ArmController("/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_8513332303635140E1A0-if00") # this is correct for the standard arduino on linux
# armcontroller = seriallib.ArmController("COM3") # windows, change to match serial port shown in arduino ide?

bin1_labels = ["plastic", "glass", "paper"]
bin2_labels = ["misc", "cardboard", "metal"]

if GUI:
      window = tk.Tk()
      window.title("Waste Sorter")
      detect_state_label = tk.Label(window, text="Detect state")
      detect_state_label.pack()
            
      detect_state_value = tk.Label(window, text="Waiting")
      detect_state_value.pack()

      arm_label = tk.Label(window, text="Arm state")
      arm_label.pack()

      arm_value = tk.Label(window, text="Waiting")
      arm_value.pack()
      
      

def main():
      while True:
            if GUI:
                  detect_state_value.config(text="Waiting")
                  arm_value.config(text="Waiting")
                  window.update()
            # detect if there is an object
            img = get_waste_image(0)
            
            if GUI:
                  detect_state_value.config(text="Detected object, classifying...")
                  window.update()
            
            # process the image and classify it
            label = classify_waste(model, img, output_as_string=True)
            
            if GUI:
                  detect_state_value.config(text="Classified as: " + str(label))
                  arm_value.config(text="Grabbing...")
                  window.update()

            try:
                  # img present, pickup with arm.
                  armcontroller.grab()
            except seriallib.exceptions.ArmException as e:
                  if GUI:
                        arm_value.config(text="grab Error: " + str(e))
                        window.update()
                  print(e)
            if GUI:
                  arm_value.config(text="waiting 1 sec")
                  window.update()
            sleep(1)

            try:
                  if label in bin1_labels:
                        if GUI:
                              arm_value.config(text="Moving to bin 1")
                              window.update()
                        armcontroller.move_bin1()
                  elif label in bin2_labels:
                        if GUI:
                              arm_value.config(text="Moving to bin 2")
                              window.update()
                        armcontroller.move_bin2()
                  
            except seriallib.exceptions.ArmException as e:
                  if GUI:
                        arm_value.config(text="drop Error: " + str(e))
                        window.update()
                  print(e)

            

main()

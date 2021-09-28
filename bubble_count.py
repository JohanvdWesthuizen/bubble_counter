# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import time
import cv2
import os
from datetime import datetime
import os.path

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

save_path = '/home/pi/Desktop/OpenCV/data'
start_time = datetime.now()
file_name = start_time.strftime("%H-%M-%S")
completeName = os.path.join(save_path, file_name+".txt")
data_file = open(completeName, "w")

timeout = time.time() + 60*5			# 5 min from now

all_data = []

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	time.sleep(0.05)
	#print(datetime.now())
	image = frame.array
	image = image[100:500, 100:400] #Crop y:y+h and x:x+w

	# show the frame
	cv2.imshow("Frame", image)

	hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	# cv2.imshow("hsv_image", hsv_image)

	#lower mask (0-10)
	lower_red_hsv = np.array([0, 50, 50])
	upper_red_hsv = np.array([10, 255, 255])
	filter1 = cv2.inRange(hsv_image, lower_red_hsv, upper_red_hsv)
	#upper mask (170-180)
	lower_red_hsv = np.array([170, 50, 50])
	upper_red_hsv = np.array([180, 255, 255])
	filter2 = cv2.inRange(hsv_image, lower_red_hsv, upper_red_hsv)

	#join the filters
	hsv_filter = filter1 + filter2

	output_hsv = image.copy()
	output_hsv[np.where(hsv_filter == 0)] = 0

	cv2.imshow("output_hsv", output_hsv)

	output_hsv = cv2.cvtColor(output_hsv, cv2.COLOR_BGR2GRAY)
	num_red = cv2.countNonZero(output_hsv)
	# print(frame.size)
	tot_pix = output_hsv.size
	# print(tot_pix)
	# print('The number of red pixels is: ' + str(num_red))
	ratio = round(((num_red/tot_pix) * 100), 2)

	percent_red = ' Percentage red: ' + str(ratio)
	data = str(datetime.now()) + percent_red
	print(data)
	data_file.write(data + '\n')


	all_data.append(ratio)
	# if len(data) > 20:
	# 	data.pop(0)
	# # roll_avg = round((sum(data) / len(data)), 1)
	# roll_avg = round(np.average(data), 2)
	# roll_std = round(np.std(data), 2)
	# print(f"Rolling average of red: {roll_avg} +- {roll_std}")

	if time.time() > timeout:
		break

	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break

# print(all_data)
avg = round(np.average(all_data), 2)
std = round(np.std(all_data), 2)
print(avg)
print(std)

data_file.write('Average: ' + str(avg) + '\n')
data_file.write('St.dev: ' + str(std) + '\n')

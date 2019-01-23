# import the necessary packages
import time
import cv2
import pantilthat
import sys
import requests
import picamera
import firebase_admin
import dlib
import threading
import face_recognition

from datetime import datetime
from datetime import date
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from firebase_admin import firestore
from picamera.array import PiRGBArray 
from picamera import PiCamera


#  
pic = 0
pic_detected = 0
# Initializing camera position
# current values
xc = 0
yc = 0
# new values
xn = 0
yn = 0
delta_x = 10
delta_y = 10


def doRecognizePerson(faceNames, fid):
    time.sleep(2)
  # Placeholder for a function which will recognize if the detected person is not one of the
  # persons recently detected (pictures are stored in ./faces_detected
    faceNames[ fid ] = "Person " + str(fid)


#-----------------------------------------------------------------------------------------------------------#
# INITIALIZING FIRESTORE DATABASE                                                                           #
#-----------------------------------------------------------------------------------------------------------#

# Initialize Firebase database (tracking the number of objects detected)
# Firestore will store a structure of dates and counters (numberOfFaces, numberOfEyes, ...) on a daily basis
# Dedicated Collections are create for each type of counters.
# In each collection, separate documents will be created for each day
# In each document, fields are created containing the number of objects detected and the date/time the last object was detected.

try:
  cred = credentials.Certificate("./keys/serviceAccountKey.json")
  #URL
  databaseURL = 'https://opencv-camera-tracking.firebaseio.com/'

  firebase_admin.initialize_app(cred, {
  'databaseURL': databaseURL,
})
  # Init firestore
  db = firestore.client() 
  print(db)

except:
  print('Unable to initialize Firebase: {}'.format(sys.exc_info()[0]))
  sys.exit(1)

  # ---------------------------------------------------------------------------------------------------------------#
  # INITIALIZE LOCAL COUNTERS                                                                                     #
  #----------------------------------------------------------------------------------------------------------------#

# Initialize counters (from firebase)
# numberOfGms_initValue
# numberOfSmiles_initVal
count_faces = 0
count_eyes = 0
# Current Day And Time in datetime format
date_today = datetime.utcnow().date()
print('today', date_today)
# Create reference to the faces_tracked collection
faces_tracked_ref = db.collection(u'faces_tracked')
# Create reference to the faces_tracked collection
eyes_tracked_ref = db.collection(u'eyes_tracked')

# Retrieve the faces_tracked and eyes_tracked data for the input with the most recent date (datetime format)
# We only pick the last one
days_faces = faces_tracked_ref.order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()
days_eyes = eyes_tracked_ref.order_by(u'date', direction=firestore.Query.DESCENDING).limit(1).get()

for day_faces in days_faces:
  # Check if this is the current day and iniitalize the counter value with the value of the day if applicable
  # to_dict -> translate to dictionary datatype
  # We have to do this because what we get from firestore is a dictionary 
  date_database = day_faces.to_dict()["date"].date() 
  if date_today == date_database :
      count_faces = day_faces.to_dict()["count_items"]
      print("count_faces_initialized", str(count_faces))

for day_eyes in days_eyes:
  # Check if this is the current day and iniitalize the counter value with the value of the day if applicable
  date_database = day_eyes.to_dict()["date"].date()
  if date_today == date_database :
      count_eyes = day_eyes.to_dict()["count_items"]
      print("count_eyes_initialized", str(count_eyes))     

# Initialize  Camera
try:
  # initialize the camera and grab a reference to the raw camera capture
  camera = PiCamera()   # instance of a PiCamera object
  camera.rotation = 180
  camera.resolution = (640, 480)
  camera.framerate = 32
  rawCapture = PiRGBArray(camera, size=(640, 480))
except:
  print('Unable to initialize Pi Camera: {}'.format(sys.exc_info()[0]))
  sys.exit(1)

# allow the camera to warmup
time.sleep(0.1)


# Load cascading XML classifiers (faces, eyes, phones, ...)
eye_cascade = cv2.CascadeClassifier('./cascades/haarcascade_eye.xml')
face_cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalface_default.xml')
phone_cascade = cv2.CascadeClassifier('./cascades/phone_cascade.xml') # todo
smile_cascade = cv2.CascadeClassifier('./cascades/haarcascade_smile.xml')

# Tracker from dlib library (approach to do face detection once and then use correlation tracker
# to keep track of the relevant region from frame to frame)



# Create two opencv named windows
# cv2.namedWindow("base-image",cv2.WINDOW_AUTOSIZE)
# cv2.namedWindow("result_image",cv2.WINDOW_AUTOSIZE)
# Start the window thread for the two windows we are using
# cv2.startWindowThread()

# Variables holding the current frame number and the current faceID and eyeID
frameCounter = 0  # Needed to control when we will run a full detection loop
currentFaceID = 0 
currentEyeID = 0

# Variables holding the correlation trackers and the name per faceID and eyeID
faceTrackers = {}
eyeTrackers = {}
faceNames = {}
eyeNames = {}




#-----------------------------------------------------------------------------------------------------------#
# HERE STARTS THE DETECTION AND TRACKING LOOP                                                               #
#-----------------------------------------------------------------------------------------------------------#

# Used principe from articles Guido Diepen (combination of detection and tracking multiple faces)
# Part 1: https://www.guidodiepen.nl/2017/02/detecting-and-tracking-a-face-with-python-and-opencv/?fbclid=IwAR1fEIeZ0V5zhf7cwjtYtJwGaf23I83SIoO_cemxG1HhcgPx4W1kDNdagN4
# Part 2: https://www.guidodiepen.nl/2017/02/tracking-multiple-faces/?fbclid=IwAR24KDrHDsqBDOV8qaqCzj3OfZBQPH1idLbWpeZLHTE-7R3MTJBvPkO-37E 

            #STEPS:
            # * Update all trackers and remove the ones that are not 
            #   relevant anymore (based on quality of the tracking)
            # * Every 10 frames:
            #       + Use face detection on the current frame and look
            #         for faces and eyes. 
            #       + For each found face, check if centerpoint is within
            #         existing tracked box. If so, nothing to do
            #       + If centerpoint is NOT in existing tracked box, then
            #         we add a new tracker with a new face-id

# Start continuous frame capturing from the camera (one loop of continous monitoring)
# capture frames from the camera using the continuous capturing function)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
  # grab the raw NumPy array representing the image
  image = frame.array

  #Increase the framecounter
  frameCounter += 1
  
# Update all the trackers and remove the ones for which the update indicated the quality was not good enough
  fidsToDelete = [] # Face Ids
  for fid in faceTrackers.keys():
    trackingQuality = faceTrackers[ fid ].update( image )

    #If the tracking quality is good enough, we must delete this tracker
    if trackingQuality < 7:
      fidsToDelete.append( fid )

  for fid in fidsToDelete:
    print("Removing fid " + str(fid) + " from list of trackers")
    faceTrackers.pop( fid , None )

  eidsToDelete = [] # Eye Ids
  for eid in eyeTrackers.keys():
    trackingQuality = eyeTrackers[ eid ].update( image )

    #If the tracking quality is good enough, we must delete
    #this tracker
    if trackingQuality < 7:
      eidsToDelete.append( eid )

  for eid in eidsToDelete:
    print("Removing eid " + str(eid) + " from list of trackers")
    eyeTrackers.pop( eid , None ) 

#Every 10 frames, we will have to determine which faces and eyes are present in the frame
  if (frameCounter % 10) == 0:


    #For the face detection, we need to make use of a gray colored image
    #so we will convert the captured image to a gray-based image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #Now use the haar cascade detector to find all faces in the image
    #It returns an array of rectangles (coordinates, width, heigth) which match the faces.
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 5, minSize=(20, 10))  # effectively detecting eyes
    faces = face_cascade.detectMultiScale(gray, 1.3, 4, minSize=(30, 30))  # effectively detecting faces
    print("Using the cascade detector to detect faces and eyes")

    #Loop over the faces you detected and check if this face is included in the tracker list (based on positions)
    #We need to convert it to int here because of the
    #requirement of the dlib tracker. If we omit the cast to
    #int here, you will get cast errors since the detector
    #returns numpy.int32 and the tracker requires an int
    for (_x, _y, _w, _h) in faces:
      x = int(_x)
      y = int(_y)
      w = int(_w)
      h = int(_h)

      #calculate the centerpoint of the detected face
      x_bar = x + 0.5 * w
      y_bar = y + 0.5 * h

      #Variable holding information which faceid we 
      #matched with
      matchedFid = None

      #Now loop over all the trackers and check if the 
      #centerpoint of the face is within the box of a 
      #tracker
      for fid in faceTrackers.keys():
        tracked_position =  faceTrackers[fid].get_position()

        t_x = int(tracked_position.left())
        t_y = int(tracked_position.top())
        t_w = int(tracked_position.width())
        t_h = int(tracked_position.height())


        #calculate the centerpoint
        t_x_bar = t_x + 0.5 * t_w
        t_y_bar = t_y + 0.5 * t_h

        #check if the centerpoint of the face is within the 
        #rectangleof a tracker region. Also, the centerpoint
        #of the tracker region must be within the region 
        #detected as a face. If both of these conditions hold
        #we have a match
        if ( ( t_x <= x_bar   <= (t_x + t_w)) and 
            ( t_y <= y_bar   <= (t_y + t_h)) and 
            ( x   <= t_x_bar <= (x   + w  )) and 
            ( y   <= t_y_bar <= (y   + h  ))):
          matchedFid = fid


      #If no matched fid, then we have to create a new tracker and add a new detected face (to improve with face recognition)
      if matchedFid is None:
        print("Creating new face tracker " + str(currentFaceID))
        


        # Store picture in face_detected directory (to enable face recognition) not using this now
        # pic_detected += 1
        # image_name = camera.capture('faces_detected/face%s.jpg' % pic_detected)


        # Create and store the tracker if you didn't exist yet
        tracker = dlib.correlation_tracker()
        tracker.start_track(image,
                            dlib.rectangle( x-10,
                                            y-20,
                                            x+w+10,
                                            y+h+20))

        faceTrackers[ currentFaceID ] = tracker

        #Start a new thread that is used to simulate 
                        #face recognition. This is not yet implemented in this
                        #version :)
        t = threading.Thread( target = doRecognizePerson ,
                          args=(faceNames, pic_detected))
        t.start()




        # Increment counter incrementing the number of faces detected (only incremented for a new detection)  
        count_faces += 1 
        print ("Found" , format(count_faces), "faces !" ) # Todo rewrite cleaner
               
        date_time = datetime.utcnow()
        date_today = date.today()
        print("Today" + str(date_today))

        # Save to firestore
        # Faces tracked
      
        doc_ref = db.collection(u'faces_tracked').document(u'day_' + str(date_today)) # change day_ to moment_
        doc_ref.set({
          u'count_items': count_faces,
          u'date': date_time
        })

        #Increase the currentFaceID counter
        currentFaceID += 1

  # Same process as faces but now eyes
    for (_x, _y, _w, _h) in eyes:
      x = int(_x)
      y = int(_y)
      w = int(_w)
      h = int(_h)

      #calculate the centerpoint of the detected eye
      x_bar = x + 0.5 * w
      y_bar = y + 0.5 * h

      #Variable holding information which eyeid we 
      #matched with
      matchedEid = None

      #Now loop over all the trackers and check if the 
      #centerpoint of the eye is within the box of a 
      #tracker
      for eid in eyeTrackers.keys():
        tracked_position =  eyeTrackers[eid].get_position()

        t_x = int(tracked_position.left())
        t_y = int(tracked_position.top())
        t_w = int(tracked_position.width())
        t_h = int(tracked_position.height())


        #calculate the centerpoint
        t_x_bar = t_x + 0.5 * t_w
        t_y_bar = t_y + 0.5 * t_h

        #check if the centerpoint of the eye is within the 
        #rectangleof a tracker region. Also, the centerpoint
        #of the tracker region must be within the region 
        #detected as an eye. If both of these conditions hold
        #we have a match
        if ( ( t_x <= x_bar   <= (t_x + t_w)) and 
            ( t_y <= y_bar   <= (t_y + t_h)) and 
            ( x   <= t_x_bar <= (x   + w  )) and 
            ( y   <= t_y_bar <= (y   + h  ))):
          matchedEid = eid


      #If no matched eid, then we have to create a new tracker and add a new detected eye (to improve)
      if matchedEid is None:
        print("Creating new eye tracker " + str(currentEyeID))
        # Increment counter incrementing the number of eyes detected (only incremented for a new detection)  
        count_eyes += 1 
        print ("Found" , format(count_eyes), "eyes !" ) # Todo rewrite cleaner
               
        date_time = datetime.utcnow()
        date_today = date.today()
        print("Today" + str(date_today))

        # Save to firestore
        # Eyes tracked
        # 
        doc_ref = db.collection(u'eyes_tracked').document(u'day_' + str(date_today)) # change day_ to moment_
        doc_ref.set({
            u'count_items': count_eyes,
            u'date': date_time
          })

        
        #Create and store the tracker 
        tracker = dlib.correlation_tracker()
        tracker.start_track(image,
                            dlib.rectangle( x-10,
                                            y-20,
                                            x+w+10,
                                            y+h+20))

        eyeTrackers[ currentEyeID ] = tracker

        #Increase the currentFaceID counter
        currentEyeID += 1

    #Now loop over all the trackers we have and draw the rectangle
    #around the detected faces and eyes

  for fid in faceTrackers.keys():
    tracked_position =  faceTrackers[fid].get_position()

    t_x = int(tracked_position.left())
    t_y = int(tracked_position.top())
    t_w = int(tracked_position.width())
    t_h = int(tracked_position.height())

    #Drawing a rectangle for each matched image on the base image (in blue)
    cv2.rectangle(image,(t_x, t_y),(t_x + t_w, t_y + t_h),(255,0,0),2)


  for eid in eyeTrackers.keys():
    tracked_position =  eyeTrackers[eid].get_position()

    t_x = int(tracked_position.left())
    t_y = int(tracked_position.top())
    t_w = int(tracked_position.width())
    t_h = int(tracked_position.height())

     #Drawing a rectangle for each matched image on the base image (in green)
    cv2.rectangle(image,(t_x, t_y),(t_x + t_w, t_y + t_h),(0,255,0),2)

  # Put the amount of faces and eyes you saw in a day here
  cv2.putText(image, str("Faces :" + str(count_faces)),(10,30), cv2.FONT_ITALIC, 1,(255,0,0),2,cv2.LINE_AA)
  cv2.putText(image, str("Eyes :" + str(count_eyes)),(10,70), cv2.FONT_ITALIC, 1,(0,255,0),2,cv2.LINE_AA)
  largeResult = cv2.resize(image,(775,600))

  # we can do it in seperate windows but now all in one
  cv2.imshow("Frame", largeResult)
  
# Controling the system (PTZ , taking picture, stopping the script)

  # Wait for key
  key = cv2.waitKey(1) & 0xFF # Save key for easy usage
  # clear the stream in preparation for the next frame
  rawCapture.truncate(0)

  # if the `c` key was pressed, break from the loop
  if key == ord('c'):
    break
  # if the `p` key was pressed, take a picture
  elif key == ord('p'):
    pic += 1
    # Save the image in the images folder
    image_name = camera.capture('images/image%s.jpg' % pic)
    print('Printed the image in images folder!')

  # Controlling the pantilt hat with controls
  # In a later version, this will be replaced by a tracking algorithm
  # Add zooming too ?

  elif key == ord('q'):
    xn=xc+delta_x
    pantilthat.pan(xn)
    xc=xn

  elif key == ord('d'):
    xn=xc-delta_x
    pantilthat.pan(xn)
    xc=xn

  elif key == ord('z'):
    yn=yc+delta_y
    pantilthat.tilt(yn)
    yc=yn

  elif key == ord('s'):
    yn = yc - delta_y
    pantilthat.tilt(yn)
    yc = yn

# Todo make it cleaner with functions and main
cv2.destroyAllWindows()
# import the necessary packages
import sys
import firebase_admin
from datetime import datetime
from datetime import date
from datetime import timedelta
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

# Initialize Firebase database (tracking the number of objects detected)
# Firestore will  store a structure of dates and counters (numberOfFaces, numberOfGSM, numberOfSmiles, ...) on a daily basis
# Dedicated Collections are create for each type of counters.
# In each collection, separate documents will be created for each day
# In each document, fields are created containing the number of objects detected and the date/time the last object was detected.

#-----------------------------------------------------------------------------------------------------------#
# INITIALIZING FIRESTORE DATABASE                                                                           #
#-----------------------------------------------------------------------------------------------------------#

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

# Current Day And Time in datetime format
date_today = datetime.utcnow().date()
print('today', date_today)

# Save to firestore

for i in range(1,20):

  # Create reference to the faces_tracked collection
  doc_ref = db.collection(u'faces_tracked').document(u'day_' + str(date.today() - timedelta(days=i)))
  doc_ref.set({
    u'count_items': i * 5,
    u'date': datetime.now() - timedelta(days=i)
  })

  # Create reference to the faces_tracked collection
  doc_ref = db.collection(u'eyes_tracked').document(u'day_' + str(date.today() - timedelta(days=i)))
  doc_ref.set({
    u'count_items': i * 2 ,
    u'date': datetime.now() - timedelta(days=i)
  })

print("Data successfully generated")

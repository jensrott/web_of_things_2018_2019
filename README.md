# Eindopdracht WOT

## Jens Rottiers - New Media Development

## Assignment
Create an app or program that possibly can be used on the open house day of my college.

## What I did
I created an app that tracks the amount of faces and eyes people look at a camera they pass by.  
The data can be viewed and ordered in a table. That way you can see how many people passed that location per day.  
For a more detailed description about the app see the about page in the client.

### How to use the app?

#### What do you need?
* A [Raspberry Pi](https://www.kiwi-electronics.nl/raspberry-pi-3-model-b-plus-basic-pack-red-white?search=raspberry%20pi&description=true) 
* A [Raspberry Pi Camera](https://www.kiwi-electronics.nl/raspberry-pi-camera-en-accessoires/raspberry-pi-camera-board-v2-8mp)
* A [Full kit - Pan-Tilt HAT](https://www.kiwi-electronics.nl/raspberry-pi-camera-en-accessoires/raspberry-pi-camera-board-v2-8mp) (optional)
* My repo with all the code

#### Start the React client
First create a project in [Firebase](https://console.firebase.google.com/)  
Add your firebase credentials to the app. You can do this [here](https://console.firebase.google.com/project/opencv-camera-tracking/overview)  
Add your credentials to **client/camera-app/src/keys/firebaseConfig-example.js** and rename it to **firebaseConfig.js**  
Run **npm install** to install the dependencies  
Run **npm run start** to start the front-end

#### Start the Python script
In order to make Python communicate with Firestore you need to generate a **serviceAccountKey**  
You can do this by going to this [link](https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk)  
Add your credentials to **pi/keys/serviceAccountKey-example.json** and rename it to **serviceAccountKey.json**  
Run **python3 raspberry_tracking_detection.py** to start the tracking and detection script  
If you want to first generate some fake data run **python3 firestore_create_dummy_data.py**
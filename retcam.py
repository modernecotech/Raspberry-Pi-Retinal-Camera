#
#Lynx Fundus Camera software. 
#Copyright WWW.OICO.CO.UK 2015. 
#
#
#The software uses the following libraries:
#Tkinter for the GUI.
#picamera for the image preview and capture
#simplecv for image cropping and management
#RPI.GPIO for controlling the LEDs and flash
#img2dcm library to generate the DICOM images
#pydicom to add attributes to DICOM file
# 
#use ttk.notebook function to add tabs. 
# This version of the software is for use on ODROID C1 hardware and UVC camera

import Tkinter
from Tkinter import *
import ttk 
from ttk import *
import tkFileDialog
import time
from time import sleep
import datetime
import sys, subprocess
import cPickle as pickle

#uncomment the libraries below only on a raspberry pi.
#These libraries control the camera and LEDs
import picamera
import RPi.GPIO as GPIO

camera = picamera.PiCamera()

#import the pydicom library to edit the DICOM file elements
import dicom

#use P1 header pin numbering convention for the raspberry pi GPIO. so pin 1-40
GPIO.setmode(GPIO.BOARD)

#Setup the GPIO pins for the fixation LEDs (low power)
GPIO.setup(29, GPIO.OUT, initial=0) # LED1
GPIO.setup(31, GPIO.OUT, initial=0) # LED2
GPIO.setup(33, GPIO.OUT, initial=0) # LED3
GPIO.setup(35, GPIO.OUT, initial=0) # LED4
GPIO.setup(37, GPIO.OUT, initial=0) # LED5


#illumination and flash LED GPIO pins
GPIO.setup(36, GPIO.OUT, initial=0) # IR LED
GPIO.setup(38, GPIO.OUT, initial=0) # white LED



#starting the main user interface
root = Tk()
#for large HD screen use below
#root.geometry('400x400+1370+1')
#for 7" screen use below
root.geometry('400x400+345+1')
#for 3.2" screen use below
#root.geometry('300x300+1+1')

root.title("OICO Fundus Camera")
root.wm_iconbitmap('@'+'logo-1.xbm')

#The three tabs of the user interface
note=ttk.Notebook(root)
tab1=ttk.Frame(note);
tab1.columnconfigure(0, weight=1)
tab1.rowconfigure(0, weight=1)
tab1.grid(column=3, row=20, sticky=(N,W,E,S))
tab2=ttk.Frame(note);
tab2.grid(column=5, row=20, sticky=(N,W,E,S))
tab3=ttk.Frame(note);
tab3.grid(column=3, row=20, sticky=(N,W,E,S))
tab4=ttk.Frame(note);
tab4.grid(column=3, row=20, sticky=(N,W,E,S))
tab5=ttk.Frame(note);
tab5.grid(column=3, row=20, sticky=(N,W,E,S))
note.add(tab1, text='Patient Details')
note.add(tab2, text='Camera')
note.add(tab3, text='Setup')
note.add(tab4, text='Help')
note.add(tab5, text='About')
note.pack()


#tab1 The Patient details

#Name
forenameval = StringVar()
ttkforenameval = ttk.Entry(tab1, textvariable=forenameval).grid(column=1, row=0)
forenameLabel=ttk.Label(tab1, text="Forename").grid(column=0, row=0)
surnameval = Tkinter.StringVar()
ttksurnameval = ttk.Entry(tab1, textvariable=surnameval).grid(column=1, row=1)
surnameLabel=ttk.Label(tab1, text="Surname").grid(column=0, row=1)
s1=ttk.Separator(tab1, orient=HORIZONTAL).grid(row=2, columnspan=3, stick="ew", pady=5, padx=5)

#gender details
genderlabel=ttk.Label(tab1, text="Gender").grid(column=0, row=3)
genderval=StringVar()
genderMale=ttk.Radiobutton(tab1, text='Male', variable=genderval, value='M').grid(column=1,row=3)
genderFemale=ttk.Radiobutton(tab1, text='Female', variable=genderval, value='F').grid(column=2,row=3)
s2=ttk.Separator(tab1, orient=HORIZONTAL).grid(row=4, columnspan=3, stick="ew", pady=5, padx=5)


dateofbirthlabel=ttk.Label(tab1, text="Date of Birth").grid(column=0, row=5)
dateofbirthlabelD=ttk.Label(tab1, text="Day").grid(column=0, row=6)
dateofbirthD=StringVar()
ttkdateofbirthD = Spinbox(tab1,from_=1.0, to=31, textvariable=dateofbirthD).grid(column=1, row=6)
dateofbirthlabelM=ttk.Label(tab1, text="Month").grid(column=0, row=7)
dateofbirthM=StringVar()
ttkdateofbirthM = Spinbox(tab1,from_=1.0, to=12, textvariable=dateofbirthM).grid(column=1, row=7)
dateofbirthlabelY=ttk.Label(tab1, text="Year").grid(column=0, row=8)
dateofbirthY=StringVar()
ttkdateofbirthY = Spinbox(tab1,from_=1900.0, to=2050.00, textvariable=dateofbirthY).grid(column=1, row=8)
#ttk.Label(tab1, textvariable=dateofbirth).grid(column=1,row=9)
s3=ttk.Separator(tab1, orient=HORIZONTAL).grid(row=10, columnspan=3, stick="ew", pady=5, padx=5)


#Patient Number
patientID = StringVar()
ttkpatientID = ttk.Entry(tab1, textvariable=patientID).grid(column=1, row=11)
patientIDLabel=ttk.Label(tab1, text="Patient ID").grid(column=0, row=11)


#Series number
seriesNumber = StringVar()
ttkSeriesNumber = ttk.Entry(tab1, textvariable=seriesNumber).grid(column=1, row=12)
seriesNumberLabel=ttk.Label(tab1, text="Series Number").grid(column=0, row=12)

#Study ID
StudyID = StringVar()
ttkStudyID = ttk.Entry(tab1, textvariable=StudyID).grid(column=1, row=13)
StudyIDLabel=ttk.Label(tab1, text="Study ID").grid(column=0, row=13)


#Patient Comments
PatientComments = StringVar()
ttkPatientComments = ttk.Entry(tab1, textvariable=PatientComments).grid(column=1, row=14)
PatientCommentsLabel=ttk.Label(tab1, text="Patient Comments").grid(column=0, row=14)



#Selecting the eye
eyeLabel=ttk.Label(tab2, text="Select eye").grid(column=0, row=0)
eyeLR=StringVar()
rEye=ttk.Radiobutton(tab2, text='Right Eye', variable=eyeLR, value='RightEye').grid(column=0, row=1)
lEye=ttk.Radiobutton(tab2, text='Left Eye', variable=eyeLR, value='LeftEye').grid(column=2, row=1)

#tab2 camera operation

def preview_toggle(tog=[0]):
	tog[0] = not tog[0]
	if tog[0]:
		camera.stop_preview()
	else:
		camera.preview_fullscreen=False
		camera.led=False
		#for large HD screen use below
		#camera.preview_window=(0,0,1450,1000)
		#for 7" screen use below
		camera.preview_window=(-70,1,750,540)
		#for 3.2" screen use below
		#camera.preview_window=(0,0,300,200)
		camera.start_preview()


#start camera preview button
preview_toggle_button = ttk.Button(tab2, text='Camera Preview', command=preview_toggle).grid(column=4, row=1)
s20=ttk.Separator(tab2, orient=HORIZONTAL).grid(row=2, columnspan=5, stick="ew", pady=5, padx=5)


def gpio1():
        GPIO.output(29,True) #LED1 0 degree
        GPIO.output(31,False) #LED2 90 degrees
        GPIO.output(33,False) #LED3 180 degrees
        GPIO.output(35,False) #LED4 270 degrees
        GPIO.output(37,False) #LED5  centre

def gpio2():
	GPIO.output(29,False) #LED1 0 degree
	GPIO.output(33,False) #LED3 180 degrees
	GPIO.output(37,False) #LED5 centre
	if eyeLR.get() == 'RightEye':
        	GPIO.output(31,True) #LED2 90 degrees
        	GPIO.output(35,False) #LED4 270 degrees
	else:
        	GPIO.output(31,False) #LED2 90 degrees
        	GPIO.output(35,True) #LED4 270 degrees
		

def gpio3():
        GPIO.output(29,False) #LED1 0 degree
        GPIO.output(31,False) #LED2 90 degrees
        GPIO.output(33,True) #LED3 180 degrees
        GPIO.output(35,False) #LED4 270 degrees
        GPIO.output(37,False) #LED5 centre

def gpio4():
	GPIO.output(29,False) #LED1 0 degree
	GPIO.output(33,False) #LED3 180 degrees
	GPIO.output(37,False) #LED5 centre
	if eyeLR.get() == 'RightEye':
        	GPIO.output(31,False) #LED2 90 degrees	
        	GPIO.output(35,True) #LED4 270 degrees
	else:
        	GPIO.output(31,True) #LED2 90 degrees
        	GPIO.output(35,False) #LED4 270 degrees


def gpio5():
        GPIO.output(29,False) #LED1 0 degree
        GPIO.output(31,False) #LED2 90 degrees
        GPIO.output(33,False) #LED3 180 degrees
        GPIO.output(35,False) #LED4 270 degrees
        GPIO.output(37,True) #LED5 centre

def gpiooff():
        GPIO.output(29,False)   #LED1 0 degree
        GPIO.output(31,False) #LED2 90 degrees
        GPIO.output(33,False) #LED3 180 degrees
        GPIO.output(35,False) #LED4 270 degrees
        GPIO.output(37,False) #LED5 centre


#fixation LED control buttons
fixationLabel1=ttk.Label(tab2, text='Manual fixation target selection LED').grid(column=0, row=4, columnspan=4)
fixationLED=StringVar()
zerofix=ttk.Radiobutton(tab2, text='upper', variable=fixationLED, value='0',command=gpio1).grid(column=2, row=5, stick="nesw")
ninetyfix=ttk.Radiobutton(tab2, text='nasal', variable=fixationLED, value='90',command=gpio2).grid(column=3, row=7, stick="nesw")
oneeightyfix=ttk.Radiobutton(tab2, text='lower', variable=fixationLED, value='180',command=gpio3).grid(column=2, row=9, stick="nesw")
twoseventyfix=ttk.Radiobutton(tab2, text='temporal', variable=fixationLED, value='270',command=gpio4).grid(column=0, row=7)
offfix=ttk.Radiobutton(tab2, text='cent', variable=fixationLED, value='centre', command=gpio5).grid(column=2, row=7, stick="nesw")
ninetyfix=ttk.Radiobutton(tab2, text='OFF', variable=fixationLED, value='off',command=gpiooff).grid(column=5, row=4, stick="nesw")
s22=ttk.Separator(tab2, orient=HORIZONTAL).grid(row=10, columnspan=5, stick="ew", pady=5, padx=5)



#tab2 toggle LED illumination
def led_illumination_on():
        if led_illumination_string.get() == 'IR':
                print "IR" 
                GPIO.output(36,True)  #start infrared 
		GPIO.output(38,False) #stop white
        elif led_illumination_string.get() == 'WHITE':
                print "WHITE"
                GPIO.output(36,False)  #stop infrared 
		GPIO.output(38,True)   #start white
	else :
		print "OFF"
                GPIO.output(36,False)  #stop infrared 
		GPIO.output(38,False)   #stop white


#Illumination LED control buttons
illuminationLabel=ttk.Label(tab2, text='LED illumination').grid(column=0, row=11, columnspan=2)
led_illumination_string=StringVar()
led_illumination_on_btn =ttk.Radiobutton(tab2, text='IR', variable=led_illumination_string, value='IR', command=led_illumination_on).grid(column=2, row=11)
led_illumination_on_btn =ttk.Radiobutton(tab2, text='White', variable=led_illumination_string, value='WHITE', command=led_illumination_on).grid(column=3, row=11)
led_illumination_on_btn =ttk.Radiobutton(tab2, text='OFF', variable=led_illumination_string, value='OFF', command=led_illumination_on).grid(column=4, row=11)
s23=ttk.Separator(tab2, orient=HORIZONTAL).grid(row=12, columnspan=5, stick="ew", pady=5, padx=5)


#Sequence for picture capture
tempIDjpg = StringVar()
tempIDdcm = StringVar()
tempIDdt = StringVar()
def picCapture_start():
	tempIDdt.set(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
	tempID= surnameval.get() + '_' + forenameval.get() + '_' + dateofbirthD.get() + dateofbirthM.get() + dateofbirthY.get() + '_' + patientID.get() + '_' + eyeLR.get() + '_' + genderval.get() + '_' + tempIDdt.get()
	camera.resolution = (2592,1944)
	camera.capture('/home/pi/images/'+ tempID + '.jpg')
	#Sequence for saving dicom file
	tempIDjpg.set('/home/pi/images/' + tempID + '.jpg')
	tempIDdcm.set('/home/pi/images/' + tempID + '.dcm')
	if imageVersion.get() == 'JD':
		dicomout()
	elif imageVersion.get() == 'D':
		dicomout()
		time.sleep(2)
		subprocess.call(["rm", tempIDjpg.get()])
		
def dicomout():
	subprocess.call(["img2dcm", tempIDjpg.get(), tempIDdcm.get()])
	ds=dicom.read_file(tempIDdcm.get())
	#generating initial DICOM file with the SOP Class UID for ophthalmic photos and OICO unique ROOT ID. 
	ds.SOPClassUID="1.2.840.10008.5.1.4.1.1.77.1.5.1"
	ds.SOPInstanceUID="1.2.840.10008.5.1.4.1.1.77.1.5.1"+tempIDdt.get()
	ds.StudyDate=datetime.datetime.now().strftime("%Y-%m-%d")
	ds.StudyTime=datetime.datetime.now().strftime("%H:%M:%S")
	ds.PatientsName=forenameval.get() + " " + surnameval.get()
	ds.UID="1.2.826.0.1.3680043.9.3918"
	ds.PatientBirthDate=dateofbirthY.get() + dateofbirthM.get() + dateofbirthD.get()
	ds.PatientSex=genderval.get()
	ds.PatientComments=PatientComments.get()
	ds.StudyID=StudyID.get()
	ds.SeriesNumber= seriesNumber.get()
	ds.ReferringPhysiciansName= PhysicianName.get()
	ds.OperatorsName=OperatorName.get()
	ds.InstitutionName=InstitutionName.get()
	ds.InstitutionAddress=Address.get()
	ds.save_as(tempIDdcm.get())


#Taking picture sequence APS including flash button
picCaptureLabel=ttk.Label(tab2, text='Capture Picture').grid(column=0, row=13, columnspan=3)
picCapture_button = ttk.Button(tab2, text='Capture', command=picCapture_start).grid(column=4, row=13)


#Tab 3 setup
#Selecting image output versions
imageVersion=StringVar()
InstitutionName = StringVar()
InstitutionAddress = StringVar()
OperatorName = StringVar()
PhysicianName = StringVar()
#loading from pickled saved settings
pkl_file=open('settings.pkl', 'rb')
SAVED_SETTING=pickle.load(pkl_file)
pkl_file.close()
imageVersion.set(SAVED_SETTING[0])
InstitutionName.set(SAVED_SETTING[1])
InstitutionAddress.set(SAVED_SETTING[2])
OperatorName.set(SAVED_SETTING[3])
PhysicianName.set(SAVED_SETTING[4])

imageversionLabel=ttk.Label(tab3, text="Select image output").grid(column=0, row=0)
jpeganddicom=ttk.Radiobutton(tab3, text='JPEG & DICOM', variable=imageVersion, value='JD').grid(column=1, row=0, stick="nesw")
jpegonly=ttk.Radiobutton(tab3, text='JPEG Only', variable=imageVersion, value='J').grid(column=1, row=1, stick="nesw")
dicomonly=ttk.Radiobutton(tab3, text='DICOM Only', variable=imageVersion, value='D').grid(column=1, row=2, stick="nesw")

#Institution and operator details
institutionlabel=ttk.Label(tab3, text='Institution and Operator details').grid(column=0, row=4)
ttkInstitutionName= ttk.Entry(tab3, textvariable=InstitutionName).grid(column=1, row=5)
InstitutionNameLabel=ttk.Label(tab3, text="Institution Name").grid(column=0, row=5)

ttkInstitutionAddress= ttk.Entry(tab3, textvariable=InstitutionAddress).grid(column=1, row=6)
InstitutionAddressLabel=ttk.Label(tab3, text="Institution Address").grid(column=0, row=6)

ttkOperatorName= ttk.Entry(tab3, textvariable=OperatorName).grid(column=1, row=7)
OperatorNameLabel=ttk.Label(tab3, text="Operator Name").grid(column=0, row=7)

ttkPhysicianName= ttk.Entry(tab3, textvariable=PhysicianName).grid(column=1, row=8)
PhysicianNameLabel = ttk.Label(tab3, text="Physician Name").grid(column=0, row=8)

def saveSettings():
	SAVED_SETTINGS = [imageVersion.get(), InstitutionName.get(), InstitutionAddress.get(), OperatorName.get(), PhysicianName.get()]
	output = open('settings.pkl', 'wb')
	pickle.dump(SAVED_SETTINGS, output)
	output.close()

#saving settings for tab3 using pickle
savesettings_button = ttk.Button(tab3, text='Save Settings', command=saveSettings).grid(column=1, row=10)


#tab4 with help
helpLabel=ttk.Label(tab4, text='Operating Instructions for illumination and optics\n').grid(column=0, row=0, stick="nesw")
helpText=ttk.Label(tab4, text='The operator sequence is as follows.\n 1- Verify that settings are correct.\n 2-Enter the patient details\n3-Go to camera tab and click on preview button twice\n4-Use the focus to focus the patient eye\n5-Take an image by clicking the capture button or clicking the \nphysical trigger\n6-The images are saved automatically under the images folder\n7-Note that JPEG images do NOT save patient and other\n information DICOM is recommended').grid(column=0, row=1, stick="nesw")

#tab5 about
aboutLabel=ttk.Label(tab5, text='This fundus camera was developed and produced by\n\n Ophthalmic Instrument Company (c) 2015\n London, United Kingdom\n\n Chief Developers are Mr Aysar Aziz and Dr Hayder Aziz\n\n Contact Details for customer support can be found on\n www.oico.co.uk').grid(column=0, row=0)
logoimage=PhotoImage(file='/home/pi/logo-1.ppm')
helpImageLabel=ttk.Label(tab5, image=logoimage).grid(column=0, row=1, stick="s")
#looping the main Tkinter user interface
root.mainloop()

#uncomment when connected to pi
GPIO.cleanup()
camera.close()

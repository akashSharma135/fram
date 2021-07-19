""" importing the necessary modules """
import face_recognition
import cv2
import numpy as np
from tkinter import *
import os
from datetime import date
from datetime import datetime
import csv
from tkinter.filedialog import askopenfile
from tkinter.messagebox import showwarning
import shutil
import subprocess as sp

# Specifying the path
path = f'./attendance/{str(date.today().year)}/{str(date.today().month)}'
directory = '.\img\known'

"""
    Passing a reference of VideoCapture to the start_capturing()
"""
def start_capturing(video_capture):
    # Load a sample picture and learn how to recognize it.
    images = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            images.append(f)

    load_image = []
    face_encoding = []
    for image in images:
        load_image.append(face_recognition.load_image_file(f"{image}"))
    # converting the list into numpy array
    load_image = np.asarray(load_image)
    for image in load_image:
        face_encoding.append(face_recognition.face_encodings(image)[0])
    # Converting the list into numpy array
    face_encoding = np.asarray(face_encoding)

    # Create arrays of known face encodings and their names
    known_face_encodings = []
    for known_face_encoding in face_encoding:
        known_face_encodings.append(known_face_encoding)

    known_face_names = []
    with open('name.csv', 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            known_face_names.append(row[0])
        known_face_names = [x.upper() for x in known_face_names]
        known_face_names.sort()

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                mark_attendence(name)

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img=frame, text=name, org=(left + 6, bottom - 6), fontFace=font, fontScale=0.7,
            color=(255, 255, 255), thickness=1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

"""
    Marking the attendence
"""
def mark_attendence(name):
    if name != "Unknown":
        nameList = []
        if not os.path.exists(path):
            os.makedirs(path)

        # If the file doesn't exists, then create it
        if os.path.isfile(path + '/' + str(date.today()) + '.csv') == False:
            with open(path + '/' + str(date.today()) + '.csv', 'a+') as f:
                pass
        else:
            with open(path + '/' + str(date.today()) + '.csv', 'r+') as f:

                # Reading the csv file if the data already exists
                if os.path.getsize(f'{path}/{str(date.today())}.csv') != 0:
                    myDataList = csv.reader(f)
                    for row in myDataList:
                        nameList.append(row[0])

            with open(path + '/' + str(date.today()) + '.csv', 'a', newline='') as f:
                # Creating a writer object
                csvwriter = csv.writer(f)
                # if name doesn't exists in the file then insert it
                if name not in nameList:
                    now = datetime.now()
                    dtString = now.strftime(' %H:%M:%S')
                    list = [name, dtString]
                    csvwriter.writerow(list)


"""
    Function for opening the file
"""
def open_file():
    file = askopenfile(mode ='r', filetypes =[('CSV Files', '*.csv')], initialdir = './attendance', title = "Open A File")
    if file is not None:
          programName = "Notepad.exe"
          # Converting TextIOWrapper object into string
          fileName = file.name
          sp.Popen([programName, fileName])


"""
    Add new image to the data
"""
def add_new_image():
    # Open the dialog box
    file = askopenfile(mode = 'a', filetypes = (("png files", "*.png"), ("jpg files", "*.jpg"), ("jpeg files", "*.jpeg")), title = "Add New Image")
    shutil.copy(file.name, './img/known')


"""
    Submitting the new name
"""
def submit():
    name=name_var.get()
    name_var.set("")
    add_name_to_file(name)


"""
    method to add name to the file
"""
def add_name_to_file(name):
    list = os.listdir('./img/known')
    num_of_image = len(list)
    row_count = 0
    with open('./name.csv') as f:
        csv_reader = csv.reader(f)
        row_count = sum(1 for row in csv_reader)
    if num_of_image > row_count:
        with open("name.csv", 'a') as file:
            file.write(name + '\n')


"""
    method to access admin authorities
"""
def login(object, authorizeWindow):
    name = username_var.get()
    username_var.set("")
    password = password_var.get()
    password_var.set("")
    username = ""
    psw = ""

    with open('password.csv', 'r') as file:
        authentication_details = []
        csv_reader = csv.reader(file)
        for row in csv_reader:
            username = row[0]
            psw = row[1]

    if name == username and password == psw:
        authorizeWindow.destroy()
        object()
    else:
        authorizeWindow.destroy()
        showwarning("Warning", "Username or Password doesn't match!!")

"""
    method to change the username or password
"""
def change_authentication_details(usernameWindow):
    old_username = old_username_var.get()
    new_username = new_username_var.get()
    old_password = old_password_var.get()
    new_password = new_password_var.get()

    username = ""
    psw = ""

    with open('password.csv', 'r', newline='') as file:
        # authentication_details = []
        csv_reader = csv.reader(file)
        for row in csv_reader:
            username = row[0]
            psw = row[1]

    if old_username == username and old_password == psw:
        with open('password.csv', 'w', newline='') as file:
            csv_writer = csv.writer(file)
            authentication_details = [new_username, new_password]
            csv_writer.writerow(authentication_details)

    usernameWindow.destroy()


"""
    Window for changing the username or password
"""
def change_authentication_details_window():
    usernameWindow = Toplevel(root)
    usernameWindow.title("Change Username")
    usernameWindow.geometry("400x400")
    usernameWindow.resizable(0, 0)
    old_username = Label(usernameWindow, text = "Old Username").place(x = 30, y = 50)
    new_username = Label(usernameWindow, text = "New Username").place(x = 30, y = 80)
    old_password = Label(usernameWindow, text = "Old Password").place(x = 30, y = 110)
    new_password = Label(usernameWindow, text = "New Password").place(x = 30, y = 140)
    old_username_entry = Entry(usernameWindow, textvariable = old_username_var ).place(x = 120, y = 50)
    new_username_entry = Entry(usernameWindow, textvariable = new_username_var).place(x = 120, y = 80)
    old_password_entry = Entry(usernameWindow, textvariable = old_password_var).place(x = 120, y = 110)
    new_password_entry = Entry(usernameWindow, textvariable = new_password_var).place(x = 120, y = 140)
    exit_btn = Button(usernameWindow, text = "Exit",activebackground = "green", command = lambda:usernameWindow.destroy()).place(x = 80, y = 170)
    submit_btn = Button(usernameWindow, text = "Change",activebackground = "red", command = lambda:change_authentication_details(usernameWindow)).place(x = 150, y = 170)


"""
    method for adding new name
"""
def add_name_window():
    nameWindow = Toplevel(root)
    nameWindow.title("Add Name")
    nameWindow.geometry("300x200")
    nameWindow.resizable(0, 0)
    name = Label(nameWindow, text = "Name").place(x = 30,y = 50)
    name_entry = Entry(nameWindow, textvariable = name_var).place(x = 80, y = 50)
    exit_btn = Button(nameWindow, text = "Exit",activebackground = "green", command = lambda:nameWindow.destroy()).place(x = 80, y = 130)
    submitbtn = Button(nameWindow, text = "Submit",activebackground = "red", command = lambda:submit()).place(x = 80, y = 90)


"""
    add name window
"""
def authorize_user_window(object):
    authorizeWindow = Toplevel(root)
    authorizeWindow.title("Login")
    authorizeWindow.geometry("400x400")
    authorizeWindow.resizable(0, 0)
    authorizeWindow.configure(background='cyan')
    name = Label(authorizeWindow, text = "Username", background="cyan", foreground="black").place(x = 40, y = 60)
    name_entry = Entry(authorizeWindow, textvariable = username_var).place(x = 120, y = 60)
    password = Label(authorizeWindow, text = "Password", background="cyan", foreground="black").place(x = 40, y = 90)
    password_entry = Entry(authorizeWindow, textvariable = password_var).place(x = 120, y = 90)
    login_btn = Button(authorizeWindow, text = "Login", background="green2", activebackground = "red", command = lambda:login(object, authorizeWindow), height = 2, width = 5).place(x = 120, y = 150)


"""
    open the instruction window
"""
def open_instruction_window():

    # Toplevel object which will
    # be treated as a new window
    newWindow = Toplevel(root)

    # sets the title of the
    # Toplevel widget
    newWindow.title("New Window")
    newWindow.configure(background='AntiqueWhite3')

    # sets the geometry of toplevel
    newWindow.geometry("500x200")
    newWindow.resizable(0, 0)

    # A Label widget to show in toplevel
    Label(newWindow, text="'Start' - Press to capture window").place(x = 50, y = 10)

    Label(newWindow, text ="'Q' - Press to close the capturing window").place(x = 50, y = 50)

    Label(newWindow, text = "Must add the name after inserting a new image").place(x = 50, y = 90)


# User Interface
root = Tk()

# Specifying the window properties
root.geometry("600x600")
root.resizable(0, 0)
root.title("FRAM")
root.configure(background='turquoise')

# naming input variables for particular fields
name_var = StringVar()
username_var = StringVar()
password_var = StringVar()
old_username_var = StringVar()
new_username_var = StringVar()
old_password_var = StringVar()
new_password_var = StringVar()

# create a toplevel menu
menubar = Menu(root)
menubar.add_command(label="Instuctions", command=open_instruction_window)
# Add file menu
file = Menu(menubar, tearoff = 0, background='AntiqueWhite3', foreground='black', activebackground='white', activeforeground='black')
menubar.add_cascade(label="File", menu=file)
file.add_command(label="Add New Image", command= lambda: authorize_user_window(add_new_image))
file.add_command(label="Add New Name", command= lambda: authorize_user_window(add_name_window))
file.add_command(label="Change Username/Password", command= lambda: change_authentication_details_window())
file.add_separator()
file.add_command(label ='Exit', command = root.destroy)

#Configuring the menubar on the root
root.config(menu=menubar)

# Start button, to start the video
start_button = Button(root, text="Start", command= lambda: start_capturing(cv2.VideoCapture(0)), background="SpringGreen2", padx=10, pady=10, font="AppleSystemUIFont 18 normal roman")
start_button.place(relx=0.5, rely=0.2, anchor=CENTER)

# Quit Button, To quit the app
quit_button = Button(root, text="Quit", command=root.destroy, background="red2", padx=10, pady=10, font="AppleSystemUIFont 18 normal roman")
quit_button.place(relx=0.5, rely=0.4, anchor=CENTER)

# Open Button, to open the file opening dialog box
open_btn = Button(root, text ='Open', command = lambda:authorize_user_window(open_file), background="DodgerBlue2", padx=10, pady=10, font="AppleSystemUIFont 18 normal roman")
open_btn.place(relx=0.5, rely=0.6, anchor=CENTER)

# Entry point for the main UI
root.mainloop()

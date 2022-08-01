#!/bin/python3
# -*- coding:utf-8 -*-
# PYTHON 3 ONLY


'''
This is a little fly-killer game.
Goal is to click as many flies as possible.
But spare the butterflies!
________________________________________________________________________
INSTALLATION (LINUX - Debian and variants like Ubuntu):
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
go to the terminal an type following commands:

	sudo apt-get install python3 python3-tk
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade pathlib
	python3 -m pip install --upgrade Pillow

after that, you can start the game by typing

	python3 flies.py
	
or just

	./flies
________________________________________________________________________
INSTALLATION (WINDOWS 8 or higher)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You got to download python version 3.

then run "cmd.exe" install library (tk should be on board already)
and start the game script:

	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade pathlib
	python3 -m pip install --upgrade Pillow
	python3 flies.py


Coded with
	Debian/GNU Linux 11 Bullseye
	Kernel 5.10.0-16-amd64
	Python 3.9.2
	Tcl/Tk version 8.6
	pathlib-1.0.1
	Pillow-9.2.0
	
have fun :-)
'''


# library imports
from multiprocessing import Process
import tkinter as tk
from tkinter import *
import tkinter.messagebox
from pathlib import Path
import random
from PIL import Image, ImageTk, ImageOps

version_string = "2022.7b1"
# determine the path of the script - useful if the script is running from another directory
script_path = Path(__file__).resolve().parent


# configuration variables
cfg_fullscreen = False		        # fill the window, but not with canvas :-(
cfg_screen_resolution = "800x600"	# game made for 800x600, other res not yet implemented :-(
cfg_mouse_cursor_visible = True		# on touch screens cursor is ugly!
cfg_assets_folder = Path(script_path/"assets/") # paths compatible with all OSes

cfg_countdown = 90	                # time left to kill at game start
cfg_next_level_multi = 5	        # X * level = number flies to be killed for next level
cfg_butterfly_probability = 6       # probability X : 1 that the butterfly comes (each second)
cfg_butterfly_visible_seconds = 6	# number of seconds the butterfly will stay visible
cfg_butterfly_penalty_time = 5	    # countdown goes down when killing butterflies

# all the picture files to be loaded
cfg_pics_flies = ["fly01.png",
                  "fly02.png",
                  "fly03.png",
                  "fly04.png",
                  "fly05.png",
                  "fly06.png",
                  "fly07.png",
                  "fly08.png",
                  "fly09.png",
                  "fly10.png"]

cfg_pics_butterflies = ["butterfly1.png",
                        "butterfly2.png",
                        "butterfly3.png",
                        "butterfly4.png"]

cfg_pics_bg = ["background1.jpg",
               "background2.jpg",
               "background3.jpg",
               "background4.jpg"]

cfg_pics_special_bg = ["background_killer.jpg",
                       "background_sunset.jpg",
                       "background_fly_love.jpg",
                       "background_butterflies.jpg",
                       "background_dead_butterfly.jpg"]

cfg_pics_blood = ["blood1.png",
                  "blood2.png",
                  "blood3.png",
                  "blood4.png",
                  "blood5.png",
                  "blood6.png",
                  "blood7.png",
                  "blood8.png",
                  "blood9.png"]

cfg_pics_rainbow = ["rainbow_splash1.png",
                  "rainbow_splash2.png",
                  "rainbow_splash3.png"]

# all the text messages, so it's easier to translate the game
cfg_killer_messages       = ["Yo!\nThe game is NOT to kill butterflies!",
                             "You would kill\nlittle children, too,\nwouldn't you?!",
                             "May butterflies visit you at night, when you sleep...\nMany, many butterflies...\nand then it's time for revenge!",
                             "How can you do so?\nthat's just inhuman \U0001F928",
                             "Ya like that, hu?",
                             "Poor, lovely butterflies \U0001F614"]
                             
msg_window_title = "Flies"
msg_welcome      = "Here we are.\nYou have\n" + str(cfg_countdown) + " seconds to kill as many flies as possible\n...I said »flies«! \N{winking face}"
msg_info         = "Welcome to FLIES!\nA litte game written\n2022 by M. J. Konrad\nIt's open source and - I think so - well commented,\nso do whatever you want :-)"

# header, where the stats are shown
msg_header_time_left               = "TIME LEFT: "
msg_header_seconds_left            = "s LEFT. "
msg_header_killed_flies            = " KILLED FLIES. "
msg_header_level                   = "Level:"
msg_header_killed_no_butterfly     = " NO BUTTERFLY KILLED \U0001F642"
msg_header_killed_one_butterfly    = " KILLED A BUTTERFLY! \U0001F633"
msg_header_killed_few_butterflies  = " BUTTERFLIES KILLED! \U0001F928"
msg_header_killed_many_butterflies = " BUTTERFLIES KILLED! \N{disappointed face}"

msg_dont_kill_butterflies  = "OUCH!\nDon't kill butterflies!!\n"
msg_penalty_time           = " seconds penalty time!\n"
msg_hurry_up               = "What?! Come on, come on, hurry!!"
msg_timeout                = "Time out!\n\n"
msg_killed_no_butterfly    = "You didn't kill any butterfly!\nMay the butterflies be with you. \U0001F60C\n\n"
msg_killed_few_butterflies = "You didn't kill so many butterflies!\nThose where Accidents, right?\n\n"
msg_butterfly_murderer     = "You're a damned butterfly murderer!\nShame!! Hope you'll have nightmares. \U0001F614\n\n"
msg_num_flies_killed       = " flies killed, that are\n"
msg_kills_per_minute       = "\nkills per minute.\n\n\n...but anyway...\nthe flies will win in the end \U0001F60C"
msg_fly_enthusiast         = "Fly enthusiast!\nYou did not kill a single fly.\nThis is not a TV show.\nYou have to play yourself..."
msg_quit_game              = "Quit Game"


class Flies(tk.Tk):
	'''main class'''
	####################################################################
	def __init__(self):
		'''init, will be called first'''
		super().__init__() # so we can use tk.TK attributes and behaviors
		
		# set up the window
		self.title(msg_window_title)
		self.geometry(cfg_screen_resolution)
		if cfg_fullscreen: self.attributes("-fullscreen", True)
		if not cfg_mouse_cursor_visible: self.config(cursor="none")
		# and the canvas inside it
		self.canvas = Canvas(self)
		self.canvas.pack(expand=YES, fill=tk.BOTH)
		
		# init game variables
		self.game_level = 1                 # game level to start from
		self.flies_killed_current_level = 0 # nothing killed for now
		self.flies_killed_total = 0
		self.butterflies_killed = 0
		self.butterfly_is_visible = False   # there's no butterfly at the beginning
		self.butterfly_stays_visible = cfg_butterfly_visible_seconds
		self.countdown = cfg_countdown
		
		# this lists will be filled to get images out of them
		self.pics_bg = list()             # all backgrounds
		self.pics_special_bg = list()     # special backgrounds :-)
		self.pics_flies = list()          # all flies
		self.pics_butterflies = list()    # all butterflies
		self.pics_blood = list()          # all the splatter stuff
		self.pics_rainbow = list()        # rainbow blood
		self.fly = list()                 # flies currently visible on the screen
		self.blood_splash = list()        # blood splashes staying on the screen
		self.rainbow = list()             # rainbow blood splashes on screen
		self.butterfly = None             # first, there is no butterfly!
		
		self.load_images() # before using images they must be loaded
		
		self.change_background_image() # set the background image with all parameters
		title_bar = self.canvas.create_rectangle(0,0,800,40, fill="#000000999")
		
		self.create_fly()       # create the first fly
		self.create_butterfly() # create butterfly (it's not visible for now!)
		
		# bind the last fly element in the list (it's the only one yet) to the click event
		self.canvas.tag_bind(self.fly[-1], "<Button-1>", self.fly_clicked)
		
		# first time text init with all parameters, no text needed yet
		self.obj_countdown_text = self.canvas.create_text(
		  10, 12, text="", fill="green", anchor=NW, font=('Helvetica','20','bold'))
		
		self.withdraw() # msgbox went to the background, so hide main window
		tkinter.messagebox.showinfo(message=msg_welcome, parent=self) # show welcome message
		self.deiconify() # let main window appear again
		
		self.after(1, self.update_timer) # call the timer first to start it
		self.mainloop()                  # start the main loop (Tk)
	
	
	####################################################################
	def update_timer(self):
		'''does stuff and call itself back after 1000 milliseconds'''
		self.countdown -= 1     # simply count down
		self.update_text()      # let the player see what's going on
		
		# probability of butterfly is coming
		if random.randint(0, cfg_butterfly_probability) == 1:
			# change visibly variable
			self.butterfly_is_visible = True
			# make butterfly object visible
			self.canvas.itemconfig(self.butterfly, state="normal")
		
		if self.butterfly_is_visible == True:
			# decrase time butterfly stays visible
			self.butterfly_stays_visible -= 1
			# get the butterfly object on top (otherwise e.g. blood is above it)
			self.canvas.tag_raise(self.butterfly)
			if self.butterfly_stays_visible == 0: # should butterfly disapear?
				self.create_butterfly() # set new coordinates and make it invisble
		
		if self.countdown <= 0: # when the time is out
			self.game_over()    # the game is over
		else:
			self.after(1000, self.update_timer) # come back here in 1000 ms
	
	
	####################################################################
	def fly_clicked(self, event):
		'''a fly was clicked! There're lots of things to do!'''
		if self.countdown > 0:
			self.flies_killed_current_level += 1 # one more fly was killed this level
			self.flies_killed_total += 1         # total kills +1, too
			self.update_text()                   # we have to show what happened
			
			# the bloody game - one more blood splash have to be added to the pool
			self.blood_splash.append(self.canvas.create_image(
			event.x, event.y, image=random.choice(self.pics_blood), anchor=CENTER))
			
			# all flies change position now
			for i in self.fly:
				self.canvas.moveto(i, random.randint(50, 750), random.randint(50, 550))
				self.canvas.tag_raise(i)
			
			# look if there're enough kills in this level to level up
			if self.flies_killed_current_level==self.game_level * cfg_next_level_multi:
				self.game_level += 1
				self.flies_killed_current_level = 0			
				self.create_fly() # each new level borns a new fly :-)
				# each new fly must be able to get clicked
				self.canvas.tag_bind(self.fly[-1], "<Button-1>", self.fly_clicked)
	
	
	####################################################################
	def butterfly_clicked(self, event):
		'''a butterfly was clicked :-('''
		if self.countdown > 0:
			self.butterflies_killed += 1
			self.update_text()
			
			# create a new rainbow blood splash
			self.rainbow.append(self.canvas.create_image(
			event.x, event.y, image=random.choice(self.pics_rainbow), anchor=CENTER))
			
			if self.butterflies_killed == 1:
				# show message for first killed butterfly (informative)
				tkinter.messagebox.showinfo(
				message=msg_dont_kill_butterflies +
				str(cfg_butterfly_penalty_time) + msg_penalty_time + msg_hurry_up)
			else:
				# show message for more killed butterflies (more fun)
				tkinter.messagebox.showinfo(message=random.choice(cfg_killer_messages))
			
			self.countdown -= cfg_butterfly_penalty_time # penalization must be
			self.canvas.delete(self.butterfly) # old butterfly has to go
			self.create_butterfly()            # a new butterfly waiting to become visible :-)
	
	
	####################################################################
	def load_images(self):
		'''loads the images and make the usable for Tk'''
		print("Loading images...")
		for i in cfg_pics_bg:                            # for each image path:
			imgTemp = Image.open(cfg_assets_folder/i)    # open the image
			img = imgTemp.resize((800, 600))             # resize it
			self.pics_bg.append(ImageTk.PhotoImage(img)) # and make it usable for Tk
		
		for i in cfg_pics_flies:
			imgTemp = Image.open(cfg_assets_folder/i)
			img = ImageOps.contain(imgTemp, (100, 100))
			self.pics_flies.append(ImageTk.PhotoImage(img))
		
		for i in cfg_pics_butterflies:
			imgTemp = Image.open(cfg_assets_folder/i)
			img = ImageOps.contain(imgTemp, (220, 220))
			self.pics_butterflies.append(ImageTk.PhotoImage(img))
		
		for i in cfg_pics_blood:
			imgTemp = Image.open(cfg_assets_folder/i)
			img = ImageOps.contain(imgTemp, (100, 100))
			self.pics_blood.append(ImageTk.PhotoImage(img))
		
		for i in cfg_pics_rainbow:
			imgTemp = Image.open(cfg_assets_folder/i)
			img = ImageOps.contain(imgTemp, (150, 150))
			self.pics_rainbow.append(ImageTk.PhotoImage(img))
		
		for i in cfg_pics_special_bg:
			imgTemp = Image.open(cfg_assets_folder/i)
			img = ImageOps.contain(imgTemp, (800, 600))
			self.pics_special_bg.append(ImageTk.PhotoImage(img))
	
	
	####################################################################
	def update_text(self):
		'''updates the text element'''
		if self.butterflies_killed == 0:
			txt = (str(self.countdown) + msg_header_seconds_left +
			       str(self.flies_killed_total) + msg_header_killed_flies +
			       msg_header_killed_no_butterfly)
		elif self.butterflies_killed == 1:
			txt = (str(self.countdown) + msg_header_seconds_left +
			       str(self.flies_killed_total) + msg_header_killed_flies +
			       msg_header_killed_one_butterfly)		
		elif self.butterflies_killed > 3:
			txt = (str(self.countdown) + msg_header_seconds_left +
			       str(self.flies_killed_total) + msg_header_killed_flies +
			       str(self.butterflies_killed) + msg_header_killed_many_butterflies)
		else:
			txt = (str(self.countdown) + msg_header_seconds_left +
			       str(self.flies_killed_total) + msg_header_killed_flies +
			       str(self.butterflies_killed) + msg_header_killed_few_butterflies)
		
		self.canvas.itemconfig(self.obj_countdown_text, text=txt)
	
	
	####################################################################
	def create_fly(self):
		'''creates a new fly'''
		self.fly.append(self.canvas.create_image(
		  random.randint(20,780), random.randint(40,580), image=random.choice(self.pics_flies), anchor=CENTER))
	
	
	####################################################################
	def create_butterfly(self):
		'''creates a butterfly. The visibly is handled in the update_timer function
		There is only one butterfly at a time, so no list is needed'''
		# if there already was a butterfly created, delete it
		if not self.butterfly == None:
			self.canvas.delete(self.butterfly)
		
		self.butterfly_is_visible = False
		self.butterfly_stays_visible = cfg_butterfly_visible_seconds
		self.butterfly = self.canvas.create_image(
		  random.randint(20,780), random.randint(40,580),
		  image=random.choice(self.pics_butterflies),
		  anchor=CENTER, state="hidden")
		# bind the new butterfly to click event
		self.canvas.tag_bind(self.butterfly, "<Button-1>", self.butterfly_clicked)
	
	
	####################################################################
	def change_background_image(self):
		'''changes the background image'''
		self.obj_background = self.canvas.create_image(
		  0, 0, image=random.choice(self.pics_bg), anchor=NW)
	
	
	####################################################################
	def game_over(self):
		'''Just shows the stats and quit'''
		
		# calculate kills per minute. This gives a score regardless ot the game duration
		kills_per_minute = self.flies_killed_total / cfg_countdown * 60
		
		# different background images for the last scene
		if self.butterflies_killed == 0:
			self.canvas.delete("all")
			self.obj_background = self.canvas.create_image(
			 0, 0, image=self.pics_special_bg[3], anchor=NW)
		
		if self.butterflies_killed > 3:
			self.canvas.delete("all")
			self.obj_background = self.canvas.create_image(
			 0, 0, image=self.pics_special_bg[4], anchor=NW)
		
		if kills_per_minute > 80:
			self.canvas.delete("all")
			self.obj_background = self.canvas.create_image(
			 0, 0, image=self.pics_special_bg[0], anchor=NW)

		if self.flies_killed_total == 0:
			self.canvas.delete("all")
			self.obj_background = self.canvas.create_image(
			 0, 0, image=self.pics_special_bg[2], anchor=NW)
		
		
		msg = msg_timeout # first part of the message is the same ever
		
		# customize the rest of the message depending on what the player did
		if self.butterflies_killed == 0: msg=msg + msg_killed_no_butterfly
		elif self.butterflies_killed <= 2: msg = msg + msg_killed_few_butterflies
		else: msg=msg + msg_butterfly_murderer
		         
		if self.flies_killed_total > 0:
			msg = (msg + str(self.flies_killed_total) + msg_num_flies_killed +
			  str(kills_per_minute) + msg_kills_per_minute)
		else: msg = (msg + msg_fly_enthusiast)
			  
		tkinter.messagebox.showinfo(message=msg) # show the message
		
		# create a quit button
		quit_button = Button(self, text=msg_quit_game, command=quit)
		quit_button.place(x=690,  y=560,  width=100, height=30)


Flies() # time to start it all

print("Quit game now (main windows was closed)...")
quit(0) # sure is sure
 

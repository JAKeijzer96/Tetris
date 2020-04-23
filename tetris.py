# -------------------------------
# Name: Tetris
# Author: Jasper Keijzer
# Language: Python 3.6.9
# 
# Created: 10/04/2020
# Inspiration & source for large amount of code:
# TigerhawkT3
# https://github.com/TigerhawkT3/tetris
# https://www.youtube.com/playlist?list=PLQ7bGgvf9FtGJV3P4gj1cWdBYacQo7bKz
# -------------------------------

try:
	import tkinter as tk
except ImportError:
	print('The tkinter module cannot be found or is not installed')
try:
	from tkinter import messagebox
except ImportError:
	print('The tkinter/messagebox module cannot be found or is not installed')
try:
	from tkinter import Toplevel
except ImportError:
	print('The tkinter/Toplevel module cannot be found or is not installed')
try:
	import pygame as pg
except ImportError:
	audio = None
	print('The pygame module cannot be found or is not installed\nThere will be no audio')
else:
	audio = True
try:
	from matrix_rotation import rotate_array as rot_arr
except ImportError:
	print('The matrix_rotation module cannot be found or is not installed'\
		'The original code can be found on https://github.com/TigerhawkT3/matrix_rotation')
import random
import sys
import time

class Shape():
	def __init__(self, key, shape, piece, row, column, coords):
		'''
		key is the name of the shape
		shape is a 2D array presentation with '*'
		piece is a 2D array with references to canvas child objects
		row is the current row of the object
		column is the current column of the object
		coords is a list of tuples of 4 integers (x1,y1,x2,y2) with the coordinates of the object
		'''
		self.key = key
		self.shape = shape
		self.piece = piece
		self._row = row
		self.column = column
		self.coords = coords
		self._rotation_index = 0
		self.hover_time = self.spin_time = time.perf_counter()
	@property
	def row(self):
		return self._row
	@row.setter
	def row(self, newrow):
		if newrow != self._row:
			self._row = newrow
			self.hover_time = time.perf_counter()
	@property
	def rotation_index(self):
		return self._rotation_index
	@rotation_index.setter
	def rotation_index(self, newvalue):
		self._rotation_index = newvalue
		self.spin_time = time.perf_counter()
	@property
	def hover(self):
		# 0.5 is a magic number, hover for max 0.5 second
		return time.perf_counter() - self.hover_time < 0.5
	@property
	def spin(self):
		# 0.5 is a magic number, spin for max 0.5 second
		return time.perf_counter() - self.spin_time < 0.5

class Tetris():
	def __init__(self, parent, audio=None):
		# Check for flags in the command line
		self.debug = 'debug' in sys.argv[1:]
		self.random = 'random' in sys.argv[1:]
		self.spin = 'spin' in sys.argv[1:]
		self.hover = 'nohover' not in sys.argv[1:] # defaults to true
		parent.title('Tetris')
		self.parent = parent
		self.audio = audio
		if self.audio: # if pygame import succeeded
			pg.mixer.init(buffer=512)
			try: # try importing the sound files from the current directory
				self.sounds = {name:pg.mixer.Sound(name)
									for name in ('music.ogg',
													'settle.ogg',
													'clear.ogg',
													'lose.ogg',
													'levelup.ogg')}
			except pg.error as e: # if sound files are missing, disable audio
				self.audio = None
				print(e)
			else:
				self.audio = {'m':True, 'x':True} # if sound files are present,
				for char in 'mMxX': # enable audio and bind keys
					self.parent.bind(char, self.toggle_audio)
		self.board_width = 10 # Initialize board width and height in number of squares
		self.board_height = 24 
		self.canvas_width = 300 # Initialize canvas width and height in number of pixels
		self.canvas_height = 720
		self.square_width = self.canvas_width//10
		self.high_score = 0
		self.high_level = 0
		# Defining the 7 shapes as 2D arrays. Empty strings mean open spaces, non-empty strings
		# are where the squares of the shape are
		self.shapes = {'S':[['*', ''],
									['*', '*'],
									['', '*']],
							'Z':[['', '*'],
									['*', '*'],
									['*', '']],
							'J':[['', '*'],
									['', '*'],
									['*', '*']],
							'L':[['*', ''],
									['*', ''],
									['*', '*']],
							'O':[['*', '*'],
									['*', '*']],
							'I':[['*'],
									['*'],
									['*'],
									['*']],
							'T':[['*', '*', '*'] ,
									['', '*', '']]}
		# Assigning colors to the shapes	
		self.colors = {'S':'green',
							'Z':'yellow',
							'J':'turquoise',
							'L':'orange',
							'O':'blue',
							'I':'red',
							'T':'violet'}
		# Binding a set of keys that the user may like the use
		for key in ('<Down>', '<Left>', '<Right>'):
			self.parent.bind(key, self.shift)
		for key in ('<Up>', 'w', 'W', 'q', 'Q', 'e', 'E'):
			self.parent.bind(key, self.rotate)
		for key in ('<space>', 's', 'S', 'a', 'A', 'd', 'D'):
			self.parent.bind(key, self.snap)
		self.parent.bind('<Escape>', self.pause)
		self.parent.bind('<Control-n>', self.draw_board)
		self.parent.bind('<Control-N>', self.draw_board)
		self.parent.bind('g', self.toggle_guides)
		self.parent.bind('G', self.toggle_guides)
		# Set some variables to None initially, will be assigned immediately on game start
		# When a game is lost, these variables will be destroyed or reset to None
		self.canvas = None
		self.preview_canvas = None
		self.ticking = None
		self.spawning = None		
		# Using stringvar to automatically update the corresponding labels
		self.score_var = tk.StringVar()
		self.high_score_var = tk.StringVar()
		self.level_var = tk.StringVar()
		self.high_level_var = tk.StringVar()
		# High score and highest level are 0 initially and will not be reset when starting a new game
		self.high_score_var.set('High Score:\n0')
		self.high_level_var.set('Highest level:\n0')
		# Creating and gridding labels
		self.preview_label = tk.Label(root,
											text='Next piece:',
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.preview_label.grid(row=0, column=1, sticky='S')
		self.score_label = tk.Label(root,
											textvariable=self.score_var,
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.score_label.grid(row=2, column=1)
		self.high_score_label = tk.Label(root,
											textvariable=self.high_score_var,
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.high_score_label.grid(row=3, column=1)
		self.level_label = tk.Label(root,
											textvariable=self.level_var,
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.level_label.grid(row=4, column=1)
		self.high_level_label = tk.Label(root,
											textvariable=self.high_level_var,
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.high_level_label.grid(row=5, column=1)
		self.help_button = tk.Button(parent, text='Help', command=lambda: self.pause(help=True))
		self.help_button.grid(row=6, column=1)
		# Start the game by calling the draw_board() function
		self.draw_board()

	def draw_board(self, event=None):
		'''
		Draws the board and canvas and starts the game
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		# after_cancel any tick() and spawn() calls from a previous game
		if self.ticking:
			self.parent.after_cancel(self.ticking)
		if self.spawning:
			self.parent.after_cancel(self.spawning)
		# Set the score to 0
		self.score_var.set('Score:\n0')
		self.level_var.set('Level:\n0')
		# Make an empty board for the 2D array representations of the shapes
		# TODO comment field
		self.board = [['' for column in range(self.board_width)]
							for row in range(self.board_height)]
		self.field = [[None for column in range(self.board_width)]
							for row in range(self.board_height)]
		# Destroy any canvas from a previous game and make a new one
		if self.canvas:
			self.canvas.destroy()	
		self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
		self.canvas.grid(row=0, column=0, rowspan=7) # rowspan == the number of labels+preview piece
		self.horizontal_seperator = self.canvas.create_line(0,self.canvas_height//6,
													self.canvas_width, self.canvas_height//6, width=2)
		self.vertical_seperator = self.canvas.create_line(self.canvas_width, 0,
													self.canvas_width, self.canvas_height, width=2)
		# Destroy any preview_canvas from a previous game, make a new one and grid it
		if self.preview_canvas:
			self.preview_canvas.destroy()	
		self.preview_canvas = tk.Canvas(root,
												width=5*self.square_width,
												height=5*self.square_width)
		self.preview_canvas.grid(row=1, column=1)
		# Set variables to their default values
		self.score = 0
		self.tickrate = 1000
		self.cleared_lines = 0
		self.level = 0
		self.levelup = 0
		self.max_level = 20
		# Determine how much the game speeds up per level, currently linear progression
		self.level_increment = self.tickrate//self.max_level
		self.piece_is_active = False
		self.paused = False
		self.bag = [] # Used to randomly pick a piece from a bag without replacement
		self.preview()
		# Initially grid the guidelines at the side of the board,
		# they will move with the active piece once it has spawned
		self.guides = [self.canvas.create_line(0, 0, 0, self.canvas_height),
							self.canvas.create_line(self.canvas_width,
															0,
															self.canvas_width,
															self.canvas_height)]
		self.guide_fill = 'black'
		self.toggle_guides() # Start with guidelines off
		self.pausewindow = None
		self.spawning = self.parent.after(self.tickrate, self.spawn) # spawn a piece
		self.ticking = self.parent.after(self.tickrate*2, self.tick) # start ticking
		if self.audio and self.audio['m']: # start the audio on an endless loop
			self.sounds['music.ogg'].stop() # stop any music from a previous game
			self.sounds['music.ogg'].play(loops=-1)

	def toggle_guides(self, event=None):
		'''
		Toggle the guidelines on/off
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		self.guide_fill = '' if self.guide_fill else 'black'
		self.canvas.itemconfig(self.guides[0], fill=self.guide_fill)
		self.canvas.itemconfig(self.guides[1], fill=self.guide_fill)

	def toggle_audio(self, event=None):
		'''
		Toggle the music or sound effects on/off
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		# if this function is called without a keypress, we do not know which sounds to toggle
		if not event:
			print('Error: toggle_audio called without keypress event')
			return
		key = event.keysym.lower()
		self.audio[key] = not self.audio[key] # invert value for index key
		if key == 'm':
			if not self.audio[key]: # stop the endless loop
				self.sounds['music.ogg'].stop()
			else: # restart the endless loop
				self.sounds['music.ogg'].play(loops=-1)

	def pause(self, event=None, help=False):
		'''
		Pauses the game
		Parameter:
			event (event): a keypress event, defaulting to None
			help (bool): variable to determine whether to show the pause or help text, defaulting to None
		'''
		if self.piece_is_active and not self.paused:
			self.paused = True # pause the game
			self.piece_is_active = False
			self.sounds['music.ogg'].fadeout(500)
			self.parent.after_cancel(self.ticking) # cancel any tick() calls
			# Show a popup saying the game is paused. Resume the game when popup is closed
			# if the user clicks OK or the red X on the top right of the window
			if help:
				self.pausewindow = Toplevel(width=200)
				self.pausewindow.protocol('WM_DELETE_WINDOW', self.pause)
				title = 'Help'
				message_content = 'Welcome to Tetris! The goal of the game is to get the highest possible score'\
						'before the board fills up. Fill a row to clear it, but be careful not to leave any gaps!'\
						'The pieces fall faster and faster as you progress though the levels.\n\n'\
						'Controls:\nUse the arrow keys to move the piece around the board.\n'\
						'Press Q to rotate anti-clockwise, and E to rotate clock-wise.\n'\
						'Press A or D to move the piece as far left or right as possible.\n'\
						'Press S or Space to instantly move the piece to the bottom.\n'\
						'Press G to toggle guidelines.\n'\
						'Press M to toggle music, and X to toggle sound effects\n'\
						'Press the Escape button to pause the game.\n'\
						'If you want to start over, press Ctrl + N for a new game.\n\n'\
						'Good luck!'
				message = tk.Message(self.pausewindow, text=message_content)
				message.pack()
				button = tk.Button(self.pausewindow, text='Ok', command=self.pause)
				button.pack()
			else:
				if messagebox.askquestion(title='Game paused', message='The game has been paused,\n'+
														'close this window to continue.', type='ok', icon='info'):
					self.pause()
		elif self.paused: # resume the game
			if self.pausewindow:
				self.pausewindow.destroy()
			self.paused = False
			self.piece_is_active = True
			self.sounds['music.ogg'].play(loops=-1)
			self.ticking = self.parent.after(self.tickrate, self.tick)

	def print_board(self):
		'''
		Prints the board to the console for debugging purposes
		'''
		for row in self.board:
			print(*(cell or ' ' for cell in row), sep='')

	def check(self, shape, row, column, length, width):
		'''
		Check wheter we may rotate or move a piece or if the space is already occupied
		or the intented space is off the board. Return True if the move is allowed
		Parameters:
			shape (2D list): the 2D array representation of the current piece
			row (int): the row of the shape
			column (int): the column of the shape
			length (int): the (vertical) length of the shape
			width (int): the (horizontal) width of the shape
		'''
		# zip returns tuples of (rowindex, row of shape)
		for row_number, squares in zip(range(row, row+length), shape):
			# zip returns tuples of (columnindex, square of shape)
			for column_number, square in zip(range(column, column+width), squares):
				if (row_number not in range(self.board_height) # if row_number is negative or too large
					or column_number not in range(self.board_width) # or the same with column_number
					or (square and self.board[row_number][column_number] == 'x')): # or the intended
																				# space is occupied by a settled piece
						return
		return True

	def move(self, shape, row, column, length, width):
		'''
		Move the piece to a given position
		Parameters:
			shape (2D list): the 2D array representation of the current piece
			row (int): the row the piece should move to
			column (int): the column the piece should move to
			length (int): the (vertical) length of the piece
			width (int): the (horizontal) width of the piece
		'''
		square_idxs = iter(range(4)) # iterator of 4 indices
		# r = .. would reassign a local variable
		# r[:] = .. takes all elements of the object		
		# Removing the shape from the board by iterating over the rows
		# and blanking the cell if it was previously occupied by the shape,
		# otherwise (e.g. settled piece) it remains as it was
		for r in self.board:
			r[:] = ['' if cell=='*' else cell for cell in r]

		# Put shape on the board and piece on the canvas
		# zip returns tuples of (rowindex, row of shape)
		for row_number, squares in zip(range(row, row+length), shape):
			# zip returns tuples of (columnindex, square of shape)
			for column_number, square in zip(range(column, column+width), squares):
				if square:
					self.board[row_number][column_number] = square # put the square on the board
					square_idx = next(square_idxs)
					coords = (column_number * self.square_width,
										row_number * self.square_width,
										(column_number+1)*self.square_width,
										(row_number+1)*self.square_width)
					self.active_piece.coords[square_idx] = coords
					self.canvas.coords(self.active_piece.piece[square_idx], coords)
		# Update the properties of active_piece
		self.active_piece.row = row
		self.active_piece.column = column
		self.active_piece.shape = shape
		self.move_guides(column, column+width) # move the guidelines

		if self.debug: # Print the board if the debug flag has been set
			self.print_board()
		return True

	def check_and_move(self, shape, row, column, length, width):
		# If self.check is false, the function will return false without
		# checking (and executing) self.move
		return self.check(shape, row, column, length, width
			) and self.move(shape, row, column, length, width)

	def rotate(self, event=None):
		'''
		Rotates the active piece 90 degrees, direction depends on the event
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		# Don't rotate inactive pieces
		if not self.piece_is_active:
			return
		# Don't rotate squares
		if len(self.active_piece.shape) == len(self.active_piece.shape[0]):
			# Notify the piece that it has 'rotated', used for easyspin delay mechanic
			self.active_piece.rotation_index = self.active_piece.rotation_index
			return
		# Retrieve information about the active piece
		row = self.active_piece.row
		column = self.active_piece.column
		length = len(self.active_piece.shape)
		width = len(self.active_piece.shape[0])
		# find the coordinates of the center of the old shape
		x_center = column + width//2
		y_center = row + length//2
		
		direction = event.keysym
		if direction in {'q', 'Q'}:
			# rotate left/anticlockwise
			shape = rot_arr(self.active_piece.shape, -90)
			# 4 is a magic number, number of sides on a rectangle
			rotation_index = (self.active_piece.rotation_index - 1) % 4
			rx, ry = self.active_piece.rotation[rotation_index]
			rotation_offsets = -rx, -ry
		elif direction in {'e', 'E', 'Up', 'w', 'W'}:
			# rotate right/clockwise
			shape = rot_arr(self.active_piece.shape, 90)
			rotation_index = self.active_piece.rotation_index
			rotation_offsets = self.active_piece.rotation[rotation_index]
			# 4 is a magic number, number of sides on a rectangle
			rotation_index = (rotation_index + 1) % 4

		length = len(shape) # length of new shape
		width = len(shape[0]) # width of new shapes
		row = y_center - length//2 # row of new shape
		column = x_center - width//2 # column of new shape
		# correct x,y values to make the rotation feel more natural
		x_correction, y_correction = rotation_offsets
		row += y_correction
		column += x_correction

		# call check_and_move to see if the rotation is allowed, and execute it if it is
		if self.check_and_move(shape, row, column, length, width):
			# Update rotation index for next x,y correction
			self.active_piece.rotation_index = rotation_index
			return
		
		# If default check_and_move failed, try kicking the piece
		for y,x in zip(( 0, 0,-1, 0, 0,-2, -1,-1),
							(-1, 1, 0,-2, 2, 0, -1, 1)):
			if self.check_and_move(shape, row+y, column+x, length, width):
				self.active_piece.rotation_index = rotation_index
				return

	def tick(self):
		'''
		Shifts the active piece down one row and calls itself after self.tickrate
		'''
		# If the piece is active and NOT(the spin feature is active and the piece is currently spinning)
		if self.piece_is_active and not (self.spin and self.active_piece.spin):
			self.shift()
		self.ticking = self.parent.after(self.tickrate, self.tick)
	
	def shift(self, event=None):
		'''
		Shift the active piece down, left or right depending on the event
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		if not self.piece_is_active:		# We do not want to move settled pieces
			return
		# Retrieve information about the active piece
		row = self.active_piece.row
		column = self.active_piece.column
		length = len(self.active_piece.shape)
		width = len(self.active_piece.shape[0])
		# The function may be called by tick with no event, in which case
		# the piece will move down, or it may be called by a button press event
		# in which case direction is will be the name of the button
		direction = (event and event.keysym) or 'Down'
		if direction == 'Down':	
			row += 1
		elif direction == 'Left':
			column -= 1
		elif direction == 'Right':
			column += 1

		success = self.check_and_move(self.active_piece.shape, row, column, length, width)


		# If we're moving down and the piece is blocked by something on the row below
		# and NOT(the feature is on and we're hovering), then settle
		if direction == 'Down' and not success and not (self.hover and self.active_piece.hover): 
			self.settle()

	def settle(self):
		'''
		Settles the current active_piece and spawns a new one after self.tickrate
		'''
		self.piece_is_active = False
		# Changing the notation of the previously active piece to
		# denote that it has now settled
		for row in self.board:
			row[:] = ['x' if cell=='*' else cell for cell in row]
		# Putting square id for each piece in the field
		for (x1,y1,x2,y2),piece in zip(self.active_piece.coords, self.active_piece.piece):
			self.field[y1//self.square_width][x1//self.square_width] = piece
		# line_numbers is a list of indices of any full rows
		line_numbers = [idx for idx, row in enumerate(self.board) if all(row)]
		if line_numbers: # if any lines are full
			self.cleared_lines += len(line_numbers)
			self.levelup += len(line_numbers)
			if self.levelup >= 10:
				if self.audio['x']:
					self.sounds['levelup.ogg'].play()
				self.level = self.cleared_lines//10 # level up for every 10 lines cleared
				self.high_level = max(self.level, self.high_level)
				self.levelup -= 10
				self.tickrate = 1000 - self.level_increment * self.level # increase the tickrate
				self.level_var.set('Level:\n{}'.format(self.level))
				self.high_level_var.set('Highest level:\n{}'.format(self.high_level))
			elif self.audio and self.audio['x']: # if we haven't leveled up, play clear sound instead
				self.sounds['clear.ogg'].play() 
			self.clear(line_numbers) # clear the lines
			# Update the score, +1 because we start at level 0
			self.score += (40,100,300,1200)[len(line_numbers)-1]*(self.level+1)
			if all(not cell for row in self.board for cell in row): # If the board is empty now,
				self.score += 1200*(self.level+1) # give a bonus score for clearing the board
			self.high_score = max(self.score, self.high_score)		
			self.score_var.set('Score:\n{}'.format(self.score))
			self.high_score_var.set('High Score:\n{}'.format(self.high_score))
		# Lose if there is any square in the top 4 rows when this function is called 
		if any(any(row) for row in self.board[:4]):
			self.lose()
			return
		if self.audio and self.audio['x'] and not line_numbers: # if audio is on and we didn't clear lines
			self.sounds['settle.ogg'].play() # or lose the game, play the settle sound
		# Spawn in a new piece after self.tickrate, or if a line has been cleared and the tickrate
		# is shorter than the line-clearing animation, wait for the animation to finish
		# 500 is a magic number, board_width times the animation delay in clear_iter()
		self.spawning = self.parent.after(500 if line_numbers and self.tickrate<500
											else self.tickrate, self.spawn)
	
	def preview(self):
		'''
		Shows a preview of the next piece that will be spawned
		'''
		self.preview_canvas.delete(tk.ALL) # Delete the previous preview
		if not self.bag: # if the bag is empty or there is no bag
			if self.random: # If the random flag has been set, randomly pick a piece
				self.bag.append(random.choice('SZJLOIT')) # WITHOUT replacement
			else:
				self.bag = random.sample('SZJLOIT', 7) # Put the names of the 7 pieces in random order
		key = self.bag.pop() # Randomly pick a piece from a bag WITH replacement
		shape = rot_arr(self.shapes[key], random.choice((0,90,180,270))) # randomly rotate the shape
		self.preview_piece = Shape(key, shape, [], 0, 0, [])

		# enumerate returns tuples of (y_coordinate, row of shape)
		for y, row in enumerate(shape):
			# enumerate returns tuples of (x_coordinate, cell in row of shape)
			for x, cell in enumerate(row):
				if cell:
					self.preview_piece.coords.append((self.square_width*x+self.square_width//2,
																self.square_width*y+self.square_width//2,
																self.square_width*(x+1)+self.square_width//2,
																self.square_width*(y+1)+self.square_width//2))
					self.preview_piece.piece.append(
						self.preview_canvas.create_rectangle(self.preview_piece.coords[-1],
																fill=self.colors[key],
																width=3)
															)

		self.preview_piece.rotation_index = 0
		# cycle of coordinates to move the piece slightly each time it rotates
		# to make the rotation feel more natural
		if 3 in (len(shape), len(shape[0])): # 2x3 or 3x2 shape
			self.preview_piece.rotation = [(0,0),
													(1, 0),
													(-1, 1),
													(0, -1)]
		else: # I shape
			self.preview_piece.rotation = [(1,-1),
													(0, 1),
													(0,0),
													(-1, 0)]	
		if len(shape) < len(shape[0]):
			self.preview_piece.rotation_index += 1
			if len(shape[0]) == 4: # increased row for horizontal I piece
				self.preview_piece.row = 1

	def move_guides(self, left, right):
		'''
		Move the guidelines to the left- and rightmost column of the piece
		Parameters:
			left (int): the index of the leftmost column of the piece
			right (int): the index of the rightmost column of the piece
		'''
		left *= self.square_width
		right *= self.square_width
		self.canvas.coords(self.guides[0], left, 0, left, self.canvas_height)
		self.canvas.coords(self.guides[1], right, 0, right, self.canvas_height)

	def spawn(self):
		'''
		Spawn the preview piece in the board and create a new preview piece
		'''
		self.piece_is_active = True
		self.active_piece = self.preview_piece
		width = len(self.active_piece.shape[0]) # width of the shape
		start_column = (10-width)//2 # start the shape in the middle of the board
		self.active_piece.coords = []
		self.active_piece.piece = []
		self.active_piece.row = self.preview_piece.row
		self.active_piece.column = start_column
		self.preview()
		# enumerate returns tuples of (y_coordinate, row of shape)
		for y, row in enumerate(self.active_piece.shape):
			# Spawn in the shape
			self.board[y][start_column:start_column+width] = self.active_piece.shape[y]
			# enumerate returns tuples of (x_coordinate, cell in row of shape)
			for x, cell in enumerate(row, start=start_column):
				if cell:
					self.active_piece.coords.append((self.square_width*x,
																self.square_width*(y+self.active_piece.row),
																self.square_width*(x+1),
																self.square_width*(y+self.active_piece.row+1)))
					self.active_piece.piece.append(
						self.canvas.create_rectangle(self.active_piece.coords[-1],
																fill=self.colors[self.active_piece.key],
																width=3))
		self.move_guides(start_column, start_column+width) # update the guidelines
		if self.debug: # print the board to the console if the debug flag was set
			self.print_board()

	def lose(self):
		'''
		Ends the current game and clears the board
		'''
		self.piece_is_active = False
		if self.audio and self.audio['x']:
			self.sounds['lose.ogg'].play()
		if self.audio and self.audio['m']:
			self.sounds['music.ogg'].stop() # stop the musics endless loop
		self.parent.after_cancel(self.ticking) # cancel any tick() calls
		self.parent.after_cancel(self.spawning) # cancel any spawn() calls
		self.clear_iter(range(len(self.board))) # clear the entire board

	def snap(self, event=None):
		'''
		Move the piece as far down, left or right as possible
		Parameter:
			event (event): a keypress event, defaulting to None
		'''
		down = {'space', 's', 'S'}
		left = {'a', 'A'}
		right = {'d', 'D'}
		if not self.piece_is_active: # We do not want to move settled pieces
			return
		# Retrieve information about the active piece
		row = self.active_piece.row
		column = self.active_piece.column
		length = len(self.active_piece.shape)
		width = len(self.active_piece.shape[0])

		direction = event.keysym
		while True:
			# Keep checking for possible moves in the given direction until the 
			# piece hits a wall or a settled piece, break the loop when that happens
			if self.check(self.active_piece.shape,
									row+(direction in down),
									column+(direction in right) - (direction in left),
									length, width):
				row += direction in down
				column += (direction in right) - (direction in left)
			else:
				break
		# Move to the last checked position
		self.move(self.active_piece.shape, row, column, length, width)
		if direction in down: # Settle the piece if the user snapped down
			self.settle()

	def clear(self, line_numbers):
		'''
		Clear the given line
		Parameter:
			line_numbers (list): a list of int indices of full rows
		'''
		for idx in line_numbers:\
			# Remove the full row from the board and create an empty one on top
			self.board.pop(idx)
			self.board.insert(0, ['' for column in range(self.board_width)])
		self.clear_iter(line_numbers)

	def clear_iter(self, line_numbers, current_column=0):
		'''
		Provides an animation to clear full lines
		Parameters:
			line_numbers: indices of the lines to clear
			current_column: current column of the current line to clear
		'''
		for row in line_numbers:
			if row%2:
				cc = current_column
			else: # Reverse animation in even rows
				cc = self.board_width - current_column - 1
			square = self.field[row][cc]
			self.field[row][cc] = None
			self.canvas.delete(square)
		if current_column < self.board_width-1:
			# withouth lambda the function would be called immediately, because the
			# after() function needs to evaluate what it will call after the given amount of time
			self.parent.after(50, lambda: self.clear_iter(line_numbers, current_column+1))
		else:
			for idx, row in enumerate(self.field):
				offset = sum(row_number > idx for row_number in line_numbers)*self.square_width
				for square in row:
					if square:
						self.canvas.move(square, 0, offset)
			for row in line_numbers:
				self.field.pop(row)
				self.field.insert(0, [None for column in range(self.board_width)])

root = tk.Tk()
tetris = Tetris(root, audio)
root.mainloop()
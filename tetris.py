# -------------------------------
# Name: Idle clicker
# Author: Jasper Keijzer
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

class Shape():
	def __init__(self, key, shape, piece, row, column, coords):
		'''
		Shape is a 2D array presentation with '*'
		piece is a 2D array with references to canvas child objects
		'''
		self.key = key
		self.shape = shape
		self.piece = piece
		self.row = row
		self.column = column
		self.coords = coords

class Tetris():
	def __init__(self, parent):
		self.debug = 'debug' in sys.argv[1:]
		self.random = 'random' in sys.argv[1:]
		parent.title('Tetris')
		self.parent = parent
		if audio: # if pygame import succeeded
			pg.mixer.init(buffer=512)
			try:
				self.sounds = {name:pg.mixer.Sound(name)
									for name in ('music.ogg',
													'settle.ogg',
													'clear.ogg',
													'lose.ogg',
													'levelup.ogg')}
			except pg.error as e:
				self.audio = None
				print(e)
			else:
				self.audio = {'m':True, 'x':True}
				for char in 'mMxX':
					self.parent.bind(char, self.toggle_audio)
		
		
		self.board_width = 10
		self.board_height = 24
		self.canvas_width = 300
		self.canvas_height = 720
		self.square_width = self.canvas_width//10
		self.high_score = 0

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
		self.colors = {'S':'green',
							'Z':'yellow',
							'J':'turquoise',
							'L':'orange',
							'O':'blue',
							'I':'red',
							'T':'violet'}
		for key in ('<Down>', 's', 'S', '<Left>', 'a', 'A', '<Right>', 'd', 'D'):
			self.parent.bind(key, self.shift)
		for key in ('<Up>', 'w', 'W', 'q', 'Q', 'e', 'E'):
			self.parent.bind(key, self.rotate)
		for key in ('<space>', 'f', 'F', '<Caps_Lock>'):
			self.parent.bind(key, self.snap)
		self.parent.bind('<Escape>', self.pause)
		self.parent.bind('<Control-n>', self.draw_board)
		self.parent.bind('<Control-N>', self.draw_board)
		self.parent.bind('g', self.toggle_guides)
		self.parent.bind('G', self.toggle_guides)

		self.canvas = None
		self.preview_canvas = None
		self.ticking = None
		self.spawning = None
		self.guide_fill = 'black'
		self.score_var = tk.StringVar()
		self.high_score_var = tk.StringVar()
		self.level_var = tk.StringVar()
		self.max_level_var = tk.StringVar()
		self.high_score_var.set('High Score:\n0')
		self.max_level_var.set('Max level:\n0')
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
		self.level_label.grid(row=5, column=1)
		self.max_level_label = tk.Label(root,
											textvariable=self.max_level_var,
											width=15,
											height=3,
											font=('Arial', 13, 'bold'))
		self.max_level_label.grid(row=6, column=1)	
		self.draw_board()

	def draw_board(self, event=None):
		if self.ticking:
			self.parent.after_cancel(self.ticking)
		if self.spawning:
			self.parent.after_cancel(self.spawning)
		self.score_var.set('Score:\n0')
		self.level_var.set('Level:\n0')
		self.board = [['' for column in range(self.board_width)]
							for row in range(self.board_height)]
		self.field = [[None for column in range(self.board_width)]
							for row in range(self.board_height)]
		if self.canvas:
			self.canvas.destroy()	
		self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
		self.canvas.grid(row=0, column=0, rowspan=7)
		self.horizontal_seperator = self.canvas.create_line(0,self.canvas_height//6,
													self.canvas_width, self.canvas_height//6, width=2)
		self.vertical_seperator = self.canvas.create_line(self.canvas_width, 0,
													self.canvas_width, self.canvas_height, width=2)
		if self.preview_canvas:
			self.preview_canvas.destroy()	
		self.preview_canvas = tk.Canvas(root,
												width=5*self.square_width,
												height=5*self.square_width)
		self.preview_canvas.grid(row=1, column=1)
		self.score = 0
		self.tickrate = 1000
		self.cleared_lines = 0
		self.level = 0
		self.levelup = 0
		self.max_level = 20
		self.level_increment = self.tickrate//self.max_level
		self.piece_is_active = False
		self.paused = False
		self.bag = []
		self.preview()
		self.guides = [self.canvas.create_line(0, 0, 0, self.canvas_height),
							self.canvas.create_line(self.canvas_width,
															0,
															self.canvas_width,
															self.canvas_height)]
		self.toggle_guides() # Start with guidelines off
		self.spawning = self.parent.after(self.tickrate, self.spawn)
		self.ticking = self.parent.after(self.tickrate*2, self.tick)
		if self.audio and self.audio['m']:
			self.sounds['music.ogg'].play(loops=-1)

	def toggle_guides(self, event=None):
		self.guide_fill = '' if self.guide_fill else 'black'
		self.canvas.itemconfig(self.guides[0], fill=self.guide_fill)
		self.canvas.itemconfig(self.guides[1], fill=self.guide_fill)

	def toggle_audio(self, event=None):
		if not event:
			return
		key = event.keysym.lower()
		self.audio[key] = not self.audio[key]
		if key == 'm':
			if not self.audio[key]:
				self.sounds['music.ogg'].stop()
			else:
				self.sounds['music.ogg'].play(loops=-1)

	def pause(self, event=None):
		if self.piece_is_active and not self.paused:
			self.paused = True
			self.piece_is_active = False
			self.parent.after_cancel(self.ticking)
			if messagebox.askquestion(title='Game paused', message='The game has been paused,\n'+
														'close this window to continue.', type='ok', icon='info'):
				self.pause()
		elif self.paused:
			self.paused = False
			self.piece_is_active = True
			self.ticking = self.parent.after(self.tickrate, self.tick)

	# Used for printing the board in debug mode
	def print_board(self):
		for row in self.board:
			print(*(cell or ' ' for cell in row), sep='')

	def check(self, shape, row, column, length, width):
		# Check wheter we may rotate or move a piece or if the space is already occupied
		# or the intented space is off the board
		for row_number, squares in zip(range(row, row+length), shape):
			for column_number, square in zip(range(column, column+width), squares):
				if (row_number not in range(self.board_height)
					or column_number not in range(self.board_width)
					or (square and self.board[row_number][column_number] == 'x')):
						return
		return True

	def move(self, shape, row, column, length, width):
		square_idxs = iter(range(4)) # iterator of 4 indices

		# r = .. would reassign a local variable
		# r[:] = .. takes all elements of the object		
		# Removing the shape from the board by iterating over the rows
		# and blanking the cell if it was previously occupied by the shape,
		# otherwise (e.g. settled piece) it remains as it was
		for r in self.board:
			r[:] = ['' if cell=='*' else cell for cell in r]

		# Put shape on the board and piece on the canvas
		for row_number, squares in zip(range(row, row+length), shape):
			for column_number, square in zip(range(column, column+width), squares):
				if square:
					self.board[row_number][column_number] = square
					square_idx = next(square_idxs)
					coords = (column_number * self.square_width,
										row_number * self.square_width,
										(column_number+1)*self.square_width,
										(row_number+1)*self.square_width)
					self.active_piece.coords[square_idx] = coords
					self.canvas.coords(self.active_piece.piece[square_idx], coords)
		self.active_piece.row = row
		self.active_piece.column = column
		self.active_piece.shape = shape

		self.move_guides(column, column+width)
		if self.debug:
			self.print_board()
		return True

	def check_and_move(self, shape, row, column, length, width):
		# If self.check is false, the function will return false without
		# checking (and executing) self.move
		return self.check(shape, row, column, length, width
			) and self.move(shape, row, column, length, width)

	def rotate(self, event=None):
		# Don't rotate inactive pieces
		if not self.piece_is_active:
			return
		# Don't rotate squares
		if len(self.active_piece.shape) == len(self.active_piece.shape[0]):
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
			rotation_index = (rotation_index + 1) % 4

		length = len(shape) # length of new shape
		width = len(shape[0]) # width of new shapes
		row = y_center - length//2 # row of new shape
		column = x_center - width//2 # column of new shape
		x_correction, y_correction = rotation_offsets
		row += y_correction
		column += x_correction

		if not self.check_and_move(shape, row, column, length, width):
			return

		self.active_piece.rotation_index = rotation_index

	def tick(self):
		self.shift()
		self.ticking = self.parent.after(self.tickrate, self.tick)
	
	def shift(self, event=None):
		down = {'Down', 's', 'S'}
		left = {'Left', 'a', 'A'}
		right = {'Right', 'd', 'D'}
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
		if direction in down:	
			row += 1
		elif direction in left:
			column -= 1
		elif direction in right:
			column += 1

		success = self.check_and_move(self.active_piece.shape, row, column, length, width)

		if direction in down and not success:
			self.settle()

	def settle(self):
		self.piece_is_active = False
		# Changing the notation of the previously active piece to
		# denote that it has now settled
		for row in self.board:
			row[:] = ['x' if cell=='*' else cell for cell in row]
		# Putting square id for each piece in the field
		for (x1,y1,x2,y2),piece in zip(self.active_piece.coords, self.active_piece.piece):
			self.field[y1//self.square_width][x1//self.square_width] = piece
		# See if we need to clear any full lines and add the score
		line_numbers = [idx for idx, row in enumerate(self.board) if all(row)]
		if line_numbers:
			self.score += (40,100,300,1200)[len(line_numbers)-1]*(self.level+1)
			self.clear(line_numbers)
			if all(not cell for row in self.board for cell in row): # Bonus score for clearing the board
				self.score += 1200*(self.level+1)
			self.high_score = max(self.score, self.high_score)
			self.cleared_lines += len(line_numbers)
			self.levelup += len(line_numbers)
			if self.levelup >= 10:
				if self.audio['x']:
					self.sounds['levelup.ogg'].play()
				self.level = self.cleared_lines//10
				self.max_level = max(self.level, self.max_level)
				self.levelup -= 10
				self.tickrate = 1000 - self.level_increment * self.level
				self.level_var.set('Level:\n{}'.format(self.level))
				self.max_level_var.set('Max level:\n{}'.format(self.max_level))
			self.score_var.set('Score:\n{}'.format(self.score))
			self.high_score_var.set('High Score:\n{}'.format(self.high_score))
		# Lose if there is any square in the top 4 rows when this function is called 
		if any(any(row) for row in self.board[:4]):
			self.lose()
			return
		if self.audio and self.audio['x'] and not line_numbers: # if audio is on and we didn't clear lines
			self.sounds['settle.ogg'].play() # or lose the game, play the settle sound
		self.spawning = self.parent.after(self.tickrate, self.spawn)

	
	def preview(self):
		self.preview_canvas.delete(tk.ALL)
		# Select a shape and randomly rotate it
		if not self.bag:
			if self.random:
				self.bag.append(random.choice('SZJLOIT'))
			else:
				self.bag = random.sample('SZJLOIT', 7)
		key = self.bag.pop()
		shape = rot_arr(self.shapes[key], random.choice((0,90,180,270)))
		self.preview_piece = Shape(key, shape, [], 0, 0, [])

		for y, row in enumerate(shape):
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
			if len(shape[0]) == 4:
				self.preview_piece.row = 1



	def move_guides(self, left, right):
		left *= self.square_width
		right *= self.square_width
		self.canvas.coords(self.guides[0], left, 0, left, self.canvas_height)
		self.canvas.coords(self.guides[1], right, 0, right, self.canvas_height)

	def spawn(self):
		self.piece_is_active = True
		self.active_piece = self.preview_piece


		width = len(self.active_piece.shape[0])
		start_column = (10-width)//2

		self.active_piece.coords = []
		self.active_piece.piece = []
		self.active_piece.row = self.preview_piece.row
		self.active_piece.column = start_column

		self.preview()

		for y, row in enumerate(self.active_piece.shape):
			# Spawn in the shape
			self.board[y][start_column:start_column+width] = self.active_piece.shape[y]
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

		self.move_guides(start_column, start_column+width)

		if self.debug:
			self.print_board()

	def lose(self):
		self.piece_is_active = False
		if self.audio and self.audio['x']:
			self.sounds['lose.ogg'].play()
		if self.audio and self.audio['m']:
			self.sounds['music.ogg'].stop()
		self.parent.after_cancel(self.ticking)
		self.parent.after_cancel(self.spawning)
		self.clear_iter(range(len(self.board)))


	def snap(self, event=None):
		down = {'space'}
		left = {'Caps_Lock'}
		right = {'f', 'F'}
		if not self.piece_is_active:		# We do not want to move settled pieces
			return
		# Retrieve information about the active piece
		row = self.active_piece.row
		column = self.active_piece.column
		length = len(self.active_piece.shape)
		width = len(self.active_piece.shape[0])

		direction = event.keysym
		while True:
			if self.check(self.active_piece.shape,
									row+(direction in down),
									column+(direction in right) - (direction in left),
									length, width):
				row += direction in down
				column += (direction in right) - (direction in left)
			else:
				break
		
		self.move(self.active_piece.shape, row, column, length, width)
		if direction in down:
			self.settle()


	def clear(self, line_numbers):
		if self.audio and self.audio['x']:
			self.sounds['clear.ogg'].play()
		for idx in line_numbers:
			self.board.pop(idx)
			self.board.insert(0, ['' for column in range(self.board_width)])
		self.clear_iter(line_numbers)

	# Animation to clear the board
	def clear_iter(self, line_numbers, current_column=0):
		for row in line_numbers:
			if row%2:
				cc = current_column
			else: # Reverse animation in even rows
				cc = self.board_width - current_column - 1
			square = self.field[row][cc]
			self.field[row][cc] = None
			self.canvas.delete(square)
		if current_column < self.board_width-1:
			# withouth lambda the function would be called immediately, because 
			# after needs to evaluate what it will call after the given amount of time
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
tetris = Tetris(root)
root.mainloop()
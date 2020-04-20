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
except:
	print('The tkinter module cannot be found or is not installed')
try:
	from tkinter import messagebox
except:
	print('The tkinter/messagebox module cannot be found or is not installed')
try:
	import pygame as pg
except:
	print('The pygame module cannot be found or is not installed')
try:
	from matrix_rotation import rotate_array as rot_arr
except:
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
		parent.title('Tetris')
		self.parent = parent
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
		self.parent.bind('<Down>', self.shift)
		self.parent.bind('s', self.shift)
		self.parent.bind('S', self.shift)
		self.parent.bind('<Left>', self.shift)
		self.parent.bind('a', self.shift)
		self.parent.bind('A', self.shift)
		self.parent.bind('<Right>', self.shift)
		self.parent.bind('d', self.shift)
		self.parent.bind('D', self.shift)
		self.parent.bind('<Up>', self.rotate)
		self.parent.bind('w', self.rotate)
		self.parent.bind('W', self.rotate)
		self.parent.bind('q', self.rotate)
		self.parent.bind('Q', self.rotate)
		self.parent.bind('e', self.rotate)
		self.parent.bind('E', self.rotate)
		self.parent.bind('<space>', self.snap)
		self.parent.bind('f', self.snap)
		self.parent.bind('F', self.snap)
		self.parent.bind('<Caps_Lock>', self.snap)
		self.parent.bind('<Escape>', self.pause)
		self.parent.bind('<Control-n>', self.draw_board)
		self.parent.bind('<Control-N>', self.draw_board)

		self.canvas = None
		self.preview_canvas = None
		self.ticking = None
		self.spawning = None
		self.score_var = tk.StringVar()
		self.high_score_var = tk.StringVar()
		self.cleared_lines_var = tk.StringVar()
		self.level_var = tk.StringVar()
		self.high_score_var.set('High Score:\n0')
		self.preview_label = tk.Label(root,
											text='Next piece:',
											width=15,
											height=5,
											font=('Arial', 13, 'bold'))
		self.preview_label.grid(row=0, column=1, sticky='S')
		self.score_label = tk.Label(root,
											textvariable=self.score_var,
											width=15,
											height=5,
											font=('Arial', 13, 'bold'))
		self.score_label.grid(row=2, column=1, sticky='S')
		self.high_score_label = tk.Label(root,
											textvariable=self.high_score_var,
											width=15,
											height=5,
											font=('Arial', 13, 'bold'))
		self.high_score_label.grid(row=3, column=1, sticky='N')
		self.cleared_lines_label = tk.Label(root,
											textvariable=self.cleared_lines_var,
											width=15,
											height=5,
											font=('Arial', 13, 'bold'))
		self.cleared_lines_label.grid(row=4, column=1)
		self.level_label = tk.Label(root,
											textvariable=self.level_var,
											width=15,
											height=5,
											font=('Arial', 13, 'bold'))
		self.level_label.grid(row=5, column=1)
		self.draw_board()

	def draw_board(self, event=None):
		if self.ticking:
			self.parent.after_cancel(self.ticking)
		if self.spawning:
			self.parent.after_cancel(self.spawning)
		self.score_var.set('Score:\n0')
		self.cleared_lines_var.set('Cleared lines:\n0')
		self.level_var.set('Level:\n1')
		self.board = [['' for column in range(self.board_width)]
							for row in range(self.board_height)]
		self.field = [[None for column in range(self.board_width)]
							for row in range(self.board_height)]
		if self.canvas:
			self.canvas.destroy()	
		self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
		self.canvas.grid(row=0, column=0, rowspan=6)
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
		self.piece_is_active = False
		self.paused = False
		self.preview()
		self.spawning = self.parent.after(self.tickrate, self.spawn)
		self.ticking = self.parent.after(self.tickrate*2, self.tick)

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
		if self.debug:
			self.print_board()
		return True


	def check_and_move(self, shape, row, column, length, width):
		if self.check(shape, row, column, length, width):
			self.move(shape, row, column, length, width)
			return True



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

		success = self.check_and_move(shape, row, column, length, width)
		if not success:
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
			self.score += (40,100,300,1200)[len(line_numbers)-1]
			self.clear(line_numbers)
			if all(not cell for row in self.board for cell in row): # Bonus score for clearing the board
				self.score += 1200
			self.high_score = max(self.score, self.high_score)
			self.score_var.set('Score:\n{}'.format(self.score))
			self.high_score_var.set('High Score:\n{}'.format(self.high_score))
			self.cleared_lines += len(line_numbers)
			self.level = self.cleared_lines//2 + 1# should be 10, start at lvl 1
			if self.level < 50:
				self.tickrate = 1000 - 20 * self.level
			self.cleared_lines_var.set('Cleared lines:\n{}'.format(self.cleared_lines))
			self.level_var.set('Level:\n{}'.format(self.level))
		# Lose if there is any square in the top 4 rows when this function is called 
		if any(any(row) for row in self.board[:4]):
			self.lose()
			return
		self.spawning = self.parent.after(self.tickrate, self.spawn)

	
	def preview(self):
		self.preview_canvas.delete(tk.ALL)
		# Select a shape and randomly rotate it
		key = random.choice('SZJLOIT')
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
																width=3)
															)

		
		if self.debug:
			self.print_board()

	def lose(self):
		self.piece_is_active = False
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
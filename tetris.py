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
	import pygame as pg
except:
	print('The pygame module cannot be found or is not installed')
try:
	from matrix_rotation import rotate_array as rot_arr
except:
	print('The matrix_rotation module cannot be found or is not installed'\
		'The original code can be found on https://github.com/TigerhawkT3/matrix_rotation')
import random

class Shape():
	def __init__(self, shape, piece, row, column, coords):
		'''
		Shape is a 2D array presentation with '*'
		piece is a 2D array with references to canvas child objects
		'''
		self.shape = shape
		self.piece = piece
		self.row = row
		self.column = column
		self.coords = coords

class Tetris():
	def __init__(self, parent):
		parent.title('Tetris')
		self.parent = parent
		self.board_width = 10
		self.board_height = 24
		self.board = [['' for column in range(self.board_width)]
							for row in range(self.board_height)]
		self.canvas_width = 300
		self.canvas_height = 720
		self.square_width = self.canvas_width//10
		self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
		self.canvas.grid(row=0, column=0)
		self.seperator = self.canvas.create_line(0,self.canvas_height//6,
													self.canvas_width, self.canvas_height//6, width=2)
		self.tickrate = 1000
		self.piece_is_active = False
		self.parent.after(self.tickrate, self.tick)
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

	def print_board(self):
		for row in self.board:
			print(*(cell or ' ' for cell in row), sep='')


	def check_and_move(self, shape, row, column, length, width):
		# Check wheter we may rotate a piece or if the space is already occupied
		# or the intented space is off the board
		for row_number, squares in zip(range(row, row+length), shape):
			for column_number, square in zip(range(column, column+width), squares):
				if (row_number not in range(self.board_height)
					or column_number not in range(self.board_width)
					or (square and self.board[row_number][column_number] == 'x')):
						return


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
		self.print_board()
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
		if not self.piece_is_active:
			self.spawn()
		
		#self.parent.after(self.tickrate, self.tick)
	
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
		# If the piece is at the bottom of the board, settle
		if direction in down:	
			row_temp = row+1 # temp value
			column_temp = column # temp value
		elif direction in left:
			row_temp = row
			column_temp = column - 1
		elif direction in right:
			row_temp = row
			column_temp = column + 1

		success = self.check_and_move(self.active_piece.shape, row_temp, column_temp, length, width)

		if direction in down and not success:
			self.settle()
			return

	def settle(self):
		pass # this will check for loss by checking the height of the board content
		# size is 10x20, extra space giving 10x24
		self.piece_is_active = False
		print('clonk')
		# Changing the notation of the previously active piece to
		# denote that it has now settled
		for r in self.board:
			r[:] = ['x' if cell=='*' else cell for cell in r]
		self.parent.after(self.tickrate, self.spawn())

	def spawn(self):
		self.piece_is_active = True
		# Select a random shape and randomly rotate it
		shape = self.shapes[random.choice('SZJLOIT')]
		shape = rot_arr(shape, random.choice((0,90,180,270)))
		width = len(shape[0])
		# Place it in the middle of the board
		start_column = (10-width)//2
		self.active_piece = Shape(shape, [], 0, start_column, [])
		for y, row in enumerate(shape):
			# Spawn in the shape
			self.board[y][start_column:start_column+width] = shape[y]
			for x, cell in enumerate(row, start=start_column):
				if cell:
					self.active_piece.coords.append((self.square_width*x,
																self.square_width*y,
																self.square_width*(x+1),
																self.square_width*(y+1)))
					self.active_piece.piece.append(
						self.canvas.create_rectangle(self.active_piece.coords[-1])
					)
		self.active_piece.rotation_index = 0
		# cycle of coordinates to move the piece slightly each time it rotates
		# to make the rotation feel more natural
		if 3 in (len(shape), len(shape[0])): # 2x3 or 3x2 shape
			self.active_piece.rotation = [(0,0),
													(1, 0),
													(-1, 1),
													(0, -1)]
		else: # I shape
			self.active_piece.rotation = [(1,-1),
													(0, 1),
													(0,0),
													(-1, 0)]	
		if len(shape) < len(shape[0]):
			self.active_piece.rotation_index += 1
		
		self.print_board()

	def new(self):
		pass

	def lose(self):
		pass

	def clear(self):
		pass


root = tk.Tk()
tetris = Tetris(root)
root.mainloop()
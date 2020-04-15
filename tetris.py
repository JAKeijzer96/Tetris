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
import random
try:
	from matrix_rotation import rotate_array as rot_arr
except:
	print('The matrix_rotation module cannot be found or is not installed'\
		'The original code can be found on https://github.com/TigerhawkT3/matrix_rotation')

class Shape():
	def __init__(self, shape, piece):
		'''
		Shape is a 2D array presentation with '*'
		piece is a 2D array with references to canvas child objects
		'''

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
		self.parent.bind('<Left>', self.shift)
		self.parent.bind('<Right>', self.shift)

	def tick(self):
		if not self.piece_is_active:
			self.spawn()
		
		#self.parent.after(self.tickrate, self.tick)
	
	def shift(self, event=None):
		if not self.piece_is_active:		# We do not want to move settled pieces
			return
		# Retrieve information about the active piece
		row = self.active_piece['row']
		column = self.active_piece['column']
		length = len(self.active_piece['shape'])
		width = len(self.active_piece['shape'][0])
		# The function may be called by tick with no event, in which case
		# the piece will move down, or it may be called by a button press event
		# in which case direction is will be the name of the button
		direction = (event and event.keysym) or 'Down'
		# If the piece is at the bottom of the board, settle
		if direction == 'Down':
			if row + length >= self.board_height:
				self.settle()
				return		
			row_temp = row+1 # temp value
			column_temp = column # temp value
		elif direction == 'Left':
			if not column:
				return
			row_temp = row
			column_temp = column - 1
		elif direction == 'Right':
			if column+width >= self.board_width:
				# We do not want to move left past the first column
				# or move right past the right-most column
				return
			row_temp = row
			column_temp = column + 1
		# Looking ahead to see if there is already a piece at the possible new location
		# for the current active_piece
		# The first zip returns tuples of (row_number, [strings of the shape in that row])
		for row_number, squares in zip(range(row_temp, row_temp+length),
													self.active_piece['shape']):
			# The second zip returns tuples of (column_number, string of the shape in that (column,row) coordinate)
			for column_number, square in zip(range(column_temp, column_temp+width), squares):
				# If there's already something there, do not overwrite it with a possible
				# empty string in the rectangular 2D array containing the shape
				if square and self.board[row_number][column_number] == 'x':
					if direction == 'Down':
						self.settle()
					return
		# r = .. would reassign a local variable
		# r[:] = .. takes all elements of the object
		# Removing the shape from the board by iterating over the rows
		# and blanking the cell if it was previously occupied by the shape,
		# otherwise (e.g. settled piece) it remains as it was
		for r in self.board:
			r[:] = ['' if cell=='*' else cell for cell in r]
		
		# Increment the piece's row
		if direction == 'Down':
			row += 1
			self.active_piece['row'] = row
		elif direction == 'Left':
			# Decrement piece's column
			column -= 1
			self.active_piece['column'] = column
		elif direction == 'Right':
			# Increment piece's column
			column += 1
			self.active_piece['column'] = column
		# Iterate over the rows and columns to put the shape
		# on the board again on the new updated position
		# The first zip returns tuples of (row_number, [strings of the shape in that row])
		for row_number, squares in zip(range(row, row+length),self.active_piece['shape']):
			# The second zip returns tuples of (column_number, string of the shape in that row, column coordinate)
			for column_number, square in zip(range(column, column+width), squares):
				# If the 2D array representation of the shape has a non-empty string
				# at the current row_number, column_number coordinate, place it on the board
				if square:
					self.board[row_number][column_number] = square
		# Move the visual representation of the piece on the canvas
		for idx,coords_idx in zip(self.active_piece['piece'], range(len(self.active_piece['coords']))):
			x1,y1,x2,y2 = self.active_piece['coords'][coords_idx]
			if direction == 'Down':
				# Increment y to move the representation down
				y1 += self.square_width
				y2 += self.square_width
			elif direction == 'Left':
				# Decrement x to move the piece left
				x1 -= self.square_width
				x2 -= self.square_width
			elif direction == 'Right':
				# Increment x to move the piece right
				x1 += self.square_width
				x2 += self.square_width
			# Update the active_piece coords to their new values
			self.active_piece['coords'][coords_idx] = x1,y1,x2,y2
			self.canvas.coords(idx, self.active_piece['coords'][coords_idx])
		
		for row in self.board:
			print(row)

	def lateral(self, direction):
		pass

	def settle(self):
		pass # this will check for loss by checking the height of the board content
		# size is 10x20, extra space giving 10x24
		self.piece_is_active = False
		print('clonk')
		# Changing the notation of the previously active piece to
		# denote that it has now settled
		for r in self.board:
			r[:] = ['x' if cell=='*' else cell for cell in r]
			print(r)
		self.parent.after(self.tickrate, self.spawn())


	def spawn(self):
		self.piece_is_active = True
		# Select a random shape and randomly rotate it
		shape = self.shapes[random.choice('SZJLOIT')]
		shape = rot_arr(shape, random.choice((0,90,180,270)))
		width = len(shape[0])
		# Place it in the middle of the board
		start_column = (10-width)//2
		self.active_piece = {'shape':shape, 'piece':[], 'row':0, 'column':start_column, 'coords':[]}
		for y, row in enumerate(shape):
			# Spawn in the shape
			self.board[y][start_column:start_column+width] = shape[y]
			for x, cell in enumerate(row, start=start_column):
				if cell:
					self.active_piece['coords'].append((self.square_width*x,
																self.square_width*y,
																self.square_width*(x+1),
																self.square_width*(y+1)))
					self.active_piece['piece'].append(
						self.canvas.create_rectangle(self.active_piece['coords'][-1])
					)

	def new(self):
		pass

	def lose(self):
		pass

	def clear(self):
		pass


root = tk.Tk()
tetris = Tetris(root)
root.mainloop()
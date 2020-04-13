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
			
		self.parent.bind('<Down>', self.down)

	def tick(self):
		if not self.piece_is_active:
			self.spawn()
			self.piece_is_active = not self.piece_is_active
		
		#self.parent.after(self.tickrate, self.tick)
	
	def down(self, event=None):
		if not self.piece_is_active:
			return
		row = self.active_piece['row']
		column = self.active_piece['column']
		length = len(self.active_piece['shape'])
		width = len(self.active_piece['shape'][0])
		# Use event.keysym for event direction
		if row + length >= self.board_height:
			self.settle()
			return
		self.board[row][column:column+width] = [''] * width
		self.active_piece['row'] += 1
		row += 1
		for squares, current_row in zip(self.active_piece['shape'],
													range(row, row+length)):
			self.board[current_row][column:column+width] = squares
		for idx,coords_idx in zip(self.active_piece['piece'], range(len(self.active_piece['coords']))):
			x1,y1,x2,y2 = self.active_piece['coords'][coords_idx]
			y1 += self.square_width
			y2 += self.square_width
			self.active_piece['coords'][coords_idx] = x1,y1,x2,y2
			self.canvas.coords(idx, self.active_piece['coords'][coords_idx])
			

	def lateral(self, direction):
		pass

	def settle(self):
		pass # this will check for loss by checking the height of the board content
		# size is 10x20, extra space giving 10x24
		self.piece_is_active = not self.piece_is_active
		print('clonk')

	def spawn(self):
		shape = self.shapes[random.choice('SZJLOIT')]
		shape = rot_arr(shape, random.choice((0,90,180,270)))
		width = len(shape[0])
		start_column = (10-width)//2
		self.active_piece = {'shape':shape, 'piece':[], 'row':0, 'column':start_column, 'coords':[]}
		for y, row in enumerate(shape):
			self.board[y][start_column:start_column+width] = shape[y]
			for x, column in enumerate(row, start=start_column):
				if column:
					self.active_piece['coords'].append((self.square_width*x,
																self.square_width*y,
																self.square_width*(x+1),
																self.square_width*(y+1)))
					self.active_piece['piece'].append(
						self.canvas.create_rectangle(self.active_piece['coords'][-1])
					)
					
		for row in self.board:
			print(row)

	def new(self):
		pass

	def lose(self):
		pass

	def clear(self):
		pass


root = tk.Tk()
tetris = Tetris(root)
root.mainloop()
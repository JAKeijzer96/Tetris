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
		self.width = 300
		self.height = 720
		self.square_width = self.width//10
		self.canvas = tk.Canvas(root, width=self.width, height=self.height)
		self.canvas.grid(row=0, column=0)
		self.seperator = self.canvas.create_line(0,self.height//6,
													self.width, self.height//6, width=2)
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

	def tick(self):
		if not self.piece_is_active:
			self.spawn()
			self.piece_is_active = not self.piece_is_active
		
		#self.parent.after(self.tickrate, self.tick)
	
	def down(self):
		pass

	def lateral(self, direction):
		pass

	def settle(self):
		pass # this will check for loss by checking the height of the board content
		# size is 10x20, extra space giving 10x24
		self.piece_is_active = not self.piece_is_active

	def spawn(self):
		shape = self.shapes[random.choice('SZJLOIT')]
		shape = rot_arr(shape, random.choice((0,90,180,270)))
		width = len(shape[0])
		start_column = (10-width)//2
		self.active_piece = [shape, []]
		for y, row in enumerate(shape):
			for x, column in enumerate(row, start=start_column):
				if column:
					self.active_piece[1].append(
						self.canvas.create_rectangle(self.square_width*x,
																self.square_width*y,
																self.square_width*(x+1),
																self.square_width*(y+1))
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
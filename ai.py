import pygame, player, board, bag
from pygame.locals import *

class AI(player.Player):

	def __init__(self, theBoard, theBag, theDifficulty = 10):
		player.Player.__init__(self, "Computer", theBoard, theBag, theDifficulty)
	

		

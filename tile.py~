import pygame, time



class Tile:
	
	TILE_OUTLINE = (55, 46, 40)
	TILE_BLANK = (110, 92, 80)
	TILE_HIGHLIGHT = (100, 100, 255)
	TILE_COLOR = (220, 185, 167)
	TILE_FLASH = (200, 200, 255)
	PULSE_DURATION = 1.5
	
	SQUARE_SIZE = 32
	SQUARE_BORDER = 4

	@staticmethod
	def initialize():
		Tile.LETTER_FONT = pygame.font.Font('freesansbold.ttf', 24)
		Tile.POINTS_FONT = pygame.font.Font('freesansbold.ttf', 7)

	def __init__(self, char, pts):
		self.letter = char
		self.points = pts
		
		if char == ' ' and pts == 0:
			self.isBlank = True
		else:
			self.isBlank = False
		self.locked = False
		self.lastPulseTime = 0
		self.dirty = False
		

	def drawDirty(self, left, top, DISPLAYSURF, highlight = False):
		if self.dirty:
			self.draw(left,top,DISPLAYSURF,highlight)

	def draw(self, left, top, DISPLAYSURF, highlight = False):
		
		if highlight:
			pygame.draw.rect(DISPLAYSURF, Tile.TILE_HIGHLIGHT, (left, top, Tile.SQUARE_SIZE, Tile.SQUARE_SIZE))
		else:
			pygame.draw.rect(DISPLAYSURF, Tile.TILE_OUTLINE, (left+1, top+1, Tile.SQUARE_SIZE-2, Tile.SQUARE_SIZE-2))
			
		backColor = self.getColor()	
		pygame.draw.rect(DISPLAYSURF, backColor, (left+2, top+2, Tile.SQUARE_SIZE-4, Tile.SQUARE_SIZE-4))
		
		if not self.isBlank:
	
			letterText = Tile.LETTER_FONT.render(self.letter, True, Tile.TILE_OUTLINE, backColor)
			letterRect = letterText.get_rect()
			letterRect.center = (left + Tile.SQUARE_SIZE/2 - 3, top + Tile.SQUARE_SIZE/2)
			DISPLAYSURF.blit(letterText, letterRect)
		
	
			pointsText = Tile.POINTS_FONT.render(str(self.points), True, Tile.TILE_OUTLINE, backColor)
			pointsRect = pointsText.get_rect()
			pointsRect.center = (left + Tile.SQUARE_SIZE/2 + Tile.SQUARE_SIZE/3, top + Tile.SQUARE_SIZE/2 + Tile.SQUARE_SIZE/3)
			DISPLAYSURF.blit(pointsText, pointsRect)	
		else:
			letterText = Tile.LETTER_FONT.render(self.letter, True, Tile.TILE_BLANK, backColor)
			letterRect = letterText.get_rect()
			letterRect.center = (left + Tile.SQUARE_SIZE/2 - 3, top + Tile.SQUARE_SIZE/2)
			DISPLAYSURF.blit(letterText, letterRect)		

	def getColor(self):
		timeSince = time.time()-self.lastPulseTime
		color = Tile.TILE_COLOR
		if timeSince < Tile.PULSE_DURATION:
			highlightColor = Tile.TILE_FLASH
	#		tween = timeSince / Tile.PULSE_DURATION
	#		
	#		color = (color[0]*tween + highlightColor[0]*(1-tween), 
	#				 color[1]*tween + highlightColor[1]*(1-tween),
	#				 color[2]*tween + highlightColor[2]*(1-tween))
		else:
			self.dirty = False
					
		return color
						
						
	def pulse(self):
		self.lastPulseTime = time.time()
		self.dirty = True
		
	def lock(self):
		self.locked = True
		

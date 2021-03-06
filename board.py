import pygame, tile, player, dictionarywords, time
from pygame.locals import *

class Board:
	
	DEBUG_ERRORS = True
	
	NORMAL = 'normal'
	DOUBLEWORD = 'doubleword'
	TRIPLEWORD = 'tripleword'
	DOUBLELETTER = 'doubleletter'
	TRIPLELETTER = 'tripleletter'
	
	DICTIONARY_FILE = 'media/scrabblewords_usage.txt'
	
	GRID_SIZE = 15 			#size in # of squares
	START_POSITION = (7, 7)
	SQUARE_SIZE = tile.Tile.SQUARE_SIZE
	SQUARE_BORDER = tile.Tile.SQUARE_BORDER
	BOARD_TOP = 0
	BOARD_LEFT = 0
	
	#Prompt Details
	PROMPT_LEFT = 145
	PROMPT_TOP = 200
	PROMPT_WIDTH = 250
	PROMPT_HEIGHT = 75
	PROMPT_FONT = None
	
	
	
	BEIGE = (200, 180, 165)
	RED	= (200, 0, 0)
	BLUE = (0, 0, 200)
	PINK = (255, 100, 100)
	LBLUE = (100, 100, 255)
	
	MASK_COLOR = (0, 0, 0, 100)

	def __init__(self):
		
		self.squares = []
		for x in range(Board.GRID_SIZE):
			self.squares.append([])
			for y in range(Board.GRID_SIZE):
				
				self.squares[x].append((None, Board.NORMAL))
		
		triplewords = [(0,0), (7,0), (14,0), (0,7), (14,7), (0,14), (7,14), (14,14)]	
		for (x, y) in triplewords:
			self.squares[x][y] = (None, Board.TRIPLEWORD)
		
		doublewords = [(1,1), (2,2), (3,3), (4,4), (1,13), (2,12), (3,11), (4,10),
					   (13,1), (12,2), (11,3), (10,4), (13,13), (12,12), (11,11), (10,10),
					   (7,7)]
		for (x, y) in doublewords:
			self.squares[x][y] = (None, Board.DOUBLEWORD)
			
		tripleletters = [(5,1), (9,1), (1,5), (1,9), (5,13), (9,13), (13,5), (13,9),
						 (5,5), (9,9), (5,9), (9,5)]
		for (x, y) in tripleletters:
			self.squares[x][y] = (None, Board.TRIPLELETTER)
		
		doubleletters = [(3,0), (0,3), (11,0), (0,11), (3,14), (11,14), (14,3), (14,11),
						 (2,6), (3,7), (2,8), (6,2), (7,3), (8,2), (6,12), (7,11), (8,12),
						 (12,6), (11,7), (12,8), (6,6), (8,8), (6,8), (8,6)]
		for (x, y) in doubleletters:
			self.squares[x][y] = (None, Board.DOUBLELETTER)

		self.columnLock = -1
		self.rowLock = -1

		self.dictionary = dictionarywords.DictionaryWords(Board.DICTIONARY_FILE)

		#self.wordfreq = wordfrequency.WordFrequency()

		self.resetAllMetrics()

		Board.PROMPT_FONT = pygame.font.Font('freesansbold.ttf', 20)

	def placeTentative(self, x, y, tile):
		(boardX, boardY) = self.getBoardPosition(x, y)
		
		if self.checkLocks(boardX, boardY):
			if boardX >= 0 and boardY >= 0 and boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
				previousTile = self.squares[boardX][boardY][0]
				if previousTile == None:
					self.squares[boardX][boardY] = (tile, self.squares[boardX][boardY][1])
					if tile.isBlank:
						return ("ASK", tile)
					self.setLocks()
					return (True, tile)
		return (False, tile)

	def checkLocks(self, boardX, boardY):
		if (self.rowLock >= 0 and self.columnLock >= 0) and (boardX == self.columnLock or boardY == self.rowLock):
			locksOkay = True
		elif self.columnLock >= 0 and boardX == self.columnLock:
			locksOkay = True
		elif self.rowLock >= 0 and boardY == self.rowLock:
			locksOkay = True
		elif self.rowLock < 0 and self.columnLock < 0:
			locksOkay = True
		else:
			locksOkay = False
		return locksOkay		
		

	def setLocks(self):
		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append((x, y))

		if len(inPlay) == 0:
			self.columnLock = -1
			self.rowLock = -1

		elif len(inPlay) == 1:
			self.columnLock = inPlay[0][0]
			self.rowLock = inPlay[0][1]

		else:	
			col = inPlay[0][0]
			row = inPlay[0][1]
			inACol = True
			inARow = True
			for t in inPlay:
				if(t[0] != col):
					inACol = False
				if(t[1] != row):
					inARow = False
			

			assert inARow or inACol and not(inARow and inACol)
			
			if inACol:
				self.columnLock = col
				self.rowLock = -1
			elif inARow:
				self.columnLock = -1
				self.rowLock = row	

	def remove(self, x, y):
		(boardX, boardY) = self.getBoardPosition(x, y)	
		if boardX >= 0 and boardY >= 0 and boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
			tile = self.squares[boardX][boardY][0]
			if tile != None and not tile.locked:
				self.squares[boardX][boardY] = (None, self.squares[boardX][boardY][1])
				self.setLocks()
				return tile
		return None

	def getBoardPosition(self, x, y):
		x -= Board.BOARD_LEFT + Board.SQUARE_BORDER
		y -= Board.BOARD_TOP + Board.SQUARE_BORDER
		

		if x >= 0 and y >= 0:

			if (x % (Board.SQUARE_SIZE + Board.SQUARE_BORDER) < Board.SQUARE_SIZE - Board.SQUARE_BORDER and
			   y % (Board.SQUARE_SIZE + Board.SQUARE_BORDER) < Board.SQUARE_SIZE - Board.SQUARE_BORDER):
				boardX = (int)(x / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))
				boardY = (int)(y / (Board.SQUARE_SIZE + Board.SQUARE_BORDER))

				if boardX < Board.GRID_SIZE and boardY < Board.GRID_SIZE:
					return (boardX, boardY)
		return (-1, -1)

	def setPiece(self, (x,y), tile):
		assert x >= 0 and y >= 0 and x < Board.GRID_SIZE and y < Board.GRID_SIZE
		assert self.squares[x][y][0] == None
		self.squares[x][y] = (tile, self.squares[x][y][1])

	def play(self, isFirstTurn=True):

		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append((x, y))

		if len(inPlay) <= 0:

			if Board.DEBUG_ERRORS:
				print "Play requires at least one tile."
			return ([], -1)			
		
		col = inPlay[0][0]
		row = inPlay[0][1]
		inACol = True
		inARow = True
		for (x,y) in inPlay:
			if(x != col):
				inACol = False
			if(y != row):
				inARow = False
		
		if not inARow and not inACol:

			if Board.DEBUG_ERRORS:
				print "All tiles must be placed along a line."		
			return (self.removeTempTiles(), -1)

		if not Board.START_POSITION in inPlay and isFirstTurn:
			return(self.removeTempTiles(), -1)

		unbroken = True
		left = col
		right = col
		top = row
		bottom = row

		for (x, y) in inPlay:
			if x < left:
				left = x
			elif x > right:
				right = x
			if y < top:
				top = y
			elif y > bottom:
				bottom = y

		if inACol:
			for y in range(top, bottom+1):
				if self.squares[col][y][0] == None:
					unbroken = False
		elif inARow:
			for x in range(left, right+1):
				if self.squares[x][row][0] == None:
					unbroken = False
					
		if not unbroken:
			return(self.removeTempTiles(), -1)			

		(totalScore, spellings, seedRatio) = self.validateWords(isFirstTurn, inPlay=inPlay)
		
		#if spellings != None:
		#	for spelling in spellings:
		#		self.wordfreq.wordPlayed(spelling)
				
		#	self.wordfreq.save()
		
		if totalScore < 0:
			return(self.removeTempTiles(), -1)

		for (x,y) in inPlay:
			self.squares[x][y][0].locked = True			

		self.columnLock = -1
		self.rowLock = -1	
			
		return (None, totalScore)

	def wordScoreTreeSearch(self, conflicts, scores, bonusesApplied = []):

		if len(conflicts) == 0:
			totalScore = 0
			for (bonus, word) in bonusesApplied:
				totalScore += scores[word] * bonus
				return (totalScore, bonusesApplied)

		else:

			bonusesApplied1 = bonusesApplied[:]
			bonusesApplied1.append((conflicts[0][0], conflicts[0][1][0]))
			score1 = self.wordScoreTreeSearch(conflicts[1:], scores, bonusesApplied1)
			

			bonusesApplied2 = bonusesApplied[:]
			bonusesApplied2.append((conflicts[0][0], conflicts[0][1][1]))
			score2 = self.wordScoreTreeSearch(conflicts[1:], scores, bonusesApplied2)
			
			if score1 > score2:
				bestScore = score1
				bestBonusCombos = bonusesApplied1
			else:
				bestScore = score2
				bestBonusCombos = bonusesApplied2
			
			return (bestScore, bestBonusCombos)

	def validateWords(self, isFirstTurn, tilesPlayed=None, inPlay=None, vocabulary=-1):
		if Board.DEBUG_ERRORS:
			startTime = time.time()
		
		wordsBuilt = [] 

		if tilesPlayed != None:
			inPlay = []
			for pos, tile in tilesPlayed:
				self.setPiece(pos,tile)
				inPlay.append(pos)
					
		if Board.DEBUG_ERRORS:
			crosswordTimeStart = time.time()
			self.quickValidationTime += crosswordTimeStart - startTime			
			

		seedRatio = self.calculateSeedRatio()		

		rowsToCheck = []
		colsToCheck = []
		colsSet = []
		rowsSet = []
		for (x, y) in inPlay:
			if not x in colsSet:
				colsSet.append(x)
				colsToCheck.append((x, y))
			if not y in rowsSet:
				rowsSet.append(y)
				rowsToCheck.append((x, y))
		

		for (col, row) in rowsToCheck:
			

			left = col
			while left-1 >= 0 and self.squares[left-1][row][0] != None:	
				left -= 1
			

			right = col
			while right+1 < Board.GRID_SIZE and self.squares[right+1][row][0] != None:
				right += 1
			

			if left != right:
				wordsBuilt.append([((x,row), self.squares[x][row][0]) for x in range(left, right+1)])

		for (col, row) in colsToCheck:


			up = row
			while up-1 >= 0 and self.squares[col][up-1][0] != None:	
				up -= 1


			down = row
			while down+1 < Board.GRID_SIZE and self.squares[col][down+1][0] != None:
				down += 1


			if up != down:
				wordsBuilt.append([((col,y), self.squares[col][y][0]) for y in range(up, down+1)])
				
		crosswordMade = False	
		for word in wordsBuilt:
			for ((x,y), tile) in word:
				if tile.locked:
					crosswordMade = True	
					
		if Board.DEBUG_ERRORS:
			validationTimeStart = time.time()
			self.crosswordValidationTime += time.time() - crosswordTimeStart					
					
		if not crosswordMade and not isFirstTurn:
			#fail, word is unattached
			if Board.DEBUG_ERRORS:
				self.crosswordErrors += 1
				if tilesPlayed == None:
					print "Word placed must form at least one crossword."
			self.pullTilesFast(tilesPlayed)			
			return (-1, None, seedRatio)		
					

		spellings = []
		for word in wordsBuilt:
			spelling = ""
			for (pos, tile) in word:
				spelling += tile.letter
			spellings.append(spelling)	
			if not self.dictionary.isValid(spelling, vocabulary):

				if Board.DEBUG_ERRORS:
					self.invalidWordCount += 1
					if tilesPlayed == None:
						print "'"+spelling+"' isn't in the dictionary."
				self.pullTilesFast(tilesPlayed)				
				return (-1, None, seedRatio)
		
		if Board.DEBUG_ERRORS:
			scoringTimeStart = time.time()
			self.dictionaryValidationTime += time.time() - validationTimeStart		
		

		totalScore = 0
		

		if len(inPlay) == player.Player.TRAY_SIZE:
			totalScore += 50
		
		wordScores = {}	
		wordScoreOptimize = []	
		i=0
		for word in wordsBuilt:
			wordScores[i] = 0
			wordBonus = 1
			marks = []		
			for (x, y), tile in word:
				letterScore = tile.points
				if self.squares[x][y][0].locked == False:
					crosswords = self.shared((x,y), wordsBuilt)
					bonus = self.squares[x][y][1]
					if bonus == Board.DOUBLELETTER and not (x,y) in marks:
						letterScore *= 2
						marks.append((x,y))
					elif bonus == Board.TRIPLELETTER and not (x,y) in marks:
						letterScore *= 3
						marks.append((x,y))
					elif bonus == Board.DOUBLEWORD:
						if len(crosswords) <= 1:
							wordBonus *= 2
						else:
							if not (2, crosswords) in wordScoreOptimize:
								wordScoreOptimize.append((2, crosswords))
					elif bonus == Board.TRIPLEWORD:
						if len(crosswords) <= 1:
							wordBonus *= 3
						else:
							if not (3, crosswords) in wordScoreOptimize:
								wordScoreOptimize.append((3, crosswords))
				wordScores[i] += letterScore
			wordScores[i] *= wordBonus
			i+=1
			

		if len(wordScoreOptimize) > 0:
			(best, bestWordScores) = self.wordScoreTreeSearch(wordScoreOptimize, wordScores)
			for (bonus, word) in bestWordScores:
				wordScores[word] *= bonus	
		
		
		for score in wordScores.values():
			totalScore += score	
			
		if Board.DEBUG_ERRORS:
			self.scoringTime += time.time() - scoringTimeStart			
			

		self.pullTilesFast(tilesPlayed)
				
		return (totalScore, spellings, seedRatio)

	def resetAllMetrics(self):
		self.scoringTime = 0
		self.crosswordValidationTime = 0
		self.dictionaryValidationTime = 0
		self.quickValidationTime = 0
		self.invalidWordCount = 0
		self.crosswordErrors = 0

	def pullTilesFast(self, tilesPlayed):
		if tilesPlayed != None:
			for (x,y), tile in tilesPlayed:
				assert self.squares[x][y][0] != None
				assert self.squares[x][y][0].locked == False
				if self.squares[x][y][0].isBlank:
					self.squares[x][y][0].letter = ' '
				self.squares[x][y] = (None, self.squares[x][y][1])

	def shared(self, pos, words):
		wordsUsingPos = []
		i = 0
		for word in words:
			for (coords, tile) in word:
				if pos == coords:
					wordsUsingPos.append(i)
			i+=1
					
		return wordsUsingPos

	def removeTempTiles(self):
		inPlay = []
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None and not self.squares[x][y][0].locked:
					inPlay.append(self.squares[x][y][0])
					self.squares[x][y] = (None, self.squares[x][y][1])

		self.columnLock = -1
		self.rowLock = -1
		
		return inPlay

	def calculateSeedRatio(self):
		numSeeds = 0
		numTiles = 0
		for x in range(Board.GRID_SIZE):

			for y in range(Board.GRID_SIZE):
				if self.squares[x][y][0] != None:
					numTiles += 1
				elif ((x > 0 and self.squares[x-1][y][0] != None) or
					  (x < Board.GRID_SIZE-1 and self.squares[x+1][y][0] != None) or
					  (y > 0 and self.squares[x][y-1][0] != None) or
					  (y < Board.GRID_SIZE-1 and self.squares[x][y+1][0] != None)):
					numSeeds += 1
				
		
		
		if numSeeds == 0:
			numSeeds = 1
			
		return (numSeeds, numTiles)

	def askForLetter(self, blank, DISPLAYSURF, ALPHASURF):
		assert blank.isBlank
		
		letter = None
		self.drawLetterPrompt(DISPLAYSURF, ALPHASURF)
		while letter == None:
			for event in pygame.event.get():
				if event.type == KEYUP:
					if event.key == K_a:
						letter = 'A'
					elif event.key == K_b:
						letter = 'B'
					elif event.key == K_c:
						letter = 'C'
					elif event.key == K_d:
						letter = 'D'
					elif event.key == K_e:
						letter = 'E'
					elif event.key == K_f:
						letter = 'F'
					elif event.key == K_g:
						letter = 'G'
					elif event.key == K_h:
						letter = 'H'
					elif event.key == K_i:
						letter = 'I'
					elif event.key == K_j:
						letter = 'J'
					elif event.key == K_k:
						letter = 'K'
					elif event.key == K_l:
						letter = 'L'
					elif event.key == K_m:
						letter = 'M'
					elif event.key == K_n:
						letter = 'N'
					elif event.key == K_o:
						letter = 'O'
					elif event.key == K_p:
						letter = 'P'
					elif event.key == K_q:
						letter = 'Q'
					elif event.key == K_r:
						letter = 'R'
					elif event.key == K_s:
						letter = 'S'
					elif event.key == K_t:
						letter = 'T'
					elif event.key == K_u:
						letter = 'U'
					elif event.key == K_v:
						letter = 'V'
					elif event.key == K_w:
						letter = 'W'
					elif event.key == K_x:
						letter = 'X'
					elif event.key == K_y:
						letter = 'Y'
					elif event.key == K_z:
						letter = 'Z'
			pygame.display.update()

		blank.letter = letter

											
	def drawLetterPrompt(self, DISPLAYSURF, ALPHASURF):
		

		ALPHASURF.fill((0,0,0,0))
		pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (Board.PROMPT_LEFT, Board.PROMPT_TOP, Board.PROMPT_WIDTH+4, Board.PROMPT_HEIGHT+4))
		

		pygame.draw.rect(ALPHASURF, (0,0,0,200), (Board.PROMPT_LEFT-1, Board.PROMPT_TOP-1, Board.PROMPT_WIDTH+2, Board.PROMPT_HEIGHT+2))
		pygame.draw.rect(ALPHASURF, (255, 255, 255, 200), (Board.PROMPT_LEFT, Board.PROMPT_TOP, Board.PROMPT_WIDTH, Board.PROMPT_HEIGHT))
		
		DISPLAYSURF.blit(ALPHASURF, (0,0))
		

		promptText = Board.PROMPT_FONT.render("TYPE A LETTER A-Z", True, (0,0,0,200), (255,255,255,200))
		promptRect = promptText.get_rect()
		promptRect.center = (Board.PROMPT_LEFT+Board.PROMPT_WIDTH/2, Board.PROMPT_TOP+Board.PROMPT_HEIGHT/2)
		DISPLAYSURF.blit(promptText, promptRect)

	def drawDirty(self, DISPLAYSURF, ALPHASURF):
		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):

				(tile, bonus) = self.squares[x][y]
				if tile != None:
					left = x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_LEFT
					top = y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_TOP
					tile.drawDirty(left, top, DISPLAYSURF, (not tile.locked))
																																				
	
	def draw(self, DISPLAYSURF, ALPHASURF):

		for x in range(Board.GRID_SIZE):
			for y in range(Board.GRID_SIZE):

				left = x * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_LEFT
				top = y * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER + Board.BOARD_TOP
					
				(tile, bonus) = self.squares[x][y]
				if(bonus == Board.NORMAL):
					color = Board.BEIGE
				elif(bonus == Board.DOUBLEWORD):
					color = Board.PINK
				elif(bonus == Board.TRIPLEWORD):
					color = Board.RED
				elif(bonus == Board.DOUBLELETTER):
					color = Board.LBLUE
				elif(bonus == Board.TRIPLELETTER):
					color = Board.BLUE
				else:
					assert(False)
				pygame.draw.rect(DISPLAYSURF, color, (left, top, Board.SQUARE_SIZE, Board.SQUARE_SIZE))
				
				if(tile != None):
					if tile.locked:
						highlight = False
					else:
						highlight = True
					tile.draw(left, top, DISPLAYSURF, highlight)

		ALPHASURF.fill((0,0,0,0))
		top = Board.BOARD_TOP
		left = Board.BOARD_LEFT
		right = Board.GRID_SIZE*(Board.SQUARE_BORDER + Board.SQUARE_SIZE) + Board.SQUARE_BORDER
		bottom = Board.GRID_SIZE*(Board.SQUARE_BORDER + Board.SQUARE_SIZE) + Board.SQUARE_BORDER
		x1 = self.columnLock * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.BOARD_LEFT
		x2 = x1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER
		y1 = self.rowLock * (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.BOARD_LEFT
		y2 = y1 + (Board.SQUARE_SIZE + Board.SQUARE_BORDER) + Board.SQUARE_BORDER				
		if self.rowLock >= 0 and self.columnLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, x1-left, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, y2, x1-left, bottom-y2))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, top, right-x2, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, y2, right-x2, bottom-y2))
		elif self.rowLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, right-left, y1-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, y2, right-left, bottom-y2))
		elif self.columnLock >= 0:
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (left, top, x1-left, bottom-top))
			pygame.draw.rect(ALPHASURF, Board.MASK_COLOR, (x2, top, right-x2, bottom-top))
			
		DISPLAYSURF.blit(ALPHASURF, (0,0))

			

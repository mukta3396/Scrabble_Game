import pygame, time
import board, tile, bag
from pygame.locals import *

class Player:
	
	PROGRESS_TOP = 220
	PROGRESS_LEFT = 570
	PROGRESS_WIDTH = 140
	PROGRESS_HEIGHT = 7
	PROGRESS_MARGIN = 25
	
	PROGRESS_COLOR_BACK = (200, 200, 255)
	PROGRESS_COLOR_FRONT = (100, 100, 255)
	
	FONT_COLOR = (55, 46, 40)
	BACKGROUND_COLOR = (255, 255, 255)
	
	TIMEOUT = 15	
	
	TRAY_SIZE = 7
	
	initialized = False
	
	@staticmethod
	def initialize():
		Player.FONT = pygame.font.Font('freesansbold.ttf', 18)
		Player.initialized = True	

	def __init__(self, name, theBoard, theBag, theDifficulty = 10.0):
		if not Player.initialized:
			Player.initialize()
		
		self.tray = []
		self.score = 0
		self.name = name
		self.theBoard = theBoard
		self.theBag = theBag
		self.lastScore = 0
		
		self.usageLimit = self.theBoard.dictionary.difficultyToUsage(theDifficulty)
		self.grab()

	def grab(self):
		
		if not self.theBag.isEmpty() :
			
			numNeeded = Player.TRAY_SIZE-len(self.tray)
			for i in range(numNeeded):
				newTile = self.theBag.grab()
				if newTile != None:
					self.tray.append(newTile)
					#print newTile
		elif len(self.tray) == 0:
			return False
			
		return True
		

	def play(self, firstTurn):
		
		(tiles, points) = self.theBoard.play(firstTurn)
		
		
		if tiles == None and points >= 0:
			self.score += points
			self.lastScore = points
			gameContinues = self.grab()
			if gameContinues:
				return True
			else:
				return "END"

		elif tiles != None:		

			for t in tiles:
				self.take(t)
				assert len(self.tray) <= Player.TRAY_SIZE
				
			return False
		
		else:
			return False	

	def take(self, tile):
		assert(len(self.tray) < Player.TRAY_SIZE)
		if tile.isBlank:
			tile.letter = ' '
		self.tray.append(tile)			

	def shuffle(self):
		for tile in self.tray:
			self.theBag.putBack(tile)
		
		self.tray = []
		self.theBag.shuffle()
		self.grab()

	def drawTray(self, DISPLAYSURF):
		return None		

	def trayValue(self):
		value = 0
		for tile in self.tray:
			value += tile.points
		return value

	def givePoints(self, num):
		self.score += num

	def getScore(self):
		return score

	def executeTurn(self, isFirstTurn, DISPLAYSURF):
		
	
		startTime = time.time()
		if board.Board.DEBUG_ERRORS:
			self.maxWordTimeStamp = startTime
			self.validationTime = 0
			self.theBoard.dictionary.resetLookupTime()
			self.theBoard.resetAllMetrics()
			self.theWordsConsidered = ""
			self.maxScore = -1
				
		

		seeds = []
		if isFirstTurn:
			seeds.append((7,7)) 
		
		else:	
	
			for x in range(board.Board.GRID_SIZE):
				for y in range(board.Board.GRID_SIZE):
					if self.theBoard.squares[x][y][0] != None:

						if y > 0 and self.theBoard.squares[x][y-1][0] == None:
							if not (x, y-1) in seeds:
								seeds.append((x, y-1))

						if y < board.Board.GRID_SIZE-1 and self.theBoard.squares[x][y+1][0] == None:
							if not (x, y+1) in seeds:
								seeds.append((x, y+1))

						if x > 0 and self.theBoard.squares[x-1][y][0] == None:
							if not (x-1, y) in seeds:
								seeds.append((x-1, y))

						if x < board.Board.GRID_SIZE-1 and self.theBoard.squares[x-1][y][0] == None:
							if not (x+1, y) in seeds:
								seeds.append((x+1, y))
					
		(maxPoints, maxTiles) = -1000, None		
		self.numValidations = 0
		self.numRawValidations = 0
		
		tileSlots = []				

		for (x, y) in seeds:
			
			for lo in range(0, len(self.tray)):
				for hi in range(0, len(self.tray)-lo):
					

					horz = [((x, y), self.theBoard.squares[x][y][0])]
					loCount = 0
					hiCount = 0
					xPos, yPos = x-1, y

					while xPos > 0 and (loCount < lo or self.theBoard.squares[xPos][yPos][0] != None):
						loCount += 1
						horz.insert(0, ((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						xPos -= 1

					xPos, yPos = x+1, y
					while xPos < board.Board.GRID_SIZE-1 and (hiCount < hi or self.theBoard.squares[xPos][yPos][0] != None):
						hiCount += 1
						horz.append(((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))	
						xPos += 1	

					vert = [((x, y), self.theBoard.squares[x][y][0])]
					loCount = 0
					hiCount = 0
					xPos, yPos = x, y-1

					while yPos > 0 and (loCount < lo or self.theBoard.squares[xPos][yPos][0] != None):
						loCount += 1
						vert.insert(0, ((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						yPos -= 1

					xPos, yPos = x, y+1
					while yPos < board.Board.GRID_SIZE-1 and (hiCount < hi or self.theBoard.squares[xPos][yPos][0] != None):
						hiCount += 1
						vert.append(((xPos, yPos), self.theBoard.squares[xPos][yPos][0]))
						yPos += 1
						
					tileSlots.append(horz)
					tileSlots.append(vert)					
			
		

		tileSlotsMap = {}	
		i = 0
		originalSize = len(tileSlots)
		numEliminated = 0
		while i < len(tileSlots):
			slot = tileSlots[i]
			(x1, y1) = slot[0]
			(x2, y2) = slot[-1]
			if tileSlotsMap.get((x1,y1,x2,y2), False):
				tileSlots.pop(i)
				numEliminated += 1
			else:
				tileSlotsMap[(x1,y1,x2,y2)] = True
				i += 1
				
		tileSlots = self.reorderTileSlots(tileSlots)		
				
		if board.Board.DEBUG_ERRORS:
			initTime = time.time()-startTime	

		progress = 0
		totalProgress = len(tileSlots)
		for tileSlot in tileSlots:
			progress += 1
			emptySlots = []
			wordBuilt = []
			slotPosition = {}
			for (x, y), tile in tileSlot:
				slotPosition[(x, y)] = True
				if tile == None:
					emptySlots.append((x,y))
				wordBuilt.append(tile)
			
			self.updateProgressBar(1.0*progress/totalProgress, DISPLAYSURF)
			
			timeSpent = time.time() - startTime
			
			if timeSpent > Player.TIMEOUT:
				
				
				break
				
			(points, tiles, blanks) = self.tryEverything(isFirstTurn, wordBuilt, emptySlots, self.tray)
			if points > maxPoints:
				(maxPoints, maxTiles, maxBlanks) = (points, tiles, blanks)

		if maxTiles != None and maxTiles != []:
			self.placeTiles(maxTiles, maxBlanks)
			playedMove = True
			
			seedRatio = self.theBoard.calculateSeedRatio()

			if board.Board.DEBUG_ERRORS:
				lettersUsed = []
				for pos, tile in maxTiles:
					if tile.isBlank:
						theLetter = "_"
					else:
						theLetter = tile.letter
					lettersUsed.append(theLetter)


		else:
			playedMove = False
			
		if board.Board.DEBUG_ERRORS:
			endTime = time.time()
			timeSpent = endTime-startTime + .00001
			percentValidating = 100.0 * self.validationTime / timeSpent
			percentLookup = 100.0 * self.theBoard.dictionary.lookupTime / timeSpent
			percentInitializing = 100.0 * initTime / timeSpent
		
			totalValidationTime = (self.theBoard.quickValidationTime + self.theBoard.crosswordValidationTime +
									self.theBoard.dictionaryValidationTime + self.theBoard.scoringTime) + .00001
			percentQuickValidation = self.theBoard.quickValidationTime / totalValidationTime
			percentCrosswordValidation = self.theBoard.crosswordValidationTime / totalValidationTime
			percentDictionaryValidation = self.theBoard.dictionaryValidationTime / totalValidationTime
			percentScoring = self.theBoard.scoringTime / totalValidationTime

		return playedMove	 
	
	def tryEverything(self, isFirstTurn, word, slots, trayTiles, tilesPlaced = []):
		

		if len(slots) == 0:
		
			if board.Board.DEBUG_ERRORS:	
				startValidation = time.time()
			
			blankAssignment = []
			seedRatio = (-1, -1)

			i = 0
			spelling = ""
			for tile in word:
				
				if tile != None:
					spelling += tile.letter
				else:
					spelling += tilesPlaced[i][1].letter
					i+=1
					
	
			if not ' ' in spelling:		
				if self.theBoard.dictionary.isValid(spelling, self.usageLimit) or len(slots) == 1:
					if board.Board.DEBUG_ERRORS:
						self.numValidations += 1
						self.numRawValidations += 1
						if self.numValidations % 10 == 0:
							self.theWordsConsidered += "\n"
						self.theWordsConsidered += spelling + ", "
					(score, dummy, seedRatio) = self.theBoard.validateWords(isFirstTurn, tilesPlayed=tilesPlaced, vocabulary = self.usageLimit)
				else:
					score = -1000

			else:

				blankAssignments = self.theBoard.dictionary.matchWithBlanks(spelling, vocabulary = self.usageLimit)
			
				rawValidation = 0
			
				if len(blankAssignments) > 0:
					for assignment in blankAssignments:
						

						i = 0
						assignedSpelling = ''
						for (x, y), tile in tilesPlaced:
							if tile.isBlank:
								tile.letter = assignment[i]
								i += 1
							assignedSpelling += tile.letter
						
						if board.Board.DEBUG_ERRORS:
							self.numValidations += 1
							rawValidation = 1
							if self.numValidations % 10 == 0:
								self.theWordsConsidered += "\n"
							self.theWordsConsidered += assignedSpelling + ", "
							
						(score, dummy, seedRatio) = self.theBoard.validateWords(isFirstTurn, tilesPlayed=tilesPlaced, vocabulary = self.usageLimit)
						

						if score > 0:
							blankAssignment = assignment
							break

				else:
					score = -1000
					
				if board.Board.DEBUG_ERRORS:
					self.numRawValidations += rawValidation
					
			if board.Board.DEBUG_ERRORS:
				endValidation = time.time()
				self.validationTime += endValidation-startValidation
				
			if score > self.maxScore:
				self.maxScore = score
				self.maxWordTimeStamp = time.time()
		
			return (score, tilesPlaced, blankAssignment)

		else:
			slot = slots[0]
			(maxScore, maxTiles, maxBlanks) = (-1000, None, None)
			for tile in trayTiles:
				newTilesPlaced = tilesPlaced[:]
				newTilesPlaced.append((slot, tile))
				trayRemaining = trayTiles[:]
				trayRemaining.remove(tile)
				(score, tilesTried, blankAssignment) = self.tryEverything(isFirstTurn, word, slots[1:], trayRemaining, newTilesPlaced)
				if score > maxScore:
					maxScore, maxTiles, maxBlanks = score, tilesTried, blankAssignment
			return (maxScore, maxTiles, maxBlanks)

	def reorderTileSlots(self, tileSlots):

		orderedBySlots = [[] for i in range(Player.TRAY_SIZE+1)]
		
		for tileSlot in tileSlots:
			i = 0
			for pos, slot in tileSlot:
				if slot == None:
					i += 1
			assert i < len(orderedBySlots)	
			orderedBySlots[i].append(tileSlot)
		
		newTileSlots = []	
		for ranking in orderedBySlots:
			if len(ranking) > 0:
				for tileSlot in ranking:
					newTileSlots.append(tileSlot)
					
		return newTileSlots

	def placeTiles(self, tiles, blanks):
		
		i = 0
		for (pos, tile) in tiles:
			
			if tile.isBlank and blanks != None and i < len(blanks):
				tile.letter = blanks[i]
				i+=1
						
			self.theBoard.setPiece(pos,tile)
			tile.pulse()
			self.tray.remove(tile)

	def updateProgressBar(self, progress, DISPLAYSURF):
		progText = Player.FONT.render("Thinking...", True, Player.FONT_COLOR, Player.BACKGROUND_COLOR)
		progRect = progText.get_rect()
		progRect.left = Player.PROGRESS_LEFT
		progRect.top = Player.PROGRESS_TOP
		DISPLAYSURF.blit(progText, progRect)	
		pygame.draw.rect(DISPLAYSURF, Player.PROGRESS_COLOR_BACK, (Player.PROGRESS_LEFT, Player.PROGRESS_TOP + Player.PROGRESS_MARGIN, Player.PROGRESS_WIDTH, Player.PROGRESS_HEIGHT))
		width = progress * Player.PROGRESS_WIDTH
		pygame.draw.rect(DISPLAYSURF, Player.PROGRESS_COLOR_FRONT, (Player.PROGRESS_LEFT, Player.PROGRESS_TOP + Player.PROGRESS_MARGIN, width, Player.PROGRESS_HEIGHT))
	
		pygame.display.update()

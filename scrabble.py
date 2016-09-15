import pygame, random, sys, time
from pygame.locals import *
import board, tile, bag, player, human, ai

pygame.init()

DISPLAYSURF = pygame.display.set_mode((1000, 1200))
ALPHASURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption('Scrabble!')

tile.Tile.initialize()

import menu

SCORE_FONT = pygame.font.Font('freesansbold.ttf', 20)
SCORE_LEFT = 570
SCORE_TOP = 100
SCORE_MARGIN = 25
SCORE_PULSE = 5.0

BACKGROUND_COLOR = (255, 255, 255)
SCORE_COLOR = (55, 46, 40)

def main():

	theMenu = menu.MainMenu()
	while True:
		mouseClicked = False	
		mouseMoved = False
		SELECTION = ""	
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY = event.pos
				mouseMoved = True
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True
				
		if mouseClicked:
			SELECTION = theMenu.execute(mouseX, mouseY)
			
		if mouseMoved:
			theMenu.update(mouseX, mouseY)
			
		if SELECTION == menu.MainMenu.NEW_GAME:
			runGame()
			theMenu.redraw()
		elif SELECTION == menu.MainMenu.EXIT_GAME:
			pygame.quit()
			sys.exit()
			
		pygame.display.update()
		

def runGame():	
	theBag = bag.Bag()

	theBoard = board.Board()
	
	players = []
	
	players.append(human.Human("Player", theBoard, theBag))
	players.append(ai.AI(theBoard, theBag,theDifficulty = 10.0))
	active = 0
	computerTurn = isinstance(players[active], ai.AI)	
	firstTurn = True
	gameOver = False
	gameMenu = menu.GameMenu()
	redrawEverything(theBoard, players[active], players, gameOver, gameMenu)
	inHand = None
	stillPlaying = True
	AIstuck = False
	
	while stillPlaying:
		
		mouseClicked = False
		mouseMoved = False
		actionKeyHit = False

		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY = event.pos
				mouseMoved = True
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True
			elif event.type == KEYUP:
				if event.key == K_SPACE or event.key == K_RETURN:
					actionKeyHit = True
				if event.key == K_r:
					shuffleKeyHit = True
					

		if mouseMoved:
			gameMenu.update(mouseX, mouseY)

		if mouseClicked:
			SELECTION = gameMenu.execute(mouseX, mouseY)	

			if SELECTION == menu.GameMenu.PLAY_TURN:
				actionKeyHit = True

			if SELECTION == menu.GameMenu.MAIN_MENU:
				stillPlaying = False

					
		if (actionKeyHit or computerTurn) and not gameOver:
		
			if computerTurn:
				playedMove = players[active].executeTurn(firstTurn, DISPLAYSURF)
			else:
				playedMove = True
			
			if playedMove:	
				
				success = players[active].play(firstTurn)
				if success == "END":
					gameOver = True
					endGame(players, active, useHintBox, USERDATA)
				elif success:
					firstTurn = False
					active += 1
					if active >= len(players):
						active = 0
					computerTurn = isinstance(players[active], ai.AI)

					if computerTurn:
						AIstuck = False					

			else:
				players[active].shuffle()
				players[active].lastScore = 0
				if theBag.isEmpty():
					AIstuck = True
					
				active += 1
				if active >= len(players):
					active = 0
				computerTurn = isinstance(players[active], ai.AI)

			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	

		if mouseClicked and not computerTurn and not gameOver:
			inHand = tileGrab(mouseX, mouseY, inHand, theBoard, players[active])
			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	
			
	

		redrawNecessary(theBoard, players, gameOver)		
		pygame.display.update()

def tileGrab(x, y, hand, theBoard, theHuman):
	
	if hand == None:
		tile = theBoard.remove(x, y) 
		if tile != None:
			
			theHuman.take(tile)		
			return None
		else:
			tile = theHuman.pickup(x, y)
			if tile != None:
				return tile	 
			else:
				return None 
	else:
		(success, blank) = theBoard.placeTentative(x, y, hand)
		if success != False:
			if success == "ASK":
				theBoard.askForLetter(blank, DISPLAYSURF, ALPHASURF)
			theHuman.placeTentative()	
			return None					
		else:
			tile = theHuman.pickup(x, y)	
			return tile

def redrawEverything(board, currentPlayer, players, gameOver, gameMenu):
	DISPLAYSURF.fill(BACKGROUND_COLOR)
	board.draw(DISPLAYSURF, ALPHASURF)
	currentPlayer.drawTray(DISPLAYSURF)	
	drawScore(players, gameOver)
	gameMenu.redraw()
def redrawNecessary(board, players, gameOver):
	board.drawDirty(DISPLAYSURF, ALPHASURF)
	drawScore(players, gameOver)

def drawScore(players, gameOver):
	i = 0
	left = SCORE_LEFT
	for player in players:
		top = SCORE_TOP + SCORE_MARGIN * i
		
		sentence = player.name + ": " + str(player.score)
		
		scoreText = SCORE_FONT.render(sentence, True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = top
		DISPLAYSURF.blit(scoreText, scoreRect)
		i += 1
	

	if gameOver:
		scoreText = SCORE_FONT.render("Game finished!", True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = SCORE_TOP + SCORE_MARGIN * i
		DISPLAYSURF.blit(scoreText, scoreRect)		

def endGame(players, active, isPractice, userdata, stuck = False):

	if not stuck:
		i = 0
		surplus = 0
		for p in players:
			if i != active:
				value = p.trayValue()
				p.givePoints(-value)
				surplus += value
		players[active].givePoints(surplus)	
	
	if not isPractice:
		maxScore = -1
		maxPlayer = players[0]
		for p in players:
			if isinstance(p, human.Human):
				if userdata.has_key("bestScore") and p.score > userdata["bestScore"]:
					userdata["bestScore"] = p.score
			if p.score > maxScore:
				maxPlayer = p
				maxScore = p.score
		
if __name__ == '__main__':
	main()

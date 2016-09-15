import board, time, math

class DictionaryWords:

	def __init__(self, filename):
		self.words = {}
		self.lookupTime = 0
		dictFile = open(filename, 'r')
		for line in dictFile:
			line = line.rstrip()
			tokens = line.split()
			if len(tokens) == 1:
				count = -1
			elif len(tokens) == 2:
				count = int(tokens[1])
				
			self.words[tokens[0]] = count

	def isValid(self, word, vocabulary = -1):
		
	
		if board.Board.DEBUG_ERRORS:
			startTime = time.time()
	

		if self.words.has_key(word):
			value = self.words[word]
			success = True
			if vocabulary > 0:
				

				if value <= 0:
					value = 1
					
				if value < vocabulary:
					success = False
		
		else:
			success = False
		
		
					
		if board.Board.DEBUG_ERRORS:
			timeSpent = time.time()-startTime
			self.lookupTime += timeSpent
		
		return success

	def matchWithBlanks(self, word, vocabulary = -1, assignment=[]):
		

		if not ' ' in word:
			if self.isValid(word, vocabulary):
				return [assignment]
			else:
				return []
		else:
			i = word.find(' ')
			blankAssignments = []
			for code in range(ord('A'), ord('Z')+1):
				char = chr(code)
				if i == 0:
					newWord = char + word[1:]
				elif i == len(word)-1:
					newWord = word[:-1] + char
				else:
					newWord = word[:i] + char + word[i+1:]
				
				newAssignment = assignment[:]
				newAssignment.append(char)
				results = self.matchWithBlanks(newWord, vocabulary, newAssignment)
				for result in results:
					blankAssignments.append(result)
							
			return blankAssignments

	def resetLookupTime(self):
		self.lookupTime = 0

	def difficultyToUsage(self, difficulty):
		alpha = 10 - (difficulty/10.0)*6.5
		usage = math.exp(alpha)

		if difficulty >= 9.999:
			usage = -1
			
		return usage
	

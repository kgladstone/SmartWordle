# Smart Wordle
import string
from operator import itemgetter
import random


## INPUT: Get dictionary
def get_word_dictionary(WORD_LENGTH):
	words = set()
	with open("words.txt", "r") as f:
		for x in f:
			line = x.replace('\n','')
			if len(line) == WORD_LENGTH and line[0] == line[0].lower():
				words.add(line.upper())
	return words

## Dictionary of words that start with a letter
def letter_dict_from_index(words, letter_index):
	letter_dict = dict()
	letter_dict_counts = dict()
	for word in words:
		letter = word[letter_index]
		if letter in letter_dict:
			letter_dict[letter].append(word)
			letter_dict_counts[letter] += 1
		else:
			letter_dict[letter] = [word]
			letter_dict_counts[letter] = 1
	return (letter_dict, letter_dict_counts)


## Word count in which letters appear
def word_count_by_letter_in_word(words):
	letter_dict = dict()
	# Populate dictionary
	for ltr in string.ascii_uppercase:
		for word in words:
			if ltr in word:
				if ltr not in letter_dict:
					letter_dict[ltr] = 1
				else:
					letter_dict[ltr] += 1
	return letter_dict


## Rank letters by word count
def print_letters_by_word_count(wc_dict):
	# Create a list of tuples sorted by index 1 i.e. value field     
	listofTuples = sorted(wc_dict.items() , reverse=True, key=lambda x: x[1])
	# Iterate over the sorted sequence
	for elem in listofTuples :
		print(elem[0] , " ::" , elem[1] )   


## Score remaining words based on likelihood
def score_words(remaining_words, wc_dict):
	scoreTuples = list()

	for word in remaining_words:
		# Score individual word
		score = 0
		ltrs = set()
		for i in range(0, len(word)):
			ltrs.add(word[i])
		for j in ltrs:
			score += wc_dict[j]
		scoreTuples.append((word, score))

	#print(scoreTuples)
	sorted_scores = sorted(scoreTuples,key=itemgetter(1), reverse=True)
	#sorted_scores = scoreTuples.sort(key = lambda x: x[1], reverse=True)
	return sorted_scores


## Get feedback if secret word is known
def get_feedback(secret_word, human_guess):
	feedback = list()

	# Populate feedback list
	for i in range(0, len(human_guess)):
		if human_guess[i] == secret_word[i]:
			feedback.append((human_guess[i], 'GREEN'))
		elif human_guess[i] in set(secret_word):
			feedback.append((human_guess[i], 'YELLOW'))
		else:
			feedback.append((human_guess[i], 'GRAY'))
	return feedback

## Enter feedback if secret word is not known
def set_feedback(human_guess):
	feedback = list()

	# Populate feedback list
	for i in range(0, len(human_guess)):
		ltr = human_guess[i]
		clr = int(raw_input("For letter {} enter:\n1 : GREEN\n2 : YELLOW\n3 : GRAY\n".format(ltr))[0])
		if clr == 1:
			feedback.append((ltr, 'GREEN'))
		elif clr == 2:
			feedback.append((ltr, 'YELLOW'))
		else:
			feedback.append((ltr, 'GRAY'))
	return feedback

## Process feedback
def process_feedback(feedback, remaining_words):
	print("\n** PROCESSING FEEDBACK **")
	print("There were {} possible words left".format(len(remaining_words)))
	print(feedback)

	###### PROCESS GRAY
	## Obtain gray letters
	gray_letters = set()
	for ltr, clr in feedback:
		if clr == 'GRAY':
			gray_letters.add(ltr)
	## Remove all words that contain the gray letter
	words_to_remove = set()
	for word in remaining_words:
		for ltr in gray_letters:
			if ltr in word:
				words_to_remove.add(word)
	for word in words_to_remove:
		remaining_words.remove(word)
	print("1. Evaluating gray letters")
	print(" 1.1 Eliminating these letters entirely (absence known): {}".format(gray_letters))
	print(" 1.2 Removing {} words due to gray letters".format(len(words_to_remove)))
	print(" 1.3 There are {} possible words left".format(len(remaining_words)))

	###### PROCESS GREEN+YELLOW
	# Preserve only words with yellow or green letters
	green_yellow_letters = set()
	for ltr, clr in feedback:
		if clr == 'YELLOW' or clr == 'GREEN':
			green_yellow_letters.add(ltr)

	## Remove all words that DO NOT contain the letter
	words_to_remove = set()
	for word in remaining_words:
		for ltr in green_yellow_letters:
			if ltr not in word:
				words_to_remove.add(word)
	for word in words_to_remove:
		remaining_words.remove(word)
	print("2. Evaluating yellow/green letters (presence known)")
	print(" 2.1 Preserving only words with these letters: {}".format(green_yellow_letters))
	print(" 2.2 Removing {} words due to yellow/green letters".format(len(words_to_remove)))
	print(" 2.3 There are {} possible words left".format(len(remaining_words)))

	###### PROCESS PURE GREEN
	# Preserve only words that have a green in the right spot
	green_string = ''
	GREEN_PLACEHOLDER_CHAR = '?'
	for ltr, clr in feedback:
		if clr == 'GREEN':
			green_string += ltr
		else:
			green_string += GREEN_PLACEHOLDER_CHAR

	## Remove all words that DO NOT contain the letter in right position
	words_to_remove = set()
	for word in remaining_words:
		for i in range(0, len(green_string)):
			if green_string[i] == GREEN_PLACEHOLDER_CHAR:
				pass
			else:
				if green_string[i] != word[i]:
					words_to_remove.add(word)
	for word in words_to_remove:
		remaining_words.remove(word)

	print("3. Evaluating pure green letters")
	print(" 3.1 Preserving only words with this sequence (place known): {}".format(green_string))
	print(" 3.2 Removing {} words due to pure green letters".format(len(words_to_remove)))
	print(" 3.3 There are {} possible words left".format(len(remaining_words)))

	print("... Remaining word counts by letter:")
	wcs = word_count_by_letter_in_word(remaining_words)

	print_letters_by_word_count(wcs)

	scored_words = score_words(remaining_words, wcs)

	# If fewer than X words left, expose them
	WORDS_TO_EXPOSE_THRESOLD = 20
	if len(remaining_words) <= WORDS_TO_EXPOSE_THRESOLD:
		print("There are fewer than {} words left, and they are:".format(WORDS_TO_EXPOSE_THRESOLD))
		print(score_words(remaining_words, wcs))
	else:
		print("Top {} suggested words are:".format(WORDS_TO_EXPOSE_THRESOLD))
		print(score_words(remaining_words, wcs)[1:WORDS_TO_EXPOSE_THRESOLD])

	return remaining_words

#--------------------------------------------------------------------------------------------

#### GAME
# Start with human_guess (based on initial set of words)
# Feedback: 
## (1) do any letters exist in the right position
## (2) do any letters exist in the wrong position
## (3) do any letters not exist
# Try again with a new human_guess (based on smaller set of words)

## SIMULATOR
print("**** WELCOME TO SMARTWORDLE ****")
WORD_LENGTH = 5
remaining_words = get_word_dictionary(WORD_LENGTH)
secret_word = random.choice(list(remaining_words))
num_guesses = 0
guesses_list = list()

# Start loop
while True:
	print("*************")
	print("Number of guesses so far: {}".format(num_guesses))
	print("Guesses so far: {}".format(guesses_list))
	human_guess = raw_input("Guess a {}-letter word: ".format(WORD_LENGTH)).upper()
	guesses_list.append(human_guess)
	num_guesses += 1
	if len(human_guess) != WORD_LENGTH:
		print("Quitting game...")
		quit()
	elif human_guess == secret_word or len(remaining_words) == 1:
		print("YOU WIN!")
		quit()
	else:
		#feedback = get_feedback(secret_word, human_guess)
		feedback = set_feedback(human_guess)
		remaining_words = process_feedback(feedback, remaining_words)
		print("Keep guessing!")

###############
# TO DO LIST
### TODO: Corner case: multiple of same letter
### TODO: Incorporate knowing where a yellow letter is NOT located
### TODO: Secret is not known (currently using a computer-known random secret)

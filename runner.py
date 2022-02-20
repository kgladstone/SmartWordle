# Smart Wordle
import string
from operator import itemgetter
import random
import numpy as np


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
def process_feedback(feedback, remaining_words, do_print=False):
	if do_print:
		print("\n** PROCESSING FEEDBACK **")
		print("There were {} possible words left".format(len(remaining_words)))
		print(feedback)

	###### PROCESS GRAY
	## Obtain gray letters (and green_yellow_letters)
	green_yellow_letters = set()
	gray_letters = set()
	for ltr, clr in feedback:
		if clr == 'GRAY':
			gray_letters.add(ltr)
		else:
			green_yellow_letters.add(ltr)

	## Remove all words that contain the gray letter
	words_to_remove = set()
	gray_letters_final = set()
	for word in remaining_words:
		for ltr in gray_letters:
			if ltr in word and ltr not in green_yellow_letters:
				gray_letters_final.add(ltr)
				words_to_remove.add(word)
	for word in words_to_remove:
		remaining_words.remove(word)
	if do_print:
		print("1. Evaluating gray letters")
		print(" 1.1 Eliminating these letters entirely (absence known): {}".format(gray_letters_final))
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

	if do_print:
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

	if do_print:
		print("3. Evaluating pure green letters")
		print(" 3.1 Preserving only words with this sequence (place known): {}".format(green_string))
		print(" 3.2 Removing {} words due to pure green letters".format(len(words_to_remove)))
		print(" 3.3 There are {} possible words left".format(len(remaining_words)))


	###### PROCESS PURE YELLOW
	# Build up list of regexs with yellows that are invalid
	# Remove all words that have a yellow in the wrong spot
	yellow_letters = set()
	words_to_remove = set()
	for i, (ltr, clr) in enumerate(feedback):
		if clr == "YELLOW":
			for word in remaining_words:
				if word[i] == ltr:
					yellow_letters.add((i, ltr))
					words_to_remove.add(word)
	for word in words_to_remove:
		remaining_words.remove(word)
	yellow_letters = sorted(yellow_letters,key=itemgetter(0))

	if do_print:
		print("4. Evaluating pure yellow letters")
		print(" 4.1 Eliminating words with this sequence (place known) [zero-indexed]: {}".format(yellow_letters))
		print(" 4.2 Removing {} words due to pure yellow letters".format(len(words_to_remove)))
		print(" 4.3 There are {} possible words left".format(len(remaining_words)))

		print("... Remaining word counts by letter:")
	wcs = word_count_by_letter_in_word(remaining_words)

	if do_print:
		print_letters_by_word_count(wcs)

	scored_words = score_words(remaining_words, wcs)
	auto_next_guess = scored_words[0][0]

	# If fewer than X words left, expose them
	WORDS_TO_EXPOSE_THRESOLD = 20
	if do_print:
		if len(remaining_words) <= WORDS_TO_EXPOSE_THRESOLD:
			print("There are fewer than {} words left, and they are:".format(WORDS_TO_EXPOSE_THRESOLD))
			print(score_words(remaining_words, wcs))
		else:
			print("Top {} suggested words are:".format(WORDS_TO_EXPOSE_THRESOLD))
			print(score_words(remaining_words, wcs)[0:WORDS_TO_EXPOSE_THRESOLD])

	return remaining_words, auto_next_guess

## Start game when secret is known
def run_game(WORD_LENGTH, remaining_words, SEED_WORD, SECRET_WORD, AUTO_GUESS, OVERRIDE_CONFIRM, DO_PRINT):
	# Set up variables
	num_guesses = 0
	guesses_list = list()
	auto_next_guess = SEED_WORD
	human_prompt_guess = "Guess a {}-letter word: ".format(WORD_LENGTH)
	SECRET_KNOWN = len(SECRET_WORD) == WORD_LENGTH

	if DO_PRINT:
		print("**** WELCOME TO SMARTWORDLE ****")
	while True:
		if DO_PRINT:
			print("****************************************************")
			print("Number of guesses so far: {}".format(num_guesses))
			print("Guesses so far: {}".format(guesses_list))
			print("****************************************************")

		# Guess engine
		if AUTO_GUESS:
			if DO_PRINT:
				print(human_prompt_guess)
			human_guess = auto_next_guess
			if OVERRIDE_CONFIRM is False:
				confirm_guess = raw_input("Do you want to guess the word {} (Y/N): ".format(human_guess)).upper()[0]
				if confirm_guess != "Y":
					human_guess = raw_input(human_prompt_guess).upper()
		else:
			human_guess = raw_input(human_prompt_guess).upper()

		if DO_PRINT:
			print("You guessed {}".format(human_guess))
		guesses_list.append(human_guess)
		num_guesses += 1
		if len(human_guess) != WORD_LENGTH:
			print("Quitting game...")
			return list()
		elif SECRET_KNOWN and human_guess == SECRET_WORD:
			if DO_PRINT:
				print("YOU WIN!")
				print("Guesses were: {}".format(guesses_list))
			return guesses_list
		else:
			if SECRET_KNOWN:
				feedback = get_feedback(SECRET_WORD, human_guess)
			else:
				feedback = set_feedback(human_guess)
			remaining_words, auto_next_guess = process_feedback(feedback, remaining_words, do_print=DO_PRINT)
			if len(remaining_words) == 1 and list(remaining_words)[0] == human_guess:
				if DO_PRINT:
					print("YOU WIN!")
					print("Guesses were: {}".format(guesses_list))
				return guesses_list
			else:
				if DO_PRINT:
					print("Keep guessing!")

## Simulate a number of games
def simulate_N_games(WORD_LENGTH, SEED_WORD, NUM_GAMES):
	print("Seed word: {}".format(SEED_WORD))
	print("Starting simulation of {} games with random 'secret' words...".format(NUM_GAMES))
	results_compiled = list()
	for round in range(0, NUM_GAMES):
		remaining_words = get_word_dictionary(WORD_LENGTH)
		secret_word = random.choice(list(remaining_words))
		result = run_game(WORD_LENGTH, remaining_words, SEED_WORD, SECRET_WORD=secret_word, AUTO_GUESS=True, OVERRIDE_CONFIRM=True, DO_PRINT=False)
		results_compiled.append((result))

	# for result in results_compiled:
	# 	print("Guessed in {} turns: {}".format(len(result), result))

	print("Simulation complete!")
	guesses_per_game = [len(result) for result in results_compiled]
	print("Average number of guesses per game: {}".format(np.mean(guesses_per_game)))


#--------------------------------------------------------------------------------------------

#### GAME
# Start with human_guess (based on initial set of words)
# Feedback: 
## (1) do any letters exist in the right position
## (2) do any letters exist in the wrong position
## (3) do any letters not exist
# Try again with a new human_guess (based on smaller set of words)

## SIMULATOR

# Config
WORD_LENGTH = 5
SEED_WORD = "STARE"
AUTO_GUESS = True
remaining_words = get_word_dictionary(WORD_LENGTH)

#result = run_game(WORD_LENGTH, remaining_words, SEED_WORD, SECRET_WORD="", AUTO_GUESS=True, OVERRIDE_CONFIRM=False, DO_PRINT=True)

simulate_N_games(WORD_LENGTH, SEED_WORD, 250)
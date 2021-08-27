# Tetris Flip by Raven Ironwing (2021)
# Keyboard controls: WASD: Flip/Rotate, Arrow Keys for moving, Space for dropping.
# Gamepad controls: D pad moves, A/X rotate, B/Y Flip, right shoulder drops.

# A simple yet full featured Tetris clone.
# I used and older bare bones version of Tetris by "Kevin Chabowski"<kevin@kch42.de> as a starting point for this game (The one with no levels).
# Things I added:
# Next block, music, sound effects, levels, counter clockwise rotation, instant dropping, scoring, centered rotation, improved graphics and window scaling, updated code for python 3, gamepad support, tetris animation.

# Music attributions
# music0.ogg cuts from NES-Bach-BMV-565, TheOuterLinux, https://opengameart.org/content/nes-bach-bwv-565
# music1.ogg an 8-bit transcription by Ctske of Johann Pachelbel's Canon https://opengameart.org/content/8-bit-pachelbels-canon-in-d
# music2.ogg Techno Bach Loop, Marco, https://opengameart.org/content/techno-bach-loop
# music3.ogg c64-bach-wtk2-prelude2, TheOuterLinux, https://opengameart.org/content/c64-bach-wtk2-prelude2
# music4.ogg “Invention 4” by Johann Sebastian Bach Chiptune rendition by Haley Halcyon, https://opengameart.org/content/nes-baroque-music-bachs-invention-4
# music5 Cyberpunk Moonlight Sonata by Joth, https://opengameart.org/content/cyberpunk-moonlight-sonata
# music6 C64 - Dies Irae, TheOuterLinux, https://opengameart.org/content/c64-mozart-dies-irae
# music7.ogg Sonata 8, Kim Lightyear, Bernd Krueger https://opengameart.org/content/sonata-8-chiptune-beethoven
# music8.ogg "Twister Tetris" by poinl, https://opengameart.org/content/twister-tetris
import copy
import random, sys
from random import randrange as rand
import pygame as pg
import os
from os import path, listdir

main_folder = path.dirname(__file__) #comment out when using pyinstaller hates this when packaging into an executable for some reason.
#main_folder = '' #uncomment out when using pyinstaller
game_folder = path.join(main_folder, 'assets')
snd_folder = path.join(game_folder, 'sounds')
music_folder = path.join(game_folder, 'music')

# The configuration
config = {
	'cell_size':	20,
	'cols':		10,
	'rows':		20,
	'delay':	750,
	'maxfps':	30
}

EFFECTS_SOUNDS = {'rotate': 'rotate.ogg', 'set': 'set.ogg', 'levelup': 'levelup.ogg', 'line': 'line.ogg', 'double': 'double.ogg', 'tripple': 'tripple.ogg', 'tetris': 'tetris.ogg'}

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 155, 0)
BLUE = (0, 0, 235)
INDIGO = (75, 0, 130)
VIOLET = (163, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIGHTBLUE = (0, 155, 155)
BROWN = (165,42,42)

FONT_NAME = 'arial'
TITLE = "tetris"

COLORS = [
BLACK,
RED,
YELLOW,
GREEN,
BLUE,
ORANGE,
VIOLET,
LIGHTBLUE,
MAGENTA,
INDIGO,
CYAN,
BROWN
]


# Define the shapes of the single parts
tetris_shapes = [
	[[0, 0, 0, 0],
	 [10, 10, 10, 10],
	 [0, 0, 0, 0]],

	[[2, 2],
	 [2, 2]],

	[[0, 0, 0],
	 [8, 8, 8],
	 [0, 8, 0]],
	
	[[0, 0, 0],
	 [0, 3, 3],
	 [3, 3, 0]],

	[[0, 0, 0],
	 [1, 1, 0],
	 [0, 1, 1]],

	[[4, 0, 0],
	 [4, 4, 4],
	 [0, 0, 0]],

	[[0, 0, 0],
	 [5, 5, 5],
	 [5, 0, 0]],

]

tetris_shape = [
	 [1, 1, 1, 0, 2, 2, 0, 3, 3, 3, 0, 4, 4, 0, 5, 0, 0, 6, 6],
	 [0, 1, 0, 0, 2, 0, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0],
	 [0, 1, 0, 0, 2, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0],
	 [0, 1, 0, 0, 2, 0, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 0, 6, 0],
	 [0, 1, 0, 0, 2, 2, 0, 0, 3, 0, 0, 4, 0, 0, 5, 0, 6, 6, 0]
]
def rotate_clockwise(shape):
	# Rotates shape counterclockwise three times to rotate it clockwise.
	for i in range(0, 3):
		shape = rotate_counterclockwise(shape)
	return shape

def rotate_counterclockwise(shape):
	return [[shape[y][x]
			 for y in range(len(shape))]
			for x in range(len(shape[0]) - 1, -1, -1)]

def vflip(shape):
	return [shape[y] for y in range(len(shape) - 1, -1, -1)]

def hflip(shape):
	new_shape = []
	height = len(shape)
	width = len(shape[0])
	for j in range(0, height):
		new_row = []
		for i in range(width - 1, -1, -1):
			new_row.append(shape[j][i])
		new_shape.append(new_row)
	return new_shape

def check_collision(board, boarder, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if (cell and board[ cy + off_y][ cx + off_x]) or (cell and boarder[ cy + off_y + 1][ cx + off_x + 1]):
					return True
			except IndexError:
				return True
	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in range(config['cols'])]] + board
	
def join_matrixes(board, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			try:
				board[cy+off_y-1][cx+off_x] += val
			except:
				pass
	return board

def new_board():
	board = [ [ 0 for x in range(config['cols']) ]
			for y in range(config['rows']) ]
	board += [[ 1 for x in range(config['cols'])]]
	return board

class tetrisApp(object):
	def __init__(self):
		pg.mixer.pre_init(44100, -16, 4, 2048) #reduces delay in sound playback.
		pg.init()
		pg.mixer.init()
		pg.key.set_repeat(250,25)
		self.font_name = pg.font.match_font(FONT_NAME)  # finds the closest match on computer
		self.width = config['cell_size']*config['cols']
		self.height = config['cell_size']*config['rows']
		self.next_stone = None
		os.environ['SDL_VIDEO_CENTERED'] = '1'
		self.flags = pg.SCALED  | pg.RESIZABLE
		self.screen = pg.display.set_mode((self.width + 102, self.height + 2), self.flags)
		pg.display.set_caption(TITLE)
		icon_image = pg.image.load(path.join(game_folder, 'tetris.png'))
		pg.display.set_icon(icon_image)
		self.play_surface = pg.Surface((self.width, self.height))
		self.next_surface = pg.Surface((99, 99))
		# Loads sound effects
		self.effects_sounds = {}
		for key in EFFECTS_SOUNDS:
			self.effects_sounds[key] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[key]))

		self.level = 0
		self.score = 0
		self.lines = 0
		self.lines_required = 0
		self.lines_left = 0

		self.music_list = []
		number_of_files = len([name for name in listdir(music_folder) if path.isfile(path.join(music_folder, name))])
		for i in range(0, number_of_files):
			filename = 'music{}.ogg'.format(i)
			song = path.join(music_folder, filename)
			self.music_list.append(song)
		self.current_song = 0

		self.title_surface = pg.Surface((self.width + 82, self.height + 2))
		self.title_surface.fill(BLACK)
		self.draw_text(self.title_surface, "Mutant Python Games", 12, GREEN, (self.width + 82) // 2, 125)
		self.draw_text(self.title_surface, "UP/R CTRL - Rotate", 16, WHITE, (self.width + 82) // 2, 170)
		self.draw_text(self.title_surface, "Move with arrow keys.", 16, WHITE, (self.width + 82) // 2, 200)
		self.draw_text(self.title_surface, "Remove rows by completing them", 18, BLUE, (self.width + 82) // 2, 233)
		self.draw_text(self.title_surface, "Gamepads Supported", 14, WHITE, (self.width + 82) // 2, 255)
		self.draw_text(self.title_surface, "Press any key/button to begin.", 16, ORANGE, (self.width + 82) // 2, 320)
		tetris_surface = self.draw_tetris_title()
		nov_rect = tetris_surface.get_rect()
		self.title_surface.blit(tetris_surface, ((self.width + 82)//2 - nov_rect.width//2, 50))
		self.screen.blit(self.title_surface, (10, 0))
		pg.display.flip()

		pg.joystick.init() # Initializes all joysticks/controllers
		joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]
		loop = True
		while loop:
			for event in pg.event.get():
				if event.type == pg.KEYDOWN:
					loop = False
				elif event.type == pg.QUIT:
					self.quit()
				elif event.type == pg.JOYBUTTONDOWN:
					if event.button in [0, 1, 2, 3, 6, 7, 8, 9, 10]:
						loop = False
					elif event.button in [8, 10]:
						self.quit()

		pg.event.set_blocked(pg.MOUSEMOTION) # We do not need
		                                             # mouse movement
		                                             # events, so we
		                                             # block them.
		self.init_game()

	def level_up(self, newgame = 0):
		global config
		if not newgame:
			self.level += 1
			#self.board = new_board()
			pg.mixer.music.stop()
			self.effects_sounds['levelup'].play()
			if self.level > 9:
				self.delay -= 20
			else:
				self.delay -= 60
			if self.delay < 50:
				self.delay = 50
			self.current_song += 1  # Changes song to next in list
			if self.current_song > len(self.music_list) - 1:
				self.current_song = 0
		self.lines = 0
		self.lines_required = self.lines_left = (self.level + 1) * 5
		song = self.music_list[self.current_song]
		pg.mixer.music.load(song)
		pg.mixer.music.play(loops=-1)

	def new_stone(self):
		global COLORS
		if self.next_stone != None:
			self.stone = self.next_stone
		else:
			selected_shape = copy.deepcopy(tetris_shapes[rand(len(tetris_shapes))])
			self.stone = selected_shape
		self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
		if sum(self.stone[0]):  # Makes sure stone appears on first line.
			self.stone_y = 0
		else:
			self.stone_y = -1

		next_selected_shape = copy.deepcopy(tetris_shapes[rand(len(tetris_shapes))])
		self.next_stone = next_selected_shape

		if check_collision(self.board, self.boarder, self.stone,(self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.flips = 0
		self.delay = config['delay']
		self.start_time = self.last_drop = pg.time.get_ticks()
		self.board = new_board()
		self.boarder = self.create_boarder()
		self.level = 0
		self.score = 0
		self.next_stone = None
		self.level_up(1)
		self.new_stone()

	def create_boarder(self):
		boarder = [] # creates a matrix of zeros the size of the board surrounded but padded with 1s to use for collision detection.
		for j in range(0, len(self.board) + 2):
			new_row = []
			for i in range(0, len(self.board[0]) + 2):
				if (j in [0, len(self.board)+1]) or (i in [0, len(self.board[0])+1]):
					val = 1
				else:
					val = 0
				new_row.append(val)
			boarder.append(new_row)
		return boarder

	def center_msg(self, msg):
		self.draw_text(self.play_surface, msg,12,WHITE, self.width // 2, self.height // 2)

	def draw_text(self, surface, text, size, color, x, y, align='midtop'):
		font = pg.font.Font(self.font_name, size)
		text_surface = font.render(text, True, color)
		text_rect = text_surface.get_rect()
		if align == 'midtop':
			text_rect.midtop = (x, y)
		if align == 'midleft':
			text_rect.midleft = (x, y)
		surface.blit(text_surface, text_rect)

	def draw_tetris_title(self):
		global tetris_shape
		surface = pg.Surface((266, 70))
		matrix = tetris_shape
		cell_size = 14
		off_x, off_y = (0, 0)
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pg.draw.rect(
						surface,
						COLORS[val],
						pg.Rect(
							x * cell_size + off_x,
							y * cell_size + off_y,
							cell_size + off_x,
							cell_size + off_y), 0)
					pg.draw.rect(
						surface,
						self.get_border_color(val),
						pg.Rect(
							x * cell_size + off_x,
							y * cell_size + off_y,
							cell_size + off_x,
							cell_size + off_y), 1)
					pg.draw.rect(
						surface,
						self.get_border_color(val, 30),
						pg.Rect(
							x * cell_size + off_x + 4,
							y * cell_size + off_y + 4,
							cell_size + off_x - 5,
							cell_size + off_y - 5), 0)
		return(surface)

	def draw_matrix(self, matrix, offset, next_surf = 0, surface = None):
		off_x, off_y  = offset
		if surface == None:
			surface = self.play_surface
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					if next_surf == 0:
						pg.draw.rect(
							surface,
							COLORS[val],
							pg.Rect(
								(off_x+x) *
								  config['cell_size'],
								(off_y+y) *
								  config['cell_size'],
								config['cell_size'],
								config['cell_size']),0)
						pg.draw.rect(
							surface,
							self.get_border_color(val),
							pg.Rect(
								(off_x+x) *
								  config['cell_size'],
								(off_y+y) *
								  config['cell_size'],
								config['cell_size'],
								config['cell_size']),1)

						pg.draw.rect(
							surface,
							self.get_border_color(val, 30),
							pg.Rect(
								(off_x+x) *
								  config['cell_size']+4,
								(off_y+y) *
								  config['cell_size']+4,
								config['cell_size']-5,
								config['cell_size']-5),0)
					else: # Used for drawing next piece up.
						pg.draw.rect(
							self.next_surface,
							COLORS[val],
							pg.Rect(
								x*config['cell_size'] + off_x,
								y*config['cell_size'] + off_y,
								config['cell_size'],
								config['cell_size']),0)
						pg.draw.rect(
							self.next_surface,
							self.get_border_color(val),
							pg.Rect(
								x*config['cell_size'] + off_x,
								y*config['cell_size'] + off_y,
								config['cell_size'],
								config['cell_size']),1)
						pg.draw.rect(
							self.next_surface,
							self.get_border_color(val, 30),
							pg.Rect(
								x*config['cell_size'] + off_x + 4,
								y*config['cell_size'] + off_y + 4,
								config['cell_size'] - 5,
								config['cell_size'] - 5),0)

	def get_border_color(self, val, coldelta = 50):
		bordercolor = [0, 0, 0]
		bordercolor[0] = COLORS[val][0] - coldelta
		if bordercolor[0] < 0: bordercolor[0] = 0
		elif bordercolor[0] > 255: bordercolor[0] = 255
		bordercolor[1] = COLORS[val][1] - coldelta
		if bordercolor[1] < 0: bordercolor[1] = 0
		elif bordercolor[1] > 255: bordercolor[1] = 255
		bordercolor[2] = COLORS[val][2] - coldelta
		if bordercolor[2] < 0: bordercolor[2] = 0
		elif bordercolor[2] > 255: bordercolor[2] = 255
		return bordercolor

	def tetris_animation(self, row):
		animatrix = []
		val = 1
		for j in range(0, 4):
			a_row = []
			for i in range(0, config['cols']): # Makes a matrix of zeros to later fill with colors.
				a_row.append(0)
			animatrix.append(a_row)

		offset = int(len(animatrix[0])/2)
		for i in range(0, offset):
			for j in range(0, 4):
				rand_color1 = random.randrange(1, len(COLORS))
				rand_color2 = random.randrange(1, len(COLORS))
				animatrix[j][i + offset] = rand_color1
				animatrix[j][offset - i - 1] = rand_color2
			nov_surface = pg.Surface((self.width, config['cell_size'] * 4))
			self.draw_matrix(animatrix, (0, 0), 0, nov_surface)
			self.screen.blit(self.play_surface, (1, 1))
			self.screen.blit(nov_surface, (1, int(row * config['cell_size']) + 1))
			pg.display.update()
			self.clock.tick(config['maxfps'])

	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if not check_collision(self.board, self.boarder, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pg.display.update()
		sys.exit()

	def insta_fall(self):
		if not self.gameover and not self.paused:
			while not check_collision(self.board, self.boarder, self.stone, (self.stone_x, self.stone_y)):
				self.stone_y += 1
		self.stone_y -= 1
		self.drop

	def drop(self):
		if not self.gameover and not self.paused:
			self.stone_y += 1
			if check_collision(self.board, self.boarder, self.stone, (self.stone_x, self.stone_y)):
				self.effects_sounds['set'].play()
				self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				rows_removed = 0
				prevy = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							if prevy == 0:
								prevy = i
							self.board = remove_row(
							  self.board, i)
							rows_removed += 1
							self.lines += 1
							break
					else:
						break

				if rows_removed == 1:
					self.score += 40 * (self.level + 1)
					self.effects_sounds['line'].play()
				elif rows_removed == 2:
					self.score += 100 * (self.level + 1)
					self.effects_sounds['double'].play()
					self.lines += 1
				elif rows_removed == 3:
					self.score += 300 * (self.level + 1)
					self.effects_sounds['tripple'].play()
					self.lines += 2
				elif rows_removed > 3:
					self.score += 1200 * (self.level + 1)
					self.effects_sounds['tetris'].play()
					self.lines += 4
					self.tetris_animation(prevy)

				self.lines_left = self.lines_required - self.lines
				if self.lines_left < 0:
					self.lines_left = 0
				if self.lines_left <= 0:
					self.level_up()

	def rotate_stone(self, orientation):
		if not self.gameover and not self.paused:
			self.effects_sounds['rotate'].play()
			if orientation == 1:
				new_stone = rotate_counterclockwise(self.stone)
			elif orientation == 2:
				self.flips += 1
				new_stone = hflip(self.stone)
			elif orientation == 3:
				self.flips += 1
				new_stone = vflip(self.stone)
			else:
				new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board, self.boarder, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone

	def toggle_pause(self):
		now = pg.time.get_ticks()
		if now - self.start_time > 500:
			if not self.gameover:
				self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False

	def draw(self):
		self.screen.fill(BLACK)
		pg.draw.rect(self.screen, WHITE, (0, 0, self.width + 2, self.height + 2), 1)
		self.next_surface.fill(BLACK)
		pg.draw.rect(self.next_surface, WHITE, (0, 0, 84, 84), 1)
		self.draw_matrix(self.next_stone,(2, 2), 1)
		self.screen.blit(self.play_surface, (1, 1))
		self.draw_text(self.screen, "Score:", 20, WHITE, self.width + 50, 10)
		self.draw_text(self.screen, str(self.score), 14, WHITE, self.width + 50, 30)
		self.draw_text(self.screen, "Level:", 20, WHITE, self.width + 50, 50)
		self.draw_text(self.screen, str(self.level), 20, WHITE, self.width + 50, 70)
		self.draw_text(self.screen, "Lines Left", 16, WHITE, self.width + 50, 110)
		self.draw_text(self.screen, str(self.lines_left), 20, WHITE, self.width + 50, 142)
		pg.draw.rect(self.screen, WHITE, (self.width + 17, 130, 68, 50), 1)
		self.draw_text(self.screen, "Next", 20, WHITE, self.width + 50, 250)
		#self.draw_text(self.screen, "Flips: " + str(self.flips), 20, WHITE, self.width + 50, 190)
		self.screen.blit(self.next_surface, (self.width + 10, 275))
		pg.display.update()
	
	def run(self):
		self.gameover = False
		self.paused = False
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'UP': lambda: self.rotate_stone(1),
			'RCTRL': lambda: self.rotate_stone(0),
			'DOWN':		self.drop,
			'p':		self.toggle_pause,
			'SPACE':	lambda:self.insta_fall(),
			'a': 		lambda:self.rotate_stone(1),
			'd': 		lambda:self.rotate_stone(0),
		}

		pg.joystick.init() # Initializes all joysticks/controllers
		joysticks = [pg.joystick.Joystick(x) for x in range(pg.joystick.get_count())]

		#pg.time.set_timer(pg.USEREVENT+1, self.delay)
		self.clock = pg.time.Clock()
		last_move = 0
		move_delay = 50 # Makes the dpad move in steps
		while 1:
			self.play_surface.fill((0,0,0))
			if self.gameover:
				self.center_msg("Game Over! Press space/start to continue")
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
					                 (self.stone_x,
					                  self.stone_y))
			self.draw()

			now = pg.time.get_ticks()
			if (now - self.last_drop) > self.delay:
				self.drop()
				self.last_drop = pg.time.get_ticks()

			# gets state of hat for moving blocks.
			if pg.joystick.get_init:
				if len(joysticks) > 0:
					hat_state = joysticks[0].get_hat(0)
					ora = pg.time.get_ticks()
					if (ora - last_move) > move_delay:
						if hat_state == (1, 0):
							self.move(+1)
							last_move = pg.time.get_ticks()
						elif hat_state == (-1, 0):
							self.move(-1)
							last_move = pg.time.get_ticks()
					if hat_state == (0, -1):
						self.drop()

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.quit()
				elif event.type == pg.JOYBUTTONDOWN:
					if event.button == 0:
						self.rotate_stone(0)
					elif event.button == 1:
						self.rotate_stone(3)
					elif event.button == 5:
						self.insta_fall()
					elif event.button == 2:
						self.rotate_stone(1)
					elif event.button == 3:
						self.rotate_stone(2)
					elif event.button in [7, 9]:
						self.toggle_pause()
						self.start_game()
					elif event.button in [8, 10]:
						self.quit()
				elif event.type == pg.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pg.K_"
						+key):
							key_actions[key]()
					if (event.key == pg.K_SPACE) and self.gameover:
						self.start_game()


			self.clock.tick(config['maxfps'])

if __name__ == '__main__':
	App = tetrisApp()
	App.run()

STONE_TO_NUM = {
    "❶": 1, "❷": 2, "❸": 3, "❹": 4, "❺": 5,
    "❻": 6, "❼": 7, "❽": 8, "❾": 9, "❿": 10,
    "⓫": 11, "⓬": 12, "⓭": 13, "⓮": 14, "⓯": 15,
    "⓰": 16, "⓱": 17, "⓲": 18, "⓳": 19, "⓴": 20,
    "①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5,
    "⑥": 6, "⑦": 7, "⑧": 8, "⑨": 9, "⑩": 10,
    "⑪": 11, "⑫": 12, "⑬": 13, "⑭": 14, "⑮": 15,
    "⑯": 16, "⑰": 17, "⑱": 18, "⑲": 19, "⑳": 20
}
BLACK_STONES = "@❶❷❸❹❺❻❼❽❾❿⓫⓬⓭⓮⓯⓰⓱⓲⓳⓴"
WHITE_STONES = "!①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"

DRAW_MARK_WITH_FULL_SOLUTION = False

class GoGame:
	def __init__(self, lines: list, default_to_play: str):
		self.width = len(lines[0])
		self.height = len(lines)
		
		# y, x -> x, y
		self.board = [[0 for _ in range(self.height)] for _ in range(self.width)]

		self._solution_nums = []

		for y, line in enumerate(lines):
			for x, c in enumerate(line):
				if c == "@":
					self.board[x][y] = 1
				elif c == "!":
					self.board[x][y] = -1
				elif c == "X":
					self._solution_nums.append(((x, y), 1))
				elif c in "123456789":
					self._solution_nums.append(((x, y), int(c)))
				elif c in BLACK_STONES[1:]:
					self.board[x][y] = 1
					self._solution_nums.append(((x, y), STONE_TO_NUM[c]))
				elif c in WHITE_STONES[1:]:
					self.board[x][y] = -1
					self._solution_nums.append(((x, y), STONE_TO_NUM[c]))


		self._solution_nums.sort(key=lambda x: x[1])

		if len(self._solution_nums) == 0:
			return

		black_is_solving = default_to_play == "black"
		for point, move_num in self._solution_nums:
			is_black = (
				(black_is_solving and move_num % 2 == 1)
				or (not black_is_solving and move_num % 2 == 0)
			)
			self.play_stone(point, is_black, black_is_solving)


	def to_lines(self):
		lines = []
		for y in range(self.height):
			line = ""
			for x in range(self.width):
				num = self.board[x][y]
				if num == 0:
					line += "+"
				elif num == 1:
					line += "@"
				else:
					line += "!"
			lines.append(line)

		def num_str(move_num: int, below_num: int):
			if move_num <= 1 and DRAW_MARK_WITH_FULL_SOLUTION:
				return "X"
			if below_num == 1:
				return BLACK_STONES[move_num]
			if below_num == -1:
				return WHITE_STONES[move_num]

			return str(move_num)

		for point, move_num in self._solution_nums:
			x, y = point
			line = lines[y]
			below_num = self.board[x][y]
			if len(self._solution_nums) > 1:
				char = num_str(move_num, below_num)
			else:
				char = "X"
			line = line[:x] + char + line[x+1: ] 
			lines[y] = line

		return lines

	def _north(self, p: tuple):
		return (p[0], p[1] - 1) if p[1] - 1 >= 0 else None

	def _south(self, p: tuple):
		return (p[0], p[1] + 1) if p[1] + 1 < self.height else None

	def _east(self, p: tuple):
		return (p[0] + 1, p[1]) if p[0] + 1 < self.width else None

	def _west(self, p: tuple):
		return (p[0] - 1, p[1]) if p[0] - 1 >= 0 else None

	def _orthos_of(self, p: tuple):
		orthos = [self._north(p), self._south(p), self._east(p), self._west(p)]
		return [o for o in orthos if o is not None]

	def _select_group(self, group_list: list, point: tuple):
		group_list.append(point)
		x, y = point
		color = self.board[x][y]
		orthos = self._orthos_of(point)
		for x, y in orthos:
			if self.board[x][y] == color and (x, y) not in group_list:
				self._select_group(group_list, (x, y))

	def _count_liberties(self, group: list):
		liberties = []
		for x, y in group:
			orthos = self._orthos_of((x, y))
			for o_x, o_y in orthos:
				if self.board[o_x][o_y] == 0 and (o_x, o_y) not in liberties:
					liberties.append((o_x, o_y))
		return len(liberties)

	def _remove_surrounded_groups(self, point: tuple, was_black: bool):
		orthos = self._orthos_of(point)
		
		opp = -1 if was_black else 1
		opposing_orthos = [(x, y) for x, y in orthos if self.board[x][y] == opp]
		opposing_groups = []

		for opposing in opposing_orthos:
			if not any(opposing in group for group in opposing_groups):
				opposing_groups.append([])
				self._select_group(opposing_groups[-1], opposing)

		for group in opposing_groups:
			if self._count_liberties(group) == 0:
				for x, y in group:
					self.board[x][y] = 0

	def play_stone(
		self,
		point: tuple,
		is_black: bool,
		black_is_solving: bool,
	):
		x, y = point
		self.board[x][y] = 1 if is_black else -1
		self._remove_surrounded_groups(point, is_black)

def give_resulting_board(lines: list, default_to_play: str):
	game = GoGame(lines, default_to_play)
	return game.to_lines()
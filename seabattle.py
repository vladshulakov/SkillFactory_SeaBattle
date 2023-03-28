from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за доску'
    
class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f'({self.x}, {self.y})'
    
class Ship:
    def __init__(self, length, nose, hv):
        self.length = length
        self.nose = nose
        self.hv = hv
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            if self.hv == 0:
                ship_dots.append(Dot(self.nose.x + i, self.nose.y))
            elif self.hv == 1:
                ship_dots.append(Dot(self.nose.x, self.nose.y + i))
        return ship_dots

class Board:
    def __init__(self, size, hid, alive):
        self.size = size
        self.hid = hid
        self.alive = alive
        self.field = [[' '] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        result = '   | ' + ' | '.join([str(i + 1) for i in range(self.size)]) + ' |'
        for x, y in enumerate(self.field):
            result += '\n' + '-' * 28
            result += f'\n {chr(x + 65)} | ' + ' | '.join(y) + ' |'
        if self.hid:
            result = result.replace('■', ' ')
        return result
    
    def add_ship(self, ship):
        for cord in ship.dots:
            if self.out(cord) or cord in self.busy:
                raise BoardWrongShipException()
        for cord in ship.dots:
            self.field[cord.x][cord.y] = '■'
            self.busy.append(cord)
            
        self.ships.append(ship)
        self.contour(ship)
    
    def contour(self, ship, visible = False):
        c = ((-1, -1), (-1, 0) , (-1, 1), (0, -1), (0, 0) , (0 , 1), (1, -1), (1, 0) , (1, 1))
        for cord in ship.dots:
            for x, y in c:
                d = Dot(x + cord.x, y + cord.y)
                if not(self.out(d)) and d not in self.busy:
                    if visible:
                        self.field[d.x][d.y] = '.'
                    self.busy.append(d)

    def out(self, cord):
        return not((0<= cord.x < self.size) and (0<= cord.y < self.size))
    
    def shot(self, cord):
        if self.out(cord):
            raise BoardOutException()
        if cord in self.busy:
            raise BoardUsedException()
        
        self.busy.append(cord)

        for ship in self.ships:
            if cord in ship.dots:
                ship.lives -= 1
                self.field[cord.x][cord.y] = 'X'
                if ship.lives == 0:
                    self.alive -= 1
                    self.contour(ship, visible = True)
                    print('Корабль уничтожен')
                    return False
                else:
                    print('Корабль ранен')
                    return True
                
        self.field[cord.x][cord.y] = '.'
        print('Мимо')
        return False
    
    def game_start(self):
        self.busy = []

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                repeat = self.enemy.shot(self.ask())
                return repeat
            except BoardException as err:
                print(err)     

class AI(Player):
    def ask(self):
        cord = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {cord.x + 1} {cord.y + 1}')
        return cord

class User(Player):
    def ask(self):
        while True:
            cords = sorted(input('Ваш ход, введите координаты: ').split())
            
            if len(cords) != 2:
                print('Введите 2 координаты')
                continue
            
            y, x = cords
            
            if not(y.isdigit()) or x.upper() not in 'ABCDEF':
                print('Некорректный ввод')
                continue
            
            x, y = ord(x.upper()) - 65, int(y)
            
            return Dot(x, y-1)

class Game:
    def try_board(self):
        ships = (3, 2, 2, 1, 1, 1, 1)
        board = Board(6, False, len(ships))
        at = 0
        for i in ships:
            while True:
                at += 1
                if at > 3000:
                    return None
                ship = Ship(i, Dot(randint(0, 5), randint(0, 5)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.game_start()
        return board
    
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board
    
    def __init__(self, size = 6):
        self.size = size
        player = self.random_board()
        comp = self.random_board()
        comp.hid = True

        self.ai = AI(comp, player)
        self.user = User(player, comp)

    def greet(self):
        print('--------------------')
        print('   Приветсвуем вас  ')
        print('       в игре       ')
        print('     морской бой    ')
        print('--------------------')
        print('    формат ввода:   ')
        print(' английская буква и ')
        print('  цифра от 1 до 6   ')
        print('    через пробел    ')
        print('--------------------')

    def loop(self):
        num = 0
        while True:
            print('Доска пользователя: \n')
            print(self.user.board, '\n')
            print('Доска компьютера: \n')
            print(self.ai.board, '\n')
            if num % 2 == 0:
                print('Ходит пользователь')
                repeat = self.user.move()
            else:
                print('Ходит компьютер')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.user.board.alive == 0:
                print('Игра окончена\n Выиграл компьютер')
                break
            if self.ai.board.alive == 0:
                print('Игра окончена\n Выиграл пользователь')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()

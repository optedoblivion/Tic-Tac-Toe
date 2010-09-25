from django.template import Context, loader
from django.http import HttpResponse
from simplejson import JSONEncoder
import random

EMPTY = " "
HUMAN = "x"
COMP = "o"

def allEqual(list):
    """
        Returns True if all the elements in a list are equal, or if the list is empty.
    """
    return not list or list == [list[0]] * len(list)

class Board:

    """
        Game Board Object
    """

    PIECE_COUNT = 9

    def __init__(self):
        self.pieces = [EMPTY]*9
        self.field_names = "123456789"

    def getValidMoves(self):
        """
            @return: List of valid moves
            @rtype: C{List}
        """
        return [p for p in range(self.PIECE_COUNT) if self.pieces[p] == EMPTY]

    def hasWinner(self):
        """
            Determines if a winner exists.

            @return: Player or None
            @rtype: C{String}
        """
        winning_rows = (
                            (0,1,2),(3,4,5),(6,7,8), 
                            (0,3,6),(1,4,7),(2,5,8),
                            (0,4,8),(2,4,6)
                        )
        for row in winning_rows:
            if self.pieces[row[0]] != EMPTY and allEqual([self.pieces[i] for i in row]):
                return self.pieces[row[0]]

    def gameOver(self):
        """
            Returns True if winning player or no moves.

            @return: True or False
            @rtype: C{Boolean}
        """
        return self.hasWinner() or not self.getValidMoves()

    def makeMove(self, move, player):
        """
            Plays a move on the board.

            @attention: Does not check for legality of move.

            @param move: Index number of board piece
            @type move: C{int}
        """
        self.pieces[move] = player

    def undoMove(self, move):
        """
            Undoes a move

            @param move: index of tile to clear
            @type move: C{int}
        """
        self.makeMove(move, EMPTY)

    def getMoveName(self, move):
        """
            @param move: index position of tile
            @type move: C{int}

            @return: Name for a move
            @rtype: C{int}
        """
        return self.field_names[move]

def index(request):
    t = loader.get_template("tictactoe/index.html")
    request.session["board"] = Board()
    c = Context()
    return HttpResponse(t.render(c))

def makeHumanMove(request):
    move = request.GET.get("move", -1)
    move = int(move)
    ret = {}
    if move > 8 or move < 0:
        ret["success"] = False
        ret["data"] = "Invalid Move Value!"
        return HttpResponse(JSONEncoder().encode(ret))
    board = request.session["board"]
    possible_moves = board.getValidMoves()
    if move not in possible_moves:
        ret["success"] = False
        ret["data"] = "Move not allowed!"
        return HttpResponse(JSONEncoder().encode(ret))
    board.makeMove(move, HUMAN)
    request.session["board"] = board
    ret["success"] = True
    ret["data"] = board.gameOver()
    ret["winner"] = board.hasWinner()
    return HttpResponse(JSONEncoder().encode(ret))

def makeComputerMove(request):
    ## Grab board from session
    board = request.session["board"]
    ## Needed to map opponent for makeing generator
    opponent = {COMP: HUMAN, HUMAN: COMP}

    def judge(winner):
        if winner == COMP:
            return +1
        if winner == None:
            return 0
        return -1

    def evaluateMove(move, p=COMP):
        try:
            board.makeMove(move, p)
            if board.gameOver():
                return judge(board.hasWinner())

            ## Create a generator and do some recursion magic to make an iterable object
            ## that we can determine the winner from
            outcomes = (evaluateMove(next_move, opponent[p]) for next_move in board.getValidMoves())

            ## If the player is the computer
            if p == COMP:
                min_element = 1
                for o in outcomes:
                    if o == -1:
                        return o
                    min_element = min(o,min_element)
                return min_element
            ## If the player is human
            else:
                max_element = -1
                for o in outcomes:
                    if o == +1:
                        return o
                    max_element = max(o,max_element)
            return max_element

        finally:
            board.undoMove(move)

    moves = [(move, evaluateMove(move)) for move in board.getValidMoves()]
    random.shuffle(moves)
    moves.sort(key = lambda (move, winner): winner)
    compMove = moves[-1][0]
    board.makeMove(compMove, COMP)
    request.session["board"] = board
    ret = {}
    ret["success"] = True
    ret["data"] = compMove
    ret["winner"] = board.gameOver()
    return HttpResponse(JSONEncoder().encode(ret))




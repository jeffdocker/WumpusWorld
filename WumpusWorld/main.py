
#requires pygame, use pip install pygame

import pygame
import sys
import random
import time
import math
from queue import PriorityQueue
from constants import *

#possible player moves used to display yellow circles as a list [(r1,c1),(r2,c2)...]
player_possible_moves = []
#currently clicked player piece
selected_player_piece = ()

#lists of positions of player and enemy pieces as [(r1,c1),(r2,c2)...]
player_pieces = []
enemy_pieces = []

class move_made:
    def __init__(self,move,value):
        self.move = move
        self.value = value
    def __lt__(self, other):
        return self.value < other.value

class cell:
    def __init__(self,type,owner):
        #empty = "empty", hero = "hero" ...
        self.type = type
        #unowned = "none", player piece = "player", enemy piece = "enemy"
        self.owner = owner

WINDOW = 0

def h(board,n,h_func):
    if(h_func == 0):
        ep = []
        pp = []
        update_pieces(board,n,pp,ep)
        return len(ep)-len(pp)

    if(h_func == 1):
        ep = []
        pp = []
        distance = 0
        update_pieces(board,n,pp,ep)
        for enemy_piece in ep:
            for player_piece in pp:
                distance += math.sqrt(math.pow(abs(enemy_piece[0]-player_piece[0]),2)+math.pow(abs(enemy_piece[1]-player_piece[1]),2))
        return distance

    if(h_func == 2):
        ep = []
        pp = []
        distance = 0
        update_pieces(board,n,pp,ep)
        for enemy_piece in ep:
            for player_piece in pp:

                if((board[enemy_piece[0]][enemy_piece[1]].type == "hero" and board[player_piece[0]][player_piece[1]].type == "wumpus") or (board[enemy_piece[0]][enemy_piece[1]].type == "mage" and board[player_piece[0]][player_piece[1]].type == "hero") or (board[enemy_piece[0]][enemy_piece[1]].type == "wumpus" and board[player_piece[0]][player_piece[1]].type == "mage")):

                    distance += (2*(math.sqrt(math.pow(abs(enemy_piece[0]-player_piece[0]),2)+math.pow(abs(enemy_piece[1]-player_piece[1]),2))))
                    return distance

                elif((board[enemy_piece[0]][enemy_piece[1]].type == "wumpus" and board[player_piece[0]][player_piece[1]].type == "hero") or (board[enemy_piece[0]][enemy_piece[1]].type == "hero" and board[player_piece[0]][player_piece[1]].type == "mage") or (board[enemy_piece[0]][enemy_piece[1]].type == "mage" and board[player_piece[0]][player_piece[1]].type == "wumpus")):

                    distance += (.5*(math.sqrt(math.pow(abs(enemy_piece[0]-player_piece[0]),2)+math.pow(abs(enemy_piece[1]-player_piece[1]),2))))
                    return distance
                else:
                    distance += (math.sqrt(math.pow(abs(enemy_piece[0]-player_piece[0]),2)+math.pow(abs(enemy_piece[1]-player_piece[1]),2)))
                    return distance
        return distance

    if (h_func == 3):
        ai_heroes = 0
        ai_mages = 0
        ai_wumpuses = 0
        player_heroes = 0
        player_mages = 0
        player_wumpuses = 0

        for r in range(0, n):
            for c in range(0, n):
                if board[r][c].owner == "enemy":
                    if board[r][c].type == "hero":
                        ai_heroes += 1
                    elif board[r][c].type == "mage":
                        ai_mages += 1
                    else:
                        ai_wumpuses += 1
                elif board[r][c].owner == "player":
                    if board[r][c].type == "hero":
                        player_heroes += 1
                    elif board[r][c].type == "mage":
                        player_mages += 1
                    else:
                        player_wumpuses += 1

        return (ai_heroes - player_wumpuses) + (ai_mages - player_heroes) + (ai_wumpuses - player_mages)

    if(h_func == 4):
        ep = []
        pp = []
        win_loss = 0
        update_pieces(board,n,pp,ep)
        for player_piece in pp:
            player_piece_moves = get_possible_moves(player_piece[0], player_piece[1], board, n)
            for move in player_piece_moves:
                if board[move[0]][move[1]].owner == "enemy":
                    enemy_piece_type = board[move[0]][move[1]].type
                    player_piece_type = board[player_piece[0]][player_piece[1]].type
                    # if here, player can move to a location with an enemy piece- by definition, enemy can move to 
                    # location with a player piece on their next turn

                    # hero > wumpus, wumpus > mage, mage > hero
                    if player_piece_type == "hero" and enemy_piece_type == "wumpus":
                        win_loss -= 1
                    elif player_piece_type == "wumpus" and enemy_piece_type == "mage":
                        win_loss -= 1
                    elif player_piece_type == "mage" and enemy_piece_type == "hero":
                        win_loss -= 1
                    elif enemy_piece_type == "hero" and player_piece_type == "wumpus":
                        win_loss += 1
                    elif enemy_piece_type == "wumpus" and player_piece_type == "mage":
                        win_loss += 1
                    elif enemy_piece_type == "mage" and player_piece_type == "hero":
                        win_loss += 1
                    # if none of these, player_piece_type and enemy_piece_type must be the same, do nothing
        return win_loss


#update player_pieces and enemy_pieces
def update_pieces(board,n,player_pieces,enemy_pieces):

    player_pieces.clear()
    enemy_pieces.clear()

    for r in range(0,n):
        for c in range(0,n):
            if board[r][c].owner == "player":
                player_pieces.append((r,c))
            elif board[r][c].owner == "enemy":
                enemy_pieces.append((r,c))


def alphabeta(board,moves,depth,alpha,beta,maxPlayer,n,h_func):
    #if at depth 0, return heuristic value and current moves made
    if (depth == 0):
        return (h(board,n,0),moves)
    #copy board state and make all moves listed to get current state
    new_board = [[None for x in range(0,n)] for y in range(0,n)]
    player_pieces = []
    enemy_pieces = []
    for r in range(0,n):
        for c in range(0,n):
            new_board[r][c] = board[r][c]
    for move in moves:
        make_move(move[0],move[1],move[2],move[3],new_board)
    update_pieces(new_board,n,player_pieces,enemy_pieces)
    #if after making all moves, no enemy or no player pieces, end
    if(len(player_pieces)==0 or len(enemy_pieces)==0):
        return (h(board,n,0), moves)
    if (maxPlayer):
        prioqueue = PriorityQueue()
        value = -1*float("inf")
        #iterate over evey possible move for each exisitng piece
        for ep in enemy_pieces:
            ep_possible_moves = get_possible_moves(ep[0],ep[1],new_board,n)
            for ep_move in ep_possible_moves:
                #make move and save it along with value of heurisitc after making it
                state_ep = new_board[ep[0]][ep[1]]
                state_ep_move = new_board[ep_move[0]][ep_move[1]]
                make_move(ep[0],ep[1],ep_move[0],ep_move[1],new_board)
                pq_value = -1*h(new_board, n, h_func)
                new_board[ep[0]][ep[1]] = state_ep
                new_board[ep_move[0]][ep_move[1]] = state_ep_move
                prioqueue.put(move_made((ep[0],ep[1],ep_move[0],ep_move[1]),pq_value))
        if prioqueue.empty():
            return (h(new_board,n, 0), moves)
        ret_moves = moves
        while not prioqueue.empty():
            #take moves off of pq, run alphabeta on each using current moves with new move appended
            child = prioqueue.get()
            new_moves = moves.copy()
            new_moves.append(child.move)
            ret_alpha_beta = alphabeta(new_board,new_moves,depth-1,alpha,beta,False,n,h_func)
            #if value is reset, reset the move list that goes along with it
            if value < ret_alpha_beta[0]:
                value = ret_alpha_beta[0]
                ret_moves = ret_alpha_beta[1]
            alpha = max(alpha,value)
            if alpha >= beta:
                break
        return (value,ret_moves)
    else:
        #same thing but minimizing for player
        prioqueue = PriorityQueue()
        value = float("inf")
        for pp in player_pieces:
            pp_possible_moves = get_possible_moves(pp[0],pp[1],new_board,n)
            for pp_move in pp_possible_moves:
                state_pp = new_board[pp[0]][pp[1]]
                state_pp_move = new_board[pp_move[0]][pp_move[1]]
                make_move(pp[0],pp[1],pp_move[0],pp_move[1],new_board)
                pq_value = h(new_board, n, h_func)
                new_board[pp[0]][pp[1]] = state_pp
                new_board[pp_move[0]][pp_move[1]] = state_pp_move
                prioqueue.put(move_made((pp[0],pp[1],pp_move[0],pp_move[1]),pq_value))
        if prioqueue.empty():
            return (h(new_board,n, 0), moves)
        ret_moves = moves
        while not prioqueue.empty():
            child = prioqueue.get()
            new_moves = moves.copy()
            new_moves.append(child.move)
            ret_alpha_beta = alphabeta(new_board,new_moves,depth-1,alpha,beta,True,n,h_func)
            if value > ret_alpha_beta[0]:
                value = ret_alpha_beta[0]
                ret_moves = ret_alpha_beta[1]
            beta = min(beta,value)
            if alpha >= beta:
                break
        return (value,ret_moves)


#get possible moves for a single piece, returns list of positions [(r1,c1),(r2,c2)...]
def get_possible_moves(row,col,board,n):
    is_player = (board[row][col].owner == "player")
    possible_moves = []
    for y in range(-1,2):
        for x in range(-1,2):
            if (-1 < y+row < n) and (-1 < x+col < n) and is_player and (board[y+row][x+col].owner != "player"):
                possible_moves.append((y+row,x+col))
            elif (-1 < y+row < n) and (-1 < x+col < n) and not is_player and (board[y+row][x+col].owner != "enemy"):
                possible_moves.append((y+row,x+col))
    return possible_moves

#update board based on move of (old_row,old_col) to (new_row,new_col)
def make_move(old_row,old_col,new_row,new_col,board):

    if board[new_row][new_col].type == "empty":
        board[new_row][new_col] = board[old_row][old_col]
        board[old_row][old_col] = cell("empty","none")
    elif board[new_row][new_col].type =="pit":
        board[old_row][old_col] = cell("empty", "none")
    elif board[new_row][new_col].type == board[old_row][old_col].type:
        board[old_row][old_col] = cell("empty", "none")
        board[new_row][new_col] = cell("empty", "none")
    elif board[old_row][old_col].type == "hero":
        if board[new_row][new_col].type == "wumpus":
            board[new_row][new_col] = board[old_row][old_col]
            board[old_row][old_col] = cell("empty","none")
        elif board[new_row][new_col].type == "mage":
            board[old_row][old_col] = cell("empty", "none")
    elif board[old_row][old_col].type == "mage":
        if board[new_row][new_col].type == "hero":
            board[new_row][new_col] = board[old_row][old_col]
            board[old_row][old_col] = cell("empty","none")
        elif board[new_row][new_col].type == "wumpus":
            board[old_row][old_col] = cell("empty", "none")
    elif board[old_row][old_col].type == "wumpus":
        if board[new_row][new_col].type == "mage":
            board[new_row][new_col] = board[old_row][old_col]
            board[old_row][old_col] = cell("empty","none")
        elif board[new_row][new_col].type == "hero":
            board[old_row][old_col] = cell("empty", "none")

def draw_end(win,end_state):
    win.fill((236, 250, 0))
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 30)

    if(end_state==-1):
        textsurface = myfont.render('You suck >:(', False, (255, 0, 0))
        textsurface1 = myfont.render('You are actually a bot', False, (255, 0, 0))
        textsurface2 = myfont.render('You lost to a poorly coded machine', False, (255, 0, 0))
        textsurface3 = myfont.render('gg', False, (255, 0, 0))
        win.blit(textsurface, (20, 0))
        win.blit(textsurface1, (20, 120))
        win.blit(textsurface2, (20, 260))
        win.blit(textsurface3, (20, 380))
    elif(end_state==0):
        textsurface = myfont.render('Draw :/ gg', False, (255, 0, 0))
        win.blit(textsurface, (20, 0))
    else:
        textsurface = myfont.render('You Win :) gg', False, (255, 0, 0))
        win.blit(textsurface, (20, 0))

#color in board
def draw_board(win,board,square_size,n):
    win.fill((255,255,255))
    for r in range(0,n):
        for c in range(0,n):
            if (board[r][c]).type == "empty":
                pygame.draw.rect(win,empty,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "pit":
                pygame.draw.rect(win,pit,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "hero" and (board[r][c]).owner == "player":
                pygame.draw.rect(win,player_hero,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "mage" and (board[r][c]).owner == "player":
                pygame.draw.rect(win,player_mage,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "wumpus" and (board[r][c]).owner == "player":
                pygame.draw.rect(win,player_wumpus,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "hero" and (board[r][c]).owner == "enemy":
                pygame.draw.rect(win,enemy_hero,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "mage" and (board[r][c]).owner == "enemy":
                pygame.draw.rect(win,enemy_mage,(c*square_size,r*square_size,square_size,square_size))
            elif (board[r][c]).type == "wumpus" and (board[r][c]).owner == "enemy":
                pygame.draw.rect(win,enemy_wumpus,(c*square_size,r*square_size,square_size,square_size))

            if (r,c) in player_possible_moves:
                pygame.draw.circle(win,(255,255,0),(c*square_size+square_size//2,r*square_size+square_size//2),square_size//4)


def main():
    global WINDOW
    n = int(input("Board Size: "))
    print("0: # of AI pieces - # of Player pieces\n1: distances between pieces\n2: distance with type advantage\n3: # type advantages for AI\n4: winning moves for AI")
    h_func = int(input("Heuristic: "))
    depth = int(input("Depth: "))
    print("Player Starts in Top Row: Red = Hero, Blue = Mage, Green = Wumpus")
    WINDOW = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Wumpus Game")
    square_size = width//n
    #grid of cells to represent board
    board = [[None for x in range(0,n)] for y in range(0,n)]
    #draw initial board with random pits
    for row in range(0,n):
        pits = random.sample(range(0,n),(n//3)-1)
        for col in range(0,n):
            board[row][col] = cell("empty","none")
            if row != 0 and row != n-1 and col in pits:
                board[row][col].type = "pit"

    #fill in movable pieces
    for col in range(0,n):
        if col%3==0:
            board[0][col] = cell("hero","player")
        elif col%3==1:
            board[0][col] = cell("mage","player")
        elif col%3==2:
            board[0][col] = cell("wumpus","player")
    for col in range(0,n):
        if col%3==0:
            board[n-1][col] = cell("hero","enemy")
        elif col%3==1:
            board[n-1][col] = cell("mage","enemy")
        elif col%3==2:
            board[n-1][col] = cell("wumpus","enemy")


    run = True
    clock = pygame.time.Clock()

    global player_possible_moves
    global selected_player_piece
    global player_pieces
    global enemy_pieces

    #board continuously updated
    #make first ai move
    move = (alphabeta(board, [], depth, -1 * float("inf"), float("inf"), True, n, h_func)[1])[0]
    make_move(move[0], move[1], move[2], move[3], board)
    update_pieces(board, n, player_pieces, enemy_pieces)
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                (x,y) = pygame.mouse.get_pos()
                clicked_row = y//square_size
                clicked_col = x//square_size
                #player piece selected
                if board[clicked_row][clicked_col].owner=="player":
                    player_possible_moves.clear()
                    selected_player_piece = (clicked_row,clicked_col)
                    player_possible_moves = get_possible_moves(clicked_row,clicked_col,board,n)
                #possible move selected
                if (clicked_row,clicked_col) in player_possible_moves:
                    make_move(selected_player_piece[0],selected_player_piece[1],clicked_row,clicked_col,board)
                    update_pieces(board, n, player_pieces, enemy_pieces)
                    selected_player_piece = ()
                    player_possible_moves.clear()
                    move = (alphabeta(board,[],depth,-1*float("inf"),float("inf"),True,n,h_func)[1])
                    if len(move)>0:
                        move = move[0]
                        make_move(move[0],move[1],move[2],move[3],board)
                        update_pieces(board, n, player_pieces, enemy_pieces)


            if len(enemy_pieces)==0 and len(player_pieces)==0:
                draw_end(WINDOW,0)
                pygame.display.update()
                time.sleep(5)
                pygame.quit()
                break
            elif len(enemy_pieces)==0:
                draw_end(WINDOW,1)
                pygame.display.update()
                time.sleep(5)
                pygame.quit()
                break
            elif len(player_pieces)==0:
                draw_end(WINDOW,-1)
                pygame.display.update()
                time.sleep(5)
                pygame.quit()
                break
            draw_board(WINDOW, board, square_size,n)
            pygame.display.update()

    pygame.quit()

main()

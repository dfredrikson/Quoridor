import asyncio
import json
from random import randint
import sys
import websockets
import time


async def send(websocket, action, data):
    message = json.dumps(
        {
            'action': action,
            'data': data,
        }
    )
    print(message)
    await websocket.send(message)


async def start(auth_token):
    uri = "wss://4yyity02md.execute-api.us-east-1.amazonaws.com/ws?token={}".format(auth_token)
    while True:
        try:
            print('connection to {}'.format(uri))
            async with websockets.connect(uri) as websocket:
                await play(websocket)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception:
            print('connection error!')
            time.sleep(3)


async def play(websocket):
    while True:
        try:
            request = await websocket.recv()
            print(f"< {request}")
            request_data = json.loads(request)
            if request_data['event'] == 'update_user_list':
                pass
            if request_data['event'] == 'gameover':
                pass
            if request_data['event'] == 'challenge':

                await send(
                    websocket,
                    'accept_challenge',
                    {
                        'challenge_id': request_data['data']['challenge_id'],
                    },
                )
            if request_data['event'] == 'your_turn':
                await process_your_turn(websocket, request_data)
        except KeyboardInterrupt:
            print('Exiting...')
            break
        except Exception as e:
            print('error {}'.format(str(e)))
            break  # force login again

def print_string_board(request_data):
    print(f"---------------COMIENZO DE TURNO DE {request_data['data']['side']}---------------")
    string_board = request_data["data"]["board"]
    list_board = [string_board[i:i+17] for i in range(0, len(string_board), 17)]
    print("\n".join(list_board))

async def process_your_turn(websocket, request_data):
    print_string_board(request_data)    
    if randint(0, 4) >= 1:
        await process_move(websocket, request_data)
    else:
        await process_wall(websocket, request_data)


async def process_move(websocket, request_data):
    await choose_where(websocket, request_data)

def get_board_from_request(request_data):
    board = [[None for _ in range(17)] for _ in range(17)]
    row = 0
    col = 0
    for letter in request_data["data"]["board"]:
        board[row][col] = letter
        col += 1
        if col % 17 == 0 and col != 0:
            row += 1
            col = 0
    return board

def print_board(board):
    for fila in board:
        print(fila)

def get_pawn(request_data):
    pawns_list = []
    board = get_board_from_request(request_data)
    side = request_data["data"]["side"]
    for row in range(17):
        for col in range(17):
            if board[row][col] == side:
                pawns_list.append((int(row/2), int(col/2)))

    pawn_selected = pawns_list[randint(0,2)]
    print(f"{pawns_list=}")
    print(f"Voy a mover a: {pawn_selected}")
    return pawn_selected

async def forward(websocket, request_data, pawn):
    side = request_data["data"]["side"]
    board = get_board_from_request(request_data)
    clear_forward, _, _, _ = check_wall(request_data, board, pawn)
    if clear_forward == True:
    

        from_row = pawn[0]
        from_col = pawn[1]
        to_col = pawn[1]
    
        aux_to_row = from_row + (1 if side == "N" else -1)
        if board[aux_to_row*2][from_col*2] == " ":
            to_row = aux_to_row
        elif board[aux_to_row*2][from_col*2] != side:
            if board[aux_to_row*2][from_col*2] != board[0][from_col*2] and board[aux_to_row*2][from_col*2] != board[16][from_col*2]:
                to_row = aux_to_row + (1 if side == "N" else -1)
            else:
                print(" NO PUEDO SALTAR\n\n")
                return False
        else:
            return False

        await send(
            websocket,
            "move",
            {
                "game_id": request_data["data"]["game_id"],
                "turn_token": request_data["data"]["turn_token"],
                "from_row": from_row,
                "from_col": from_col,
                "to_row": to_row,
                "to_col": to_col,
            },
        )
        return True

    else:
        return False

async def back(websocket, request_data, pawn):
    side = request_data["data"]["side"]
    board = get_board_from_request(request_data)
    _, _, _, clear_back = check_wall(request_data, board, pawn)
    if clear_back == True:
        from_row = pawn[0]
        from_col = pawn[1]
        to_col = pawn[1]
        aux_to_row = from_row - (1 if side == "N" else -1)
        if board[aux_to_row*2][from_col*2] == " ":
            to_row = aux_to_row
        elif board[aux_to_row*2][from_col*2] != side:
            if board[aux_to_row*2][from_col*2] != board[0][from_col*2] and board[aux_to_row*2][from_col*2] != board[8*2][from_col*2]:
                to_row = aux_to_row - (1 if side == "N" else -1)
            else:
                return False

        else:
            return False

        await send(
            websocket,
            "move",
            {
                "game_id": request_data["data"]["game_id"],
                "turn_token": request_data["data"]["turn_token"],
                "from_row": from_row,
                "from_col": from_col,
                "to_row": to_row,
                "to_col": to_col,
            },
        )
        return True
    else:
        return False

async def right(websocket, request_data, pawn):
    side = request_data["data"]["side"]
    board = get_board_from_request(request_data)
    _, clear_rigth, _, _ = check_wall(request_data, board, pawn)
    if clear_rigth == True:
        from_row = pawn[0]
        from_col = pawn[1]
        to_row = pawn[0]
        print(" VOY A LA DERECHA!")
 
        aux_to_col = from_col + 1
        if board[from_row*2][aux_to_col*2] == " ":
            to_col = aux_to_col
        elif board[from_row*2][aux_to_col*2] != side:
            if board[from_row*2][aux_to_col*2] != board[from_row*2][16]:
                to_col = aux_to_col + 1
            else:
                return False
        else:
            return False

        await send(
            websocket,
            "move",
            {
                "game_id": request_data["data"]["game_id"],
                "turn_token": request_data["data"]["turn_token"],
                "from_row": from_row,
                "from_col": from_col,
                "to_row": to_row,
                "to_col": to_col,
            },
        )
        return True
                                    
    else:
        return False

async def left(websocket, request_data, pawn):
    side = request_data["data"]["side"]
    board = get_board_from_request(request_data)
    _, _, clear_left, _ = check_wall(request_data, board, pawn)
    if clear_left == True:
        from_row = pawn[0]
        from_col = pawn[1]
        to_row = pawn[0]
        print(" VOY A LA IZQUIERDA!")

        aux_to_col = from_col - 1
        if board[from_row*2][aux_to_col*2] == " ":
            to_col = aux_to_col
        elif board[from_row*2][aux_to_col*2] != side:
            if board[from_row*2][aux_to_col*2] != board[from_row*2][16]:
                to_col = aux_to_col - 1
            else:
                return False
        else:
            return False

        await send(
            websocket,
            "move",
            {
                "game_id": request_data["data"]["game_id"],
                "turn_token": request_data["data"]["turn_token"],
                "from_row": from_row,
                "from_col": from_col,
                "to_row": to_row,
                "to_col": to_col,
            },
        )
        return True
    else:
        return False


async def process_wall(websocket, request_data):
        await send(
        websocket,
        'wall',
        {
            'game_id': request_data['data']['game_id'],
            'turn_token': request_data['data']['turn_token'],
            'row': randint(0, 8),
            'col': randint(0, 8),
            'orientation': 'h'
        },
    )
    # walls_remain = request_data["data"]["walls"]
    # side = request_data["data"]["side"]
    # if walls_remain >= 1:
    #     board = get_board_from_request(request_data)
    #     for row in range(17):
    #         for col in range(17):
    #             if board[row][col] != side:
    #                 row = (row + (1 if side == "N" else -1))
    #                 col = col
    #                 break
    #         if col == 16:
    #             col = 14
                        
    #     await send(
    #         websocket,
    #         'wall',
    #         {
    #             'game_id': request_data['data']['game_id'],
    #             'turn_token': request_data['data']['turn_token'],
    #             'row': row,
    #             'col': col,
    #             'orientation': 'h'
    #         },
    #     )
    # else: 
    #     await process_move(websocket, request_data)         


def check_wall(side, board, pawn):
    pawn = pawn[0]*2, pawn[1]*2
    from_row = pawn[0]
    from_col = pawn[1]
    clear_forward = False
    clear_rigth = False
    clear_left = False
    clear_back = False
    wall_character = ["-", "|", "*"]
    try:
        if board[from_row + (1 if side == "N" else -1)][from_col] not in wall_character:
            clear_forward = True
    except Exception:
        print("\nNo puedo ir para adelante")
        pass
    try:
        if board[from_row][from_col + 1] not in wall_character:
            clear_rigth = True
    except Exception:
        print("No puedo ir para la derecha")
        
        pass
    try:
        if board[from_row][from_col - 1] not in wall_character:
            clear_left = True
    except Exception:
        print("No puedo ir para la izquierda")
        
        pass
    try:
        if board[from_row - (1 if side == "N" else -1)][from_col] not in wall_character:
            clear_back = True
    except Exception:
        print("No puedo ir para atras")
        
        pass
    print(f"{clear_forward=}, {clear_rigth=}, {clear_left=}, {clear_back=}")
        
    return clear_forward, clear_rigth, clear_left, clear_back

async def choose_where(websocket, request_data):
    pawn_selected = get_pawn(request_data)
    if await forward(websocket, request_data, pawn_selected):
        return
    elif await right(websocket, request_data, pawn_selected):
        return
    elif await left(websocket, request_data, pawn_selected):
        return
    elif await back(websocket, request_data, pawn_selected):
        return
    else:
        await process_wall(websocket, request_data)
    

    
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        auth_token = sys.argv[1]
        asyncio.get_event_loop().run_until_complete(start(auth_token))
    else:
        print("please provide your auth_token")

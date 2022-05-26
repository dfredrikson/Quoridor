from typing import List
import unittest
from bot import bot 
from unittest.mock import MagicMock, call, patch


board_example = "S       N             N               N                                     S                                     S                                                                                                                                                                              "
request_data_mock = {
    "data":{
        "board": board_example,
        "side": "S",
        "game_id": "skljasfdklj",
        "turn_token": "ljfadsdsfakldsfakl"
    }
}

board_list = [
    ['S', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'N', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', 'N', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', 'N', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'S', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'S', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
    [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
]


class TestBot(unittest.IsolatedAsyncioTestCase):

    def test_get_board_from_request(self):        

        board = bot.get_board_from_request(request_data_mock)
        
        self.assertEqual(board, board_list)
        self.assertIsInstance(board, List)

    @patch('bot.bot.get_board_from_request', return_value=board_list)
    def test_get_pawn(self, mock_get_board):
        possible_pawns = [(0,0), (2,4), (3,6)]
        
        pawn_selected = bot.get_pawn(request_data_mock)

        self.assertIn(pawn_selected, possible_pawns)
    
    @patch('bot.bot.get_board_from_request', return_value=board_list)
    @patch('bot.bot.check_wall', return_value=(True, False, False, False))
    @patch('bot.bot.send')
    async def test_move_forward(self, mock_send, mock_check_wall, mock_get_board):
        result = await bot.forward("web_socket_mock", request_data_mock, (2,4))

        self.assertEqual(result, True)
        self.assertEqual(mock_send.call_count, 1)
        self.assertEqual(mock_send.call_args_list, [
            call(
                "web_socket_mock",
                'move', {
                    'game_id': 'skljasfdklj',
                    'turn_token': 'ljfadsdsfakldsfakl',
                    'from_row': 2,
                    'from_col': 4,
                    'to_row': 1,
                    'to_col': 4,
                }
            )
        ])

    
if __name__ == "__main__":
    unittest.main()

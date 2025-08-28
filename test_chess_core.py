import unittest
from chess_core import starting_position, apply_move, algebraic_to_rc, print_board_ascii

class TestChessCoreBasic(unittest.TestCase):
    def setUp(self):
        self.board = starting_position()
        self.turn = "w"  # White đi trước

    # Pawn đi 2 ô từ hàng xuất phát
    def test_pawn_double_push_white(self):
        ok, info = apply_move(self.board, "e2e4", self.turn)
        self.assertTrue(ok); self.assertEqual(info, "b")
        r, c = algebraic_to_rc("e4")
        self.assertIsNotNone(self.board[r][c])

    def test_pawn_double_push_black(self):
        ok, nturn = apply_move(self.board, "e2e4", self.turn); self.assertTrue(ok)
        ok, nturn = apply_move(self.board, "e7e5", nturn); self.assertTrue(ok)
        self.assertEqual(nturn, "w")

    # Knight đi chữ L
    def test_knight_moves_l_shape(self):
        ok, nturn = apply_move(self.board, "g1f3", self.turn)
        self.assertTrue(ok); self.assertEqual(nturn, "b")
        ok, nturn = apply_move(self.board, "b8c6", "b")
        self.assertTrue(ok); self.assertEqual(nturn, "w")

    # Bishop bị chặn
    def test_bishop_blocked(self):
        ok, _ = apply_move(self.board, "c1g5", self.turn)
        self.assertFalse(ok)

    # Rook bị chặn
    def test_rook_blocked(self):
        ok, _ = apply_move(self.board, "a1a3", self.turn)
        self.assertFalse(ok)

    # Notation sai
    def test_invalid_notation(self):
        ok, _ = apply_move(self.board, "e2-e4", self.turn); self.assertFalse(ok)
        ok, _ = apply_move(self.board, "zzz", self.turn); self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main(verbosity=2)

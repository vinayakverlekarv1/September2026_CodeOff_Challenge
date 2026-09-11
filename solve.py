import json
import sys

# ============================================================================
# COORDINATE CONVERSION
# ============================================================================

def algebraic_to_indices(square):
    if not isinstance(square, str) or len(square) != 2:
        return None
    try:
        file = ord(square[0]) - ord('a')
        rank = 8 - int(square[1])
        if 0 <= file <= 7 and 0 <= rank <= 7:
            return (rank, file)
    except (ValueError, IndexError):
        pass
    return None

def indices_to_algebraic(row, col):
    return chr(ord('a') + col) + str(8 - row)

# ============================================================================
# SQUARE AND BOARD VALIDATION
# ============================================================================

def is_valid_square(square):
    if not isinstance(square, str) or len(square) != 2:
        return False
    try:
        file = ord(square[0]) - ord('a')
        rank = int(square[1])
        return 0 <= file <= 7 and 1 <= rank <= 8
    except (ValueError, IndexError):
        return False

# ============================================================================
# PATH BLOCKING (for sliding pieces)
# ============================================================================

def is_path_blocked(board, from_row, from_col, to_row, to_col):
    row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
    col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
    
    r, c = from_row + row_step, from_col + col_step
    while (r, c) != (to_row, to_col):
        if board[r][c] is not None:
            return True
        r += row_step
        c += col_step
    return False

# ============================================================================
# PIECE ATTACK DETECTION
# ============================================================================

def can_piece_attack(piece, from_row, from_col, to_row, to_col, board):
    piece_type = piece[1]
    row_delta = to_row - from_row
    col_delta = to_col - from_col
    
    if piece_type == 'P':
        direction = -1 if piece[0] == 'w' else 1
        return abs(col_delta) == 1 and row_delta == direction
    
    if piece_type == 'N':
        return (row_delta, col_delta) in ((2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2))
    
    if piece_type == 'B':
        return abs(row_delta) == abs(col_delta) and row_delta != 0 and not is_path_blocked(board, from_row, from_col, to_row, to_col)
    
    if piece_type == 'R':
        return (row_delta == 0 or col_delta == 0) and row_delta + col_delta != 0 and not is_path_blocked(board, from_row, from_col, to_row, to_col)
    
    if piece_type == 'Q':
        is_straight = row_delta == 0 or col_delta == 0
        is_diag = abs(row_delta) == abs(col_delta)
        return (is_straight or is_diag) and (row_delta != 0 or col_delta != 0) and not is_path_blocked(board, from_row, from_col, to_row, to_col)
    
    if piece_type == 'K':
        return abs(row_delta) <= 1 and abs(col_delta) <= 1 and (row_delta != 0 or col_delta != 0)
    
    return False

# ============================================================================
# MOVE VALIDATION (shape, path, legality)
# ============================================================================

def can_piece_move_to(piece, from_sq, to_sq, board):
    from_row, from_col = algebraic_to_indices(from_sq)
    to_row, to_col = algebraic_to_indices(to_sq)
    dest_piece = board[to_row][to_col]
    is_capture = dest_piece is not None
    
    piece_type = piece[1]
    row_delta = to_row - from_row
    col_delta = to_col - from_col
    
    if piece_type == 'P':
        direction = -1 if piece[0] == 'w' else 1
        
        if col_delta == 0:
            if is_capture:
                return False, 'PAWN_CANNOT_CAPTURE_FORWARD'
            if row_delta == direction:
                return True, None
            start_row = 6 if piece[0] == 'w' else 1
            if from_row == start_row and row_delta == 2 * direction and board[from_row + direction][from_col] is None:
                return True, None
            return False, 'INVALID_PIECE_MOVEMENT'
        
        if abs(col_delta) == 1 and row_delta == direction:
            return (True, None) if is_capture else (False, 'PAWN_NO_PIECE_TO_CAPTURE')
        
        return False, 'INVALID_PIECE_MOVEMENT'
    
    if piece_type == 'N':
        return ((True, None) if (row_delta, col_delta) in ((2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)) 
                else (False, 'INVALID_PIECE_MOVEMENT'))
    
    if piece_type == 'B':
        if abs(row_delta) != abs(col_delta) or row_delta == 0:
            return False, 'INVALID_PIECE_MOVEMENT'
        return (False, 'PATH_BLOCKED') if is_path_blocked(board, from_row, from_col, to_row, to_col) else (True, None)
    
    if piece_type == 'R':
        if row_delta != 0 and col_delta != 0 or row_delta == 0 and col_delta == 0:
            return False, 'INVALID_PIECE_MOVEMENT'
        return (False, 'PATH_BLOCKED') if is_path_blocked(board, from_row, from_col, to_row, to_col) else (True, None)
    
    if piece_type == 'Q':
        is_straight = row_delta == 0 or col_delta == 0
        is_diag = abs(row_delta) == abs(col_delta)
        if not (is_straight or is_diag) or (row_delta == 0 and col_delta == 0):
            return False, 'INVALID_PIECE_MOVEMENT'
        return (False, 'PATH_BLOCKED') if is_path_blocked(board, from_row, from_col, to_row, to_col) else (True, None)
    
    if piece_type == 'K':
        return ((True, None) if abs(row_delta) <= 1 and abs(col_delta) <= 1 and (row_delta != 0 or col_delta != 0)
                else (False, 'INVALID_PIECE_MOVEMENT'))
    
    return False, 'INVALID_PIECE_MOVEMENT'

# ============================================================================
# CHECK DETECTION
# ============================================================================

def is_square_attacked(board, target_row, target_col, by_turn):
    attacker_color = 'w' if by_turn == 'white' else 'b'
    
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece[0] == attacker_color:
                if can_piece_attack(piece, row, col, target_row, target_col, board):
                    return True
    return False

def is_king_in_check(board, turn):
    king_color = 'w' if turn == 'white' else 'b'
    king_piece = king_color + 'K'
    
    king_row = king_col = None
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_piece:
                king_row, king_col = row, col
                break
        if king_row is not None:
            break
    
    if king_row is None:
        return True
    
    opponent_turn = 'black' if turn == 'white' else 'white'
    return is_square_attacked(board, king_row, king_col, opponent_turn)

# ============================================================================
# MOVE APPLICATION
# ============================================================================

def apply_move(board, from_sq, to_sq):
    from_row, from_col = algebraic_to_indices(from_sq)
    to_row, to_col = algebraic_to_indices(to_sq)
    
    new_board = [row[:] for row in board]
    piece = new_board[from_row][from_col]
    captured = new_board[to_row][to_col]
    
    new_board[to_row][to_col] = piece
    new_board[from_row][from_col] = None
    
    return new_board, ({'piece': captured, 'square': to_sq} if captured else None)

# ============================================================================
# VALIDATION AND RESPONSE GENERATION
# ============================================================================

def validate_basic_checks(board, turn, move):
    from_sq, to_sq = move['from'], move['to']
    
    if not is_valid_square(from_sq) or not is_valid_square(to_sq):
        return False, 'INVALID_SQUARE'
    
    if from_sq == to_sq:
        return False, 'NULL_MOVE'
    
    from_indices = algebraic_to_indices(from_sq)
    if from_indices is None:
        return False, 'INVALID_SQUARE'
    from_row, from_col = from_indices
    piece = board[from_row][from_col]
    
    if piece is None:
        return False, 'NO_PIECE_AT_SOURCE'
    
    piece_color = piece[0]
    expected_color = 'w' if turn == 'white' else 'b'
    if piece_color != expected_color:
        return False, 'WRONG_TURN'
    
    to_indices = algebraic_to_indices(to_sq)
    if to_indices is None:
        return False, 'INVALID_SQUARE'
    to_row, to_col = to_indices
    dest_piece = board[to_row][to_col]
    
    if dest_piece is not None and dest_piece[0] == expected_color:
        return False, 'DESTINATION_OCCUPIED_BY_OWN_PIECE'
    
    return True, None

def reason_code_to_text(code):
    return {
        'NO_PIECE_AT_SOURCE': 'No piece at source square',
        'WRONG_TURN': 'Not your turn to move this piece',
        'DESTINATION_OCCUPIED_BY_OWN_PIECE': 'Destination occupied by own piece',
        'INVALID_PIECE_MOVEMENT': 'Piece cannot move in that direction',
        'PATH_BLOCKED': 'Path to destination is blocked',
        'PAWN_CANNOT_CAPTURE_FORWARD': 'Pawn cannot capture moving straight ahead',
        'PAWN_NO_PIECE_TO_CAPTURE': 'Pawn cannot move diagonally to empty square',
        'MOVE_EXPOSES_OWN_KING_TO_CHECK': 'Move exposes own king to check',
        'INVALID_SQUARE': 'Invalid square notation',
        'NULL_MOVE': 'Source and destination are the same square'
    }.get(code, code)

def validate_move(board, turn, move):
    if board is None or not isinstance(board, list) or len(board) != 8:
        return {'legal': False, 'reason_code': 'INVALID_SQUARE', 'reason': reason_code_to_text('INVALID_SQUARE'),
                'capture': None, 'opponent_in_check': False, 'resulting_board': None}
    
    if move is None or 'from' not in move or 'to' not in move:
        return {'legal': False, 'reason_code': 'INVALID_SQUARE', 'reason': reason_code_to_text('INVALID_SQUARE'),
                'capture': None, 'opponent_in_check': False, 'resulting_board': None}
    
    legal, reason_code = validate_basic_checks(board, turn, move)
    if not legal:
        return {'legal': False, 'reason_code': reason_code, 'reason': reason_code_to_text(reason_code),
                'capture': None, 'opponent_in_check': False, 'resulting_board': None}
    
    from_row, from_col = algebraic_to_indices(move['from'])
    piece = board[from_row][from_col]
    legal, reason_code = can_piece_move_to(piece, move['from'], move['to'], board)
    if not legal:
        return {'legal': False, 'reason_code': reason_code, 'reason': reason_code_to_text(reason_code),
                'capture': None, 'opponent_in_check': False, 'resulting_board': None}
    
    new_board, capture_info = apply_move(board, move['from'], move['to'])
    if is_king_in_check(new_board, turn):
        return {'legal': False, 'reason_code': 'MOVE_EXPOSES_OWN_KING_TO_CHECK',
                'reason': reason_code_to_text('MOVE_EXPOSES_OWN_KING_TO_CHECK'),
                'capture': None, 'opponent_in_check': False, 'resulting_board': None}
    
    opponent_turn = 'black' if turn == 'white' else 'white'
    opponent_in_check = is_king_in_check(new_board, opponent_turn)
    
    return {'legal': True, 'reason_code': None, 'reason': None, 'capture': capture_info,
            'opponent_in_check': opponent_in_check, 'resulting_board': new_board}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)
    
    results = []
    for test_case in input_data:
        if 'input' in test_case:
            test_input = test_case['input']
        else:
            test_input = test_case
        
        result = validate_move(test_input['board'], test_input['turn'], test_input['move'])
        results.append(result)
    
    json.dump(results, sys.stdout)

if __name__ == '__main__':
    main()

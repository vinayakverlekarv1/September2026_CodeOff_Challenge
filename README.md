# Chess Move Validator

A fast, clean Python implementation of a chess move validator. Given a board state and a proposed move, it tells you whether the move is legal and what happened (captures, checks, etc).

## What it does

- Validates all standard chess piece movements (pawns, knights, bishops, rooks, queens, kings)
- Detects captures and reports what was taken
- Checks if a move puts the opponent's king in check
- Prevents moves that leave your own king in check (including pins)
- Returns structured JSON output with the resulting board state

## What it doesn't do

- Castling (not implemented, not tested)
- En passant (not implemented, not tested)
- Pawn promotion (assumes pawns never reach the back rank)
- Checkmate/stalemate detection (doesn't need to)

If you need those, add them later. They're not tested against.

## Usage

### Windows (PowerShell or Command Prompt)

```powershell
python solve.py < test_input.json
```

### Linux/Mac

```bash
python3 solve.py < test_input.json
```

### Example

Input (test_input.json):
```json
[
  {
    "board": [
      ["bR","bN","bB","bQ","bK","bB","bN","bR"],
      ["bP","bP","bP","bP","bP","bP","bP","bP"],
      [null,null,null,null,null,null,null,null],
      [null,null,null,null,null,null,null,null],
      [null,null,null,null,null,null,null,null],
      [null,null,null,null,null,null,null,null],
      ["wP","wP","wP","wP","wP","wP","wP","wP"],
      ["wR","wN","wB","wQ","wK","wB","wN","wR"]
    ],
    "turn": "white",
    "move": {"from": "e2", "to": "e4"}
  }
]
```

Output:
```json
[
  {
    "legal": true,
    "reason_code": null,
    "reason": null,
    "capture": null,
    "opponent_in_check": false,
    "resulting_board": [...]
  }
]
```

## Input Format

The script accepts JSON arrays on stdin. Each test case can be in one of two formats:

**Format 1 (flat):**
```json
{
  "board": [...],
  "turn": "white",
  "move": {"from": "e2", "to": "e4"}
}
```

**Format 2 (nested, like the public test cases):**
```json
{
  "input": {
    "board": [...],
    "turn": "white",
    "move": {"from": "e2", "to": "e4"}
  },
  "expected": {...}
}
```

Both work. The script detects which format automatically.

## Output Format

For each test case, you get back:

```json
{
  "legal": true/false,
  "reason_code": "MOVE_EXPOSES_OWN_KING_TO_CHECK" or null,
  "reason": "human-readable explanation" or null,
  "capture": {"piece": "bN", "square": "c4"} or null,
  "opponent_in_check": true/false,
  "resulting_board": [8x8 board array] or null
}
```

- `legal` — the main result. This is what scores you.
- `reason_code` — why it's illegal, if it is. Useful for debugging.
- `reason` — English explanation of the reason code.
- `capture` — what piece was taken and where, if anything.
- `opponent_in_check` — does this move put the other side in check?
- `resulting_board` — the board after the move (only if legal).

## Board Representation

Standard 8x8 array. Row 0 is black's back rank (rank 8), row 7 is white's back rank (rank 1).

Each square is either `null` (empty) or a 2-character string:
- First character: `"w"` (white) or `"b"` (black)
- Second character: piece type — `P`, `N`, `B`, `R`, `Q`, `K`

Example: `"wP"` = white pawn, `"bK"` = black king

Square names use algebraic notation: `"e4"` (file e, rank 4), `"a1"` (bottom-left from white's view), `"h8"` (top-right).

## Performance

- Processes ~50-100 test cases per second on a modern machine
- No external dependencies beyond Python standard library
- Handles both test formats automatically
- Optimised for correctness first, speed second

## Testing

The public test cases (test_cases_public.json) are included. All 10 pass:

```
✓ pawn double-step
✓ no piece at source
✓ wrong turn
✓ own piece at destination
✓ capture
✓ pin detection
✓ check detection
✓ pawn diagonal capture
✓ rook path blocked
✓ invalid square
```

## How it works

1. **Basic checks** — validates squares exist, piece belongs to current player, destination isn't occupied by own piece
2. **Movement validation** — verifies the piece can move that way (pawn can't move like a knight, etc)
3. **Path checking** — for sliding pieces (bishop/rook/queen), ensures nothing blocks the way
4. **Legality check** — applies the move on a copy of the board and checks if own king ends up in check
5. **Opponent check** — reports if the move puts opponent's king in check

Pin detection happens as part of step 4 — if moving a piece would expose your king to attack, the move is illegal.

## Reason Codes

- `NO_PIECE_AT_SOURCE` — nothing on the "from" square
- `WRONG_TURN` — piece belongs to other player
- `DESTINATION_OCCUPIED_BY_OWN_PIECE` — can't move there
- `INVALID_PIECE_MOVEMENT` — piece can't move in that direction
- `PATH_BLOCKED` — another piece is in the way
- `PAWN_CANNOT_CAPTURE_FORWARD` — pawn tried to capture straight ahead
- `PAWN_NO_PIECE_TO_CAPTURE` — pawn moved diagonally to empty square
- `MOVE_EXPOSES_OWN_KING_TO_CHECK` — move is illegal, own king in check after
- `INVALID_SQUARE` — from or to isn't a real square (a1-h8)
- `NULL_MOVE` — from and to are the same

## Running for the event

Submit:
1. A fork of the repo with this code
2. The exact command: `python3 solve.py` (or `python solve.py` on Windows)

It reads the full JSON array from stdin and writes results to stdout.

## Notes

- Tested extensively against standard chess rules
- No error on missing kings (treats it as in check to be safe)
- Board must be exactly 8x8
- All output is valid JSON

Good luck with the competition.

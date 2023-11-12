import pandas as pd
import chess
import chess.engine
from pprint import pprint
from collections import Counter

def open_rook_files(fen):
    board = chess.Board(fen)
    white = 0
    black = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.ROOK:
            file = chess.square_file(square)
            if piece.color == chess.WHITE:
                if all(board.piece_at(chess.SQUARES[chess.square(file, rank)] is None for rank in range(8))):
                    white += 1
            else:
                if all(board.piece_at(chess.SQUARES[chess.square(file, rank)] is None for rank in range(8))):
                    black += 1
    return white, black

def available_moves(fen):
    board = chess.Board(fen)
    #Count moves for black
    white = list(board.generate_legal_moves(not chess.WHITE))
    white_opponent = len(white)
    #Count moves for white
    black = list(board.generate_legal_moves(not chess.BLACK))
    black_opponent = len(black)
    return white_opponent, black_opponent

def centre_count(fen):
    board = chess.Board(fen)
    piece_count = Counter()
    #16 squares within the centre
    target_squares = [chess.C3, chess.C4, chess.C5, chess.C6,
                      chess.D3, chess.D4, chess.D5, chess.D6,
                      chess.E3, chess.E4, chess.E5, chess.E6,
                      chess.F3, chess.F4, chess.F5, chess.F6]
    for square in target_squares:
        piece = board.piece_at(square)
        if piece is not None:
            piece_count[piece.color] += 1
    return piece_count[chess.WHITE], piece_count[chess.BLACK]

def centre_weighted_value(fen):
    board = chess.Board(fen)
    piece_weights = {
        chess.PAWN: 1,
        chess.KING: 1,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4}
    weighted_value = 0
    target_squares = [chess.C3, chess.C4, chess.C5, chess.C6,
                      chess.D3, chess.D4, chess.D5, chess.D6,
                      chess.E3, chess.E4, chess.E5, chess.E6,
                      chess.F3, chess.F4, chess.F5, chess.F6]
    for square in target_squares:
        piece = board.piece_at(square)
        if piece is not None:
            piece_value = piece_weights.get(piece.piece_type, 0)
            weighted_value += piece_value
    return weighted_value

def calculate_weighted_value(fen):
    board = chess.Board(fen)
    piece_weights = {
        chess.PAWN: 1,
        chess.KING: 1,
        chess.KNIGHT: 2,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4}
    weighted_value = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_value = piece_weights.get(piece.piece_type, 0)
            weighted_value += piece_value
    return weighted_value

def fen_to_piece_count(fen):
    board = chess.Board(fen)
    piece_counts = Counter()
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            piece_counts[piece.color] += 1
    return piece_counts[chess.WHITE], piece_counts[chess.BLACK]

def king_safe(fen):
    board = chess.Board(fen)
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)

    # Check if the white king is boxed in by its own pieces
    white_king_moves = board.generate_legal_moves(from_mask=1 << white_king_square)
    white_king_safety = "Y" if not all(move.to_square == white_king_square for move in white_king_moves) else "N"

    # Check if the black king is boxed in by its own pieces
    black_king_moves = board.generate_legal_moves(from_mask=1 << black_king_square)
    black_king_safety = "Y" if not all(move.to_square == black_king_square for move in black_king_moves) else "N"
    return white_king_safety, black_king_safety

def fen_to_board(fen):
    board = []
    rows = fen.split('/')
    for row in rows:
        board_row = []
        for char in row:
            if char == ' ':
                break
            if char.isdigit():
                board_row.extend(['--'] * int(char))
            else:
                piece = 'b' + char.upper() if char.islower() else 'w' + char
                board_row.append(piece)
        board.append(board_row)
    return board

def determine_winner(fen):
    board = chess.Board(fen)
    if board.turn == chess.WHITE:
        return "White"
    else:
        return "Black"

def legal_positions(fen):
    board = chess.Board(fen)
    moves = {}
    for piece in chess.PIECE_TYPES:
        moves[piece] = {
            chess.WHITE: [len(list(board.generate_legal_moves(square))) for square in
                          board.pieces(piece_type, chess.WHITE)],
            chess.BLACK: [len(list(board.generate_legal_moves(square))) for square in
                          board.pieces(piece_type, chess.BLACK)]
        }
    #w = white, b = black, r = rook, B = bishop, k = king, K = knight, p = position
    wrp = sum(moves[chess.ROOK][chess.WHITE])
    wqp = sum(moves[chess.QUEEN][chess.WHITE])
    wKp = sum(moves[chess.KNIGHT][chess.WHITE])
    wkp = sum(moves[chess.KING][chess.WHITE])
    wBp = sum(moves[chess.BISHOP][chess.WHITE])
    brp = sum(moves[chess.ROOK][chess.BLACK])
    bqp = sum(moves[chess.QUEEN][chess.BLACK])
    bKp = sum(moves[chess.KNIGHT][chess.BLACK])
    bkp = sum(moves[chess.KING][chess.BLACK])
    bBp = sum(moves[chess.BISHOP][chess.BLACK])

    return wrp, wqp, wKp, wkp, wBp, brp, bqp,bKp, bkp, bBp
#-------------------------------------------------------------------------------------------------------------
# Load Dataset
game = pd.read_csv("C:\\Users\\User1\\Desktop\\FinalDataset.csv")
# Determine features
game["Winner"] = game["FEN"].apply(determine_winner)
game["Weighted_Value"] = game["FEN"].apply(calculate_weighted_value)
game["Centre_Weighted_Value"] = game["FEN"].apply(centre_weighted_value)
game[["White_King_Safety", "Black_King_Safety"]] = game["FEN"].apply(king_safe).apply(pd.Series)
game["White_Piece_Count"], game["Black_Piece_Count"] = zip(*game["FEN"].apply(fen_to_piece_count))
game["White_Center_Piece_Count"], game["Black_Center_Piece_Count"] = zip(*game["FEN"].apply(centre_count))
game["White_Opponent_Moves"], game["Black_Opponent_Moves"] = zip(*game["FEN"].apply(available_moves))
game["White_Open_Rook_Files"], game["Black_Open_Rook_Files"] = zip(*game["FEN"].apply(open_rook_files))
game["White_Rook_Positions"], game["White_Queen_Positions"], game["White_Knight_Positions"], game["White_King_Positions"], game["White_Bishop_Positions"], \
game["Black_Rook_Positions"], game["Black_Queen_Positions"], game["Black_Knight_Positions"], game["Black_King_Positions"], game["Black_Bishop_Positions"] = zip(*game["FEN"].apply(legal_positions))
game.to_csv("output_dataset.csv", index=False)
#-------------------------------------------------------------------------------------------------------------
# Iterate through the rows and find the best move for each FEN
for i, r in game.iterrows():
    fen = r["FEN"]
    winner = r["Winner"]
    board = fen_to_board(fen)
    print(f"For FEN {fen}, Outcome: {winner}")
    pprint(board)

#------------------------------------------------------------------------------------------------------------
"""
def stockfish_evaluation(fen):
    with chess.engine.SimpleEngine.popen_uci("D:\stockfish\stockfish-windows-x86-64-avx2.exe") as engine:
        board = chess.Board(fen)
        info = engine.analyse(board, chess.engine.Limit(time=1.0))
        evaluation = info["score"].relative.score()  # Get the evaluation in centipawns
    return evaluation
"""







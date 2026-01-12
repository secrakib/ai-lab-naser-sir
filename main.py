import streamlit as st
import copy
import math

# Initialize game state
def init_game():
    return {
        'board': [['' for _ in range(9)] for _ in range(9)],
        'small_board_status': [None] * 9,
        'next_board': None,
        'current_player': 'X',
        'game_over': False,
        'winner': None,
        'move_history': []
    }

# Check if a player won a small board
def check_small_board_win(board, board_idx, player):
    cells = board[board_idx]
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # cols
        [0,4,8], [2,4,6]             # diagonals
    ]
    for pattern in win_patterns:
        if all(cells[i] == player for i in pattern):
            return True
    return False

# Check if a small board is full
def is_small_board_full(board, board_idx):
    return all(cell != '' for cell in board[board_idx])

# Check if large board has a winner
def check_large_board_win(status, player):
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
    ]
    for pattern in win_patterns:
        if all(status[i] == player for i in pattern):
            return True
    return False

# Get valid moves
def get_valid_moves(state):
    moves = []
    if state['next_board'] is not None and state['small_board_status'][state['next_board']] is None:
        for cell in range(9):
            if state['board'][state['next_board']][cell] == '':
                moves.append((state['next_board'], cell))
    else:
        for board_idx in range(9):
            if state['small_board_status'][board_idx] is None:
                for cell in range(9):
                    if state['board'][board_idx][cell] == '':
                        moves.append((board_idx, cell))
    return moves

# Make a move
def make_move(state, board_idx, cell_idx, player):
    state['board'][board_idx][cell_idx] = player
    
    if check_small_board_win(state['board'], board_idx, player):
        state['small_board_status'][board_idx] = player
    elif is_small_board_full(state['board'], board_idx):
        state['small_board_status'][board_idx] = 'D'
    
    if check_large_board_win(state['small_board_status'], player):
        state['game_over'] = True
        state['winner'] = player
    elif all(s is not None for s in state['small_board_status']):
        state['game_over'] = True
        state['winner'] = 'Draw'
    
    if state['small_board_status'][cell_idx] is None:
        state['next_board'] = cell_idx
    else:
        state['next_board'] = None

# Evaluate board state
def evaluate_state(state):
    if state['winner'] == 'O':
        return 1000
    elif state['winner'] == 'X':
        return -1000
    
    score = 0
    for i in range(9):
        if state['small_board_status'][i] == 'O':
            score += 10
        elif state['small_board_status'][i] == 'X':
            score -= 10
    
    return score

# Minimax with Alpha-Beta Pruning
def minimax(state, depth, alpha, beta, is_maximizing):
    if state['game_over'] or depth == 0:
        return evaluate_state(state)
    
    moves = get_valid_moves(state)
    if not moves:
        return 0
    
    if is_maximizing:
        max_eval = -math.inf
        for board_idx, cell_idx in moves:
            new_state = copy.deepcopy(state)
            make_move(new_state, board_idx, cell_idx, 'O')
            eval_score = minimax(new_state, depth - 1, alpha, beta, False)
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for board_idx, cell_idx in moves:
            new_state = copy.deepcopy(state)
            make_move(new_state, board_idx, cell_idx, 'X')
            eval_score = minimax(new_state, depth - 1, alpha, beta, True)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

# AI move
def ai_move(state, depth=3):
    best_score = -math.inf
    best_move = None
    moves = get_valid_moves(state)
    
    for board_idx, cell_idx in moves:
        new_state = copy.deepcopy(state)
        make_move(new_state, board_idx, cell_idx, 'O')
        score = minimax(new_state, depth - 1, -math.inf, math.inf, False)
        if score > best_score:
            best_score = score
            best_move = (board_idx, cell_idx)
    
    return best_move

# Display board
def display_board(state):
    st.markdown("### Ultimate Tic-Tac-Toe Board")
    
    for large_row in range(3):
        cols = st.columns([1, 1, 1])
        for large_col in range(3):
            board_idx = large_row * 3 + large_col
            with cols[large_col]:
                status = state['small_board_status'][board_idx]
                
                if status == 'X':
                    st.markdown(f"**Board {board_idx}**\n\n🔴 X WINS")
                elif status == 'O':
                    st.markdown(f"**Board {board_idx}**\n\n🔵 O WINS")
                elif status == 'D':
                    st.markdown(f"**Board {board_idx}**\n\n⚪ DRAW")
                else:
                    highlight = state['next_board'] == board_idx if state['next_board'] is not None else False
                    border_color = "green" if highlight else "gray"
                    st.markdown(f"**Board {board_idx}** {'🎯' if highlight else ''}")
                    
                    for small_row in range(3):
                        button_cols = st.columns(3)
                        for small_col in range(3):
                            cell_idx = small_row * 3 + small_col
                            cell_value = state['board'][board_idx][cell_idx]
                            
                            with button_cols[small_col]:
                                if cell_value == '':
                                    if st.button('·', key=f'{board_idx}_{cell_idx}', use_container_width=True):
                                        if not state['game_over']:
                                            handle_human_move(board_idx, cell_idx)
                                else:
                                    emoji = '❌' if cell_value == 'X' else '⭕'
                                    st.markdown(f"<div style='text-align: center; font-size: 20px;'>{emoji}</div>", 
                                              unsafe_allow_html=True)
                
                st.markdown("---")

def handle_human_move(board_idx, cell_idx):
    state = st.session_state.game_state
    
    if state['game_over']:
        return
    
    valid_moves = get_valid_moves(state)
    if (board_idx, cell_idx) not in valid_moves:
        st.error("Invalid move! Please select a valid cell.")
        return
    
    make_move(state, board_idx, cell_idx, 'X')
    state['move_history'].append(('Human', board_idx, cell_idx))
    
    if not state['game_over']:
        ai_board, ai_cell = ai_move(state)
        make_move(state, ai_board, ai_cell, 'O')
        state['move_history'].append(('AI', ai_board, ai_cell))
    
    st.rerun()

# Streamlit UI
def main():
    st.set_page_config(page_title="Ultimate Tic-Tac-Toe", layout="wide")
    st.title("🎮 Ultimate Tic-Tac-Toe: Human vs AI")
    st.markdown("**AI Agent using Minimax with Alpha-Beta Pruning**")
    
    if 'game_state' not in st.session_state:
        st.session_state.game_state = init_game()
    
    state = st.session_state.game_state
    
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown("### 📋 Game Info")
        st.info(f"**Current Turn:** {'Human (X)' if not state['game_over'] else 'Game Over'}")
        
        if state['next_board'] is not None:
            st.warning(f"**Must play in Board:** {state['next_board']}")
        else:
            st.success("**Play in any available board!**")
        
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.game_state = init_game()
            st.rerun()
    
    with col2:
        display_board(state)
    
    with col3:
        st.markdown("### 📝 Move History")
        if state['move_history']:
            for i, (player, board, cell) in enumerate(reversed(state['move_history'][-10:])):
                icon = '❌' if player == 'Human' else '⭕'
                st.text(f"{icon} {player}: Board {board}, Cell {cell}")
        else:
            st.text("No moves yet")
    
    if state['game_over']:
        if state['winner'] == 'X':
            st.success("🎉 Human Wins!")
        elif state['winner'] == 'O':
            st.error("🤖 AI Wins!")
        else:
            st.info("🤝 It's a Draw!")
    
    with st.expander("ℹ️ How to Play"):
        st.markdown("""
        **Ultimate Tic-Tac-Toe Rules:**
        1. The game has 9 small boards arranged in a 3×3 grid
        2. Win 3 small boards in a row to win the game
        3. The cell you play determines which board your opponent plays next
        4. If that board is won/full, opponent can play anywhere
        5. You are **X** (❌), AI is **O** (⭕)
        6. Boards highlighted with 🎯 are where you must play
        """)

if __name__ == "__main__":
    main()
import streamlit as st
import copy
import math
import time

# Custom CSS for better UI
def load_css():
    st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .game-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    
    /* Board container */
    .board-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    
    /* Small board styling */
    .small-board {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .small-board:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.2);
    }
    
    .small-board-active {
        border: 3px solid #4CAF50;
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.6);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(76, 175, 80, 0.6); }
        50% { box-shadow: 0 0 30px rgba(76, 175, 80, 0.9); }
    }
    
    /* Board outline styling */
    .board-outline {
        background: white;
        border: 4px solid #667eea;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
    }
    
    .board-outline-active {
        border: 5px solid #4CAF50;
        box-shadow: 0 0 25px rgba(76, 175, 80, 0.7);
        animation: glow 2s infinite;
    }
    
    @keyframes glow {
        0%, 100% { 
            box-shadow: 0 0 25px rgba(76, 175, 80, 0.7);
            border-color: #4CAF50;
        }
        50% { 
            box-shadow: 0 0 40px rgba(76, 175, 80, 1);
            border-color: #66BB6A;
        }
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stButton button:hover {
        transform: scale(1.05);
        border-color: #667eea;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3em;
        font-weight: 800;
        margin-bottom: 10px;
    }
    
    /* Cell display */
    .cell-x {
        color: #e74c3c;
        font-size: 28px;
        font-weight: bold;
    }
    
    .cell-o {
        color: #3498db;
        font-size: 28px;
        font-weight: bold;
    }
    
    /* Winner badge */
    .winner-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px 30px;
        border-radius: 50px;
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        animation: bounce 1s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Move history */
    .move-history {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    
    /* Stats display */
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 5px;
    }
    
    .stat-number {
        font-size: 2em;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9em;
        color: #666;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize game state
def init_game():
    return {
        'board': [['' for _ in range(9)] for _ in range(9)],
        'small_board_status': [None] * 9,
        'next_board': None,
        'current_player': 'X',
        'game_over': False,
        'winner': None,
        'move_history': [],
        'start_time': time.time()
    }

# Check if a player won a small board
def check_small_board_win(board, board_idx, player):
    cells = board[board_idx]
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],
        [0,3,6], [1,4,7], [2,5,8],
        [0,4,8], [2,4,6]
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
# Get valid moves
def get_valid_moves(state):
    moves = []
    if state['next_board'] is not None and state['small_board_status'][state['next_board']] is None:
        # Must play in the designated board
        for cell in range(9):
            if state['board'][state['next_board']][cell] == '':
                moves.append((state['next_board'], cell))
    else:
        # Can play in any board that isn't won or drawn
        for board_idx in range(9):
            if state['small_board_status'][board_idx] is None:
                for cell in range(9):
                    if state['board'][board_idx][cell] == '':
                        moves.append((board_idx, cell))
    return moves

# Make a move
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
    
    # FIX: Check if the target board (determined by cell_idx) is still available
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

# Display board with enhanced UI
def display_board(state):
    st.markdown('<div class="board-container">', unsafe_allow_html=True)
    
    for large_row in range(3):
        cols = st.columns([1, 1, 1], gap="small")
        for large_col in range(3):
            board_idx = large_row * 3 + large_col
            with cols[large_col]:
                status = state['small_board_status'][board_idx]
                is_active = state['next_board'] == board_idx if state['next_board'] is not None else False
                
                # Apply board outline styling
                outline_class = 'board-outline-active' if is_active else 'board-outline'
                st.markdown(f'<div class="{outline_class}">', unsafe_allow_html=True)
                
                # Board header
                board_title = f"**Board {board_idx}**"
                if is_active:
                    st.markdown(f"### {board_title} 🎯", unsafe_allow_html=True)
                else:
                    st.markdown(f"### {board_title}", unsafe_allow_html=True)
                
                if status == 'X':
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #ff6b6b, #ee5a6f); 
                                color: white; padding: 30px; border-radius: 15px; 
                                text-align: center; font-size: 24px; font-weight: bold;
                                box-shadow: 0 4px 15px rgba(255,107,107,0.4);'>
                        ❌ HUMAN WINS!
                    </div>
                    """, unsafe_allow_html=True)
                elif status == 'O':
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #4facfe, #00f2fe); 
                                color: white; padding: 30px; border-radius: 15px; 
                                text-align: center; font-size: 24px; font-weight: bold;
                                box-shadow: 0 4px 15px rgba(79,172,254,0.4);'>
                        ⭕ AI WINS!
                    </div>
                    """, unsafe_allow_html=True)
                elif status == 'D':
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #a8a8a8, #c0c0c0); 
                                color: white; padding: 30px; border-radius: 15px; 
                                text-align: center; font-size: 24px; font-weight: bold;
                                box-shadow: 0 4px 15px rgba(168,168,168,0.4);'>
                        🤝 DRAW
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Create 3x3 grid for cells
                    for small_row in range(3):
                        cell_cols = st.columns(3)
                        for small_col in range(3):
                            cell_idx = small_row * 3 + small_col
                            cell_value = state['board'][board_idx][cell_idx]
                            
                            with cell_cols[small_col]:
                                if cell_value == '':
                                    # Empty cell - clickable button with better visibility
                                    if st.button('□', key=f'{board_idx}_{cell_idx}', 
                                               use_container_width=True,
                                               type="primary",
                                               help="Click to place your move"):
                                        if not state['game_over']:
                                            handle_human_move(board_idx, cell_idx)
                                elif cell_value == 'X':
                                    st.markdown("<div style='text-align: center; font-size: 32px; color: #e74c3c; font-weight: bold;'>❌</div>", 
                                              unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='text-align: center; font-size: 32px; color: #3498db; font-weight: bold;'>⭕</div>", 
                                              unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)  # Close board outline
                st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def handle_human_move(board_idx, cell_idx):
    state = st.session_state.game_state
    
    if state['game_over']:
        return
    
    valid_moves = get_valid_moves(state)
    if (board_idx, cell_idx) not in valid_moves:
        st.error("❌ Invalid move! Please select a valid cell.")
        return
    
    make_move(state, board_idx, cell_idx, 'X')
    state['move_history'].append(('Human', board_idx, cell_idx))
    
    if not state['game_over']:
        with st.spinner('🤖 AI is thinking...'):
            time.sleep(0.5)  # Brief pause for better UX
            ai_board, ai_cell = ai_move(state)
            make_move(state, ai_board, ai_cell, 'O')
            state['move_history'].append(('AI', ai_board, ai_cell))
    
    st.rerun()

# Main UI
def main():
    st.set_page_config(
        page_title="Ultimate Tic-Tac-Toe",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    load_css()
    
    # Title
    st.markdown("""
    <h1 style='text-align: center; font-size: 3.5em; margin-bottom: 0;'>
        🎮 Ultimate Tic-Tac-Toe
    </h1>
    <p style='text-align: center; font-size: 1.2em; color: #666; margin-top: 0;'>
        <b>Human vs AI</b> • Powered by Minimax with Alpha-Beta Pruning
    </p>
    """, unsafe_allow_html=True)
    
    # Initialize game state
    if 'game_state' not in st.session_state:
        st.session_state.game_state = init_game()
    
    state = st.session_state.game_state
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Game Control")
        
        if st.button("🔄 New Game", use_container_width=True, type="primary"):
            st.session_state.game_state = init_game()
            st.rerun()
        
        st.markdown("---")
        
        # Game stats
        st.markdown("### 📊 Game Statistics")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{len(state['move_history'])}</div>
                <div class='stat-label'>Moves</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            x_boards = sum(1 for s in state['small_board_status'] if s == 'X')
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{x_boards}</div>
                <div class='stat-label'>Your Boards</div>
            </div>
            """, unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            o_boards = sum(1 for s in state['small_board_status'] if s == 'O')
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{o_boards}</div>
                <div class='stat-label'>AI Boards</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            elapsed = int(time.time() - state['start_time'])
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-number'>{elapsed}s</div>
                <div class='stat-label'>Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Current turn indicator
        st.markdown("### 🎲 Current Status")
        if not state['game_over']:
            st.markdown("""
            <div class='info-box'>
                <h3 style='margin: 0; color: white;'>Your Turn!</h3>
                <p style='margin: 5px 0 0 0; font-size: 0.9em;'>You play as ❌</p>
            </div>
            """, unsafe_allow_html=True)
            
            if state['next_board'] is not None:
                st.warning(f"📍 **Must play in Board {state['next_board']}**")
            else:
                st.success("✨ **Play in any available board!**")
        
        st.markdown("---")
        
        # Move history
        st.markdown("### 📝 Move History")
        if state['move_history']:
            history_container = st.container(height=300)
            with history_container:
                for i, (player, board, cell) in enumerate(reversed(state['move_history'])):
                    icon = '❌' if player == 'Human' else '⭕'
                    color = '#e74c3c' if player == 'Human' else '#3498db'
                    st.markdown(f"""
                    <div class='move-history'>
                        <span style='color: {color}; font-weight: bold;'>{icon} {player}</span>
                        <br>Board {board}, Cell {cell}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No moves yet. Make the first move!")
        
        st.markdown("---")
        
        # How to play
        with st.expander("ℹ️ How to Play"):
            st.markdown("""
            **Rules:**
            1. Win 3 small boards in a row to win
            2. Your move determines where AI plays next
            3. If that board is won/full, AI can play anywhere
            4. You are ❌ (Red), AI is ⭕ (Blue)
            
            **Strategy Tips:**
            - Control the center board
            - Force opponent to less favorable boards
            - Watch for diagonal opportunities
            """)
    
    # Main game area
    display_board(state)
    
    # Game over display
    if state['game_over']:
        if state['winner'] == 'X':
            st.markdown("""
            <div style='text-align: center; margin: 30px 0;'>
                <div class='winner-badge' style='background: linear-gradient(135deg, #ff6b6b, #ee5a6f);'>
                    🎉 CONGRATULATIONS! YOU WIN! 🎉
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()
        elif state['winner'] == 'O':
            st.markdown("""
            <div style='text-align: center; margin: 30px 0;'>
                <div class='winner-badge' style='background: linear-gradient(135deg, #4facfe, #00f2fe);'>
                    🤖 AI WINS! BETTER LUCK NEXT TIME! 🤖
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align: center; margin: 30px 0;'>
                <div class='winner-badge' style='background: linear-gradient(135deg, #a8a8a8, #c0c0c0);'>
                    🤝 IT'S A DRAW! WELL PLAYED! 🤝
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

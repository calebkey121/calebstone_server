from flask import Flask, jsonify, request
from flask_cors import CORS
from game_engine.game import GameManager
from game_engine.controllers import Controller, RandomController
from game_engine.cards import create_deck, DeckType

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store game state globally (for simplicity - in production you'd want proper session handling)
game_manager = None

class WebController(Controller):
    def __init__(self):
        self.pending_action = None
    
    def get_action(self, game_state):
        return self.pending_action
    
    def set_action(self, action):
        self.pending_action = action

# Initialize controllers
player1_controller = WebController()
player2_controller = RandomController()

def init_game():
    global game_manager
    game_manager = GameManager()
    game_manager.player1_controller = player1_controller
    game_manager.player2_controller = player2_controller

def serialize_character(char):
    return {
        'name': char.name,
        'health': char.health,
        'attack': char.attack_value,
        'can_attack': char.can_attack()
    }

def serialize_card(card):
    return {
        'name': card.name,
        'cost': card.cost,
        'health': card.health,
        'attack': card.attack_value,
        'text': card.text
    }

def serialize_player(player):
    return {
        'gold': player.gold,
        'income': player.income,
        'hero': serialize_character(player.hero),
        'army': [serialize_character(ally) for ally in player.army.allies],
        'hand': [serialize_card(card) for card in player._hand]
    }

@app.route('/game_state')
def get_game_state():
    if game_manager is None:
        init_game()
    
    game_state = game_manager.game_state
    return jsonify({
        'current_player': serialize_player(game_state.current_player),
        'opponent_player': serialize_player(game_state.opponent_player),
        'current_round': game_state.current_round,
        'is_game_over': game_manager.is_game_over()
    })

@app.route('/action', methods=['POST'])
def handle_action():
    action = request.json
    
    # Set the action for the current player's controller
    if game_manager.game_state.is_player1_turn():
        player1_controller.set_action(action)
    else:
        player2_controller.set_action(action)
    
    # Process one step of the game
    game_manager.process_turn()
    
    return jsonify({'status': 'success'})

@app.route('/new_game', methods=['POST'])
def new_game():
    init_game()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)

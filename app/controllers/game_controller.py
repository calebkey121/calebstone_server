# server/app/controllers/game_controller.py
from game_engine.game import GameManager
from game_engine.controllers import Controller, WebController
from game_engine.cards import create_deck, DeckType

class GameController:
    def __init__(self):
        self.games = {}  # Store multiple games by session_id
    
    def create_game(self, session_id):
        player1_controller = WebController()
        player2_controller = WebController()
        
        game = GameManager(player1_controller=player1_controller, player2_controller=player2_controller)
        
        self.games[session_id] = {
            'manager': game,
            'controllers': {
                'player1': player1_controller,
                'player2': player2_controller
            }
        }
        
        return {'session_id': session_id}
    
    def get_game_state(self, session_id):
        if session_id not in self.games:
            return {'error': 'Game not found'}
            
        game = self.games[session_id]['manager']
        return self._serialize_game_state(game.game_state)
    
    def process_action(self, session_id, action):
        if session_id not in self.games:
            return {'error': 'Game not found'}
            
        game = self.games[session_id]
        current_player = 'player1' if game['manager'].game_state.is_player1_turn() else 'player2'
        controller = game['controllers'][current_player]
        
        # Set the action in the controller
        controller.set_action(action)
        
        # Process the turn
        is_turn_complete = game['manager'].process_turn()
        
        return {
            'status': 'success',
            'is_turn_complete': is_turn_complete,
            'game_state': self._serialize_game_state(game['manager'].game_state)
        }
    
    def _serialize_game_state(self, game_state):
        # Convert your game state to JSON-serializable format
        return {
            'current_player': self._serialize_player(game_state.current_player),
            'opponent_player': self._serialize_player(game_state.opponent_player),
            'current_round': game_state.current_round,
            'is_game_over': game_state.get_result() != 'IN_PROGRESS'
        }
    
    def _serialize_player(self, player):
        return {
            'gold': player.gold,
            'income': player.income,
            'hero': {
                'name': player.hero.name,
                'health': player.hero.health,
                'attack': player.hero.attack_value,
                'can_attack': player.hero.can_attack()
            },
            'army': [{
                'name': ally.name,
                'health': ally.health,
                'attack': ally.attack_value,
                'can_attack': ally.can_attack()
            } for ally in player.army.allies],
            'hand': [{
                'name': card.name,
                'cost': card.cost,
                'health': card.health,
                'attack': card.attack_value,
                'text': card.text
            } for card in player._hand]
        }

# server/app/controllers/game_controller.py
from game_engine.game import GameManager
from game_engine.cards import create_deck, DeckType
from threading import Thread

class GameController:
    def __init__(self):
        self.games = {}  # Store multiple games by session_id
    
    def create_game(self, session_id):
        """Start a new game in a separate thread."""
        game_thread = Thread(target=self.run_game, args=(session_id,))
        game_thread.daemon = True  # Ensures the thread exits when the main program exits
        game_thread.start()
        return {'session_id': session_id}
    
    def run_game(self, session_id):
        """Function to run the game loop for a session."""
        game = GameManager()
        
        # Store the game in the dictionary
        self.games[session_id] = {
            'manager': game,
            'controllers': {
                'player1': game.player1_controller.type,
                'player2': game.player2_controller.type
            }
        }
        
        # Start the game loop
        game.run_game()  # This will keep running until the game ends
        
        # Clean up after the game is over
        del self.games[session_id]
    
    def get_game_state(self, session_id):
        if session_id not in self.games:
            return {'error': 'Game not found'}
            
        game = self.games[session_id]['manager']
        return self._serialize_game_state(game.game_state)
    
    def process_action(self, session_id, action):
        if session_id not in self.games:
            return {'error': 'Game not found'}
            
        game = self.games[session_id]
        # uncomment
        # current_player = 'player1' if game['manager'].game_state.is_player1_turn() else 'player2'
        # controller = game['controllers'][current_player]
        controller = game['manager'].player1_controller # change from hardcoding
        
        # Set the action in the controller
        controller.set_action(action)
        
        return {
            'status': 'success',
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

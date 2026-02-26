# server/app/controllers/game_controller.py
from calebstone_engine.game.game_manager import GameManager
from calebstone_engine.game.game_state import GameResult
from calebstone_engine.config import PlayerConfig
#from calebstone_engine.cards import create_deck, DeckType
from threading import Thread

import time

class GameController:
    def __init__(self):
        self.games = {}  # Store multiple games by session_id
    
    def create_game(self, session_id, p1_type="random", p2_type="random"):
        """Start a new game in a separate thread."""
        game_thread = Thread(target=self.run_game, args=(session_id, p1_type, p2_type))
        game_thread.daemon = True  # Ensures the thread exits when the main program exits
        game_thread.start()
        return {'session_id': session_id}
    
    def run_game(self, session_id, p1_type, p2_type):
        """Function to run the game loop for a session."""
        p1_cfg = PlayerConfig(
            player_id="p1",
            controller=p1_type,
            hero="Caleb",
        )
        p2_cfg = PlayerConfig(
            player_id="p2",
            controller=p2_type,
            hero="Dio",
        )
        game = GameManager(p1_config=p1_cfg, p2_config=p2_cfg)
        
        # Store the game in the dictionary
        self.games[session_id] = {
            'manager': game,
            'controllers': {
                'player1': game.p1_controller.type,
                'player2': game.p2_controller.type
            }
        }
        
        # Start the game loop
        game.run_game()  # This will keep running until the game ends
        
        # At end of game, update the game status and result
        result = game.game_state.get_result()
        entry = self.games.get(session_id)
        if entry is not None:
            entry["status"] = "finished"
            entry["finished_at"] = time.time()
            entry["result"] = result.name.lower()  # "in_progress" / "tie" / "p1_win" / "p2_win"
    
    def get_game_state(self, session_id):
        if session_id not in self.games:
            return {'error': 'Game not found'}

        entry = self.games[session_id]
        game = entry['manager']
        state = self._serialize_game_state(game.game_state)
        state["status"] = entry.get("status", "running")
        state["result"] = entry.get("result", "in_progress")
        state["finished_at"] = entry.get("finished_at")
        return state
    
    def process_action(self, session_id, action):
        if session_id not in self.games:
            return {'error': 'Game not found'}
        
        game = self.games[session_id]
        if game.get("status") == "finished":
            return {
                "error": "Game is finished",
                "status": "finished",
                "result": game.get("result"),
                "game_state": self._serialize_game_state(game["manager"].game_state),
            }
            
        game = self.games[session_id]
        # uncomment
        # current_player = 'player1' if game['manager'].game_state.is_p1_turn() else 'player2'
        # controller = game['controllers'][current_player]
        p1_turn = game['manager'].game_state.current_player == game['manager'].game_state.p1
        controller = game['manager'].p1_controller if p1_turn else game['manager'].p2_controller
        
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
            'opposing_player': self._serialize_player(game_state.opposing_player),
            'current_round': game_state.current_round,
            'is_game_over': game_state.get_result() != GameResult.IN_PROGRESS
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

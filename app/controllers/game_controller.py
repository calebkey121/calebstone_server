# server/app/controllers/game_controller.py
from calebstone_engine.game.game_manager import GameManager
from calebstone_engine.game.game_state import GameResult
from calebstone_engine.config import PlayerConfig
#from calebstone_engine.cards import create_deck, DeckType
from threading import Thread

import time
import uuid as _uuid

SCHEMA_VERSION = 1
ACTION_WAIT_TIMEOUT_SECONDS = 2.0

class GameController:
    def __init__(self):
        self.games = {}  # Store multiple games by session_id

    def _wrap_response(self, session_id, payload: dict) -> dict:
        """Prepend schema_version, game_state_version, and session_id to every response."""
        entry = self.games.get(session_id)
        if entry is not None:
            entry["game_state_version"] = entry.get("game_state_version", 0) + 1
            gsv = entry["game_state_version"]
        else:
            gsv = 1
        return {
            "schema_version": SCHEMA_VERSION,
            "game_state_version": gsv,
            "session_id": session_id,
            **payload,
        }

    def create_game(self, session_id, p1_type="random", p2_type="random"):
        """Start a new game in a separate thread."""
        # Seed the session entry so _wrap_response can increment game_state_version from 0.
        self.games[session_id] = {"game_state_version": 0}
        game_thread = Thread(target=self.run_game, args=(session_id, p1_type, p2_type))
        game_thread.daemon = True  # Ensures the thread exits when the main program exits
        game_thread.start()
        return self._wrap_response(session_id, {})
    
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

        # Merge into existing entry to preserve game_state_version counter.
        entry = self.games.setdefault(session_id, {})
        entry['manager'] = game
        entry['controllers'] = {
            'player1': game.p1_controller.type,
            'player2': game.p2_controller.type
        }

        # Assign stable instance_ids to all cards currently in hand + army.
        # Map: id(python_obj) -> instance_id string. Grows as new objects appear.
        instance_ids = {}
        for player in (game.game_state.p1, game.game_state.p2):
            for card in player._hand:
                instance_ids[id(card)] = f"iid-{_uuid.uuid4().hex[:12]}"
            for ally in player.army.allies:
                instance_ids[id(ally)] = f"iid-{_uuid.uuid4().hex[:12]}"
        entry['instance_ids'] = instance_ids

        # Start the game loop
        game.run_game()  # This will keep running until the game ends
        
        # At end of game, update the game status and result
        result = game.game_state.get_result()
        entry = self.games.get(session_id)
        if entry is not None:
            entry["status"] = "finished"
            entry["finished_at"] = time.time()
            entry["result"] = result.name.lower()  # "in_progress" / "tie" / "p1_win" / "p2_win"
    
    def _get_or_assign_iid(self, entry, obj):
        """Return the stable instance_id for obj, creating one if first seen."""
        iids = entry['instance_ids']
        key = id(obj)
        if key not in iids:
            iids[key] = f"iid-{_uuid.uuid4().hex[:12]}"
        return iids[key]

    def get_game_state(self, session_id):
        if session_id not in self.games:
            return {'error': 'Game not found'}

        entry = self.games[session_id]
        if 'manager' not in entry:
            # Background thread hasn't initialised yet — return envelope with empty game_state.
            return self._wrap_response(session_id, {
                'status': 'starting',
                'game_state': {},
                'legal_actions': [],
            })
        game = entry['manager']
        payload = self._serialize_game_state(game.game_state, entry)
        payload["status"] = entry.get("status", "running")
        payload["result"] = entry.get("result", "in_progress")
        payload["finished_at"] = entry.get("finished_at")
        payload["legal_actions"] = [] if payload["status"] == "finished" else self._build_legal_actions(entry)
        return self._wrap_response(session_id, payload)

    def process_action(self, session_id, action):
        if session_id not in self.games:
            return {'error': 'Game not found'}

        entry = self.games[session_id]
        if 'manager' not in entry:
            return self._wrap_response(session_id, {
                'status': 'starting',
                'game_state': {},
                'legal_actions': [],
            })

        if entry.get("status") == "finished":
            return self._wrap_response(session_id, {
                "error": "Game is finished",
                "status": "finished",
                "result": entry.get("result"),
                "game_state": self._serialize_game_state(entry["manager"].game_state, entry),
                "legal_actions": [],
            })

        # Reject legacy index-based payloads.
        if action and any(k in action for k in ("card_index", "attacker_index", "target_index")):
            return {"error": "index-based actions are not supported; use instance_id fields", "status": 400}, 400

        # Translate instance_id fields to engine indices before forwarding.
        engine_action = self._translate_action(entry, action)
        if engine_action is None:
            return {"error": "unknown or untranslatable instance_id in action", "status": 400}, 400

        manager = entry["manager"]
        try:
            submit_result = manager.submit_action_and_wait(
                engine_action,
                timeout=ACTION_WAIT_TIMEOUT_SECONDS,
            )
        except AttributeError:
            return {
                "error": "engine missing submit_action_and_wait(action, timeout)",
                "status": 500,
            }, 500

        if submit_result is False:
            return {"error": "action rejected", "status": 422}, 422

        if isinstance(submit_result, dict) and not submit_result.get("applied", True):
            status = int(submit_result.get("status", 422))
            return {
                "error": submit_result.get("error", "action rejected"),
                "status": status,
            }, status

        return self._wrap_response(session_id, {
            'status': 'success',
            'game_state': self._serialize_game_state(manager.game_state, entry),
            'legal_actions': self._build_legal_actions(entry),
        })

    def _translate_action(self, entry, action):
        """Convert an instance_id-based action dict to engine index-based format.

        Returns the translated dict, or None if a required instance_id is not found.
        end_turn passes through unchanged (no IDs involved).
        """
        if not action:
            return None
        action_type = action.get("type")

        if action_type == "end_turn":
            return {"type": "end_turn"}

        if action_type == "play_card":
            iid = action.get("card_instance_id")
            if iid is None:
                return None
            idx = self._iid_to_hand_index(entry, iid)
            if idx is None:
                return None
            return {"type": "play_card", "card_index": idx}

        if action_type == "attack":
            attacker_iid = action.get("attacker_id")
            target_iid = action.get("target_id")
            if attacker_iid is None or target_iid is None:
                return None
            attacker_idx = self._iid_to_army_index(entry, attacker_iid)
            target_idx = self._iid_to_enemy_index(entry, target_iid)
            if attacker_idx is None or target_idx is None:
                return None
            return {"type": "attack", "attacker_index": attacker_idx, "target_index": target_idx}

        # Unknown action type — pass through as-is (engine will reject it).
        return action

    def _build_legal_actions(self, entry):
        """Translate engine legal actions (index-based) to API legal actions (instance_id-based)."""
        manager = entry["manager"]
        if hasattr(manager, "get_legal_actions"):
            actions = manager.get_legal_actions()
        else:
            actions = manager.game_state.possible_actions()

        if not isinstance(actions, list):
            return []

        legal_actions = []
        for action in actions:
            wire_action = self._engine_action_to_wire_action(entry, action)
            if wire_action is not None:
                legal_actions.append(wire_action)
        return legal_actions

    def _engine_action_to_wire_action(self, entry, action):
        if not isinstance(action, dict):
            return None

        action_type = action.get("type")
        gs = entry["manager"].game_state

        if action_type == "end_turn":
            return {"type": "end_turn"}

        if action_type == "play_card":
            card_index = action.get("card_index")
            if not isinstance(card_index, int):
                return None
            hand = gs.current_player._hand
            if card_index < 0 or card_index >= len(hand):
                return None
            card = hand[card_index]
            return {
                "type": "play_card",
                "card_instance_id": self._get_or_assign_iid(entry, card),
            }

        if action_type == "attack":
            attacker_index = action.get("attacker_index")
            target_index = action.get("target_index")
            if not isinstance(attacker_index, int) or not isinstance(target_index, int):
                return None
            attackers = gs.current_player.all_characters()
            targets = gs.opposing_player.all_characters()
            if attacker_index < 0 or attacker_index >= len(attackers):
                return None
            if target_index < 0 or target_index >= len(targets):
                return None
            attacker = attackers[attacker_index]
            target = targets[target_index]
            return {
                "type": "attack",
                "attacker_id": self._get_or_assign_iid(entry, attacker),
                "target_id": self._get_or_assign_iid(entry, target),
            }

        return None

    def _iid_to_hand_index(self, entry, iid):
        gs = entry['manager'].game_state
        player = gs.current_player
        for i, card in enumerate(player._hand):
            if entry['instance_ids'].get(id(card)) == iid:
                return i
        return None

    def _iid_to_army_index(self, entry, iid):
        """Attacker is always the current player. index 0 = hero, 1+ = allies."""
        gs = entry['manager'].game_state
        player = gs.current_player
        if entry['instance_ids'].get(id(player.hero)) == iid:
            return 0
        for i, ally in enumerate(player.army.allies):
            if entry['instance_ids'].get(id(ally)) == iid:
                return i + 1
        return None

    def _iid_to_enemy_index(self, entry, iid):
        """Target is always the opposing player. index 0 = hero, 1+ = allies."""
        gs = entry['manager'].game_state
        player = gs.opposing_player
        if entry['instance_ids'].get(id(player.hero)) == iid:
            return 0
        for i, ally in enumerate(player.army.allies):
            if entry['instance_ids'].get(id(ally)) == iid:
                return i + 1
        return None

    def _serialize_game_state(self, game_state, entry):
        game_result = game_state.get_result()
        winner_player_id = None
        if game_result == GameResult.P1_WIN:
            winner_player_id = game_state.p1._config.player_id
        elif game_result == GameResult.P2_WIN:
            winner_player_id = game_state.p2._config.player_id

        active_player_id = None
        if game_state.current_player is not None:
            active_player_id = game_state.current_player._config.player_id

        # Seat-stable snapshots (recommended for clients): never flip with turn.
        p1_state = self._serialize_player(game_state.p1, entry)
        p2_state = self._serialize_player(game_state.p2, entry)

        # Turn-relative views (legacy compatibility with current clients).
        current_player_state = p1_state
        opposing_player_state = p2_state
        if active_player_id == game_state.p2._config.player_id:
            current_player_state = p2_state
            opposing_player_state = p1_state

        # Convert your game state to JSON-serializable format
        return {
            'players': {
                'p1': p1_state,
                'p2': p2_state,
            },
            'current_player': current_player_state,
            'opposing_player': opposing_player_state,
            'round': game_state.current_round,
            'is_game_over': game_result != GameResult.IN_PROGRESS,
            'active_player_id': active_player_id,
            'winner_player_id': winner_player_id,
        }

    def _serialize_player(self, player, entry):
        return {
            'player_id': player._config.player_id,
            'gold': player.gold,
            'income': player.income,
            'deck_count': player.deck_size(),
            'hero': {
                'instance_id': self._get_or_assign_iid(entry, player.hero),
                'name': player.hero.name,
                'health': player.hero.health,
                'max_health': player.hero.max_health,
                'attack': player.hero.attack_value,
                'can_attack': player.hero.can_attack()
            },
            'army': [{
                'instance_id': self._get_or_assign_iid(entry, ally),
                'card_id': ally.id.name.lower() if ally.id is not None else None,
                'name': ally.name,
                'cost': ally.cost,
                'health': ally.health,
                'attack': ally.attack_value,
                'text': ally.text,
                'can_attack': ally.can_attack(),
                'zone': 'army',
                'tags': [],
            } for ally in player.army.allies],
            'hand': [{
                'instance_id': self._get_or_assign_iid(entry, card),
                'card_id': card.id.name.lower() if card.id is not None else None,
                'name': card.name,
                'cost': card.cost,
                'health': card.health,
                'attack': card.attack_value,
                'text': card.text,
                'zone': 'hand',
                'tags': [],
            } for card in player._hand]
        }

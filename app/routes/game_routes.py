# server/app/routes/game_routes.py
from flask import Blueprint, jsonify, request
from app.controllers.game_controller import GameController
from calebstone_engine.cards.cards import CARD_CATALOG
import uuid

game_routes = Blueprint('game', __name__)
game_controller = GameController()

@game_routes.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy!"}), 200

@game_routes.route('/new_game', methods=['POST'])
def new_game():
    data = request.get_json(silent=True) or {}
    p1_type = data.get('player1_controller', 'human')
    p2_type = data.get('player2_controller', 'random')

    session_id = str(uuid.uuid4())
    result = game_controller.create_game(session_id, p1_type, p2_type)
    return jsonify(result)

@game_routes.route('/game_state/<session_id>', methods=['GET'])
def get_game_state(session_id):
    state = game_controller.get_game_state(session_id)
    if 'error' in state and state.get('error') == 'Game not found':
        return jsonify(state), 404
    return jsonify(state)

@game_routes.route('/game_state', methods=['GET'])
def get_all_game_states():
    session_ids = list(game_controller.games.keys())
    return jsonify(session_ids)

@game_routes.route('/turn_history/<session_id>', methods=['GET'])
def get_turn_history(session_id):
    history = game_controller.get_turn_history(session_id)
    if 'error' in history and history.get('error') == 'Game not found':
        return jsonify(history), 404
    return jsonify(history)

@game_routes.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    result = game_controller.delete_session(session_id)
    if isinstance(result, tuple):
        body, status = result
        return jsonify(body), status
    return jsonify(result)

@game_routes.route('/action/<session_id>', methods=['POST'])
def handle_action(session_id):
    action = request.json
    result = game_controller.process_action(session_id, action)
    # process_action may return (dict, status_code) for 400 errors.
    if isinstance(result, tuple):
        body, status = result
        return jsonify(body), status
    return jsonify(result)

@game_routes.route('/card_library', methods=['GET'])
def get_card_library():
    cards = []
    for card in CARD_CATALOG.values():
        entry = {
            "card_id": card.id.name.lower(),
            "name": card.name,
            "cost": card.cost,
            "attack": card.attack_value,
            "health": card.health,
            "tags": [],
        }
        if card.text:
            entry["text"] = card.text
        cards.append(entry)
    return jsonify({
        "schema_version": 1,
        "cardset_version": 1,
        "cards": cards,
    })

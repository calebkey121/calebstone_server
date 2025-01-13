# server/app/routes/game_routes.py
from flask import Blueprint, jsonify, request
from app.controllers.game_controller import GameController
import uuid

game_routes = Blueprint('game', __name__)
game_controller = GameController()

@game_routes.route('/new_game', methods=['POST'])
def new_game():
    session_id = str(uuid.uuid4())
    result = game_controller.create_game(session_id)
    return jsonify(result)

@game_routes.route('/game_state/<session_id>', methods=['GET'])
def get_game_state(session_id):
    state = game_controller.get_game_state(session_id)
    return jsonify(state)

@game_routes.route('/game_state', methods=['GET'])
def get_all_game_states():
    session_ids = list(game_controller.games.keys())
    return jsonify(session_ids)

@game_routes.route('/action/<session_id>', methods=['POST'])
def handle_action(session_id):
    action = request.json
    result = game_controller.process_action(session_id, action)
    return jsonify(result)

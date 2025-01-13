from flask import Blueprint, jsonify
from game_engine.cards import CARD_CATALOG

card_routes = Blueprint('cards', __name__)

@card_routes.route('/cards', methods=['GET'])
def get_all_cards():
    cards_data = {}
    for key, card in CARD_CATALOG.items():
        cards_data[key] = {
            'name': card.name,
            'cost': card.cost,
            'attack_value': card.attack_value,
            'health': card.health,
            'effect_text': card.text if card.text else "No effect",
            'type': 'Ally'  # Can be extended if we add more card types
        }
    return jsonify(cards_data)

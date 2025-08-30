# server/app/routes/game_routes.py
from flask import Blueprint, jsonify, request
from app.controllers.game_controller import GameController
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

# fix this to come from calebstone_engine or something
@game_routes.route('/card_library', methods=['GET'])
def get_card_library():
    return jsonify({
  "default": {
	"name": "Default Card",
	"art_texture": "WyndhavenEnclave",
	"attack": 10,
	"health": 15,
	"cost": 2,
	"text": "A generic card."
  },
  "Wyndhaven Enclave": {
	"name": "Wyndhaven Enclave",
	"art_texture": "WyndhavenEnclave",
	"attack": 23,
	"health": 39,
	"cost": 4,
	"text": "A stronghold of the noble houses, fortified against the darkness beyond."
  },
  "Ruthless Baroness": {
	"name": "Ruthless Baroness",
	"art_texture": "WyndhavenEnclave",
	"attack": 35,
	"health": 17,
	"cost": 3,
	"text": "Her icy gaze commands the loyalty of the desperate and the depraved."
  },
  "Underground Kingpin": {
	"name": "Underground Kingpin",
	"art_texture": "WyndhavenEnclave",
	"attack": 8,
	"health": 29,
	"cost": 2,
	"text": "Strings of power tug at the shadows, manipulating the flow of coin and goods."
  },
  "Crown's Secretkeeper": {
	"name": "Crown's Secretkeeper",
	"art_texture": "WyndhavenEnclave",
	"attack": 13,
	"health": 22,
	"cost": 3,
	"text": "Whispers and rumors are her currency, trading favors to maintain the monarch's grip on power."
  },
  "Forgebound Smith": {
	"name": "Forgebound Smith",
	"art_texture": "WyndhavenEnclave",
	"attack": 27,
	"health": 31,
	"cost": 4,
	"text": "Tempered in the heart of the forge, her weapons are as lethal as they are beautiful."
  },
  "Guild Enforcer": {
	"name": "Guild Enforcer",
	"art_texture": "WyndhavenEnclave",
	"attack": 19,
	"health": 12,
	"cost": 3,
	"text": "Brutal and unyielding, the Guild's enforcers maintain order through fear and intimidation."
  },
  "Plague Doctor": {
	"name": "Plague Doctor",
	"art_texture": "WyndhavenEnclave",
	"attack": 7,
	"health": 41,
	"cost": 2,
	"text": "Garbed in the dark robes of a healer, but harboring a sinister purpose."
  },
  "Bandit Outlaw": {
	"name": "Bandit Outlaw",
	"art_texture": "WyndhavenEnclave",
	"attack": 33,
	"health": 26,
	"cost": 4,
	"text": "A life on the wrong side of the law has honed her skills, but hardened her heart."
  },
  "Banshee's Wail": {
	"name": "Banshee's Wail",
	"art_texture": "WyndhavenEnclave",
	"attack": 15,
	"health": 9,
	"cost": 2,
	"text": "A chilling cry that pierces the veil, heralding the arrival of the restless dead."
  },
  "Bone Collector": {
	"name": "Bone Collector",
	"art_texture": "WyndhavenEnclave",
	"attack": 21,
	"health": 37,
	"cost": 3,
	"text": "Gathering the remains of the fallen, empowered by the spirits of the departed."
  },
  "Bow Marshal": {
	"name": "Bow Marshal",
	"art_texture": "WyndhavenEnclave",
	"attack": 11,
	"health": 24,
	"cost": 3,
	"text": "A skilled archer sworn to defend the realm, ever vigilant against unseen threats."
  },
  "Castle Ward": {
	"name": "Castle Ward",
	"art_texture": "WyndhavenEnclave",
	"attack": 29,
	"health": 14,
	"cost": 4,
	"text": "Stalwart defenders of the keep, their blades and shields form an unyielding bulwark."
  },
  "Court Alchemist": {
	"name": "Court Alchemist",
	"art_texture": "WyndhavenEnclave",
	"attack": 5,
	"health": 19,
	"cost": 2,
	"text": "Concocting potent elixirs and volatile compounds, a master of the arcane."
  },
  "Crypt Creeper": {
	"name": "Crypt Creeper",
	"art_texture": "WyndhavenEnclave",
	"attack": 18,
	"health": 6,
	"cost": 2,
	"text": "A ghastly apparition, drawn from the depths of the earth to do its master's bidding."
  },
  "Cursed Squire": {
	"name": "Cursed Squire",
	"art_texture": "WyndhavenEnclave",
	"attack": 31,
	"health": 13,
	"cost": 4,
	"text": "A knight's former companion, haunting the mortal realm, cursed to remain earthbound."
  },
  "Dire Wolf": {
	"name": "Dire Wolf",
	"art_texture": "WyndhavenEnclave",
	"attack": 20,
	"health": 34,
	"cost": 3,
	"text": "A massive, savage predator prowling the wilderness, driven by an insatiable hunger."
  },
  "Ghoul Vanguard": {
	"name": "Ghoul Vanguard",
	"art_texture": "WyndhavenEnclave",
	"attack": 14,
	"health": 28,
	"cost": 3,
	"text": "Decaying corpses, animated by dark magic, serve as the first line of defense."
  },
  "Ghostly Raider": {
	"name": "Ghostly Raider",
	"art_texture": "WyndhavenEnclave",
	"attack": 9,
	"health": 42,
	"cost": 2,
	"text": "The restless spirit of a fallen soldier, compelled to haunt the mortal realm."
  },
  "Graveyard Sentinel": {
	"name": "Graveyard Sentinel",
	"art_texture": "WyndhavenEnclave",
	"attack": 25,
	"health": 11,
	"cost": 4,
	"text": "A guardian from beyond the veil, tasked with protecting the sanctity of the dead."
  },
  "Highland Scout": {
	"name": "Highland Scout",
	"art_texture": "WyndhavenEnclave",
	"attack": 16,
	"health": 30,
	"cost": 3,
	"text": "Skilled in the ways of the wilderness, a keen observer of the land and its secrets."
  },
  "Highwayman's Ambush": {
	"name": "Highwayman's Ambush",
	"art_texture": "WyndhavenEnclave",
	"attack": 22,
	"health": 8,
	"cost": 3,
	"text": "A sudden strike from the shadows, preying on the unwary and the vulnerable."
  },
  "Jousting Champion": {
	"name": "Jousting Champion",
	"art_texture": "WyndhavenEnclave",
	"attack": 37,
	"health": 21,
	"cost": 4,
	"text": "A skilled warrior renowned for her prowess in the tournament, a master of the lance."
  },
  "Mercenary Captain": {
	"name": "Mercenary Captain",
	"art_texture": "WyndhavenEnclave",
	"attack": 12,
	"health": 36,
	"cost": 3,
	"text": "Leading a band of hardened soldiers, her loyalty lies with the highest bidder."
  },
  "Mournful Spirit": {
	"name": "Mournful Spirit",
	"art_texture": "WyndhavenEnclave",
	"attack": 28,
	"health": 10,
	"cost": 4,
	"text": "A sorrowful wraith, forever haunted by the anguish of its mortal existence."
  },
  "Necromancer of the Forgotten Depths": {
	"name": "Necromancer of the Forgotten Depths",
	"art_texture": "WyndhavenEnclave",
	"attack": 40,
	"health": 14,
	"cost": 5,
	"text": "A master of the dark arts, commanding the legions of the undead from the deepest chasms."
  },
  "Necromancer of the Vale": {
	"name": "Necromancer of the Vale",
	"art_texture": "WyndhavenEnclave",
	"attack": 26,
	"health": 20,
	"cost": 4,
	"text": "A twisted practitioner of necromantic sorcery, raising the dead to do her bidding."
  },
  "Necropolis Guard": {
	"name": "Necropolis Guard",
	"art_texture": "WyndhavenEnclave",
	"attack": 32,
	"health": 18,
	"cost": 4,
	"text": "Skeletal sentinels, sworn to protect the sacred crypts and tombs from desecration."
  },
  "Phantom Steed": {
	"name": "Phantom Steed",
	"art_texture": "WyndhavenEnclave",
	"attack": 15,
	"health": 27,
	"cost": 3,
	"text": "A ghostly mount, summoned from the ether to carry its rider into the fray."
  },
  "Revenant Archer": {
	"name": "Revenant Archer",
	"art_texture": "WyndhavenEnclave",
	"attack": 24,
	"health": 16,
	"cost": 3,
	"text": "A restless spirit, wielding a bow with unerring accuracy, driven by an undying purpose."
  },
  "Royal Falconer": {
	"name": "Royal Falconer",
	"art_texture": "WyndhavenEnclave",
	"attack": 17,
	"health": 23,
	"cost": 3,
	"text": "A skilled hunter, commanding a fierce raptor as an extension of her own will."
  },
  "Shadow of the Past": {
	"name": "Shadow of the Past",
	"art_texture": "WyndhavenEnclave",
	"attack": 30,
	"health": 8,
	"cost": 4,
	"text": "A spectral echo, whispers of a bygone era, haunting the present with memories of the past."
  },
  "Siege Engineer": {
	"name": "Siege Engineer",
	"art_texture": "WyndhavenEnclave",
	"attack": 19,
	"health": 25,
	"cost": 3,
	"text": "A master of siege weaponry, capable of raining destruction upon the enemy's fortifications."
  },
  "Skeletal Knight": {
	"name": "Skeletal Knight",
	"art_texture": "WyndhavenEnclave",
	"attack": 36,
	"health": 15,
	"cost": 4,
	"text": "A fallen champion, returned from the grave, driven by an undying loyalty to its lord."
  },
  "Spectral Ferryman": {
	"name": "Spectral Ferryman",
	"art_texture": "WyndhavenEnclave",
	"attack": 13,
	"health": 33,
	"cost": 3,
	"text": "A ghostly figure, tasked with guiding the souls of the departed across the river Styx."
  },
  "Tomb Warden": {
	"name": "Tomb Warden",
	"art_texture": "WyndhavenEnclave",
	"attack": 22,
	"health": 21,
	"cost": 3,
	"text": "An ancient guardian, sworn to protect the sanctity of the dead and the secrets they hold."
  },
  "Undead Creature": {
	"name": "Undead Creature",
	"art_texture": "WyndhavenEnclave",
	"attack": 27,
	"health": 19,
	"cost": 4,
	"text": "A shambling husk, animated by dark magic, driven by an insatiable hunger for the living."
  },
  "Village Blacksmith": {
	"name": "Village Blacksmith",
	"art_texture": "WyndhavenEnclave",
	"attack": 14,
	"health": 31,
	"cost": 3,
	"text": "A skilled artisan, forging sturdy blades and armor to equip the defenders of the realm."
  },
  "Wandering Minstrel": {
	"name": "Wandering Minstrel",
	"art_texture": "WyndhavenEnclave",
	"attack": 6,
	"health": 38,
	"cost": 2,
	"text": "A traveling bard, weaving tales of heroism and tragedy, bringing news and entertainment."
  },
  "Icelord of Despair": {
	"name": "Icelord of Despair",
	"art_texture": "WyndhavenEnclave",
	"attack": 43,
	"health": 22,
	"cost": 5,
	"text": "A cruel and relentless tyrant, his icy grip extends over the frozen wastes, crushing all who stand in his path."
  }
}
)

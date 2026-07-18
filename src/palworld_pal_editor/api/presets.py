from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from palworld_pal_editor.passive_presets import (
    create_active_preset,
    create_preset,
    delete_active_preset,
    delete_preset,
    import_active_document,
    import_document,
    load_active_document,
    load_document,
    update_active_preset,
    update_preset,
)
from palworld_pal_editor.utils.util import reply


presets_blueprint = Blueprint("presets", __name__)


@presets_blueprint.route("/passives", methods=["GET"])
@jwt_required()
def get_passive_presets():
    return reply(0, load_document())


@presets_blueprint.route("/passives", methods=["POST"])
@jwt_required()
def post_passive_preset():
    try:
        return reply(0, create_preset(request.get_json(silent=True) or {}))
    except ValueError as error:
        return reply(1, None, str(error)), 400


@presets_blueprint.route("/passives/<preset_id>", methods=["PATCH"])
@jwt_required()
def patch_passive_preset(preset_id):
    try:
        return reply(0, update_preset(preset_id, request.get_json(silent=True) or {}))
    except KeyError as error:
        return reply(1, None, str(error)), 404
    except ValueError as error:
        return reply(1, None, str(error)), 400


@presets_blueprint.route("/passives/<preset_id>", methods=["DELETE"])
@jwt_required()
def remove_passive_preset(preset_id):
    try:
        delete_preset(preset_id)
        return reply(0)
    except KeyError as error:
        return reply(1, None, str(error)), 404


@presets_blueprint.route("/passives/import", methods=["POST"])
@jwt_required()
def import_passive_presets():
    payload = request.get_json(silent=True) or {}
    try:
        return reply(0, import_document(payload.get("document", payload), bool(payload.get("replace", False))))
    except ValueError as error:
        return reply(1, None, str(error)), 400


@presets_blueprint.route("/actives", methods=["GET"])
@jwt_required()
def get_active_presets():
    return reply(0, load_active_document())


@presets_blueprint.route("/actives", methods=["POST"])
@jwt_required()
def post_active_preset():
    try:
        return reply(0, create_active_preset(request.get_json(silent=True) or {}))
    except ValueError as error:
        return reply(1, None, str(error)), 400


@presets_blueprint.route("/actives/<preset_id>", methods=["PATCH"])
@jwt_required()
def patch_active_preset(preset_id):
    try:
        return reply(0, update_active_preset(preset_id, request.get_json(silent=True) or {}))
    except KeyError as error:
        return reply(1, None, str(error)), 404
    except ValueError as error:
        return reply(1, None, str(error)), 400


@presets_blueprint.route("/actives/<preset_id>", methods=["DELETE"])
@jwt_required()
def remove_active_preset(preset_id):
    try:
        delete_active_preset(preset_id)
        return reply(0)
    except KeyError as error:
        return reply(1, None, str(error)), 404


@presets_blueprint.route("/actives/import", methods=["POST"])
@jwt_required()
def import_active_presets():
    payload = request.get_json(silent=True) or {}
    try:
        return reply(0, import_active_document(payload.get("document", payload), bool(payload.get("replace", False))))
    except ValueError as error:
        return reply(1, None, str(error)), 400

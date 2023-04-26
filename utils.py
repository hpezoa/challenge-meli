from flask import abort, jsonify
import db as database
from bson.objectid import ObjectId

client = database.init()
profiles_collection = client["profiles"]

def check_permissions(profile_id, required_permissions, app):
    print(profile_id)
    try:
        profile_id = ObjectId(profile_id)
        print("exito")
    except:
        print("fallo")
        return jsonify({'error': 'Invalid profile ID format'}), 400
    print(profile_id)
    profile = profiles_collection.find_one({'_id': profile_id})
    print(profile)
    if not profile:
        abort(403, 'Profile not found')
    for permission in required_permissions:
        print(profile['permissions'])
        if permission not in profile['permissions'][app]:
            abort(403, f"Permission '{permission}' required")

def get_permissions(profile_id):
    try:
        profile_id = ObjectId(profile_id)
    except:
        raise ValueError("Invalid profile ID")

    profile = profiles_collection.find_one({'_id': profile_id})
    if not profile:
        return None

    permissions = profile.get('permissions')
    return permissions

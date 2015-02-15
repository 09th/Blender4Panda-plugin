
order = 100
target = 'material'

def invoke(all_data, target_data, material, context, fname, flags=None):
    target_data['use_physics'] = material.game_settings.physics
    if material.game_settings.physics:
        target_data['phys_friction'] = material.physics.friction
        target_data['phys_elasticity'] = material.physics.elasticity

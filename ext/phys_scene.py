order = 2
target = 'scene'

def invoke(all_data, target_data, context, fname, flags=None):
    target_data['phys_gravity'] = context.scene.game_settings.physics_gravity
    target_data['phys_step_max'] = context.scene.game_settings.physics_step_max
    target_data['phys_step_sub'] = context.scene.game_settings.physics_step_sub
    target_data['phys_deactivation_linear_threshold'] = context.scene.game_settings.deactivation_linear_threshold
    target_data['phys_deactivation_angular_threshold'] = context.scene.game_settings.deactivation_angular_threshold
    target_data['phys_deactivation_time'] = context.scene.game_settings.deactivation_time
    target_data['phys_fps'] = context.scene.game_settings.fps
    

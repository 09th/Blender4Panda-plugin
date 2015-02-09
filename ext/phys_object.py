from mathutils import Vector

order = 1
target = 'object'

def invoke(all_data, target_data, obj, context, fname, flags=None):
    target_data['phys_type'] = obj.game.physics_type
    target_data['phys_mass'] = obj.game.mass
    target_data['phys_radius'] = obj.game.radius
    target_data['phys_form_factor'] = obj.game.form_factor
    target_data['phys_velocity_min'] = obj.game.velocity_min
    target_data['phys_velocity_max'] = obj.game.velocity_max
    target_data['phys_damping'] = obj.game.damping
    target_data['phys_rotation_damping'] = obj.game.rotation_damping
    target_data['phys_lock_rotation'] = (obj.game.lock_rotation_x,
                                         obj.game.lock_rotation_y,
                                         obj.game.lock_rotation_z)
    target_data['phys_lock_location'] = (obj.game.lock_location_x,
                                         obj.game.lock_location_y,
                                         obj.game.lock_location_z)
    if obj.game.use_collision_bounds:
        target_data['phys_collision_bounds'] = obj.game.collision_bounds_type
        target_data['phys_collision_margin'] = obj.game.collision_margin
        target_data['phys_bb'] = ((Vector(obj.bound_box[6]) - Vector(obj.bound_box[0]))*0.5)[:]
    target_data['invisible'] = obj.hide_render

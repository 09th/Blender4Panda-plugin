from mathutils import Vector
from math import pi

order = 100
target = 'object'

def invoke(all_data, target_data, obj, context, fname, flags=None):
    target_data['phys_type'] = obj.game.physics_type
    target_data['phys_mass'] = obj.game.mass
    target_data['phys_radius'] = obj.game.radius
    target_data['phys_form_factor'] = obj.game.form_factor
    target_data['phys_velocity_min'] = obj.game.velocity_min
    target_data['phys_velocity_max'] = obj.game.velocity_max
    target_data['phys_linear_damping'] = obj.game.damping
    target_data['phys_angular_damping'] = obj.game.rotation_damping
    target_data['phys_collision_group'] = obj.game.collision_group[:]
    target_data['phys_collision_mask'] = obj.game.collision_mask[:]
    target_data['phys_deactivation'] = not obj.game.use_sleep
    target_data['phys_lock_rotation'] = (obj.game.lock_rotation_x,
                                         obj.game.lock_rotation_y,
                                         obj.game.lock_rotation_z)
    target_data['phys_lock_location'] = (obj.game.lock_location_x,
                                         obj.game.lock_location_y,
                                         obj.game.lock_location_z)
    if obj.game.use_anisotropic_friction:
        target_data['phys_friction_coefficients'] = obj.game.friction_coefficients[:]
    if obj.game.use_collision_bounds:
        target_data['phys_collision_bounds'] = obj.game.collision_bounds_type
        target_data['phys_collision_margin'] = obj.game.collision_margin
        target_data['phys_bb'] = ((Vector(obj.bound_box[6]) - Vector(obj.bound_box[0]))*0.5)[:]
    if obj.type == 'MESH':
        target_data['phys_mat_order'] = [mat.name for mat in obj.data.materials]
    target_data['invisible'] = obj.hide_render
    
    constraints = []
    for con in obj.constraints:
        if con.type == 'RIGID_BODY_JOINT':
            con_dict = {}
            # have no idea about con.child
            con_dict['name'] = con.name
            con_dict['pivot_type'] = con.pivot_type #enum in [‘BALL’, ‘HINGE’, ‘CONE_TWIST’, ‘GENERIC_6_DOF’]
            if con.target:
                con_dict['target'] = con.target.name
            con_dict['use_angular_limits'] = (con.use_angular_limit_x, 
                                              con.use_angular_limit_y,
                                              con.use_angular_limit_z)
            con_dict['use_linear_limits'] = (con.use_limit_x, 
                                             con.use_limit_y,
                                             con.use_limit_z)
            con_dict['pivot_pos'] = (con.pivot_x,
                                     con.pivot_y,
                                     con.pivot_z)
            con_dict['pivot_axis'] = (con.axis_x / pi * 180,
                                      con.axis_y / pi * 180,
                                      con.axis_z / pi * 180)
            con_dict['angular_limits'] = ((con.limit_angle_min_x / pi * 180, con.limit_angle_max_x / pi * 180),
                                          (con.limit_angle_min_y / pi * 180, con.limit_angle_max_y / pi * 180),
                                          (con.limit_angle_min_z / pi * 180, con.limit_angle_max_z / pi * 180))
            con_dict['linear_limits'] = ((con.limit_min_x, con.limit_max_x),
                                         (con.limit_min_y, con.limit_max_y),
                                         (con.limit_min_z, con.limit_max_z))
            con_dict['use_linked_collision'] =  con.use_linked_collision
            constraints.append(con_dict)
    if constraints:
        target_data['constraints'] = constraints

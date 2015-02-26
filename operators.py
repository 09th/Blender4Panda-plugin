import imp, bpy, random, mathutils, bpy_extras, bpy_extras.view3d_utils
import json, math
from bpy.types import Operator
from bpy.props import IntProperty, StringProperty, BoolProperty
from mathutils import Vector,Quaternion, Matrix
from bpy_extras.io_utils import ExportHelper, ImportHelper
from .utils import *

POSSIBLE_OBJ_TYPES = ["MESH", "EMPTY", "LAMP"]

### Sketch operator
class SketchAssets(Operator):
    bl_idname = "se4p3d.sketch_assets" 
    bl_label = "Sketch Assets"
    bl_description = "Start Sketching"
    
    rot_step={'WHEELUPMOUSE':10, 'WHEELDOWNMOUSE':-10}
    
    def __init__(self):
        self.mouse_click = False
        self.mouse_click_hist = False
        #self.radius = bpy.context.window_manager.sketch_assets_distance
        self.radius = 1.0
        self.counter = 0
        self.cur_pos = Vector((0,0,0))
        self.old_pos = Vector((100000,100000,100000))
        self.distance = Vector((0,0,0))
        self.stroke_dir = Vector((0,0,0))
        self.viewport_mode = 'NONE'
        
        self.first_pos = Vector((0,0,0))
        self.first_norm = Vector((1,0,0))
        
        self.show_manipulator = None
        self.last_object = None
        self.selected_object = None
        
        bpy.context.window_manager.se4p3d_assets_placing_enabled = True
    
    def project_cursor(self, event):
        mouse_coord = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))

        transform = bpy_extras.view3d_utils.region_2d_to_location_3d
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        #### cursor used for the depth location of the mouse
        depth_location = bpy.context.scene.cursor_location

        ### Viewport origin
        start = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_coord)
        end = transform(region, rv3d, mouse_coord, bpy.context.space_data.region_3d.view_location)
        end = start+(end-start)*2000
        ### Cast ray from view to mouselocation
        #ray = bpy.context.scene.ray_cast(start , start+(end-start)*2000)
        ray = bpy.context.scene.ray_cast(start , end)
        
        return start, end, ray
        
    
    def rotate_to_dir(self, object, dir):
        scale = Vector(object.scale)
        
        rot = object.matrix_local.normalized().to_3x3()
        object_norm = rot.col[2]
        projectedStrokeDir = (dir - object_norm * (object_norm * dir)).normalized()
        strokeQuat = rot.col[0].rotation_difference(projectedStrokeDir) 
        rot = strokeQuat.to_matrix() * rot
        pos = object.location
        trans = rot.to_4x4()
        trans.translation = pos
        object.matrix_local = trans
        
        object.scale = scale
    
    
    def copy_from_asset(self, asset, parent = None, iteration=0):
        bpy.context.scene.objects.active = None
        if iteration == 0:
            parent = bpy.data.objects[asset.ref_object_name].copy()
            bpy.context.scene.objects.link(parent)
            parent['asset'] = True
            parent['type'] = asset.type
            parent['asset_name'] = asset.name
            parent['canvas'] = asset.use_as_canvas
        '''
        for child in parent.children:
            dupli_child = child.copy()
            bpy.context.scene.objects.link(dupli_child)
            dupli_child.parent = parent
            
            dupli_child['asset'] = True
            dupli_child['type'] = 'OBJECT'
            dupli_child['asset_name'] = asset.name
            dupli_child['canvas'] = asset.use_as_canvas
            
            for child_child in child.children:
                self.copy_from_asset(asset, child, iteration + 1)
        '''
        parent.draw_type = 'TEXTURED'
        parent.show_name = False

        for object in bpy.context.selected_objects:
            object.select = False 
            
        bpy.context.scene.objects.active = parent
        parent.select = True
        return parent
    
    def get_ground_align_matrix(self, norm, pos, asset):
        scale = bpy.data.objects[asset.ref_object_name].scale.to_tuple()
        m = Matrix()
        m[0][0],m[1][1],m[2][2] = scale
        scale = m
        surface_rotation = Vector((0,0,1)).rotation_difference(norm).normalized()
        object_rotation = Quaternion().slerp(surface_rotation,asset.surface_affect)
        rot = object_rotation.to_matrix().normalized()
        trans = rot.to_4x4()
        trans.translation = (pos + Vector((0,0,asset.z_offset)))
        trans *= Matrix.Rotation(asset.start_rot_z, 4, 'Z')
        return trans * scale
    
    def place_object(self, pos, norm, dir, asset, disableStrokeDir = False):
        ### adds a duplicate Object a.t the Cursor Position
        #context = bpy.context
        #asset = context.window_manager.sketch_assets_list[context.window_manager.sketch_assets_list_index]
        #ob = bpy.data.objects[asset.ref_object_name]
        #if asset.type in ['OBJECT', 'EMPTY', 'LAMP', 'SOUND']:
        copy = self.copy_from_asset(asset)
        asset_obj = bpy.data.objects[asset.ref_object_name]
        #elif asset.type == 'GROUP':
        #    group = bpy.data.groups[asset.ref_object_name]
        #    if len(group.objects)>0:
        #        randint = len(group.objects)
        #        random_ob = random.randint(0,randint)-1
        #        ob = group.objects[random_ob]
        #        if ob.parent == None:
        #            copy = self.copy_mesh_object(ob,ob,asset.name)
        #        else:
        #            copy = self.copy_mesh_object(ob.parent,ob.parent,asset.name) 
        #else:
        #    copy = None    
        if copy != None:
            #bpy.context.scene.objects.link(copy)
            ###
            '''
            surface_rotation = Vector((0,0,1)).rotation_difference(norm)
            object_rotation = Quaternion().slerp(surface_rotation,asset.surface_affect)
            rot = object_rotation.to_matrix()
            
            if asset.stroke_orient and not disableStrokeDir:
                object_norm = rot.col[2]
                projectedStrokeDir = (dir - object_norm * (object_norm * dir)).normalized()
                strokeQuat = rot.col[0].rotation_difference(projectedStrokeDir)
                rot = strokeQuat.to_matrix() * rot
            
            
            location = pos
            trans = rot.to_4x4()
            trans.translation = location
            copy.matrix_world = trans * Matrix.Translation(Vector((0,0,1)) * asset.z_offset)
            '''
            copy.matrix_world = self.get_ground_align_matrix(norm, pos, asset)
            #copy.matrix_local = trans * Matrix.Translation(Vector((0,0,1)) * asset.z_offset)
            
            self.last_object = copy
            
            ### add random scale
            '''
            if asset.type in ['OBJECT','EMPTY']:
                random_scale_x = random.uniform(asset_obj.scale[0],asset_obj.scale[0]*asset.rand_scale_x)/asset_obj.scale[0]
                random_scale_y = random.uniform(asset_obj.scale[1],asset_obj.scale[1]*asset.rand_scale_y)/asset_obj.scale[1]
                random_scale_z = random.uniform(asset_obj.scale[2],asset_obj.scale[2]*asset.rand_scale_z)/asset_obj.scale[2]
                #random_scale_x = random.uniform(asset_obj.scale[0],asset_obj.scale[0]*asset.rand_scale_x)
                #random_scale_y = random.uniform(asset_obj.scale[1],asset_obj.scale[1]*asset.rand_scale_y)
                #random_scale_z = random.uniform(asset_obj.scale[2],asset_obj.scale[2]*asset.rand_scale_z)
            elif asset.type in ['GROUP']:
                random_scale_x = random.uniform(ob.scale[0],ob.scale[0]*asset.rand_scale_x)
                random_scale_y = random.uniform(ob.scale[1],ob.scale[1]*asset.rand_scale_y)
                random_scale_z = random.uniform(ob.scale[2],ob.scale[2]*asset.rand_scale_z)
            
            if asset.type in ['OBJECT','EMPTY']:
                if asset.constraint_rand_scale:
                    scale = Vector((random_scale_x,random_scale_x,random_scale_x))
                else:
                    scale = Vector((random_scale_x,random_scale_y,random_scale_z))


            if asset.type in ['OBJECT','EMPTY']:
                copy.scale[0] = asset_obj.scale[0] * asset.scale * scale[0]
                copy.scale[1] = asset_obj.scale[1] * asset.scale * scale[1]
                copy.scale[2] = asset_obj.scale[2] * asset.scale * scale[2]
            elif asset.type in ['GROUP']:
                copy.scale[0] = ob.scale[0] * asset.scale * scale[0]
                copy.scale[1] = ob.scale[1] * asset.scale * scale[1]
                copy.scale[2] = ob.scale[2] * asset.scale * scale[2]
            '''
    
    def add_object(self, ray, asset):
        ### adds a duplicate Object at the Cursor Position
        #context = bpy.context
        #asset = context.window_manager.sketch_assets_list[context.window_manager.sketch_assets_list_index]
        if self.counter == 0:
            self.place_object(ray[3],ray[4],self.stroke_dir, asset, True)
        else:
            self.place_object(ray[3],ray[4],self.stroke_dir, asset)
        self.counter += 1
    
    def modal(self, context, event):
        
        if len(context.scene.se4p3d.assets_list) > 0:
            if context.scene.se4p3d.assets_list_index >= len(context.scene.se4p3d.assets_list):
                context.scene.se4p3d.assets_list_index = len(context.scene.se4p3d.assets_list) - 1
            asset = context.scene.se4p3d.assets_list[context.scene.se4p3d.assets_list_index]
        else:
            #asset = None
            return {'PASS_THROUGH'}
            
        self.mouse_click_hist = self.mouse_click
        
        t_panel = context.area.regions[1]
        n_panel = context.area.regions[3]
        
        view_3d_region_x = Vector((context.area.x + t_panel.width, context.area.x + context.area.width - n_panel.width))
        view_3d_region_y = Vector((context.region.y, context.region.y+context.region.height))
        
        in_view_3d = False
        
        ### hinder to make fullscreen
        if (event.shift and event.type == "SPACE") or (event.ctrl and (event.type == "UP_ARROW" or event.type == "DOWN_ARROW" or event.type == "RIGHT_ARROW" or event.type == "LEFT_ARROW")):
            return{'RUNNING_MODAL'}
        
        if event.mouse_y > view_3d_region_y[1]:
            return{'RUNNING_MODAL'}
        
        ### check if mouse is in 3d viewport
        if event.mouse_x > view_3d_region_x[0] and event.mouse_x < view_3d_region_x[1] and event.mouse_y > view_3d_region_y[0] and event.mouse_y < view_3d_region_y[1]:
            in_view_3d = True
        else:
            in_view_3d = False
        
        if in_view_3d:
            ### set paint cursor
            if not event.ctrl and not event.shift:
                bpy.context.window.cursor_modal_set("PAINT_BRUSH")
            elif event.ctrl:
                bpy.context.window.cursor_modal_set("KNIFE")
            elif event.shift:
                bpy.context.window.cursor_modal_set("EYEDROPPER")   
                
            ### Assets Distance for Paint Strokes
            #self.radius = bpy.context.window_manager.sketch_assets_distance
            ### set MouseClick
            if (event.value == 'PRESS' or event.value == 'CLICK') and event.type == 'LEFTMOUSE':
                self.mouse_click = True
                bpy.context.scene.objects.active = None
                bpy.ops.object.select_all(action='DESELECT')
                
                if not context.user_preferences.system.use_region_overlap:
                    if in_view_3d:
                       return{'RUNNING_MODAL'}
            if (event.value == 'RELEASE' and event.type == 'MOUSEMOVE'):
                self.mouse_click = False
                
            if self.mouse_click_hist and not self.mouse_click:
                if self.last_object != None:
                    
                    self.last_object.select = True
                    bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_x/2,asset.rand_rot_x/2), axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='LOCAL')
                    bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_y/2,asset.rand_rot_y/2), axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL')
                    bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_z/2,asset.rand_rot_z/2), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='LOCAL')
                    
                    ### make object single user
                    #if asset.make_single_user and self.last_object.type == "MESH":
                    #    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)
                    self.last_object.select = False
                                    
                self.first_pos = Vector((0,0,0))
                self.first_norm = Vector((1,0,0))
                self.counter = 0
                self.last_object = None
                self.old_pos = Vector((100000,100000,100000))
                if asset == None:
                    msg = "Paint Stroke - "
                else:
                    msg = "Paint Stroke - " + asset.name
                bpy.ops.ed.undo_push(message=msg)
            
            ### Cast Ray from mousePosition and set Cursor to hitPoint
            if asset.ref_object_name in context.scene.objects:
                context.scene.objects.unlink(bpy.data.objects[asset.ref_object_name])
            ray_start,ray_end, ray = self.project_cursor(event)
            ray_hit = ray[0]
            ray_hit_object = ray[1]
            #ray_hit_object_matrix = ray[2].to_translation()
            ray_hit_position = ray[3]
            if not ray_hit:
                # If not hit object - intersect with base plane
                pt0 = mathutils.geometry.intersect_line_plane(ray_start, ray_end, Vector((0,0,0)), Vector((0,0,1)))
                if pt0:
                    ray_hit = True
                    ray_hit_position = pt0
                    ray = (True, None, ray[2], pt0, Vector((0,0,1)))
            if ray_hit == True:                       
                self.cur_pos = ray_hit_position
                self.stroke_dir = (self.cur_pos - self.old_pos).normalized()
                self.distance = self.old_pos - self.cur_pos
                ###
                if (ray_hit_object and ('asset' not in ray_hit_object or ('canvas' in ray_hit_object and ray_hit_object['canvas']))) or not ray_hit_object:
                    if not self.mouse_click and not (event.ctrl or event.shift):
                        asset_obj = bpy.data.objects[asset.ref_object_name]
                        if asset.ref_object_name not in context.scene.objects:
                            context.scene.objects.link(asset_obj)
                        #asset_obj.location = self.cur_pos
                        if event.alt:
                            if event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE'):
                                asset.start_rot_z += math.radians(self.rot_step[event.type])
                        asset_obj.matrix_world = self.get_ground_align_matrix(ray[4], self.cur_pos, asset)                                                 
                        if event.alt:
                            return {'RUNNING_MODAL'}
                        #return {'PASS_THROUGH'}
                    
                    ### add Object on Cursor Position
                    if self.mouse_click == True and not event.ctrl and not event.shift:
                        
                        if asset.stroke_orient:
                            if self.last_object != None:
                                self.rotate_to_dir(self.last_object, self.stroke_dir)
                                
                        #distance = asset.distance
                        #asset_scale = asset.scale
                        
                        if self.distance.magnitude > asset.distance * asset.scale:
                            self.old_pos = self.cur_pos
                            ### add random rotation
                            if self.last_object != None:
                                self.last_object.select = True
                                #asset = context.window_manager.sketch_assets_list[context.window_manager.sketch_assets_list_index]
                                bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_x/2,asset.rand_rot_x/2), axis=(1, 0, 0), constraint_axis=(True, False, False), constraint_orientation='LOCAL')
                                bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_y/2,asset.rand_rot_y/2), axis=(0, 1, 0), constraint_axis=(False, True, False), constraint_orientation='LOCAL')
                                bpy.ops.transform.rotate(value=random.uniform(-asset.rand_rot_z/2,asset.rand_rot_z/2), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='LOCAL')
                                
                                ### make object single user
                                #if asset.make_single_user and self.last_object.type == "MESH":
                                #    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)
                                
                                self.last_object.select = False
                                
                            ### if object does not exist anymore remove it from the asset list
                            
                            self.add_object(ray, asset)
                            #try:
                            #    self.add_object(ray, context, asset)
                            #except:
                            #    bpy.context.window_manager.se4p3d_assets_placing_enabled = False
                            #    #bpy.context.window_manager.sketch_assets_list.remove(bpy.context.window_manager.sketch_assets_list_index)
                            #    self.report({'WARNING'},'Object or Group with that name does not exist anymore!')
                ###
                ### highlight hovered object
                if ray_hit_object and (event.ctrl or event.shift):
                    distances = []
                    for object in context.scene.objects:
                        if "asset" in object:
                            if object.type != 'MESH':
                                distances.append((pnt2line(object.location, ray_start, ray_end), object))
                    object = None
                    distances.sort()
                    if distances and distances[0][0] < 0.5:
                        object = distances[0][1]
                    #if (ray_hit_object and not 'place' in ray_hit_object):
                    if ray_hit_object:
                        if object:
                            if (ray_hit_object.location - ray_start).length_squared < (object.location - ray_start).length_squared:
                                object = ray_hit_object
                        else:
                            object = ray_hit_object
                    if object and 'asset' in object and not object['canvas']:
                        bpy.ops.object.select_all(action='DESELECT')
                        self.selected_object = object
                        self.selected_object.select = True
                        bpy.context.scene.objects.active = self.selected_object
                    
                    if self.mouse_click and self.selected_object:
                        #print(event.ctrl, event.shift)
                        ### delete selected object
                        if event.ctrl:
                            delete_recursive(self.selected_object)
                            self.selected_object = None
                        ### pick selected object form list
                        if event.shift:
                            if 'asset_name' in self.selected_object:
                                for i, asset in enumerate(context.scene.se4p3d.assets_list):
                                    if asset.name == self.selected_object['asset_name']:                                        
                                        context.scene.se4p3d.assets_list_index = i
                                        break

                ### unselect objects                    
                elif not event.ctrl and not event.shift and event.value == 'RELEASE':
                    if self.selected_object != None:
                        self.selected_object.select = False
                        bpy.context.scene.objects.active = None
                    self.selected_object = None
                
        else:
            bpy.context.window.cursor_modal_set("DEFAULT")
            if asset.ref_object_name in context.scene.objects:
                context.scene.objects.unlink(bpy.data.objects[asset.ref_object_name])
        
        if event.type == "ESC" and event.value == 'CLICK':
            if self.mouse_click:
                self.mouse_click = False
            else:
                context.window_manager.se4p3d_assets_placing_enabled = False
        
        if context.window_manager.se4p3d_assets_placing_enabled == False:
            context.window.cursor_modal_set("DEFAULT")
            context.space_data.show_manipulator = self.show_manipulator
            context.space_data.region_3d.view_perspective = self.viewport_mode
            if asset.ref_object_name in context.scene.objects:
                context.scene.objects.unlink(bpy.data.objects[asset.ref_object_name])
            return{'FINISHED'}
        return {'PASS_THROUGH'}
        #return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self.show_manipulator = context.space_data.show_manipulator
            context.space_data.show_manipulator = False
            if context.space_data.region_3d.view_perspective == 'PERSP':
                self.viewport_mode = 'PERSP'
                
            elif context.space_data.region_3d.view_perspective == 'ORTHO':
                self.viewport_mode = 'ORTHO'
                context.space_data.region_3d.view_perspective = 'PERSP'
                   
            return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.se4p3d_assets_placing_enabled = False
        context.window.cursor_modal_set("DEFAULT")
        context.space_data.show_manipulator = self.show_manipulator
        
        context.space_data.region_3d.view_perspective = self.viewport_mode
        return {'CANCELLED'}
        
        

class SE4P3DDummy(Operator):
    bl_idname = "se4p3d.dummy"
    bl_label = "Dummy operator"
    
    def execute(self, context):
        print("dummy operator")
        return {"FINISHED"}

'''
class AddObjectToAssetsSurfaceList(Operator):
    bl_idname = "se4p3d.add_object_to_assets_surface_list" 
    bl_label = "Add Object to Assets Surface list"
    bl_description = "Adds Object to the surface list. Assets can only be painted on objects in that list."
    
    def execute(self, context):
        ob = context.scene.objects.active
        
        if ob != None:
            if ob.type == "MESH":
                item = context.scene.se4p3d.assets_surface_list.add()
                item.name = ob.name
                context.scene.se4p3d.assets_surface_list_index = len(context.scene.se4p3d.assets_surface_list)-1
                ob['place'] = True
            else:
                self.report({'WARNING'},'Please select a Mesh Object.')
                return{'FINISHED'}
        else:
            self.report({'WARNING'},'Please select an Asset before adding it to the list.')
            
        
        return{'FINISHED'}
'''
        
def add_object_to_assetslist(ob, context):
    #if 'asset' in ob:
    #    return
    item = context.scene.se4p3d.assets_list.add()
    item.name = ob.name
    item.ref_object_name = ob.name
    
    if ob.type == "MESH":
        item.type = 'OBJECT'
    elif ob.type == "EMPTY":
        item.type = 'EMPTY'
    elif ob.type == "LAMP":
        item.type = 'LAMP'
    
    #item2 = context.scene.se4p3d.assets_list.add()
    #item2.name = context.scene.objects.active.name
    #if ob.type == "MESH":
    #    item2.type = 'OBJECT'
    #elif ob.type == "EMPTY":
    #    item2.type = 'EMPTY'
    context.scene.se4p3d.assets_list_index = len(context.scene.se4p3d.assets_list)-1
    ob.draw_type = 'WIRE'
    ob.show_name = True
    if ob.name in context.scene.objects:
        context.scene.objects.unlink(ob)
    return True

        
class AddObjectToAssetsList(Operator):
    bl_idname = "se4p3d.add_object_to_assetslist" 
    bl_label = "Add Object to Assetslist"
    bl_description = "Adds object to the asset list with custom settings for painting."
    
    def execute(self, context):
        ob = context.scene.objects.active
        if ob != None:
            #if 'place' in ob:
            #    self.report({'WARNING'},'Object is already set as Canvas!')
            #    return{'FINISHED'}
            if ob.type in POSSIBLE_OBJ_TYPES:
                #if 'asset' in ob:
                #    self.report({'WARNING'},'Asset already in use.')
                add_object_to_assetslist(ob, context)
            else:
                self.report({'WARNING'},'Please select a proper Object.')
        else:
            self.report({'WARNING'},'Please select an Asset before adding it to the list.')
            
        
        return{'FINISHED'}


class RemoveObjectFromAssetsList(Operator):
    bl_idname = "se4p3d.remove_object_from_assetslist" 
    bl_label = "Remove asset and all linked objects"
    bl_description = "Remove asset or group from the asset list."
    
    idx = IntProperty()
    
    list = StringProperty()
    #idxName = StringProperty()
    
    def invoke(self, context, event):
        wm = context.window_manager 
        return wm.invoke_confirm(self,event)
    
    def execute(self, context):
        #assets_list = getattr(context.scene.se4p3d, self.list)
        
        #if self.list == 'assets_surface_list':
        #    asset = assets_list[self.idx].name
        #    if asset in bpy.data.objects and 'place' in bpy.data.objects[asset]:
        #        del(bpy.data.objects[asset]['place'])
        
        #assets_list.remove(self.idx)
        asset = context.scene.se4p3d.assets_list[self.idx]
        ref_obj = bpy.data.objects[asset.ref_object_name]
        context.scene.objects.link(ref_obj)
        ref_obj.show_name = False
        ref_obj.draw_type = 'TEXTURED'
        for obj in bpy.data.objects:
            if 'asset_name' in obj and obj['asset_name'] == asset.name:
                delete_recursive(obj)
        context.scene.se4p3d.assets_list.remove(self.idx)

        return{'FINISHED'}


class ExportScene(bpy.types.Operator, ExportHelper):
    ''' Export scene
    '''
    
    bl_idname = "export.panda3d_scene"
    bl_label = "Export scene for Panda3D"

    # ExportHelper mixin class uses this
    filename_ext = ".jsd"

    filter_glob = StringProperty(
            default="*.jsd",
            options={'HIDDEN'},
            )
            
    single_geom_mode = BoolProperty(name="Single geom mode",
                                    description="All scene static geometry will store in single file", 
                                    default=True)
    auto_export_egg = BoolProperty(name="Auto export .EGG",
                                   description="Automatically export all needed EGG files (YABEE required).", 
                                   default=True)

    
    def draw(self, context):
        layout = self.layout
        #layout.prop(self, "single_geom_mode")
        layout.prop(self, "auto_export_egg")
        

    def execute(self, context):
        from .ext import extensions
        flags = []
        if self.single_geom_mode:
            flags.append('SINGLE_GEOM_MODE')
        if self.auto_export_egg:
            flags.append('AUTO_EXPORT_EGG')
        export_dict = {'scene':{},
                       'objects':{},
                       'assets':{},
                       'materials':{}
                       }
        
        for e in extensions:
            if e.target == 'prepare':
                e.invoke(export_dict, context, self.filepath, flags)
        
        for e in extensions:
            if e.target == 'scene':
                e.invoke(export_dict, export_dict['scene'], context, self.filepath, flags)
            elif e.target == 'material':
                for material in bpy.data.materials:
                    if material.users > 0:
                        mat_dict = {}
                        if material.name in export_dict['materials']:
                            mat_dict = export_dict['materials'][material.name]
                        e.invoke(export_dict, mat_dict, material, context, self.filepath, flags)
                        if mat_dict:
                            export_dict['materials'][material.name] = mat_dict
            elif e.target == 'object':
                for obj in context.scene.objects:
                    obj_dict = {}
                    if obj.name in export_dict['objects']:
                        obj_dict = export_dict['objects'][obj.name]
                    e.invoke(export_dict, obj_dict, obj, context, self.filepath, flags)
                    if obj_dict:
                        export_dict['objects'][obj.name] = obj_dict
            elif e.target == 'asset':
                for asset in context.scene.se4p3d.assets_list:
                    asset_dict = {}
                    if asset.name in export_dict['assets']:
                        asset_dict = export_dict['assets'][asset.name]
                    e.invoke(export_dict, asset_dict, asset, context, self.filepath, flags)
                    if asset_dict:
                        export_dict['assets'][asset.name] = asset_dict
            elif e.target not in ('prepare', 'finishing'):
                print('ERROR:EXTENSION: unknown target "%s"' % e.target)
                
        for e in extensions:
            if e.target == 'finishing':
                e.invoke(export_dict, context, self.filepath, flags)
       
        
        f = open(self.filepath, 'w')
        f.write(json.dumps(export_dict, indent=4, sort_keys=True))
        f.close()
        return {'FINISHED'}


class LoadLibrary(bpy.types.Operator, ImportHelper):
    '''Load library
    '''
    
    bl_idname = "se4p3d.load_library"
    bl_label = "Load library from external file"
    
    filter_glob = StringProperty(
            default="*.blend",
            options={'HIDDEN'},
            )
            
    def execute(self, context):
        #print('load library execute', self.filepath)
        with bpy.data.libraries.load(self.filepath) as (data_from, data_to):
            data_to.objects = data_from.objects
        for obj in data_to.objects:
            if obj.type in POSSIBLE_OBJ_TYPES:
                add_object_to_assetslist(obj, context)
            else:
                bpy.data.objects.remove(obj)
        return {'FINISHED'}

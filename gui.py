import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty, CollectionProperty, StringProperty

class UI_UL_sketcher_list(bpy.types.UIList):
    
    icons = {'MESH':'OBJECT_DATAMODE',
             'OBJECT':'OBJECT_DATAMODE',
             'GROUP':'GROUP',
             'LAMP':'LAMP'
            }
    
    def __init__(self):
        self.ico = ''
        
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        row = layout.row()

        self.ico = self.icons[item.type]
        if item.use_as_canvas:
            self.ico = 'OUTLINER_OB_SURFACE'
                
        #row.label(text=item.name,icon=self.ico)
        row.prop(item, "name",icon=self.ico, text="", emboss=False)
        op = row.operator("se4p3d.remove_object_from_assetslist", icon='X', text="", emboss=False)
        op.idx = int(index)



class SE4P3DUI(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "SE4P3D"
    bl_label = "Scene editor for Panda3D"
    
    bpy.types.WindowManager.se4p3d_assets_placing_enabled = BoolProperty(description="Disable Skecthing", default=False)
    bpy.types.WindowManager.se4p3d_assets_box = BoolProperty(description="", default=True)
    bpy.types.WindowManager.se4p3d_assets_surface_box = BoolProperty(description="", default=True)
    
    @classmethod
    def poll(cls, context):
        return (context.scene)
        
    def draw(self, context):
        '''
        col = self.layout.column()
        row = self.layout.row()
        split = self.layout.split()
        '''
        scene = bpy.context.scene
        ob = context.object
        wm = context.window_manager
        box = self.layout.box()
        row = box.column()
        row.operator("se4p3d.reload_modules", text="Reload modules")
        #row = box.column()
        row.operator('export.panda3d_scene', text = "Export scene")
        
        ### Sketch Button
        if wm.se4p3d_assets_placing_enabled == False:
            row.operator('se4p3d.sketch_assets',icon="GREASEPENCIL", text = "Enable Sketching")
        else:
            row.prop(wm, 'se4p3d_assets_placing_enabled', icon="GREASEPENCIL",text="Disable Sketching")
        
        ### Assets list
        if wm.se4p3d_assets_box:
            row = box.column()
            row.prop(wm,'se4p3d_assets_box',emboss = False, text="Asset Library",icon="DOWNARROW_HLT")
            row = box.row()
            row.template_list("UI_UL_sketcher_list", "assets_list", scene.se4p3d, "assets_list", scene.se4p3d, "assets_list_index", rows=5)
            
            row = box.column(align=True)
            row.operator("se4p3d.add_object_to_assetslist", icon='OBJECT_DATAMODE', text="Add Object to List")
            row.operator("se4p3d.load_library", icon='FILESEL', text="Load library")
            
            # Temporary unavailable
            #if len(bpy.data.groups) > 0:                
            #    row.operator_menu_enum("se4p3d.dummy","group_name", icon='GROUP', text="Add Group to List")

            assetList = context.scene.se4p3d.assets_list
            idx = context.scene.se4p3d.assets_list_index
            if idx < len(assetList):
                row = box.column(align=True)
                row.label(text="Asset Settings:")
                row = box.column(align=True)
                row.label(text='Reference:' + assetList[idx].ref_object_name)
                row.prop(assetList[idx], 'code_class', text="Python Class")
                row.prop(assetList[idx], 'use_as_canvas', text="Canvas")

                row = box.column(align=True)
                #row.prop(assetList[idx], 'make_single_user',text="Single User Object")
                row.prop(assetList[idx], 'distance',text="Asset Distance")
                row.prop(assetList[idx], 'z_offset', text="Z-Offset")

                row = box.column(align=True)
                row.prop(assetList[idx], 'surface_affect', text="Surface affect")
                row.prop(assetList[idx], 'rand_rot_x', text="Random Rotation X")
                row.prop(assetList[idx], 'rand_rot_y', text="Random Rotation Y")
                row.prop(assetList[idx], 'rand_rot_z', text="Random Rotation Z")
                row.prop(assetList[idx], 'stroke_orient',icon="CURVE_PATH", text="Sketch In Stroke Direction",toggle=True)
                
                row = box.column(align=True)
                row.prop(assetList[idx], 'scale', text="Asset Scale")
                if assetList[idx].constraint_rand_scale:
                    row.prop(assetList[idx], 'rand_scale_x', text="Random Scale")
                    row.prop(assetList[idx], 'constraint_rand_scale',icon="LINKED", text="Constraint Scale",toggle=True)
                else:
                    row.prop(assetList[idx], 'rand_scale_x', text="Random Scale X")
                    row.prop(assetList[idx], 'rand_scale_y', text="Random Scale Y")
                    row.prop(assetList[idx], 'rand_scale_z', text="Random Scale Z")
                    row.prop(assetList[idx], 'constraint_rand_scale',icon="UNLINKED", text="Constraint Scale",toggle=True)
                

                #Icon test
                #box.row()
                #for ico in ['BLENDER', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_DOWN', 'DISCLOSURE_TRI_RIGHT', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'DOT', 'X', 'GO_LEFT', 'PLUG', 'UI', 'NODE', 'NODE_SEL', 'FULLSCREEN', 'SPLITSCREEN', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ZOOMIN', 'ZOOMOUT', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'LINK_AREA', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'DOTSUP', 'DOTSDOWN', 'LINK', 'INLINK', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'LINKED', 'UNLINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'RENDER_REGION', 'BORDER_RECT', 'BORDER_LASSO', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BLANK1', 'LAMP', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'EDIT', 'GAME', 'RADIO', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TEXTURE_SHADED', 'VIEW3D', 'IPO', 'OOPS', 'BUTS', 'FILESEL', 'IMAGE_COL', 'INFO', 'SEQUENCE', 'TEXT', 'IMASEL', 'SOUND', 'ACTION', 'NLA', 'SCRIPTWIN', 'TIME', 'NODETREE', 'LOGIC', 'CONSOLE', 'PREFERENCES', 'ASSET_MANAGER', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'FACESEL_HLT', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'LIGHTPAINT', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LAMP_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'POSE_DATA', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'PACKAGE', 'UGLYPACKAGE', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'SETTINGS', 'RENDER_ANIMATION', 'RENDER_STILL', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'RNA', 'RNA_ADD', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LAMP', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'RESTRICT_VIEW_OFF', 'RESTRICT_VIEW_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_RENDER_ON', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LAMP', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_POSE', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'LAMP_POINT', 'LAMP_SUN', 'LAMP_SPOT', 'LAMP_HEMI', 'LAMP_AREA', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'MODIFIER', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'CONSTRAINT_DATA', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_SMOKE', 'MOD_SOLIDIFY', 'MOD_SCREW', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_AUDIO', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'SPACE2', 'SPACE3', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'ROTATE', 'CURSOR', 'ROTATECOLLECTION', 'ROTATECENTER', 'ROTACTIVE', 'ALIGN', 'SMOOTHCURVE', 'SPHERECURVE', 'ROOTCURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'MAN_TRANS', 'MAN_ROT', 'MAN_SCALE', 'MANIPUL', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_INCREMENT', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'PASTEDOWN', 'COPYDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'SNAP_SURFACE', 'RETOPO', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'BBOX', 'WIRE', 'SOLID', 'SMOOTH', 'POTATO', 'ORTHO', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'NDOF_DOM', 'NDOF_TURN', 'NDOF_FLY', 'NDOF_TRANS', 'LAYER_USED', 'LAYER_ACTIVE', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'LONGDISPLAY', 'SHORTDISPLAY', 'GHOST', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'BACK', 'FORWARD', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'IMAGEFILE', 'BRUSH_ADD', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_DARKEN', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_LIGHTEN', 'BRUSH_MIX', 'BRUSH_MULTIPLY', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_SUBTRACT', 'BRUSH_TEXDRAW', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'BRUSH_VERTEXDRAW', 'VIEW3D_VEC', 'EDIT_VEC', 'EDITMODE_DEHLT', 'EDITMODE_HLT', 'DISCLOSURE_TRI_RIGHT_VEC', 'DISCLOSURE_TRI_DOWN_VEC', 'MOVE_UP_VEC', 'MOVE_DOWN_VEC', 'X_VEC', 'SMALL_TRI_RIGHT_VEC']:
                #    row.operator_menu_enum("se4p3d.dummy","test", icon=ico, text=ico)



            else:
            #    pass
                if len(assetList) > 0:
                    context.scene.se4p3d.assets_list_index = len(assetList)-1
                #else:
                #    bpy.context.scene.se4p3d.assets_list_index = 0
        else:
            box = self.layout.box()
            row = box.column(align=True)
            row.prop(wm,'se4p3d_assets_box',emboss = False, text="Asset Library",icon="RIGHTARROW")
        




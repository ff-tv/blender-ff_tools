import bpy
from mathutils import Vector
from pathlib import Path
from math import pi, sin, cos

from .utils.render_utils import (
    render_png_passes,
    render_exr_passes,
    render_playblast_mp4,
    toggle_use_compositing
)


# ============================================
# OPERATORS
# ============================================

class FF_OT_PngRender(bpy.types.Operator):
    '''Setup PNG render with passes'''
    bl_idname = "ffrend.png_render"
    bl_label = "PNG Render"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render_png_passes(context)
        self.report({'INFO'}, "PNG Render setup complete.")
        return {"FINISHED"}


class FF_OT_ExrRender(bpy.types.Operator):
    '''Setup EXR render with passes'''
    bl_idname = "ffrend.exr_render"
    bl_label = "EXR Render"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render_exr_passes(context)
        self.report({'INFO'}, "EXR Render setup complete.")
        return {"FINISHED"}


class FF_OT_PlayblastMp4(bpy.types.Operator):
    '''Setup playblast MP4'''
    bl_idname = "ffrend.playblast_mp4"
    bl_label = "Playblast MP4"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render_playblast_mp4(context)
        self.report({'INFO'}, "Playblast MP4 setup complete.")
        return {"FINISHED"}


class FF_OT_ToggleCompositing(bpy.types.Operator):
    '''Toggle use compositing'''
    bl_idname = "ffrend.toggle_compositing"
    bl_label = "Toggle Compositing"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        toggle_use_compositing(context)
        state = "ON" if context.scene.render.use_compositing else "OFF"
        self.report({'INFO'}, f"Compositing {state}.")
        return {"FINISHED"}


class FF_OT_PrepareCharSheet(bpy.types.Operator):
    '''Prepare character sheet: Place cameras around subject and create stitched image'''
    bl_idname = "ffrend.prepare_char_sheet"
    bl_label = "Prepare Character Sheet"
    bl_options = {"REGISTER", "UNDO"}

    num_cameras: bpy.props.IntProperty(
        name="Number of Cameras",
        description="Number of cameras to place around subject",
        default=8,
        min=4,
        max=36
    )

    def execute(self, context):
        # Get selected object
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        import math
        
        subject = selected_objects[0]
        subject_location = subject.location
        
        # Get subject bounds for camera positioning
        bpy.ops.object.select_all(action='DESELECT')
        subject.select_set(True)
        bpy.context.view_layer.objects.active = subject
        
        # Calculate subject dimensions from bound_box
        bbox_corners = [Vector(corner) for corner in subject.bound_box]
        min_x = min(corner.x for corner in bbox_corners)
        max_x = max(corner.x for corner in bbox_corners)
        min_y = min(corner.y for corner in bbox_corners)
        max_y = max(corner.y for corner in bbox_corners)
        min_z = min(corner.z for corner in bbox_corners)
        max_z = max(corner.z for corner in bbox_corners)
        
        # Get dimensions
        dim_x = max_x - min_x
        dim_y = max_y - min_y
        dim_z = max_z - min_z
        max_dim = max(dim_x, dim_y, dim_z)
        
        # Calculate radius - enough to frame the whole subject
        radius = max_dim * 2.0
        
        # Camera height at center of subject
        camera_height = subject_location.z + (dim_z * 0.3)
        
        # Create collection for char sheet cameras
        charsheet_collection = bpy.data.collections.new(f"CharSheet_{subject.name}")
        bpy.context.scene.collection.children.link(charsheet_collection)
        
        # Create cameras
        camera_images = []
        
        for i in range(self.num_cameras):
            angle = (2 * pi * i) / self.num_cameras
            
            # Calculate camera position in circle using sin/cos
            cam_x = subject_location.x + radius * cos(angle)
            cam_y = subject_location.y + radius * sin(angle)
            
            # Create camera data
            cam_data = bpy.data.cameras.new(name=f"Camera_{subject.name}_{i+1}")
            cam_data.lens = 50
            cam_data.sensor_width = 32
            
            # Create camera object
            cam_obj = bpy.data.objects.new(f"Camera_{subject.name}_{i+1}", cam_data)
            charsheet_collection.objects.link(cam_obj)
            
            # Position camera
            cam_obj.location = (cam_x, cam_y, camera_height)
            
            # Make camera look at subject
            cam_obj.rotation_euler = (0, 0, 0)
            constraint = cam_obj.constraints.new(type='TRACK_TO')
            constraint.target = subject
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
            
            camera_images.append((cam_obj, i + 1))
        
        self.report({'INFO'}, f"Created {self.num_cameras} cameras for character sheet")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class FF_OT_Setup360Turnaround(bpy.types.Operator):
    '''Setup 360 degree turnaround camera around selected object'''
    bl_idname = "ffrend.setup_360_turnaround"
    bl_label = "Setup 360 Turnaround Camera"
    bl_options = {"REGISTER", "UNDO"}

    distance: bpy.props.FloatProperty(
        name="Distance",
        description="Distance from subject",
        default=5.0,
        min=1.0,
        max=50.0
    )

    height: bpy.props.FloatProperty(
        name="Height",
        description="Camera height",
        default=1.5,
        min=0.1,
        max=20.0
    )

    duration: bpy.props.IntProperty(
        name="Duration (frames)",
        description="Animation duration",
        default=100,
        min=24,
        max=1000
    )

    def execute(self, context):
        # Get selected object
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh object selected")
            return {'CANCELLED'}
        
        subject = selected_objects[0]
        subject_location = subject.location
        
        # Create camera data
        cam_data = bpy.data.cameras.new(name=f"Turnaround_{subject.name}")
        cam_data.lens = 35
        cam_data.sensor_width = 32
        
        # Create camera object
        camera = bpy.data.objects.new(f"Turnaround_{subject.name}", cam_data)
        bpy.context.scene.collection.objects.link(camera)
        
        # Position camera at starting point
        camera.location = (subject_location.x + self.distance, subject_location.y, subject_location.z + self.height)
        
        # Make camera look at subject
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = subject
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'
        
        # Create orbit path (circle)
        bpy.ops.curve.primitive_nurbs_circle_add(
            radius=self.distance,
            enter_editmode=False,
            align='WORLD',
            location=(subject_location.x, subject_location.y, subject_location.z + self.height)
        )
        path = bpy.context.active_object
        path.name = f"OrbitPath_{subject.name}"
        
        # Make circle horizontal
        path.rotation_euler = (0, 0, 0)
        
        # Add follow path constraint
        path_constraint = camera.constraints.new(type='FOLLOW_PATH')
        path_constraint.target = path
        path_constraint.use_curve_follow = True
        path_constraint.up_axis = 'UP_Y'
        
        # Animate camera along path
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = self.duration
        
        # Set path animation
        path.data.path_duration = self.duration
        path.data.eval_time = 0
        path.data.keyframe_insert(data_path="eval_time", frame=1)
        path.data.eval_time = 100
        path.data.keyframe_insert(data_path="eval_time", frame=self.duration)
        
        # Set camera as active
        bpy.context.scene.camera = camera
        
        self.report({'INFO'}, f"360 turnaround camera setup complete")
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# ============================================
# PROPERTIES
# ============================================

# Asset type options
ASSET_TYPE_ITEMS = [
    ('model', 'Model', 'Model render'),
    ('blocking', 'Blocking', 'Blocking render'),
    ('sculpt', 'Sculpt', 'Sculpt render'),
    ('shading', 'Shading', 'Shading render'),
    ('rig', 'Rig', 'Rig render'),
]

# Shot type options
SHOT_TYPE_ITEMS = [
    ('element', 'Element', 'Element render'),
    ('vfx', 'VFX', 'VFX render'),
    ('lighting', 'Lighting', 'Lighting render'),
    ('char', 'Character', 'Character render'),
    ('bg', 'Background', 'Background render'),
    ('fg', 'Foreground', 'Foreground render'),
]


class FF_RendProperties(bpy.types.PropertyGroup):
    """Custom properties for FF Render tools"""
    
    # Render type selection (radio button behavior)
    render_type: bpy.props.EnumProperty(
        name="Render Type",
        description="Select render type",
        items=[
            ('asset', 'Asset', 'Asset render'),
            ('shot', 'Shot', 'Shot render'),
        ],
        default='asset',
        options={'ANIMATABLE'}
    )
    
    # Asset type dropdown
    asset_type: bpy.props.EnumProperty(
        name="Asset Type",
        description="Select asset type",
        items=ASSET_TYPE_ITEMS,
        default='model',
        options={'ANIMATABLE'}
    )
    
    # Shot type dropdown
    shot_type: bpy.props.EnumProperty(
        name="Shot Type",
        description="Select shot type",
        items=SHOT_TYPE_ITEMS,
        default='element',
        options={'ANIMATABLE'}
    )
    
    # Custom suffix input
    custom_suffix: bpy.props.StringProperty(
        name="Custom Suffix",
        description="Custom suffix for output filename (auto-filled based on type selection)",
        default="",
        options={'ANIMATABLE'}
    )
    
    # Use same directory (output path = blender file location)
    use_same_dir: bpy.props.BoolProperty(
        name="Use Same Directory",
        description="Use the same output directory as blender file location",
        default=False,
        options={'ANIMATABLE'}
    )
    
    # Use subdirectory (create subfolder based on filename)
    use_subdir: bpy.props.BoolProperty(
        name="Use Subdirectory",
        description="Create subdirectory based on blender filename",
        default=True,
        options={'ANIMATABLE'}
    )
    
    # Use file version (extract version from filename)
    use_file_version: bpy.props.BoolProperty(
        name="Use File Version",
        description="Extract and use version number from blender filename",
        default=True,
        options={'ANIMATABLE'}
    )


# ============================================
# PANELS
# ============================================

# Original N-Panel (kept for backward compatibility)
class FfPollRend():
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    @classmethod
    def poll(cls, context):
        return context.scene.ff_rend == True


class FF_PT_Rend(FfPollRend, bpy.types.Panel):
    bl_idname = "FF_PT_Rend"
    bl_label = "Rendering"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text='CAMERA TOOLS')
        row = col.row(align=True)
        row.operator("ffrend.prepare_char_sheet", text="Prepare Char Sheet", icon="OUTLINER_OB_CAMERA")
        row = col.row(align=True)
        row.operator("ffrend.setup_360_turnaround", text="Setup 360 Turnaround", icon="CON_TRACKTO")


# NEW: Inject buttons into existing Output Properties panel
class FF_PT_OutputPanel(bpy.types.Panel):
    """Inject custom render buttons into Output Properties"""
    bl_idname = "FF_PT_OutputPanel"
    bl_label = "FF Render Tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'output'
    bl_order = 1  # Lower number = appears earlier in the panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Check if properties are registered
        if not hasattr(scene, 'ff_rend_props'):
            layout.label(text="Properties not registered yet", icon="ERROR")
            return
            
        props = scene.ff_rend_props
        
        # Create a box for our custom settings
        box = layout.box()
        box.label(text="FF Render Tools", icon="IMAGE_PLANE")
        
        # Row 1: Render Type + Type-specific dropdown
        row = box.row(align=True)
        row.prop(props, "render_type", text="")
        if props.render_type == 'asset':
            row.prop(props, "asset_type", text="")
        else:
            row.prop(props, "shot_type", text="")
        
        # Row 2: Custom suffix
        row = box.row(align=True)
        row.prop(props, "custom_suffix", text="Custom Suffix")
        
        # Row 3: All checkboxes in one row
        row = box.row(align=True)
        row.prop(props, "use_same_dir", text="Same Dir")
        row.prop(props, "use_subdir", text="Subdir")
        row.prop(props, "use_file_version", text="Version")
        
        box.separator()
        
        # Row 4: Render operators (PNG, EXR, Playblast)
        row = box.row(align=True)
        row.operator("ffrend.png_render", text="PNG", icon="IMAGE_DATA")
        row.operator("ffrend.exr_render", text="EXR", icon="IMAGE_DATA")
        row.operator("ffrend.playblast_mp4", text="Playblast", icon="RENDER_ANIMATION")


# ============================================
# REGISTRATION (handled in __init__.py)
# ============================================

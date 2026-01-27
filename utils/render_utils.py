import bpy
import re
from pathlib import Path


def extract_version_from_filename(filename):
    """
    Extract version number from filename like 'asset_john_v3.blend' -> 'v3'
    """
    # Match pattern like _v1, _v2, _v001, etc.
    match = re.search(r'_v(\d+)', filename, re.IGNORECASE)
    if match:
        return f"v{match.group(1)}"
    return None


def build_output_path(context, render_type, output_mode='renders'):
    """
    Build output path based on all properties
    
    Args:
        context: Blender context
        render_type: 'png', 'exr', or 'playblast'
        output_mode: 'renders' or 'previews'
    """
    scene = context.scene
    props = scene.ff_rend_props
    
    # Get blender file info
    bfp = Path(bpy.data.filepath)
    if not bfp.name:
        raise ValueError("Please save the blender file first")
    
    filename = bfp.name
    base_name = bpy.path.basename(filename).split('.')[0]
    
    # Determine base path
    if props.use_same_dir:
        # Use same directory as blender file
        base_path = bfp.parent
    else:
        # Use parent directory
        base_path = bfp.parent.parent
    
    # Add output mode (renders or previews)
    output_path = base_path / output_mode
    
    # Build suffix based on render type
    suffix_parts = []
    
    if props.render_type == 'asset':
        suffix_parts.append('asset')
        # Add asset type
        if props.asset_type:
            suffix_parts.append(props.asset_type)
    else:  # shot
        suffix_parts.append('shot')
        # Add shot type
        if props.shot_type:
            suffix_parts.append(props.shot_type)
    
    # Add custom suffix if provided
    if props.custom_suffix.strip():
        suffix_parts.append(props.custom_suffix.strip())
    
    # Add version if enabled
    if props.use_file_version:
        version = extract_version_from_filename(filename)
        if version:
            suffix_parts.append(version)
    
    # Join suffix parts with underscores
    suffix = '_'.join(suffix_parts)
    
    # Build final path
    if props.use_subdir:
        # Create subdirectory based on blender filename
        output_path = output_path / base_name / suffix
    else:
        # Just add suffix to output path
        output_path = output_path / suffix
    
    # Create directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    return output_path, suffix


def render_png_passes(context):
    """
    Setup PNG render with passes
    """
    # Build output path
    output_path, suffix = build_output_path(context, 'png', 'renders')
    
    # Set output path and settings
    context.scene.render.filepath = output_path.as_posix() + '/image_'
    context.scene.render.image_settings.file_format = 'PNG'
    context.scene.render.image_settings.color_mode = 'RGBA'
    context.scene.render.image_settings.color_depth = '8'
    context.scene.render.use_file_extension = True
    context.scene.render.use_compositing = True
    context.scene.render.resolution_percentage = 100
    
    # Setup compositing nodes
    context.scene.use_nodes = True
    print ("DONE")
    # Remove existing output nodes
    # output_nodes = [x for x in context.scene.node_tree.nodes if x.type == 'OUTPUT_FILE']
    # for node in output_nodes:
    #     context.scene.node_tree.nodes.remove(node)
    
    # # Get render layer node
    # rend_lyr_nodes = [x for x in context.scene.node_tree.nodes if x.type == 'R_LAYERS']
    # rend_lyr_node = rend_lyr_nodes[0] if rend_lyr_nodes else None
    
    # if rend_lyr_node:
    #     tree = context.scene.node_tree
    #     np = rend_lyr_node.location
    #     iteration = 1
        
    #     # Setup render passes
    #     render_passes = {
    #         "DiffCol": context.scene.view_layers[0].use_pass_diffuse_color,
    #         "DiffDir": context.scene.view_layers[0].use_pass_diffuse_direct,
    #         "GlossCol": context.scene.view_layers[0].use_pass_glossy_color,
    #         "GlossDir": context.scene.view_layers[0].use_pass_glossy_direct,
    #         "Shadow": context.scene.view_layers[0].use_pass_shadow,
    #         "AO": context.scene.view_layers[0].use_pass_ambient_occlusion,
    #         "Mist": context.scene.view_layers[0].use_pass_mist,
    #         "Emit": context.scene.view_layers[0].use_pass_emit,
    #         "Normal": context.scene.view_layers[0].use_pass_normal,
    #         "Depth": context.scene.view_layers[0].use_pass_z
    #     }
        
    #     for each_pass, is_enabled in render_passes.items():
    #         if is_enabled:
    #             n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
    #             tree.links.new(rend_lyr_node.outputs[each_pass], n.inputs[0])
    #             n.base_path = output_path.as_posix() + '/' + each_pass
    #             npx = np.x + 800
    #             npy = np.y - (iteration * 100)
    #             n.location = ((npx, npy))
    #             iteration = iteration + 1
        
    #     # Setup AOVs
    #     aovs = context.scene.view_layers[0].aovs
    #     for aov in aovs:
    #         print(aov.name)
    #         n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
    #         tree.links.new(rend_lyr_node.outputs[aov.name], n.inputs[0])
    #         n.base_path = output_path.as_posix() + '/' + aov.name
    #         npx = np.x + 800
    #         npy = np.y - (iteration * 100)
    #         n.location = ((npx, npy))
    #         iteration = iteration + 1


def render_exr_passes(context):
    """
    Setup EXR render with passes
    """
    # Build output path
    output_path, suffix = build_output_path(context, 'exr', 'renders')
    
    # Set output path and settings for EXR
    context.scene.render.filepath = output_path.as_posix() + '/image_'
    context.scene.render.image_settings.file_format = 'OPEN_EXR'
    context.scene.render.image_settings.color_mode = 'RGBA'
    context.scene.render.image_settings.color_depth = '16'
    context.scene.render.use_file_extension = True
    context.scene.render.use_compositing = True
    context.scene.render.resolution_percentage = 100
    
    # Setup compositing nodes
    context.scene.use_nodes = True
    
    # Remove existing output nodes
    output_nodes = [x for x in context.scene.node_tree.nodes if x.type == 'OUTPUT_FILE']
    for node in output_nodes:
        context.scene.node_tree.nodes.remove(node)
    
    # Get render layer node
    rend_lyr_nodes = [x for x in context.scene.node_tree.nodes if x.type == 'R_LAYERS']
    rend_lyr_node = rend_lyr_nodes[0] if rend_lyr_nodes else None
    
    if rend_lyr_node:
        tree = context.scene.node_tree
        np = rend_lyr_node.location
        iteration = 1
        
        # Setup render passes
        render_passes = {
            "DiffCol": context.scene.view_layers[0].use_pass_diffuse_color,
            "DiffDir": context.scene.view_layers[0].use_pass_diffuse_direct,
            "GlossCol": context.scene.view_layers[0].use_pass_glossy_color,
            "GlossDir": context.scene.view_layers[0].use_pass_glossy_direct,
            "Shadow": context.scene.view_layers[0].use_pass_shadow,
            "AO": context.scene.view_layers[0].use_pass_ambient_occlusion,
            "Mist": context.scene.view_layers[0].use_pass_mist,
            "Emit": context.scene.view_layers[0].use_pass_emit,
            "Normal": context.scene.view_layers[0].use_pass_normal,
            "Depth": context.scene.view_layers[0].use_pass_z
        }
        
        for each_pass, is_enabled in render_passes.items():
            if is_enabled:
                n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
                tree.links.new(rend_lyr_node.outputs[each_pass], n.inputs[0])
                n.base_path = output_path.as_posix() + '/' + each_pass
                npx = np.x + 800
                npy = np.y - (iteration * 100)
                n.location = ((npx, npy))
                iteration = iteration + 1
        
        # Setup AOVs
        aovs = context.scene.view_layers[0].aovs
        for aov in aovs:
            print(aov.name)
            n = context.scene.node_tree.nodes.new(type='CompositorNodeOutputFile')
            tree.links.new(rend_lyr_node.outputs[aov.name], n.inputs[0])
            n.base_path = output_path.as_posix() + '/' + aov.name
            npx = np.x + 800
            npy = np.y - (iteration * 100)
            n.location = ((npx, npy))
            iteration = iteration + 1


def render_playblast_mp4(context, res=100):
    """
    Setup preview mp4 playblast
    """
    # Build output path
    output_path, suffix = build_output_path(context, 'playblast', 'previews')
    
    # Get blender filename for mp4 name
    bfp = Path(bpy.data.filepath)
    base_name = bpy.path.basename(bfp.name).split('.')[0]
    
    # Set output path and settings for MP4
    context.scene.render.filepath = output_path.as_posix() + '/' + base_name + '_' + suffix + '.mp4'
    context.scene.render.image_settings.file_format = 'FFMPEG'
    context.scene.render.ffmpeg.format = 'MPEG4'
    context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    context.scene.render.ffmpeg.gopsize = 4
    context.scene.render.resolution_percentage = res


def toggle_use_compositing(context):
    """
    Toggle use compositing setting
    """
    context.scene.render.use_compositing = not context.scene.render.use_compositing

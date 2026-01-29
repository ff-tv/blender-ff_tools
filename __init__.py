# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "FF_Tools",
    "author" : "lalamax3d",
    "description" : "simple tools for myself",
    "blender" : (5, 0, 0),
    "version" : (0, 5, 1),
    "location" : "View3D",
    "warning" : "",
    "category" : "Animation"
}

import bpy
from bpy import context as context

from . ff_model import FfModelingPropGrp
from . ff_anim import FfAnimPropGrp
from . ff_model import SelectHalfMesh_OT_Operator, ReMirror_OT_Operator, FindMissingFiles_OT_Operator, FixDuplicateMaterials_OT_Operator,UpdateSelectionFilterClass_OT_Operator,UpdateDeselectionFilterClass_OT_Operator,CreateAssetsFromSelectionEmpty_OT_Operator,CreateAssetsFromSelectionMesh_OT_Operator, UpdateSceneMatsNormalMapStrength_OT_Operator, BulkImportClass_OT_Operator, FF_PT_Model
from . ff_facecap import FfFaceCapPropGrp
from . ff_rig import UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator, SetQuatRotations_OT_Operator , exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator, FF_PT_Rig
from . ff_anim import CopyIklegs_OT_Operator, CopyIkArms_OT_Operator, KeySelectionOp_OT_Operator, KeyDeletionOp_OT_Operator, FF_PT_Anim
from . ff_anim import EnableFcurveModifers_OT_Operator, EnableFcurveModifersAll_OT_Operator, DisableFcurveModifers_OT_Operator, DisableFcurveModifersAll_OT_Operator
from . ff_anim import MirrorFcurveModifers_OT_Operator, CopyFcurveModifiers_OT_Operator
from . ff_rend import FF_OT_PngRender, FF_OT_ExrRender, FF_OT_PlayblastMp4, FF_OT_SetupCharSheet, FF_OT_RenderCharSheet, FF_OT_Setup360Turnaround, FF_PT_Rend, FF_PT_OutputPanel


from . ff_sk import SkZeroAll_OT_Operator,SkAnimateAll_OT_Operator,SkBindToBone_OT_Operator
from . ff_facecap import ReadFaceCapJson_OT_Operator, SetupFcBoneProps_OT_Operator, SetupFcSingleDriver_OT_Operator, SetupFcDrivers_OT_Operator
# VARIABLES - globals for GUI button presses
bpy.types.Scene.ff_general = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_rigging = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_anim = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_facecap = bpy.props.BoolProperty(default=False)
bpy.types.Scene.ff_rend = bpy.props.BoolProperty(default=False)

# bpy.types.Scene.ff_skFilter = bpy.props.StringProperty(default='search shape')
bpy.types.Scene.ff_anim_kr = bpy.props.IntProperty(default=4,min=2,max=9,step=1)

# below line is special
bpy.types.Scene.ff_model_prop_grp = bpy.props.PointerProperty(type=FfModelingPropGrp)
bpy.types.Scene.ff_anim_prop_grp = bpy.props.PointerProperty(type=FfAnimPropGrp)
bpy.types.Scene.ff_rig_prop_grp = bpy.props.PointerProperty(type=FfFaceCapPropGrp)





# MAIN PANEL CONTROL
class FF_PT_Panel(bpy.types.Panel):
    bl_idname = "FF_PT_Panel"
    bl_label = "Film Factory Tools"
    bl_category = "FF_Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self,context):
        #active_obj = context.active_object
        layout = self.layout

        col = layout.column(align=1)
        row = col.row(align = True)
        row.prop(bpy.context.scene,"ff_general",text="Misc",icon="EDITMODE_HLT")
        row.prop(bpy.context.scene,"ff_rigging",text="Rigg",icon="ARMATURE_DATA")
        row.prop(bpy.context.scene,"ff_anim",text="Anim",icon="POSE_HLT")
        row.prop(bpy.context.scene,"ff_rend",text="Rend",icon="IMAGE_PLANE")

classes = (
        SelectHalfMesh_OT_Operator, ReMirror_OT_Operator, FindMissingFiles_OT_Operator, FixDuplicateMaterials_OT_Operator,CreateAssetsFromSelectionEmpty_OT_Operator,CreateAssetsFromSelectionMesh_OT_Operator,UpdateSelectionFilterClass_OT_Operator,UpdateDeselectionFilterClass_OT_Operator,UpdateSceneMatsNormalMapStrength_OT_Operator,BulkImportClass_OT_Operator,
        SkZeroAll_OT_Operator, SkAnimateAll_OT_Operator, SkBindToBone_OT_Operator,
        UseSingleSideControls_OT_Operator, SelectOneSidedObjects_OT_Operator, SetEulerRotations_OT_Operator,SetQuatRotations_OT_Operator,
        exportDriversToJson_OT_Operator, importDriversFromJson_OT_Operator,
        CopyIkArms_OT_Operator, CopyIklegs_OT_Operator,
        KeySelectionOp_OT_Operator,KeyDeletionOp_OT_Operator,
        EnableFcurveModifers_OT_Operator,EnableFcurveModifersAll_OT_Operator,
        DisableFcurveModifers_OT_Operator, DisableFcurveModifersAll_OT_Operator,
        MirrorFcurveModifers_OT_Operator, CopyFcurveModifiers_OT_Operator, 
        ReadFaceCapJson_OT_Operator, SetupFcBoneProps_OT_Operator,SetupFcSingleDriver_OT_Operator,SetupFcDrivers_OT_Operator,
        FF_OT_PngRender, FF_OT_ExrRender, FF_OT_PlayblastMp4, FF_OT_SetupCharSheet, FF_OT_RenderCharSheet, FF_OT_Setup360Turnaround,
        FF_PT_Panel, FF_PT_Model, FF_PT_Rig, FF_PT_Anim, FF_PT_Rend, FF_PT_OutputPanel)


def register():
    from .ff_rend import FF_RendProperties
    
    # Register FF_RendProperties first (before other classes that might use it)
    bpy.utils.register_class(FF_RendProperties)
    
    # Register all other classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Register custom properties for render tools
    bpy.types.Scene.ff_rend_props = bpy.props.PointerProperty(type=FF_RendProperties)


def unregister():
    from .ff_rend import FF_RendProperties
    
    # Unregister custom properties first
    if hasattr(bpy.types.Scene, 'ff_rend_props'):
        del bpy.types.Scene.ff_rend_props
    
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister FF_RendProperties last
    bpy.utils.unregister_class(FF_RendProperties)

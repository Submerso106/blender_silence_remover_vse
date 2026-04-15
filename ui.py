import bpy

class SilenceRemoverPanel(bpy.types.Panel):
    bl_label = "Silence Remover"
    bl_idname = "SEQUENCER_PT_silence_remover"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Silence Remover'

    def draw(self, context):
        props = context.scene.properties

        layout = self.layout
        layout.label(text="Remove silences from selected audio strips")
        layout.separator()

        layout.label(text="Export Options:")
        col = layout.column(align=True)
        col.prop(props, "same_filepath_as_source", text="Same Filepath as Source")
        if not props.same_filepath_as_source:
            col.prop(props, "export_filepath", text="Export Filepath")
        layout.separator()

        layout.label(text="Silence Detection Options:")
        col = layout.column(align=True)
        col.prop(props, "min_silence_len", text="Min Silence Length (ms)", emboss=True)
        col.prop(props, "silence_thresh", text="Silence Threshold (dBFS)", emboss=True)
        col.prop(props, "step", text="Seek Step (ms)", emboss=True)
        col.prop(props, "padding", text="Padding (ms)", emboss=True)
        layout.operator(
            "sequencer.remove_silence", 
            text="Remove Silence",
            emboss=True
        )

class SilenceRemoverProperties(bpy.types.PropertyGroup):
    export_filepath: bpy.props.StringProperty(
        name="Export Filepath",
        description="Filepath for the exported audio file",
        default=""
    ) #type: ignore
    same_filepath_as_source: bpy.props.BoolProperty(
        name="Same Filepath as Source",
        description="Use the same filepath as the source audio file for the exported audio file",
        default=True
    )#type: ignore
    min_silence_len: bpy.props.IntProperty(
        name="Min Silence Length",
        description="Minimum length of silence to be removed (ms)",
        default=400,
        min=0
    ) #type: ignore
    silence_thresh: bpy.props.IntProperty(
        name="Silence Threshold",
        description="Threshold for what is considered silence (dBFS)",
        default=-40,
        min=-100,
        max=10
    ) #type: ignore
    step: bpy.props.IntProperty(
        name="Seek Step",
        description="Step size for seeking through the audio (ms). Smaller values can be more accurate but slower",
        default=10,
        min=1
    ) #type: ignore
    padding: bpy.props.IntProperty(
        name="Padding",
        description="Amount of silence to keep at the beginning and end of each cut (ms)",
        default=200,
        min=0
    ) #type: ignore

def register():
    bpy.utils.register_class(SilenceRemoverPanel)
    bpy.utils.register_class(SilenceRemoverProperties)
    bpy.types.Scene.properties = bpy.props.PointerProperty(type=SilenceRemoverProperties)

def unregister():
    bpy.utils.unregister_class(SilenceRemoverPanel)
    bpy.utils.unregister_class(SilenceRemoverProperties)
    del bpy.types.Scene.properties
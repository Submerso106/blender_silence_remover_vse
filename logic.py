import bpy
from pydub import AudioSegment
from pydub import silence

class SEQUENCER_OT_remove_silence(bpy.types.Operator):
    bl_idname = "sequencer.remove_silence"
    bl_label = "Remove Silence"

    def execute(self, context):
        seq = context.scene.sequence_editor.active_strip  
        props = context.scene.properties     

        if not seq or seq.type != 'SOUND':
            self.report({'ERROR'}, "Selecione uma strip de áudio")
            return {'CANCELLED'}

        filepath = bpy.path.abspath(seq.sound.filepath)
        audio = AudioSegment.from_file(filepath)

        cuts = silence.split_on_silence(
            audio,
            min_silence_len=props.min_silence_len,
            silence_thresh=props.silence_thresh,
            seek_step=props.step,
            keep_silence=props.padding
        )

        cut_audio = AudioSegment.empty()
        cut_path = props.export_filepath if not props.same_filepath_as_source else filepath

        for cut in cuts:
            cut_audio += cut

        cut_audio.export(cut_path + ".mp3", format="mp3")

        scene = context.scene
        fps = scene.render.fps
        channel = seq.channel
        current_frame = seq.frame_start
        
        # Remove a strip original
        bpy.ops.sequencer.delete()

        bpy.context.scene.sequence_editor.sequences_all
        seq_editor = context.scene.sequence_editor

        new_strip = seq_editor.sequences.new_sound(
            name="Cut",
            filepath=cut_path + ".mp3",
            channel=channel,
            frame_start=int(current_frame)
        )

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(SEQUENCER_OT_remove_silence)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_remove_silence)  
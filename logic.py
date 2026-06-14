import os
import bpy
from pydub import AudioSegment
from pydub import silence

class SEQUENCER_OT_set_silence_remover_mode(bpy.types.Operator):
    bl_idname = "vse.set_silence_remover_mode"
    bl_label = "Set Silencer Remover Mode"
    bl_description = "Set the mode for silence removal"

    value: bpy.props.StringProperty()#type: ignore

    def execute(self, context):
        context.scene.properties.mode = self.value
        return {'FINISHED'}

class SEQUENCER_OT_remove_silence(bpy.types.Operator):
    bl_idname = "sequencer.remove_silence"
    bl_label = "Remove Silence"

    def make_cuts(self, props, audio):
        cuts = silence.split_on_silence(
            audio,
            min_silence_len=props.min_silence_len,
            silence_thresh=props.silence_thresh,
            seek_step=props.step,
            keep_silence=props.padding
        )

        return cuts

    def remove_silence_audio(self, context, props, seq, audio):
        cuts = self.make_cuts(props, audio)

        cut_audio = AudioSegment.empty()
        cut_path = props.export_filepath if not props.same_filepath_as_source else filepath
        base = os.path.splitext(cut_path)[0]
        output_path = base + "_cut"

        for cut in cuts:
            cut_audio += cut

        cut_audio.export(output_path + ".mp3", format="mp3")

        channel = seq.channel
        current_frame = seq.frame_start
        
        bpy.ops.sequencer.delete()

        seq_editor = context.scene.sequence_editor

        seq_editor.sequences.new_sound(
            name="Cut",
            filepath=output_path + ".mp3",
            channel=channel,
            frame_start=int(current_frame)
        )

    def remove_silence_video(self, context, props, seq, audio):
        cuts = self.make_cuts(props, audio)

        

    def execute(self, context):
        seq = context.scene.sequence_editor.active_strip  
        props = context.scene.properties  

        if not seq or seq.type != 'SOUND':
            self.report({'ERROR'}, "Selecione uma strip de áudio")
            return {'CANCELLED'} 
        
        filepath = bpy.path.abspath(seq.sound.filepath)
        audio = AudioSegment.from_file(filepath)

        if props.mode == "Audio": self.remove_silence_audio(context, props, seq, audio)  
        if props.mode == "Video": self.remove_silence_audio(context, props, seq, audio)

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(SEQUENCER_OT_remove_silence)
    bpy.utils.register_class(SEQUENCER_OT_set_silence_remover_mode)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_remove_silence)  
    bpy.utils.unregister_class(SEQUENCER_OT_set_silence_remover_mode)
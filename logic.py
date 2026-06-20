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
    bl_options = {'REGISTER', 'UNDO'}

    scene_fps = None

    def new_audio_without_silence(self, props, seq, audio):
        self.report({'DEBUG'}, "Removing Silence, may freeze Blender for a while")
        cuts = silence.split_on_silence(
            audio,
            min_silence_len=props.min_silence_len,
            silence_thresh=props.silence_thresh,
            seek_step=props.step,
            keep_silence=props.padding
        )

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
    
    def split_silence(self, context: bpy.types.Context, props, seq, audio):
        silences = silence.detect_silence(
            audio,
            min_silence_len=props.min_silence_len,
            silence_thresh=props.silence_thresh,
            seek_step=props.step,
        )

        bpy.context.preferences.view.show_splash = False
        fps_const = 1000 / self.scene_fps
        offset = int(seq.frame_start)

        cut_silences = []
        sequences = context.scene.sequence_editor.sequences

        """ for split in silences:
            start_frame = int(offset) + int((split[0] + props.padding) / fps_const)
            end_frame = int(offset) + int(split[1] / fps_const)
            
            bpy.ops.sequencer.split(frame=start_frame, side="RIGHT")

            bpy.ops.sequencer.split(frame=end_frame, side="RIGHT")

            for s in sequences:
                if s.frame_start == start_frame:
                    cut_silences.append(s)
                    print(s.frame_start) """

        previous = None
        name = seq.name
        filepath = bpy.path.abspath(seq.sound.filepath)
        channel = seq.channel
        frame = 0# props.padding / fps_const
        index = 0

        bpy.ops.sequencer.delete()
        
        for split in silences:
            start_frame = offset + int((split[0] + props.padding) / fps_const)
            end_frame = offset + int(split[1] / fps_const)
            previous_end_frame = offset + int(silences[index - 1][1] / fps_const) if index > 0 else 0

            strip = sequences.new_sound(
                name=name,
                filepath=filepath,
                channel=channel,
                frame_start= end_frame,
            )
            
            if previous != None:
                duration = int(start_frame - previous_end_frame)
                previous.frame_final_duration = duration
                frame += duration

            strip.frame_offset_start = end_frame - offset
            strip.frame_start = 2*offset - end_frame + frame
            previous = strip  
            index += 1   

        bpy.context.preferences.view.show_splash = True

        """ for strip in cut_silences:
            print(strip.frame_start)
            strip.select = True """

    def remove_silence_audio(self, context, props, seq, audio):
        cuts = self.new_audio_without_silence(props, seq, audio)

    def remove_silence_video(self, context, props, seq, audio):
        silences = self.split_silence(context, props, seq, audio)

        

    def execute(self, context):
        seq = context.scene.sequence_editor.active_strip  
        props = context.scene.properties  
        self.scene_fps = context.scene.render.fps / context.scene.render.fps_base

        if not seq or seq.type != 'SOUND':
            self.report({'ERROR'}, "Selecione uma strip de áudio")
            return {'CANCELLED'} 
        
        filepath = bpy.path.abspath(seq.sound.filepath)
        audio = AudioSegment.from_file(filepath)

        if props.mode == "Audio": self.remove_silence_audio(context, props, seq, audio)  
        if props.mode == "Video": self.remove_silence_video(context, props, seq, audio)

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(SEQUENCER_OT_remove_silence)
    bpy.utils.register_class(SEQUENCER_OT_set_silence_remover_mode)

def unregister():
    bpy.utils.unregister_class(SEQUENCER_OT_remove_silence)  
    bpy.utils.unregister_class(SEQUENCER_OT_set_silence_remover_mode)
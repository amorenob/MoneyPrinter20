from moviepy.editor import TextClip, ImageClip, CompositeVideoClip

class FramedTextVideoClip():
    """A TextClip with a frame around it."""

    def __init__(self, text, frame_filename, font, fontsize, color, duration, frame_opacity=1, txt_padding=None, txt_left_margin=None):
        self.text = text
        self.frame_filename = frame_filename
        self.font = font
        self.fontsize = fontsize
        self.color = color
        self.duration = duration
        self.frame_clip = None
        self.text_clip = None
        self.frame_opacity = frame_opacity
        self.txt_left_margin = txt_left_margin
        self.txt_padding = txt_padding

        # Create the framed clip
        self.create_framedclip()

    def create_framedclip(self):
        # This creates a framed text clip
        # It will be composed as follows>
        # 1. A transition in frame clip if frame_in_effect is not None else a image frame
        # 2. A transition in clip with the text if text_in_effect is not None else a text clip
        # 3. A transition out clip with the text if text_out_effect is not None else a text clip
        # 4. A transition out frame clip if frame_out_effect is not None else a image frame
        # 5. A composite clip with all the clips

        # Create a frame clip
        self.frame_clip = ImageClip(
            self.frame_filename, 
            duration=self.duration,
        ).set_opacity(self.frame_opacity)

        # Ser the size of the text clip
        if self.txt_padding is not None:
            txt_size =  (self.frame_clip.size[0] - self.txt_padding*2, self.frame_clip.size[1] - self.txt_padding*2)
        else:
            txt_size = self.frame_clip.size
        
        # Set center by default
        pos_x = (self.frame_clip.w - txt_size[0])/2
        pos_y = (self.frame_clip.h - txt_size[1])/2
        txt_pos = (pos_x, pos_y)
        txt_align = 'center'

        # Set left margin if it is defined
        if self.txt_left_margin is not None:
            txt_align = 'west'
            txt_pos = (self.txt_left_margin, 'center')
            txt_size = (txt_size[0] - self.txt_left_margin, txt_size[1])


        # Create a text clip
        self.text_clip = TextClip(
            self.text, 
            fontsize=self.fontsize, 
            font=self.font,
            color=self.color,
            # bg_color='red', 
            size=txt_size,
            align=txt_align,
            method="caption",
        ).set_duration(self.duration).set_position(txt_pos)



        return None

    def apply_txt_effect(self, effect_function, *args, **kwargs):
        self.text_clip = effect_function(self.text_clip, *args, **kwargs)

    def apply_frame_effect(self, effect_function, *args, **kwargs):
        self.frame_clip = effect_function(self.frame_clip, *args, **kwargs)

    def get_composed_clip(self):
        # Create a composite clip with the frame and the text
        return CompositeVideoClip([self.frame_clip, self.text_clip], size=self.frame_clip.size).set_duration(self.duration)


    
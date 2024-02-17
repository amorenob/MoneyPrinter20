from moviepy.editor import TextClip, CompositeVideoClip, ImageClip, VideoFileClip
from moviepy.config import change_settings
from tiktokvoice import tts
from dotenv import load_dotenv
from utils import *
from animations import *
from sm_clips.sm_clips import FramedTextVideoClip
from search import search_for_stock_videos, save_video
import os
from PIL import Image
import yaml
import time

# Load environment variables
load_dotenv("./.env")

# Set environment variables
change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# Load the configuration file
with open('videos_config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)


video_type = 'TikTokQuesAns01'
config = config[video_type]

# Constants
OUTPUT_DIR = "./files"
TEMP_DIR = "./temp"
RESOURCES_DIR = "./rsc"

def create_quest_ans_clip(question, answers, ans_id):

    # get files configs
    quest_frame_fname = os.path.join(RESOURCES_DIR, config['QUEST_FRAME'])
    ans_frame_fname = os.path.join(RESOURCES_DIR, config['ANS_FRAME'])

    # Create a background clip based in a image
    bg_filename = os.path.join(RESOURCES_DIR, config['BACKGROUND_IMAGE'])
    bg_clip = ImageClip(
        bg_filename
        ).set_duration(config['QUEST_DURATION'])

    # Add bg audio
    bg_audio = AudioFileClip(os.path.join(RESOURCES_DIR, config['BACKGROUND_AUDIO']))\
        .subclip(5, config['QUEST_DURATION']+5)
    bg_clip = bg_clip.set_audio(bg_audio)

    bg_video = get_bg_videoclip(question, config['QUEST_DURATION'])

    quest_clip = FramedTextVideoClip(
        question, 
        frame_filename=quest_frame_fname, 
        font=config['FONT'], 
        fontsize=config['FONT_SIZE'], 
        color=config['FONT_COLOR'], 
        duration=config['QUEST_DURATION'], 
        txt_padding=config['QUEST_PADDING'], 
    )
    quest_clip.apply_txt_effect(slide_in, direction='left', duration=0.3)
    quest_clip = quest_clip.get_composed_clip().set_position(('center', config['TOP_MARGIN']))


    # Get the set the audio for the question
    quest_audio = get_audio_clip(question, config['VOICE']).set_start(0.3)
    # Add the audio to the question clip
    quest_clip = quest_clip.set_audio(quest_audio)

    # Position the question at the top
    current_height = quest_clip.pos(0)[1] + quest_clip.size[1] + config['ANS_PADDING']

    # Create the answer clips
    ans_clips = []
    for i, answer in enumerate(answers):
        ans_clips.append(FramedTextVideoClip(
            "({}) {}".format(chr(65+i), answer), 
            frame_filename=ans_frame_fname, 
            font=config['FONT'], 
            fontsize=config['FONT_SIZE'], 
            color=config['FONT_COLOR'], 
            duration=config['QUEST_DURATION']-config['ANS_START_TIME']-1,
            frame_opacity=config['ANS_FRAME_OPACITY'],
            txt_left_margin=config['ANS_LEFT_MARGIN'], 
        ))
        # Apply the effect to the answer
        ans_clips[i].apply_txt_effect(words_effect, 'cascade', duration=1)
        ans_clips[i].apply_txt_effect(fade_out, duration=1)
        ans_clips[i].apply_frame_effect(fade_out, duration=1)

        # Set the position of each answer 
        ans_clips[i] = ans_clips[i]\
            .get_composed_clip()\
            .set_position(('center', current_height))\
            .set_start(config['ANS_START_TIME'])
        current_height += ans_clips[i].size[1] + config['ANS_PADDING']

    # Create countdown from video clip
    countdown_clip = VideoFileClip(
        os.path.join(RESOURCES_DIR, config['COUNTDOWN_FILE'])
        ).set_duration(5).set_start(config['QUEST_DURATION']-5)
    countdown_clip = countdown_clip.set_position(config['COUNTDOWN_POSITION'])

    # Create a new higlited clip with a diferent color for the correct answer
    correct_ans_clip = FramedTextVideoClip(
        f"({chr(65+ans_id)}) {answers[ans_id]}", 
        frame_filename=ans_frame_fname, 
        font=config['FONT'], 
        fontsize=config['FONT_SIZE'], 
        color=config['HIGHLIGHT_COLOR'], 
        duration=2, 
        frame_opacity=config['ANS_FRAME_OPACITY'],
        txt_left_margin=config['ANS_LEFT_MARGIN'], 
    )
    # Apply the effect to the answer
    correct_ans_clip.apply_txt_effect(fade_in, duration=1)

    # Set the position of the correct answer
    correct_ans_clip = correct_ans_clip\
        .get_composed_clip()\
        .set_position(('center', ans_clips[ans_id].pos(2)[1]))\
        .set_start(config['QUEST_DURATION']-2)

    # Get and set audio for the correct answer
    correct_ans_audio = get_audio_clip(f"{chr(97+ans_id)}, {answers[ans_id]}", config['VOICE'])\
        .set_start(config['QUEST_DURATION']-2)
    correct_ans_clip = correct_ans_clip.set_audio(correct_ans_audio)

    clips_list = [ bg_video,  quest_clip, ] + ans_clips + [correct_ans_clip, countdown_clip]
    return CompositeVideoClip(clips_list).set_duration(config['QUEST_DURATION'])

def get_audio_clip(text, voice):
    filename = os.path.join(TEMP_DIR, "audio.mp3")
    tts(text, voice, filename)
    return AudioFileClip(filename)



def get_bg_videoclip(question, duration):
    search_term = "Capital cities"
    # Search for a video of the given search term
    video_urls = []
    # Search for a video
    found_urls = search_for_stock_videos(
        search_term, os.getenv("PEXELS_API_KEY"), 10, duration, config['VIDEO_SIZE']
    )
    # Check for duplicates
    for url in found_urls:
        if url not in video_urls:
            video_urls.append(url)

    # Define video_paths
    video_paths = []

    # Save the videos
    for video_url in video_urls:
        try:
            saved_video_path = save_video(video_url)
            video_paths.append(saved_video_path)
        except Exception:
            print("Error saving video")
    if len(video_paths) == 0:
        return None
    bg_x, bg_y = config['VIDEO_SIZE']
    bg_video = VideoFileClip(video_paths[0])\
        .subclip(0, duration)

    # Crop the video. video should be 1920x1080 aligned to the center
    x1 = (bg_video.w - bg_x)/2
    y1 = (bg_video.h - bg_y)/2
    x2 = x1 + bg_x
    y2 = y1 + bg_y
    bg_video = bg_video.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    return bg_video



if __name__ == "__main__":
    composed_clip = create_quest_ans_clip(
        "¿Wich is the capital of France?", 
        ["Paris", "London", "Berlin", "Madrid"],
        2
    )
    composed_clip.write_videofile(os.path.join(OUTPUT_DIR, "test.mp4"), fps=24)
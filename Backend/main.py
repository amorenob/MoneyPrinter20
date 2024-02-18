from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip
from moviepy.config import change_settings
from tiktokvoice import tts
from dotenv import load_dotenv
from utils import *
from animations import *
from sm_clips.sm_clips import FramedTextVideoClip
from search import search_for_stock_videos, save_video
from gpt import generate_trivia_questions
import os
from PIL import Image
import yaml
import json

# Load environment variables
load_dotenv("../.env")

# Set environment variables
change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

# Load the configuration file
with open('videos_config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)


video_type = 'TikTokQuesAns01'
config = config[video_type]
bg_last_cut = 0
# Constants
OUTPUT_DIR = "../files"
TEMP_DIR = "./temp"
RESOURCES_DIR = "../rsc"

def create_quest_ans_clip(question, answers, ans_id, bg_video_path=None, language="english"):
    global bg_last_cut
    # get files configs
    quest_frame_fname = os.path.join(RESOURCES_DIR, config['QUEST_FRAME'])
    ans_frame_fname = os.path.join(RESOURCES_DIR, config['ANS_FRAME'])
    countdown_video_fname = os.path.join(RESOURCES_DIR, config['COUNTDOWN_FILE'])
    countdown_audio_fname = os.path.join(RESOURCES_DIR, config['COUNTDOWN_AUDIO'])


    # Create countdown from video clip
    countdown_clip = VideoFileClip(countdown_video_fname)\
        .subclip(6-config['COUNTDOWN_TIME'])
    countdown_clip = countdown_clip.set_position(config['COUNTDOWN_POSITION'])

    # Get the set the audio for the question
    voice = config['VOICE'][language]
    quest_audio = get_audio_clip(question, voice)\
        .set_start(config['QUEST_EFECT']['duration'] )

    # Calculate question duration
    question_duration = \
        config['QUEST_EFECT']['duration'] + quest_audio.duration +\
        countdown_clip.duration + config['CORRECT_ANS']['duration'] 
    
    print(f"Question duration: {question_duration}")
    quest_clip = FramedTextVideoClip(
        question, 
        frame_filename=quest_frame_fname, 
        font=config['FONT'], 
        fontsize=config['FONT_SIZE'], 
        color=config['FONT_COLOR'], 
        duration=question_duration, 
        txt_padding=config['QUEST_PADDING'], 
    )

    # Apply opening effect to the question
    quest_clip.apply_txt_effect(
        animations[config['QUEST_EFECT']['effect_function']],
        direction=config['QUEST_EFECT']['direction'],
        duration=config['QUEST_EFECT']['duration']
    )
    quest_clip.apply_frame_effect(
        animations[config['QUEST_EFECT']['effect_function']],
        direction='down',
        duration=config['QUEST_EFECT']['duration']
    )

    quest_clip = quest_clip.get_composed_clip().set_position(('center', config['TOP_MARGIN']))
    # Add the audio to the question clip
    quest_clip = quest_clip.set_audio(quest_audio)

    # Add sound to the countdown
    countdown_audio = AudioFileClip(countdown_audio_fname)\
        .set_start(quest_audio.duration + config['QUEST_EFECT']['duration'] - 0.5)\
        .subclip(0, countdown_clip.duration)
    countdown_clip = countdown_clip\
        .set_start(quest_audio.duration + config['QUEST_EFECT']['duration'] - 0.5)\
        .set_audio(countdown_audio)

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
            duration=question_duration-config['ANS_START_TIME']-1,
            frame_opacity=config['ANS_FRAME_OPACITY'],
            txt_left_margin=config['ANS_LEFT_MARGIN'], 
        ))
        # Apply the effect to the answer
        ans_clips[i].apply_txt_effect(words_effect, 'cascade', duration=1)
        ans_clips[i].apply_txt_effect(fade_out, duration=0.5)
        ans_clips[i].apply_frame_effect(fade_out, duration=0.5)

        # Set the position of each answer 
        ans_clips[i] = ans_clips[i]\
            .get_composed_clip()\
            .set_position(('center', current_height))\
            .set_start(config['ANS_START_TIME'])
        current_height += ans_clips[i].size[1] + config['ANS_PADDING']

    # Create a new higlited clip with a diferent color for the correct answer
    correct_ans_clip = FramedTextVideoClip(
        f"({chr(65+ans_id)}) {answers[ans_id]}", 
        frame_filename=ans_frame_fname, 
        font=config['FONT'], 
        fontsize=config['FONT_SIZE'], 
        color=config['HIGHLIGHT_COLOR'], 
        duration=config['CORRECT_ANS']['duration'], 
        frame_opacity=config['ANS_FRAME_OPACITY'],
        txt_left_margin=config['ANS_LEFT_MARGIN'], 
    )
    # Apply the effect to the answer
    correct_ans_clip.apply_txt_effect(fade_in, duration=1)

    # Set the position of the correct answer
    correct_ans_clip = correct_ans_clip\
        .get_composed_clip()\
        .set_position(('center', ans_clips[ans_id].pos(2)[1]))\
        .set_start(question_duration-2)

    # Get and set audio for the correct answer
    correct_ans_audio = get_audio_clip(f"{chr(97+ans_id)}, {answers[ans_id]}", voice)\
        .set_start(question_duration-2)
    correct_ans_clip = correct_ans_clip.set_audio(correct_ans_audio)



    # if not bg_video_path create a image based bg
    if not bg_video_path:
        bg_video = ImageClip(
            os.path.join(RESOURCES_DIR, config['BACKGROUND_IMAGE'])
            ).set_duration(question_duration)
    else: 

        bg_video = VideoFileClip(bg_video_path)\
            .loop(60)\
            .set_audio(None)\
            .subclip(bg_last_cut, question_duration + bg_last_cut)
        bg_last_cut += question_duration
        # Crop the video. video should be 1920x1080 aligned to the center
        bg_x, bg_y = config['VIDEO_SIZE']
        x1 = (bg_video.w - bg_x)/2
        y1 = (bg_video.h - bg_y)/2
        x2 = x1 + bg_x
        y2 = y1 + bg_y
        bg_video = bg_video.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    

    clips_list = [ bg_video,  quest_clip, ] + ans_clips + [correct_ans_clip, countdown_clip]
    return CompositeVideoClip(clips_list).set_duration(question_duration)

def get_audio_clip(text, voice):
    filename = os.path.join(TEMP_DIR, "audio.mp3")
    tts(text, voice, filename)
    return AudioFileClip(filename)


def get_bg_videoclip(topic, duration):

    # Search for a video of the given search term
    video_urls = []
    # Search for a video
    found_urls = search_for_stock_videos(
        topic, os.getenv("PEXELS_API_KEY"), 10, duration, config['VIDEO_SIZE']
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

    return video_paths[0]


def create_trivia_clip(topic, language="english"):

    bg_video_path = get_bg_videoclip(topic, 18)
    # generate trivia questions
    trivias = generate_trivia_questions(topic, 5, language, "gpt4")

    clips = []
    for trivia in trivias:
        clips.append(create_quest_ans_clip(trivia['question'], trivia['options'], trivia['correct_answer_index'], bg_video_path, language))
    
    trivia_video = concatenate_videoclips(clips)
    # Add bg audio
    bg_audio = AudioFileClip(os.path.join(RESOURCES_DIR, config['BACKGROUND_AUDIO']))\
        .subclip(5, trivia_video.duration+5)\
        .volumex(0.3)

    trivia_video = trivia_video.set_audio(CompositeAudioClip([trivia_video.audio, bg_audio]))
    trivia_video.write_videofile(os.path.join(OUTPUT_DIR, "trivia_video.mp4"), fps=24)

    return os.path.join(OUTPUT_DIR, "trivia_video.mp4")


if __name__ == "__main__":

    
    composed_clip = create_trivia_clip("World capitals")
    print(f"Trivia video: {composed_clip}")

    
from main import create_quest_ans_clip


if __name__ == "__main__":
    # Generate trivia questions
    video = create_quest_ans_clip(
        "Cual es la capital de Francia?", 
        ["Paris", "Londres", "Berlin", "Madrid"], 
        0, 
        language="spanish"
    )
    # Save the video
    video.write_videofile("../files/test_q.mp4")
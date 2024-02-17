from moviepy.editor import TextClip
import textwrap
from PIL import Image

# Wrap text function
def wrap_text(text, font, font_size, max_width):
    # Create a test clip to measure text width
    test_clip = TextClip("I", fontsize=font_size, font=font)
    print(test_clip.size)
    max_chars = max_width // test_clip.size[0]  # Estimate max number of characters per line
    print(max_chars)
    wrapped_text = textwrap.fill(text, width=max_chars)
    return wrapped_text

# Resise image function
def resize_image(filename, size):
    img = Image.open(filename)
    img = img.resize(size)
    img.save(filename)
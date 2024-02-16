import numpy as np

from moviepy.editor import *
from moviepy.video.tools.segmenting import findObjects


# helper function
rotMatrix = lambda a: np.array( [[np.cos(a),np.sin(a)], 
                                 [-np.sin(a),np.cos(a)]] )

def vortex(screenpos,i,nletters):
    d = lambda t : 1.0/(0.3+t**8) #damping
    a = i*np.pi/ nletters # angle of the movement
    v = rotMatrix(a).dot([-1,0])
    if i%2 : v[1] = -v[1]
    return lambda t: screenpos+400*d(t)*rotMatrix(0.5*d(t)*a).dot(v)
    
def cascade(screenpos, i, nletters):
    speed_factor = 1.8  # Increase to speed up, decrease to slow down
    v = np.array([0, -1])
    d = lambda t: 1 if (speed_factor * t) < 0 else abs(np.sinc(speed_factor * t) / (1 + (speed_factor * t)**4))
    return lambda t: screenpos + v * 400 * d(speed_factor * t - 0.15 * i)



def arrive(screenpos, i, nletters):
    speed_factor = 1.8  # Increase to speed up, decrease to slow down
    v = np.array([-1, 0])
    d = lambda t: max(0, 3 - 3 * (speed_factor * t))
    return lambda t: screenpos - 400 * v * d(speed_factor * t - 0.2 * i)

    
def vortexout(screenpos,i,nletters):
    d = lambda t : max(0,t) #damping
    a = i*np.pi/ nletters # angle of the movement
    v = rotMatrix(a).dot([-1,0])
    if i%2 : v[1] = -v[1]
    return lambda t: screenpos+400*d(t-0.1*i)*rotMatrix(-0.2*d(t)*a).dot(v)


# WE ANIMATE THE LETTERS

def moveLetters(letters, funcpos):
    return [ letter.set_pos(funcpos(letter.screenpos,i,len(letters)))
              for i,letter in enumerate(letters)]


def words_effect(txtClip, frame_clip, funcpos, duration=2):
    # dic of functions
    functions = {'vortex': vortex, 'cascade': cascade, 'arrive': arrive, 'vortexout': vortexout}
    f = functions[funcpos]
    # get the clip size
    size = txtClip.size
    org_duration = txtClip.duration

    cvc = CompositeVideoClip([txtClip.set_pos('center')], size=size).subclip(0,duration)
    # WE USE THE PLUGIN findObjects TO LOCATE AND SEPARATE EACH LETTER
    letters = findObjects(cvc, 50)  # a list of ImageClips
    clip1 = CompositeVideoClip(moveLetters(letters, f), size=size).subclip(0,duration)
    clip2 = txtClip.subclip(duration, org_duration).set_position('center')
    return concatenate_videoclips([clip1, clip2]).set_position(txtClip.pos(0))




def fade_in(clip, duration):
    return clip.crossfadein(duration)

def fade_out(clip, duration):
    return clip.crossfadeout(duration)

def slide_in(clip, frame_clip, duration):
    # slide in from the left side changing the position
    #save final position
    final_pos = clip.pos(0)

    
    starting_x = frame_clip.w

    if final_pos[0]=='center':
        final_x = (frame_clip.w - clip.w)/2
        t_factor = (frame_clip.w - final_x)/duration
    else:
        final_x = frame_clip.w - clip.w
        t_factor = frame_clip.w/duration


    def new_pos(t):
        t = min(t, duration)
        x = max(starting_x - t * t_factor, final_x)
        return (x, final_pos[1])
    
    return clip.set_pos(new_pos)
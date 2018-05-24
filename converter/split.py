import cv2
import os
import numpy as np
import sys
import tempfile


def split(root, file, amnt=None, delta=1, direction='forward', init=0):
    """Splits mp4 videos into individual frames.

    Args:
        root -- The folder containing the video to split.
        file -- File name.
        amnt -- (Optional) How many frames to split, None splits entire video (default None).
        delta -- (Optional) Interval between frames to split (default 1).
        direction -- (Optional) Whether to split forwards or backwards (default forward).
        init -- (Optional) Frame to start splitting from, starts from the end of the 
            video if direction is 'backwards' (default 0)

    Returns:
        A path containing the unique folder containing the frames.

    Raises:
        TODO fill this doc out
    """

    # TODO Write context manager for vc and wrap everything in a with statement.
    # TODO Maybe change vars so you don't reassign the parameters?
    # TODO make exceptions and stuff.
    # TODO UPDATE WHEN YOU'RE DELETING FROM THE MIDDLE (look at math req in split mid)

    # Opens the video file, if it can't be opened throws an error
    vid_path = os.path.join(root, file)
    print(root, file, vid_path)
    vc = cv2.VideoCapture(vid_path)
    if not vc.isOpened():
        # Maybe use a different error? Idk
        raise(FileNotFoundError("Couldn't open video file"))

    # If amnt is set to none, default to splitting the entire video
    maxFrames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
    if not amnt:
        amnt = maxFrames

    # Set the initial frame to split from
    vc.set(cv2.CAP_PROP_POS_FRAMES, init)

    # Make the unique directory that will contain the frames
    folder = tempfile.mkdtemp(dir=root)

    # Set up method if direction is backwards
    if direction == 'backward':
        print("splitting backwards")
        tempval = round(maxFrames - amnt*delta,-1) # The round is just for pretty numbers, not necessary
        init = tempval if tempval > 0 else 0
        amnt = maxFrames

    # Perform the actual video splitting from init to amnt
    print('init:'+str(init), 'delta:'+str(delta), 'amnt*delta+init:'+str(amnt*delta+init), 'amnt:'+str(amnt),
          'maxfrm:'+str(maxFrames))
    print(vid_path)
    for x in range(init, amnt*delta+init, delta):
        if (x < maxFrames) & (x >= 0):
            vc.set(cv2.CAP_PROP_POS_FRAMES, x)
            rval, frame = vc.read()
            if rval:
                cv2.imwrite(folder+'/'+str(x)+'.png', frame)
            else:
                break
    print("split complete")
    vc.release()
    return folder

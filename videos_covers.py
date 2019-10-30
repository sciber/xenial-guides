#!/usr/bin/python3
'''
Creates cover image in JPEG for every mp4 video file in VIDEO_PATH directory
'''

import os

VIDEO_PATH = os.path.join('media', 'video')


def _get_video_filenames():
    video_filenames = []
    for filename in os.listdir(VIDEO_PATH):
        if filename.endswith(".mp4"):
            video_filenames.append(os.path.join(VIDEO_PATH, filename[0:-4]))
    return video_filenames


def create_videos_cover_images():
    video_filenames = _get_video_filenames()
    for filename in video_filenames:
        print(filename + '.mp4')
        command = 'ffmpeg -i {}.mp4 {}.jpg'.format(filename, filename)
        os.system(command)


print('Creating cover images for files:')

create_videos_cover_images()

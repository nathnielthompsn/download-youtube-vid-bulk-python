import os
import json
import subprocess
import yt_dlp

# Load video list from JSON file
with open('file/vid.json', 'r', encoding='utf-8') as file:
    video_list = json.load(file)

output_dir = 'ssets'

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Download a stream and save it to a file using yt-dlp
def download_stream(url, stream_type, output):
    ydl_opts = {}
    
    if stream_type == 'video':
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]',
            'outtmpl': output,
        }
    elif stream_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]',
            'outtmpl': output,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Merge video and audio using ffmpeg and add LUT and watermark
def merge_video_audio(video_path, audio_path, output_path):
    lut_path = 'file/lut.cube'
    watermark_path = 'file/wm.png'
    command = (
        f'ffmpeg -i "{video_path}" -i "{audio_path}" -i "{watermark_path}" '
        f'-filter_complex "[0:v]lut3d={lut_path}[v];'
        f'[v][2:v]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2[vout]" '
        f'-map "[vout]" -map 1:a -c:v libx264 -c:a aac -strict experimental "{output_path}"'
    )
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise Exception(f"Error: {process.stderr.decode()}")

# Download and merge video and audio
def download_and_merge(url, video_output, audio_output, final_output):
    try:
        print(f'Downloading video to {video_output}...')
        download_stream(url, 'video', video_output)

        print(f'Downloading audio to {audio_output}...')
        download_stream(url, 'audio', audio_output)

        print(f'Merging video and audio to {final_output}...')
        merge_video_audio(video_output, audio_output, final_output)

        print('Cleaning up temporary files...')
        os.remove(video_output)
        os.remove(audio_output)

        print(f'Video downloaded and merged successfully: {final_output}')
    except Exception as err:
        print(err)

# Process each video in the list sequentially
def process_videos(video_list):
    for index, video in enumerate(video_list):
        video_filename = os.path.join(output_dir, f'temp_{video["title"]}_{index}.mp4')
        audio_filename = os.path.join(output_dir, f'temp_{video["title"]}_{index}.m4a')
        output_filename = os.path.join(output_dir, f'{video["title"]}.mp4')

        download_and_merge(video['url'], video_filename, audio_filename, output_filename)

# Run the process
process_videos(video_list)

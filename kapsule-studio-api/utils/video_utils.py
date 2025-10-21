import logging
import ffmpeg
import os
import math

logger = logging.getLogger(__name__)


def merge_audio_video(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Merge video and audio files using FFmpeg.
    Loops the video to match audio duration if needed.
    
    Args:
        video_path: Path to video file (silent video from Veo)
        audio_path: Path to audio file (user's music track)
        output_path: Path where merged video should be saved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Merging video and audio...")
        logger.info(f"  Video: {video_path}")
        logger.info(f"  Audio: {audio_path}")
        logger.info(f"  Output: {output_path}")
        
        # Validate input files exist
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get duration of both video and audio
        video_probe = ffmpeg.probe(video_path)
        audio_probe = ffmpeg.probe(audio_path)
        
        video_duration = float(video_probe['format']['duration'])
        audio_duration = float(audio_probe['format']['duration'])
        
        # Get video stream info
        video_info = next((s for s in video_probe['streams'] if s['codec_type'] == 'video'), None)
        if video_info:
            logger.info(f"  Video resolution: {video_info.get('width')}x{video_info.get('height')}")
            logger.info(f"  Video codec: {video_info.get('codec_name')}")
        
        logger.info(f"  Video duration: {video_duration:.2f}s")
        logger.info(f"  Audio duration: {audio_duration:.2f}s")
        
        # Load streams
        video_stream = ffmpeg.input(video_path)
        audio_stream = ffmpeg.input(audio_path)
        
        # If video is shorter than audio, loop it
        if video_duration < audio_duration:
            # Calculate how many loops we need
            loop_count = math.ceil(audio_duration / video_duration)
            logger.info(f"  Looping video {loop_count} times to match audio duration")
            
            # Use loop filter and trim to exact audio duration
            video_stream = (
                video_stream
                .video  # Explicitly select video stream
                .filter('loop', loop=loop_count - 1, size=32767)  # loop filter
                .filter('setpts', 'N/FRAME_RATE/TB')  # reset timestamps
                .filter('trim', duration=audio_duration)  # trim to exact audio length
                .filter('setpts', 'PTS-STARTPTS')  # reset PTS after trim
            )
            
            # Re-encode video since we applied filters
            (
                ffmpeg
                .output(
                    video_stream,
                    audio_stream.audio,
                    output_path,
                    vcodec='libx264',  # Need to re-encode with filters
                    acodec='aac',
                    audio_bitrate='192k',
                    video_bitrate='2M',
                    preset='fast',  # Fast encoding preset
                    crf=23,  # Quality setting
                    **{
                        'pix_fmt': 'yuv420p',  # Ensure compatibility
                        'movflags': '+faststart'  # Move moov atom to beginning for mobile Safari streaming
                    }
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        else:
            # Video is same length or longer - just merge
            logger.info(f"  Video is long enough, trimming to audio duration")
            
            # Trim video to audio duration
            video_stream = video_stream.video.filter('trim', duration=audio_duration).filter('setpts', 'PTS-STARTPTS')
            
            (
                ffmpeg
                .output(
                    video_stream,
                    audio_stream.audio,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    audio_bitrate='192k',
                    video_bitrate='2M',
                    preset='fast',
                    crf=23,
                    **{
                        'pix_fmt': 'yuv420p',
                        'movflags': '+faststart'  # Move moov atom to beginning for mobile Safari streaming
                    }
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        
        logger.info(f"Successfully merged video and audio to: {output_path}")
        
        return True
        
    except ffmpeg.Error as e:
        logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error merging video and audio: {str(e)}")
        return False


def cleanup_temp_files(*file_paths: str) -> None:
    """
    Delete temporary files.
    
    Args:
        *file_paths: Variable number of file paths to delete
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")


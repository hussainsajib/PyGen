import os
import subprocess
import imageio_ffmpeg
from factories.mushaf_fast_render import MushafRenderer
from processes.performance import PerformanceMonitor

class FFmpegEngine:
    def __init__(self, renderer: MushafRenderer, output_path: str, fps: int = 24):
        self.renderer = renderer
        self.output_path = output_path
        self.fps = fps
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def generate(self, duration_sec: float, audio_path: str = None, performance_monitor: PerformanceMonitor = None):
        """Generates the video file using FFmpeg piped sequence."""
        width, height = self.renderer.resolution
        
        # 1. Video Encoding Phase
        # We write to a temporary video file first if audio is needed
        temp_video_path = self.output_path if not audio_path else self.output_path + ".temp.mp4"
        
        ffmpeg_cmd = [
            self.ffmpeg_exe,
            '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{width}x{height}',
            '-pix_fmt', 'rgb24',
            '-r', str(self.fps),
            '-i', '-', # Input from pipe
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-pix_fmt', 'yuv420p',
            temp_video_path
        ]
        
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
        
        total_frames = int(duration_sec * self.fps)
        
        for frame_idx in range(total_frames):
            timestamp_sec = frame_idx / self.fps
            frame = self.renderer.get_frame_at(timestamp_sec)
            process.stdin.write(frame.tobytes())
            
            if frame_idx % (self.fps * 10) == 0:
                print(f"  [FFmpeg] Progress: {frame_idx}/{total_frames} frames", flush=True)
            
            if performance_monitor and frame_idx % self.fps == 0:
                performance_monitor.update_peak()
                
        process.stdin.close()
        process.wait()
        
        if process.returncode != 0:
            stderr = process.stderr.read().decode()
            raise RuntimeError(f"FFmpeg video encoding failed: {stderr}")
            
        # 2. Audio Merging Phase
        if audio_path and os.path.exists(audio_path):
            merge_cmd = [
                self.ffmpeg_exe,
                '-y',
                '-i', temp_video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest', # Match the duration of the shortest stream
                self.output_path
            ]
            
            merge_process = subprocess.run(merge_cmd, capture_output=True)
            if merge_process.returncode != 0:
                raise RuntimeError(f"FFmpeg audio merging failed: {merge_process.stderr.decode()}")
                
            # Clean up temp video
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
        return self.output_path

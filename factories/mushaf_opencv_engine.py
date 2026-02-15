import os
import cv2
import subprocess
import imageio_ffmpeg
from factories.mushaf_fast_render import MushafRenderer
from processes.performance import PerformanceMonitor

class OpenCVEngine:
    def __init__(self, renderer: MushafRenderer, output_path: str, fps: int = 24):
        self.renderer = renderer
        self.output_path = output_path
        self.fps = fps
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def generate(self, duration_sec: float, audio_path: str = None, performance_monitor: PerformanceMonitor = None):
        """Generates the video file using OpenCV VideoWriter."""
        width, height = self.renderer.resolution
        
        # 1. Video Encoding Phase
        temp_video_path = self.output_path if not audio_path else self.output_path + ".temp.mp4"
        
        # Define the codec and create VideoWriter object
        # 'mp4v' or 'avc1' are common for MP4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
        out = cv2.VideoWriter(temp_video_path, fourcc, self.fps, (width, height))
        
        total_frames = int(duration_sec * self.fps)
        
        for frame_idx in range(total_frames):
            timestamp_sec = frame_idx / self.fps
            frame_rgb = self.renderer.get_frame_at(timestamp_sec)
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
            
            if frame_idx % (self.fps * 10) == 0:
                print(f"  [OpenCV] Progress: {frame_idx}/{total_frames} frames", flush=True)
            
            if performance_monitor and frame_idx % self.fps == 0:
                performance_monitor.update_peak()
                
        out.release()
        
        # 2. Audio Merging Phase (via FFmpeg)
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
                '-shortest',
                self.output_path
            ]
            
            merge_process = subprocess.run(merge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if merge_process.returncode != 0:
                raise RuntimeError(f"FFmpeg audio merging failed")
                
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
        return self.output_path

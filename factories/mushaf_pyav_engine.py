import os
import av
import subprocess
import imageio_ffmpeg
import numpy as np
from factories.mushaf_fast_render import MushafRenderer
from processes.performance import PerformanceMonitor

class PyAVEngine:
    def __init__(self, renderer: MushafRenderer, output_path: str, fps: int = 24):
        self.renderer = renderer
        self.output_path = output_path
        self.fps = fps
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def generate(self, duration_sec: float, audio_path: str = None, performance_monitor: PerformanceMonitor = None):
        """Generates the video file using PyAV for direct stream encoding."""
        width, height = self.renderer.resolution
        
        # 1. Video Encoding Phase
        temp_video_path = self.output_path if not audio_path else self.output_path + ".temp.mp4"
        
        container = av.open(temp_video_path, mode='w')
        stream = container.add_stream('libx264', rate=self.fps)
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'
        # Set CRF for high quality and speed
        stream.options = {'crf': '18', 'preset': 'ultrafast'}
        
        total_frames = int(duration_sec * self.fps)
        
        for frame_idx in range(total_frames):
            timestamp_sec = frame_idx / self.fps
            frame_rgb = self.renderer.get_frame_at(timestamp_sec)
            
            # Create PyAV frame from numpy array
            frame = av.VideoFrame.from_ndarray(frame_rgb, format='rgb24')
            frame.pts = frame_idx # Set Presentation Timestamp
            
            for packet in stream.encode(frame):
                container.mux(packet)
            
            if performance_monitor and frame_idx % self.fps == 0:
                performance_monitor.update_peak()
                
        # Flush the encoder
        for packet in stream.encode():
            container.mux(packet)
            
        container.close()
        
        # 2. Audio Merging Phase (via FFmpeg)
        if audio_path and os.path.exists(audio_path):
            merge_cmd = [
                self.ffmpeg_exe,
                '-y',
                '-i', temp_video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', 0,
                '-map', 1,
                '-shortest',
                self.output_path
            ]
            
            merge_process = subprocess.run(merge_cmd, capture_output=True)
            if merge_process.returncode != 0:
                raise RuntimeError(f"FFmpeg audio merging failed: {merge_process.stderr.decode()}")
                
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
        
        return self.output_path

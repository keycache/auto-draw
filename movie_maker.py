import os
from glob import glob
from typing import Iterator

import cv2
from moviepy.config import change_settings
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    ImageSequenceClip,
    VideoClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
)
from moviepy.video import fx

from constants import Resolution
from utils import comparator_alphanum, mkdir

change_settings({"FFMPEG_BINARY": "/usr/local/bin/ffmpeg"})


class MovieMaker:
    def __init__(
        self,
        source_dir: str = None,
        intro_file_path: str = None,
        outro_file_path: str = None,
        target_dir: str = None,
        target_file_name: str = None,
        bg_audio_file_path: str = None,
        duration: int = None,
        shadow_image_path: str = None,
        frame_rate: int = 10,
        freeze_last_frame: bool = True,
    ) -> None:
        self.source_dir = source_dir
        self.bg_audio_file_path = bg_audio_file_path
        self.duration = duration
        self.target_dir = target_dir
        self.target_file_name = target_file_name
        self.frame_rate = frame_rate
        self.intro_file_path = intro_file_path
        self.outro_file_path = outro_file_path
        self.resolution = Resolution.YOUTUBE_HD
        self.shadow_image_path = shadow_image_path
        self.freeze_last_frame = freeze_last_frame
        self.setup()

    def setup(self):
        mkdir(self.target_dir)

    @property
    def height(self):
        return self.resolution[0]

    @property
    def width(self):
        return self.resolution[1]

    def get_imageclip(self, source_dir: str = None) -> VideoClip:
        source_dir = os.path.realpath(source_dir)
        os.chdir(source_dir)
        image_files = sorted(
            [
                os.path.join(source_dir, img)
                for img in os.listdir(source_dir)
                if img.endswith(".png")
            ],
            key=comparator_alphanum,
        )
        print(
            f"Found ->{len(image_files)} files in {source_dir}. e.g."
            f" {image_files[0]}"
        )
        image_clip = ImageSequenceClip(image_files, self.frame_rate)
        if self.freeze_last_frame:
            image_clip_freeze = ImageSequenceClip(
                image_files[-1:], durations=[5]
            )
            image_clip = concatenate_videoclips(
                [image_clip, image_clip_freeze]
            )
        return image_clip

    def blur(self, image):
        return cv2.blur(image, (50, 50))

    def process_fg_video_clip(self, clip_path: str) -> VideoClip:
        print("Processing FG video")
        video_clip = VideoFileClip(filename=clip_path)
        video_clip = self.add_shadow(
            video_clip=video_clip, shadow_image_path=self.shadow_image_path
        )
        return video_clip

    def process_bg_video_clip(self, clip_path: str) -> VideoClip:
        print("Processing bg video")
        video_clip = VideoFileClip(
            filename=clip_path, target_resolution=self.resolution
        )
        video_clip = video_clip.fl_image(self.blur)
        return video_clip

    def process_image_clip(self, source_dir: str) -> Iterator[str]:
        print(f"Processing images to video")
        file_name = "main.mp4"
        target_file_path = os.path.join(self.target_dir, file_name)
        if os.path.exists(target_file_path):
            print(f"Image Clip exists. {target_file_path}")
            return target_file_path
        video_clip = self.get_imageclip(source_dir=source_dir)
        print(f"Saving images to video")
        video_clip_path = self.save_videoclip(
            video_clip, target_file_name=file_name
        )
        return video_clip_path

    def process_audio(
        self, video_clip: VideoClip, audio_path: str = None
    ) -> VideoClip:
        print("Processing audio")
        audio_path = audio_path or self.bg_audio_file_path
        bg_audio_clip = AudioFileClip(audio_path)
        video_clip = self.add_audio(bg_audio_clip, video_clip=video_clip)
        return video_clip

    def process_vfx(self, video_clip: VideoClip) -> VideoClip:
        print("Adding V-FX")
        video_clip = self.vfx_freeze(video_clip=video_clip, duration=2)
        video_clip = self.vfx_fadein(video_clip=video_clip)
        video_clip = self.vfx_fadeout(video_clip=video_clip)
        print("Adding V-FX complete")
        return video_clip

    def vfx_fadein(self, video_clip: VideoClip, *args, **kwargs) -> VideoClip:
        return fx.all.fadein(video_clip, kwargs.get("fadein_duration", 1))

    def vfx_fadeout(self, video_clip: VideoClip, *args, **kwargs) -> VideoClip:
        return fx.all.fadeout(video_clip, kwargs.get("fadeout_duration", 1))

    def add_audio(
        self, audio_clip: AudioFileClip, video_clip: VideoClip, *args, **kwargs
    ) -> VideoClip:
        print("Adding audio")
        speed_factor = video_clip.duration / audio_clip.duration
        print(
            f"Speed factor is {speed_factor}. {audio_clip.duration} /"
            f" {video_clip.duration}"
        )
        video_clip = video_clip.fx(vfx.speedx, speed_factor)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip = video_clip.audio_fadeout(
            kwargs.get("audio_fadeout_duration", 2)
        )
        video_clip = video_clip.audio_fadein(
            kwargs.get("audio_fadein_duration", 2)
        )
        print("Adding audio complete")
        return video_clip

    def add_shadow(
        self, video_clip: VideoClip, shadow_image_path: str
    ) -> VideoClip:
        print("Adding shadow to video")
        video_clip = video_clip.resize(height=self.height)
        video_clip = video_clip.set_position(("center", "top"))
        shadow_bg_image = ImageClip(shadow_image_path).set_duration(
            video_clip.duration
        )
        shadow_bg_image = shadow_bg_image.resize(height=self.height + 20)
        video_clip = CompositeVideoClip(
            [shadow_bg_image, video_clip]
        ).set_position(("center", "top"))
        return video_clip

    def process_freeze_video(self, freeze_frame_path):
        return ImageSequenceClip([freeze_frame_path], durations=[5])

    def process(self) -> None:
        main_clip_path = self.process_image_clip(source_dir=self.source_dir)

        intro_videoclip = VideoFileClip(
            filename=self.intro_file_path,
            target_resolution=Resolution.YOUTUBE_HD,
        )
        outro_videoclip = VideoFileClip(
            filename=self.outro_file_path,
            target_resolution=Resolution.YOUTUBE_HD,
        )

        main_videoclip_fg = self.process_fg_video_clip(
            clip_path=main_clip_path
        )

        main_videoclip_bg = self.process_bg_video_clip(
            clip_path=main_clip_path
        )
        print("Composing BG and FG video")
        main_video_clip = CompositeVideoClip(
            [main_videoclip_bg, main_videoclip_fg]
        )

        main_video_clip = self.process_vfx(video_clip=main_video_clip)

        main_video_clip = self.process_audio(
            video_clip=main_video_clip, audio_path=self.bg_audio_file_path
        )

        final_video_clip = concatenate_videoclips(
            [intro_videoclip, main_video_clip, outro_videoclip]
        )

        self.save_videoclip(video_clip=final_video_clip)

    def save_videoclip(
        self,
        video_clip: VideoClip,
        target_dir: str = None,
        target_file_name: str = None,
    ):
        target_file_name = target_file_name or self.target_file_name
        target_dir = target_dir or self.target_dir
        target_file_path = os.path.join(target_dir, target_file_name)
        print(f"Saving video to {target_file_path}")
        video_clip.write_videofile(target_file_path, fps=self.frame_rate)
        return target_file_path


if __name__ == "__main__":
    mm = MovieMaker(
        intro_file_path=".data/assets/intro.mp4",
        outro_file_path=".data/assets/outro.mp4",
        shadow_image_path=".data/assets/shadow.png",
        source_dir=".data/images/mandala-ganesha/snapshots",
        bg_audio_file_path=".data/assets/music/a-day-in-india.mp3",
        target_dir=".data/images/mandala-ganesha/video",
        target_file_name="result.mp4",
    )
    mm.process()

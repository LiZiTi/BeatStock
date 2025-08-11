import librosa
import os

# 配置音频文件路径
AUDIO_FILES_DIR = "audio_files"

# 扫描指定路径下的所有 MP3 文件
def scan_audio_files():
    audio_files = []
    for file_name in os.listdir(AUDIO_FILES_DIR):
        if file_name.lower().endswith(".mp3"):
            audio_files.append({
                "name": os.path.splitext(file_name)[0],
                "file": file_name
            })
    return audio_files

# 从音频文件中提取音符触发时间点
def extract_beat_times(audio_file_path):
    """
    简化版：提取音频中的音符触发时间点（onsets），返回时间列表
    :param audio_file_path: 音频文件路径
    :return: 音符触发时间点列表（单位：秒）
    """
    try:
        # 加载音频文件，保留原始采样率
        y, sr = librosa.load(audio_file_path, sr=None)

        # 使用默认的触发点检测
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)

        # 将触发点帧数转换为时间
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        return onset_times.tolist()
    except Exception as e:
        print(f"Error processing {audio_file_path}: {e}")
        return []
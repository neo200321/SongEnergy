import os
import librosa
import numpy as np
import subprocess
from mutagen.id3 import ID3, TBPM, TCON
from mutagen.flac import FLAC
from mutagen import File
from mutagen.mp3 import MP3

# ====== 配置部分（用户可根据需求修改） ======
INPUT_FOLDER = r"WHERE/ARE/THE/SONGS"
FFMPEG_PATH = r"XXX"
AUDIO_EXTENSIONS = [".mp3", ".flac"]
VERIFY_WRITING = True


# ====== 情绪分类配置 ======
MOOD_CATEGORIES = [
    # ===== 核心情绪 =====
    {"name": "亢奋", "bpm_range": (150, 200), "energy_range": (0.85, 1.0), "fuzzy_energy_thresh": 0.1},
    {"name": "激昂", "bpm_range": (120, 160), "energy_range": (0.6, 0.95), "fuzzy_energy_thresh": 0.15},
    {"name": "欢快", "bpm_range": (90, 130), "energy_range": (0.4, 0.85), "fuzzy_energy_thresh": 0.1},
    {"name": "舒缓", "bpm_range": (60, 100), "energy_range": (0.2, 0.65), "fuzzy_energy_thresh": 0.1},

    # ===== 需模糊匹配的分类 =====
    {"name": "忧郁", "bpm_range": (40, 80), "energy_range": (0.05, 0.4), "fuzzy_energy_thresh": 0.05},
    {"name": "感伤", "bpm_range": (50, 90), "energy_range": (0.1, 0.3), "fuzzy_energy_thresh": 0.05},
    {"name": "紧张", "bpm_range": (130, 170), "energy_range": (0.05, 0.3), "fuzzy_energy_thresh": 0.05},

    # ===== 其他分类 =====
    {"name": "空灵", "bpm_range": (20, 60), "energy_range": (0.0, 0.25)},
    {"name": "躁动", "bpm_range": (80, 140), "energy_range": (0.7, 0.9)},
    {"name": "迷幻", "bpm_range": (60, 120), "energy_range": (0.25, 0.45)},
    {"name": "温柔", "bpm_range": (70, 110), "energy_range": (0.15, 0.35)},
    {"name": "压抑", "bpm_range": (0, 200), "energy_range": (0.0, 0.05)}
]
DEFAULT_MOOD = "其它"  # 理论上不会触发


# ====== 初始化设置 ======
os.environ["PATH"] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")


def classify_mood(bpm, energy):
    """智能混合匹配策略：精确匹配 → 模糊匹配 → BPM匹配"""
    # 极端情况处理
    if energy < 0.05:
        return "压抑"
    if bpm < 20:
        return "空灵" if energy < 0.2 else "忧郁"

    # 第一阶段：精确匹配
    for cat in MOOD_CATEGORIES:
        if (cat["bpm_range"][0] <= bpm < cat["bpm_range"][1] and
            cat["energy_range"][0] <= energy < cat["energy_range"][1]):
            return cat["name"]

    # 第二阶段：模糊匹配（仅对标记分类生效）
    for cat in MOOD_CATEGORIES:
        if "fuzzy_energy_thresh" in cat:  # 只检查需要模糊匹配的分类
            bpm_center = np.mean(cat["bpm_range"])
            energy_center = np.mean(cat["energy_range"])
            if (abs(bpm - bpm_center) < 15 and
                abs(energy - energy_center) < cat["fuzzy_energy_thresh"]):
                return cat["name"]

    # 第三阶段：按BPM匹配
    for cat in MOOD_CATEGORIES:
        if cat["bpm_range"][0] <= bpm < cat["bpm_range"][1]:
            return cat["name"]

    return DEFAULT_MOOD

def analyze_bpm_and_energy(file_path):
    """
    分析音频文件的BPM和能量值
    返回: (BPM, 能量值) 或 (None, None)表示失败
    """
    try:
        y, sr = librosa.load(file_path, sr=None)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo = float(np.around(tempo.item(), 1))
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.around(rms.mean(), 3))
        mood = classify_mood(tempo, energy)
        print(f"分析成功: {file_path} -> BPM={tempo}, Energy={energy}, Mood={mood}")
        return tempo, energy
    except Exception as e:
        print(f"分析失败: {file_path} - {str(e)}")
        return None, None

def verify_tags(file_path):
    """验证标签写入结果（支持MP3/FLAC）"""
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        bpm = mood = None

        if ext == ".mp3":
            audio = ID3(file_path)
            bpm = audio.get("TBPM").text[0] if "TBPM" in audio else None
            mood = audio.get("TCON").text[0] if "TCON" in audio else None
        elif ext == ".flac":
            audio = FLAC(file_path)
            bpm = audio.get("BPM", [None])[0]
            mood = audio.get("GENRE", [None])[0]

        print(f"验证成功: {file_path} -> BPM={bpm}, Mood={mood}")
        return True
    except Exception as e:
        print(f"验证失败: {file_path} - {str(e)}")
        return False

def write_tags(file_path, bpm, energy):
    """
    将BPM写入标准标签，情绪标签写入流派字段
    """
    try:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        mood = classify_mood(bpm, energy)

        if ext == ".mp3":
            audio = ID3(file_path)
            if "TBPM" in audio:
                del audio["TBPM"]
            audio.add(TBPM(encoding=3, text=str(bpm)))
            if "TCON" in audio:
                del audio["TCON"]
            audio.add(TCON(encoding=3, text=mood))
            audio.save(file_path, v2_version=3)
            print(f".MP3标签写入成功: {file_path} -> {mood}")
        elif ext == ".flac":
            audio = FLAC(file_path)
            audio["BPM"] = str(bpm)
            audio["GENRE"] = mood
            audio.save()
            print(f".FLAC标签写入成功: {file_path} -> {mood}")
        else:
            print(f"警告: {ext} 格式暂不支持标签写入")
            return False

        if VERIFY_WRITING:
            return verify_tags(file_path)
        return True
    except Exception as e:
        print(f"标签写入失败: {file_path} - {str(e)}")
        return False

def process_audio_files():
    """批量处理音频文件：分析BPM和能量值并写入标签"""
    try:
        files = []
        for root, dirs, filenames in os.walk(INPUT_FOLDER):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in AUDIO_EXTENSIONS:
                    files.append(os.path.join(root, filename))

        if not files:
            print("未找到支持的音频文件！")
            return

        print(f"开始处理 {len(files)} 个文件...")
        print(f"处理路径: {INPUT_FOLDER}\n")

        success_count = 0
        for idx, file_path in enumerate(files, start=1):
            print(f"[{idx}/{len(files)}] 正在处理: {os.path.basename(file_path)}")

            try:
                bpm, energy = analyze_bpm_and_energy(file_path)
                if bpm is not None and energy is not None:
                    result = write_tags(file_path, bpm, energy)
                    if result:
                        print("  ✅ 处理成功")
                        success_count += 1
                    else:
                        print("  ❌ 验证失败")
                else:
                    print("  ❌ 分析失败")
            except Exception as e:
                print(f"  ❌ 处理异常: {str(e)}")
            print()  # 空行分隔

        print(f"处理完成！成功处理 {success_count}/{len(files)} 个文件")

    except Exception as e:
        print(f"致命错误: {str(e)}")

if __name__ == "__main__":
    process_audio_files()
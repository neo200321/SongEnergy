# SongEnergy

### 中文版本 (README_zh.md)

```markdown
# AutoMoodTagger - 音乐情绪自动分类工具

[](https://python.org)
[](https://opensource.org/licenses/Apache-2.0)

AutoMoodTagger 是一款智能音频分析工具，能够根据音乐声学特征自动分类歌曲情绪，并将分类结果直接写入歌曲元数据标签。解决本地音乐无法自动分类的问题，让您轻松创建符合特定场景的情绪化歌单！

## ✨ 核心功能

- **BPM分析**：使用LibROSA精确检测每分钟节拍数
- **能量值计算**：通过RMS能量算法测量歌曲强度
- **智能情绪分类**：采用多级匹配算法分配情绪标签
- **元数据写入**：直接将结果写入MP3/FLAC文件的流派标签
- **批量处理**：一键处理整个音乐库
- **验证系统**：可选标签验证确保写入成功

## 🔍 工作原理

1. 分析音频文件提取BPM和能量值
2. 使用可配置规则将歌曲分类到情绪类别
3. 将情绪标签写入歌曲的"流派"元数据字段
4. 可选验证标签是否写入成功

```python
# 情绪分类逻辑示例
def classify_mood(bpm, energy):
    # 三级匹配策略：精确匹配 → 模糊匹配 → BPM匹配
    for cat in MOOD_CATEGORIES:
        if cat["bpm_range"][0] <= bpm < cat["bpm_range"][1]:
            return cat["name"]

📦 支持的情绪分类
​亢奋: BPM 150-200, 能量值 0.85-1.0 (派对、健身)
​激昂: BPM 120-160, 能量值 0.6-0.95 (激励时刻)
​欢快: BPM 90-130, 能量值 0.4-0.85 (休闲聆听)
​舒缓: BPM 60-100, 能量值 0.2-0.65 (冥想、学习)
​忧郁: BPM 40-80, 能量值 0.05-0.4 (沉思时刻)
... 共10+种可配置分类！

⚙️ 安装与使用
前提条件
Python 3.7+
FFmpeg (用于MP3文件解码，建议配置到系统路径)

# AutoMoodTagger - Automatic Music Mood Classification

[](https://python.org)
[](https://opensource.org/licenses/Apache-2.0)

AutoMoodTagger is an intelligent audio analysis tool that automatically classifies music files based on their acoustic properties and writes mood labels directly to the file's metadata. Perfect for creating mood-based playlists for different scenarios!

## ✨ Key Features

- **BPM Analysis**: Precisely detects Beats Per Minute (BPM) using LibROSA's beat tracking
- **Energy Calculation**: Measures RMS energy to determine song intensity
- **Smart Mood Classification**: Uses a multi-stage matching algorithm to assign accurate mood labels
- **Metadata Tagging**: Writes results directly to MP3/FLAC file metadata (ID3 tags)
- **Batch Processing**: Processes entire music libraries with one command
- **Verification System**: Optional tag verification to ensure write success

## 🔍 How It Works

1. Analyzes audio files to extract BPM and energy values
2. Classifies songs into emotional categories using configurable rules
3. Writes mood labels to the "Genre" tag in metadata
4. Verifies successful tag writing (optional)

```python
# Example mood classification logic
def classify_mood(bpm, energy):
    # Multi-stage matching: precise → fuzzy → BPM-only
    for cat in MOOD_CATEGORIES:
        if cat["bpm_range"][0] <= bpm < cat["bpm_range"][1]:
            return cat["name"]

📦 Supported Mood Categories
​Ecstatic (亢奋)​: BPM 150-200, Energy 0.85-1.0 (Parties, workouts)
​Passionate (激昂)​: BPM 120-160, Energy 0.6-0.95 (Motivational sessions)
​Cheerful (欢快)​: BPM 90-130, Energy 0.4-0.85 (Casual listening)
​Relaxing (舒缓)​: BPM 60-100, Energy 0.2-0.65 (Meditation, studying)
​Melancholic (忧郁)​: BPM 40-80, Energy 0.05-0.4 (Reflective moments)
... and 10+ more configurable categories!
⚙️ Installation & Usage
Prerequisites
Python 3.7+
FFmpeg (for MP3 decoding support)


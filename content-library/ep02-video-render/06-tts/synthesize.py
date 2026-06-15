"""
06-TTS 合成脚本：将 04 脚本口播文本合成为 WAV 音频。

支持引擎：
  - cosyvoice3  （默认）调用远程 CosyVoice 3 FastAPI 服务
  - piper       本地 Piper TTS（zh_CN-huayan-medium）

用法：
  # CosyVoice 3（需先在 GPU 机器上部署服务）
  python synthesize.py --engine cosyvoice3 --cosyvoice-url http://YOUR_GPU_SERVER:9880

  # Piper（本地，无需 GPU）
  python synthesize.py --engine piper

  # 也可通过环境变量配置
  TTS_ENGINE=cosyvoice3 COSYVOICE_URL=http://YOUR_GPU_SERVER:9880 python synthesize.py

前置：
  - cosyvoice3: 远程机器部署 CosyVoice 3 FastAPI 服务（见 README.md）
  - piper:      pip install piper-tts
"""

import argparse
import json
import os
import time
import urllib.request
import wave
from pathlib import Path

# --- 配置 ---
SCRIPT_DIR = Path(__file__).parent
MODELS_DIR = SCRIPT_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
PIPER_MODEL_PATH = MODELS_DIR / "zh_CN-huayan-medium.onnx"
PIPER_MODEL_CONFIG_PATH = MODELS_DIR / "zh_CN-huayan-medium.onnx.json"
ASSETS_DIR = SCRIPT_DIR / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

# Piper 模型 Hugging Face 下载地址
_HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium"
_PIPER_MODEL_URL = f"{_HF_BASE}/zh_CN-huayan-medium.onnx"
_PIPER_CONFIG_URL = f"{_HF_BASE}/zh_CN-huayan-medium.onnx.json"

# CosyVoice 3 默认配置
DEFAULT_COSYVOICE_URL = "http://127.0.0.1:9880"
COSYVOICE_SAMPLE_RATE = 24000  # CosyVoice 3 输出采样率


def ensure_model():
    """检查模型文件是否存在，缺失则自动从 Hugging Face 或其镜像源下载。"""
    for path, url, label in [
        (MODEL_PATH, _MODEL_URL, "模型 (.onnx)"),
        (MODEL_CONFIG_PATH, _CONFIG_URL, "配置 (.onnx.json)"),
    ]:
        if path.exists():
            continue
        
        # 准备备用下载地址 (hf-mirror.com)
        urls = [url]
        if "huggingface.co" in url:
            mirror_url = url.replace("huggingface.co", "hf-mirror.com")
            urls.append(mirror_url)

        max_retries = 3
        success = False
        
        for attempt in range(1, max_retries + 1):
            for current_url in urls:
                print(f"[下载] 正在尝试下载 {label} (尝试 {attempt}/{max_retries})...")
                print(f"  URL: {current_url}")
                print(f"  目标: {path}")
                
                try:
                    req = urllib.request.Request(
                        current_url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                    )
                    
                    with urllib.request.urlopen(req, timeout=30) as response:
                        content_length = response.headers.get('Content-Length')
                        total_size = int(content_length) if content_length else None
                        
                        bytes_downloaded = 0
                        chunk_size = 1024 * 1024  # 1MB chunks
                        
                        # 使用临时文件下载，避免网络中断导致残缺文件被识别为已下载
                        tmp_path = path.with_suffix(path.suffix + ".tmp")
                        with open(tmp_path, "wb") as f:
                            while True:
                                chunk = response.read(chunk_size)
                                if not chunk:
                                    break
                                f.write(chunk)
                                bytes_downloaded += len(chunk)
                                
                                if total_size:
                                    percent = (bytes_downloaded / total_size) * 100
                                    print(f"\r  进度: {percent:.1f}% ({bytes_downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB)", end="", flush=True)
                                else:
                                    print(f"\r  进度: {bytes_downloaded / (1024*1024):.1f}MB", end="", flush=True)
                        
                        print()  # 换行
                        
                        if total_size and bytes_downloaded < total_size:
                            raise ValueError(f"下载不完整: 仅获取到 {bytes_downloaded} 字节 (共 {total_size} 字节)")
                        
                        # 成功下载，重命名临时文件
                        if tmp_path.exists():
                            if path.exists():
                                path.unlink()
                            tmp_path.rename(path)
                        
                        size_mb = path.stat().st_size / (1024 * 1024)
                        print(f"  [成功] {label} 下载完成 ({size_mb:.1f} MB)\n")
                        success = True
                        break  # 跳出 URL 循环
                        
                except Exception as e:
                    print(f"\n  [警告] 尝试失败: {e}")
                    tmp_path = path.with_suffix(path.suffix + ".tmp")
                    if tmp_path.exists():
                        try:
                            tmp_path.unlink()
                        except Exception:
                            pass
                    time.sleep(2)  # 等待后重试
            
            if success:
                break  # 跳出重试循环
                
        if not success:
            raise RuntimeError(
                f"下载失败: 历经 {max_retries} 次尝试和镜像源后仍无法下载 {label}。\n"
                f"请手动下载:\n"
                f"  {url}\n"
                f"  或镜像: {url.replace('huggingface.co', 'hf-mirror.com')}\n"
                f"  保存到: {path}"
            )
            
# ============================================================
# 04 脚本口播文本（按段落 ID 对应）
# ============================================================
# 口播文本逐段对齐 04-script/README.md 契约块的 13 段 sections[]（id 1..13）。
# segment_id 命名为 S{NN}_{slug}，与 04 段落、07 组装 scene 一一对应；
# 文本为 04 voice 字段的逐字拷贝（由 _regen_segments.py 同步），改 04 须重跑同步再重合成。
NARRATION_SEGMENTS = {
    'S01_open': (
        '做技术教程视频，最烦的是改。传统剪辑在时间轴上一帧帧拖，换个数据要重排，改个标题要重对位，一期改三轮人就废了。我的做法不一样——把整条片子写成一份配置，让程序自动渲染出片。要改哪儿，改配置里一行字，重新跑一下，新片就出来了，不碰时间轴。可我没有前后端基础，这套不是我手写的，全程用的是 Vibe Coding：用大白话把想法讲给 AI，让它去写去改，我只管说清要什么、再判断它对不对。这期就两步——先选技术路线，再搭渲染引擎。跟着走，没基础也能复制。'
    ),
    'S02_routes_intro': (
        '第一步，选路线。我没自己啃文档，是把选择题丢给 AI。我问它：想把视频写成代码、让程序自动出片，有哪些现成路线？这些路子内核都一样——用代码描述画面、编译成帧、合成视频，区别只在用什么语言、什么引擎。'
    ),
    'S03_six_routes': (
        'AI 给我摆出六条路。网页渲染，代表 Remotion，React 组件加 CSS，无头浏览器逐帧截图，适合复杂排版。Motion Canvas，写函数描述动画时序，适合代码演示。Manim，Python 描述几何公式，数学可视化神器。MoviePy，Python 操作像素加 FFmpeg，适合简单拼接。PixiJS 这类画布引擎，Canvas 上逐帧画，做复杂粒子。FFmpeg 加脚本，命令行合成，适合批量转码、字幕烧录。六条路描述层不同，但都通向同一件事——把画面编译成帧。'
    ),
    'S04_pitfalls': (
        '光报菜名没用。AI 默认给你一份四平八稳的百科对比，每个都说好话，这帮不了你做决定。真正有用的是：每条路什么时候不好使、会在哪步翻车。所以我追问——每个方案什么情况不适用、有哪些已知坑？这才逼出有判断价值的表。Remotion 适合前端栈、复杂排版、跨期复用，但组件顶层直接读浏览器对象会在打包阶段崩，授权还是 BUSL，规模化要付费。Motion Canvas 时序强，但排版生态小。Manim 是数学可视化天花板，但学习陡、排版弱、渲染慢。MoviePy 简单拼接够用，但复杂文字动效很痛苦。PixiJS 做粒子在行，但文字对齐是灾难。FFmpeg 适合兜底合成，但命令晦涩难调。这一步最关键——人盯着坑那列做减法，AI 铺信息，判断自己来。'
    ),
    'S05_why_remotion': (
        '坑看清了，最后回到我自己的需求拍板。我把约束讲给 AI：要一期一个固定模板、换数据就批量出几十期；要让 AI 自己改内容还不容易错；要跨好多期都好维护。对着这三条，Remotion 明显胜出——组件加数据分离，改一处全系列生效；每期只让 AI 填数据套现成组件，最不容易出错；一行命令就出片；网页生态随手能用。'
    ),
    'S06_vs_html': (
        '我还让 AI 把 Remotion 跟复制粘贴 HTML 那种土办法做对照。模板复用，Remotion 改一处全系列生效，复制粘贴越改越乱；让 AI 接手，Remotion 结构稳只填数据，复制粘贴容易跑偏；长期维护，Remotion 十期后还能管，复制粘贴就是灾难。代价也如实说：React 栈、BUSL 授权、规模化商用要给钱。但前端不用怕——让 AI 写、我把方向，这正是 Vibe Coding。'
    ),
    'S07_dispatch': (
        '路线定了，第二步搭引擎。好消息是，搭引擎也不靠手写，靠跟 AI 一起把配置和组件对上。仓库里的引擎叫 remotion-composer，干活很直白：你写一份配置，说清这段是什么画面，主程序 Explainer 就按配置里的 type 字段自动找对应组件去渲。comparison 是对比卡，terminal_scene 合成终端、逐行打字不用真录屏，screenshot_scene 丢截图叠光标，还有图表、概念图、分屏。'
    ),
    'S08_config': (
        '重点来了，这是用 Vibe Coding 做视频最省心的地方——我不让 AI 发明新组件，只让它照现成组件填配置。比如要个对比卡，我说左边传统剪辑、右边代码即视频，AI 产出的就是一段配置：type 写 comparison，标题、左右两栏的标签和内容填好，完事。'
    ),
    'S09_fill_vs_build': (
        '为什么这么干最稳？看对照。左边反面——让 AI 为这期从零手写新组件，既重复造轮子，又把换数据就复用弄没了。右边正确——只产出一份数据，丢给现成组件渲。关键是 Remotion 用 TypeScript 给每个 type 的字段定死了格式，AI 填错漏填，编译立刻报错。它只能在固定格子里填空，乱发挥空间压到最小——这就是没基础也能让它干得住的原因。'
    ),
    'S10_avatar': (
        '引擎里还有个 3D 主持人 VRMAvatar，定位先说死：它只是陪衬串场，不是主角。整体渲一次，再按场景裁出半身、全身景别，不用每段重搭。之前它待机只摆髋部，整条腿带着脚像钟摆一样甩；修法是在大腿上把髋部摆动反向抵消，让脚踩原地。还有条边界——坚决不做对口型数字人、不做 AI 假界面，可信度靠真实录屏。'
    ),
    'S11_ssr': (
        '搭引擎唯一反复踩的坑是 SSR。看左边：组件最外层直接读了 window，可 Remotion 打包阶段跑在 Node 里、还没进浏览器，没有 window 这对象，直接报 ReferenceError、渲染红屏。看右边怎么修：加个 typeof window 判断，是浏览器才读，不是就给默认值。更聪明的不是每次盯 AI，是把这条规则一次写死——写进 .cursor/rules 一份 mdc 文件，指向引擎源码目录，以后 AI 生成组件自动带上，不用人盯。这就是 Vibe Coding 的要点：重复的约束用规则固化交给 AI，别每次口头提醒。'
    ),
    'S12_render': (
        '到了出片，人不用写代码、不用背命令，让 AI 在终端里跑就行。cd 进 remotion-composer，npx remotion studio 可视化调试，npx remotion render 直接出片。纯命令行，以后接自动化、上云都方便。具体的 Composition 注册名，录制前让 AI 跑一次 studio 核对就好。'
    ),
    'S13_cta': (
        '回头看就两步：用 Vibe Coding 选路线，让 AI 铺信息列坑、人对着约束拍板；再搭引擎，填配置、套组件、规则兜底、AI 跑渲染。你要会的不是写代码，是讲清需求、看住坑、把规则固化给 AI——没基础也能复制。下期 EP03，用 Whisper 让字幕踩着话音跳。关注别错过。'
    ),
}


# ============================================================
# CosyVoice 3 引擎（远程 FastAPI 服务）
# ============================================================

def _cosyvoice3_synthesize_segment(
    text: str,
    output_path: Path,
    base_url: str,
    mode: str = "sft",
    spk_id: str = "中文女",
    instruct_text: str = "",
    prompt_wav_path: str = "",
):
    """调用远程 CosyVoice 3 FastAPI 服务合成单段音频，保存为 WAV。

    支持三种模式：
      - sft:        预训练音色（需 spk_id）
      - zero_shot:  零样本克隆（需 prompt_wav_path + prompt_text）
      - instruct2:  自然语言控制（需 instruct_text + prompt_wav_path）

    CosyVoice 3 FastAPI 接口（官方 runtime/python/fastapi/server.py）：
      POST /inference_sft          Form: tts_text, spk_id
      POST /inference_zero_shot    Form: tts_text, prompt_text, prompt_wav (file)
      POST /inference_instruct2    Form: tts_text, instruct_text, prompt_wav (file)

    响应为 StreamingResponse，body 是 raw PCM int16 数据（24000 Hz mono）。
    """
    import urllib.parse
    import urllib.error

    url = f"{base_url.rstrip('/')}/inference_{mode}"

    # 构建 multipart/form-data
    boundary = "----CosyVoice3Boundary"
    body_parts = []

    def add_field(name: str, value: str):
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        )

    def add_file(name: str, filename: str, data: bytes, content_type: str = "audio/wav"):
        body_parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        )
        body_parts.append(data)
        body_parts.append(b"\r\n")

    add_field("tts_text", text)

    if mode == "sft":
        add_field("spk_id", spk_id)
    elif mode == "zero_shot":
        add_field("prompt_text", instruct_text or "")
        if prompt_wav_path and Path(prompt_wav_path).exists():
            with open(prompt_wav_path, "rb") as f:
                add_file("prompt_wav", Path(prompt_wav_path).name, f.read())
    elif mode == "instruct2":
        add_field("instruct_text", instruct_text)
        if prompt_wav_path and Path(prompt_wav_path).exists():
            with open(prompt_wav_path, "rb") as f:
                add_file("prompt_wav", Path(prompt_wav_path).name, f.read())

    body_parts.append(f"--{boundary}--\r\n")

    # Encode body
    body = b""
    for part in body_parts:
        if isinstance(part, str):
            body += part.encode("utf-8")
        else:
            body += part

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            pcm_data = resp.read()
    except urllib.error.URLError as e:
        raise ConnectionError(
            f"无法连接 CosyVoice 3 服务: {url}\n"
            f"错误: {e}\n"
            f"请确认服务已启动并可访问。"
        ) from e

    # raw PCM int16 → WAV
    with wave.open(str(output_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(COSYVOICE_SAMPLE_RATE)
        wf.writeframes(pcm_data)


def synthesize_cosyvoice3(args):
    """使用远程 CosyVoice 3 服务合成所有口播段落。"""
    base_url = args.cosyvoice_url
    mode = args.cosyvoice_mode
    spk_id = args.cosyvoice_spk
    instruct_text = args.cosyvoice_instruct
    prompt_wav = args.cosyvoice_prompt_wav

    print(f"Engine: CosyVoice 3 (remote)")
    print(f"Server: {base_url}")
    print(f"Mode: {mode} | Speaker: {spk_id}")

    # 健康检查
    try:
        urllib.request.urlopen(f"{base_url.rstrip('/')}/inference_sft", timeout=5)
    except Exception:
        pass  # GET 可能返回 405，但说明服务在线

    results = []
    total_duration = 0.0

    for seg_id, text in NARRATION_SEGMENTS.items():
        output_path = ASSETS_DIR / f"{seg_id}.wav"
        print(f"\n--- Synthesizing: {seg_id} ---")
        print(f"  Text length: {len(text)} chars")

        start_time = time.time()

        _cosyvoice3_synthesize_segment(
            text=text,
            output_path=output_path,
            base_url=base_url,
            mode=mode,
            spk_id=spk_id,
            instruct_text=instruct_text,
            prompt_wav_path=prompt_wav,
        )

        elapsed = time.time() - start_time
        file_size = output_path.stat().st_size

        with wave.open(str(output_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / rate

        total_duration += duration
        results.append({
            "segment_id": seg_id,
            "output_file": str(output_path.name),
            "text_chars": len(text),
            "duration_seconds": round(duration, 2),
            "file_size_bytes": file_size,
            "synthesis_time_seconds": round(elapsed, 2),
        })
        print(f"  Duration: {duration:.2f}s | Size: {file_size} bytes | Synth time: {elapsed:.2f}s")

    _write_manifest("cosyvoice3", f"Fun-CosyVoice3-0.5B ({mode})",
                     COSYVOICE_SAMPLE_RATE, total_duration, results)


# ============================================================
# Piper 引擎（本地）
# ============================================================

def _ensure_piper_model():
    """检查 Piper 模型文件是否存在，缺失则自动从 Hugging Face 下载。"""
    for path, url, label in [
        (PIPER_MODEL_PATH, _PIPER_MODEL_URL, "模型 (.onnx)"),
        (PIPER_MODEL_CONFIG_PATH, _PIPER_CONFIG_URL, "配置 (.onnx.json)"),
    ]:
        if path.exists():
            continue
        print(f"[下载] {label} 不存在，正在从 Hugging Face 下载...")
        print(f"  URL: {url}")
        print(f"  目标: {path}")
        try:
            urllib.request.urlretrieve(url, str(path))
            size_mb = path.stat().st_size / (1024 * 1024)
            print(f"  完成 ({size_mb:.1f} MB)")
        except Exception as e:
            if path.exists():
                path.unlink()
            raise RuntimeError(
                f"下载失败: {e}\n请手动下载:\n  {url}\n  保存到: {path}"
            ) from e


def synthesize_piper(args):
    """使用本地 Piper TTS 合成所有口播段落。"""
    _ensure_piper_model()
    from piper import PiperVoice

    print(f"Engine: Piper TTS (local)")
    print(f"Loading model: {PIPER_MODEL_PATH}")
    voice = PiperVoice.load(str(PIPER_MODEL_PATH))
    print(f"Model loaded. Sample rate: {voice.config.sample_rate} Hz")

    results = []
    total_duration = 0.0

    for seg_id, text in NARRATION_SEGMENTS.items():
        output_path = ASSETS_DIR / f"{seg_id}.wav"
        print(f"\n--- Synthesizing: {seg_id} ---")
        print(f"  Text length: {len(text)} chars")

        start_time = time.time()

        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(voice.config.sample_rate)
            voice.synthesize_wav(text, wf)

        elapsed = time.time() - start_time
        file_size = output_path.stat().st_size

        with wave.open(str(output_path), "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / rate

        total_duration += duration
        results.append({
            "segment_id": seg_id,
            "output_file": str(output_path.name),
            "text_chars": len(text),
            "duration_seconds": round(duration, 2),
            "file_size_bytes": file_size,
            "synthesis_time_seconds": round(elapsed, 2),
        })
        print(f"  Duration: {duration:.2f}s | Size: {file_size} bytes | Synth time: {elapsed:.2f}s")

    _write_manifest("piper-tts", "zh_CN-huayan-medium",
                     voice.config.sample_rate, total_duration, results)


# ============================================================
# 公共工具
# ============================================================

def _write_manifest(engine: str, model: str, sample_rate: int,
                    total_duration: float, results: list):
    manifest = {
        "engine": engine,
        "model": model,
        "sample_rate": sample_rate,
        "total_duration_seconds": round(total_duration, 2),
        "total_segments": len(results),
        "segments": results,
    }
    manifest_path = ASSETS_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"DONE! {len(results)} segments synthesized.")
    print(f"Total audio duration: {total_duration:.2f}s ({total_duration/60:.1f} min)")
    print(f"Manifest: {manifest_path}")
    print(f"Assets dir: {ASSETS_DIR}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="06-TTS: 合成口播音频（支持 CosyVoice 3 / Piper）"
    )
    parser.add_argument(
        "--engine", type=str,
        default=os.environ.get("TTS_ENGINE", "cosyvoice3"),
        choices=["cosyvoice3", "piper"],
        help="TTS 引擎（默认 cosyvoice3）。也可设置环境变量 TTS_ENGINE。",
    )
    # CosyVoice 3 参数
    parser.add_argument(
        "--cosyvoice-url", type=str,
        default=os.environ.get("COSYVOICE_URL", DEFAULT_COSYVOICE_URL),
        help=f"CosyVoice 3 服务地址（默认 {DEFAULT_COSYVOICE_URL}）。也可设置 COSYVOICE_URL。",
    )
    parser.add_argument(
        "--cosyvoice-mode", type=str,
        default=os.environ.get("COSYVOICE_MODE", "sft"),
        choices=["sft", "zero_shot", "instruct2"],
        help="CosyVoice 3 推理模式（默认 sft）。",
    )
    parser.add_argument(
        "--cosyvoice-spk", type=str,
        default=os.environ.get("COSYVOICE_SPK", "中文女"),
        help="SFT 模式的说话人 ID（默认 '中文女'）。",
    )
    parser.add_argument(
        "--cosyvoice-instruct", type=str,
        default=os.environ.get("COSYVOICE_INSTRUCT", ""),
        help="instruct2/zero_shot 模式的指令文本。",
    )
    parser.add_argument(
        "--cosyvoice-prompt-wav", type=str,
        default=os.environ.get("COSYVOICE_PROMPT_WAV", ""),
        help="zero_shot/instruct2 模式的参考音频路径。",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.engine == "cosyvoice3":
        synthesize_cosyvoice3(args)
    else:
        synthesize_piper(args)

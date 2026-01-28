"""
名人数字人音频服务
提供TTS（文本转语音）和ASR（语音识别）功能
"""
import dashscope
from dashscope.audio.asr import Recognition
from dashscope.audio.tts_v2 import SpeechSynthesizer
from backend.core.config import settings
import tempfile
import os
from http import HTTPStatus
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

# Configure API Key
dashscope.api_key = settings.DASHSCOPE_API_KEY


async def transcribe_audio(file_content: bytes, file_extension: str = "wav") -> str:
    """
    语音识别：接收任意音频，转码为 16k WAV，调用 DashScope (Paraformer-Realtime) 进行识别

    Args:
        file_content: 音频文件内容（字节）
        file_extension: 文件扩展名提示

    Returns:
        识别出的文本
    """
    logger.info(f"[Celebrity AudioService] Input size: {len(file_content)} bytes, Extension: {file_extension}")

    tmp_input_path = ""
    tmp_resampled_path = ""

    try:
        # 1. 保存原始上传文件
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_input_path = tmp_file.name

        # 2. 使用 pydub 进行重采样
        logger.info(f"[Celebrity AudioService] Converting audio to 16000Hz mono wav...")

        try:
            audio = AudioSegment.from_file(tmp_input_path)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_resampled:
                tmp_resampled_path = tmp_resampled.name
                audio.export(tmp_resampled_path, format="wav")

        except Exception as e:
            logger.error(f"[Celebrity AudioService] Audio conversion failed: {e}")
            raise Exception(f"Audio conversion failed: {str(e)}")

        # 3. 调用阿里云 ASR
        logger.info(f"[Celebrity AudioService] Calling Recognition(model='paraformer-realtime-v1')...")

        recognition = Recognition(
            model='paraformer-realtime-v1',
            format='wav',
            sample_rate=16000,
            callback=None
        )

        result = recognition.call(tmp_resampled_path)

        logger.info(f"[Celebrity AudioService] Recognition status: {result.status_code}")

        if result.status_code == HTTPStatus.OK:
            text = ""
            if result.output:
                # 解析识别结果
                if isinstance(result.output, dict):
                    if 'sentence' in result.output:
                        sent_data = result.output['sentence']
                        if isinstance(sent_data, list) and len(sent_data) > 0:
                            text = sent_data[0]['text']
                        elif isinstance(sent_data, dict):
                            text = sent_data['text']
                    elif 'text' in result.output:
                        text = result.output['text']
                    elif 'sentences' in result.output:
                        text = "".join([s['text'] for s in result.output['sentences']])
                elif isinstance(result.output, list) and len(result.output) > 0:
                    if 'text' in result.output[0]:
                        text = result.output[0]['text']

            if text:
                logger.info(f"[Celebrity AudioService] Transcription Success: {text}")
                return text
            else:
                logger.warning(f"[Celebrity AudioService] Success but text is empty. Raw: {result.output}")
                return ""
        else:
            logger.error(f"[Celebrity AudioService] Recognition Error: {result.code} - {result.message}")
            raise Exception(f"ASR Error: {result.message}")

    except Exception as e:
        logger.error(f"[Celebrity AudioService] Exception: {e}")
        import traceback
        traceback.print_exc()
        raise e

    finally:
        for p in [tmp_input_path, tmp_resampled_path]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass


def synthesize_audio_sync(text: str, voice: str = None) -> bytes:
    """
    同步版本的TTS合成（用于流式端点中调用）

    Args:
        text: 要合成的文本
        voice: 音色（默认使用配置中的音色）

    Returns:
        音频数据（bytes）
    """
    if not text or not text.strip():
        return b''

    if voice is None:
        voice = settings.CELEBRITY_TTS_VOICE

    try:
        synthesizer = SpeechSynthesizer(
            model=settings.CELEBRITY_TTS_MODEL,
            voice=voice
        )
        audio = synthesizer.call(text)
        if audio and len(audio) > 0:
            return audio
        return b''
    except Exception as e:
        logger.error(f"[Celebrity AudioService] sync TTS error: {e}")
        return b''


async def synthesize_audio(text: str, voice: str = None) -> bytes:
    """
    文本转语音：使用 DashScope CosyVoice 合成语音

    Args:
        text: 要合成的文本
        voice: 音色（默认使用配置中的音色）

    Returns:
        音频数据（bytes）
    """
    logger.info(f"[Celebrity AudioService] Calling TTS for text: {text[:50]}...")

    if voice is None:
        voice = settings.CELEBRITY_TTS_VOICE

    logger.info(f"[Celebrity AudioService] Initializing SpeechSynthesizer with model='{settings.CELEBRITY_TTS_MODEL}', voice='{voice}'")
    synthesizer = SpeechSynthesizer(
        model=settings.CELEBRITY_TTS_MODEL,
        voice=voice
    )

    logger.info(f"[Celebrity AudioService] Sending text to synthesizer.call(): '{text}'")
    try:
        audio = synthesizer.call(text)
    except Exception as e:
        logger.error(f"[Celebrity AudioService] synthesizer.call() failed: {e}")
        import traceback
        traceback.print_exc()
        raise e

    logger.info(f"[Celebrity AudioService] TTS Request: text={text[:50]}... voice={voice}")

    if audio and len(audio) > 0:
        logger.info(f"[Celebrity AudioService] TTS success. Audio size: {len(audio)}")
        try:
            logger.info('[Celebrity Metric] requestId: {}, first_package_delay: {}ms'.format(
                synthesizer.get_last_request_id(),
                synthesizer.get_first_package_delay()))
        except Exception:
            pass

        return audio
    else:
        logger.error(f"[Celebrity AudioService] TTS Error: Empty audio returned")
        raise Exception(f"TTS Error: Empty audio returned")

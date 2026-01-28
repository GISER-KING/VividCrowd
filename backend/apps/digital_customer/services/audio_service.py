import dashscope
from dashscope.audio.asr import Recognition
from dashscope.audio.tts_v2 import SpeechSynthesizer
from backend.core.config import settings
import tempfile
import os
from http import HTTPStatus
from pydub import AudioSegment

# Configure API Key
dashscope.api_key = settings.DASHSCOPE_API_KEY

async def transcribe_audio(file_content: bytes, file_extension: str = "wav") -> str:
    """
    接收任意音频，转码为 16k WAV，调用 DashScope (Paraformer-Realtime) 进行识别
    """
    print(f"[AudioService] Input size: {len(file_content)} bytes, Extension hint: {file_extension}")
    
    tmp_input_path = ""
    tmp_resampled_path = ""
    
    try:
        # 1. 保存原始上传文件
        with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as tmp_file:
             tmp_file.write(file_content)
             tmp_input_path = tmp_file.name

        # 2. 使用 pydub 进行重采样 (Resampling)
        print(f"[AudioService] Converting audio to 16000Hz mono wav...")
        
        try:
            audio = AudioSegment.from_file(tmp_input_path)
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_resampled:
                tmp_resampled_path = tmp_resampled.name
                audio.export(tmp_resampled_path, format="wav")
            
        except Exception as e:
            print(f"[AudioService] FFmpeg conversion failed. Error: {e}")
            raise Exception(f"Audio conversion failed: {str(e)}")

        # 3. 调用阿里云 ASR
        print(f"[AudioService] Calling Recognition(model='paraformer-realtime-v1')...")
        
        recognition = Recognition(
             model='paraformer-realtime-v1', 
             format='wav', 
             sample_rate=16000,
             callback=None
        )
        
        result = recognition.call(tmp_resampled_path)
        
        print(f"[AudioService] Recognition status: {result.status_code}")
        
        if result.status_code == HTTPStatus.OK:
             text = ""
             if result.output:
                 if isinstance(result.output, dict):
                     # 优先尝试获取 sentences 列表并拼接
                     if 'sentences' in result.output:
                         text = "".join([s['text'] for s in result.output['sentences'] if 'text' in s])
                     elif 'sentence' in result.output:
                         sent_data = result.output['sentence']
                         if isinstance(sent_data, list):
                             text = "".join([s['text'] for s in sent_data if 'text' in s])
                         elif isinstance(sent_data, dict):
                             text = sent_data.get('text', '')
                     elif 'text' in result.output:
                         text = result.output['text']
                 elif isinstance(result.output, list):
                     # 如果直接是列表，尝试遍历拼接
                     text = "".join([item.get('text', '') for item in result.output if isinstance(item, dict)])

             if text:
                 print(f"[AudioService] Transcription Success: {text}")
                 return text
             else:
                 print(f"[AudioService] Success but text is empty. Raw: {result.output}")
                 return ""
        else:
            print(f"[AudioService] Recognition Error: {result.code} - {result.message}")
            raise Exception(f"ASR Error: {result.message}")

    except Exception as e:
        print(f"[AudioService] Exception: {e}")
        raise e
        
    finally:
        for p in [tmp_input_path, tmp_resampled_path]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

async def synthesize_audio(text: str, voice: str = "longxiaochun") -> bytes:
    """
    Synthesize text to speech using DashScope CosyVoice.
    """
    print(f"[AudioService] Calling TTS for text: {text}...")

    synthesizer = SpeechSynthesizer(
        model='cosyvoice-v1', 
        voice=voice
    )
    
    try:
        audio = synthesizer.call(text)
    except Exception as e:
        print(f"[AudioService] synthesizer.call() failed: {e}")
        raise e

    if audio and len(audio) > 0:
        print(f"[AudioService] TTS success. Audio size: {len(audio)}")
        return audio
    else:
        print(f"[AudioService] TTS Error: Empty audio returned")
        raise Exception(f"TTS Error: Empty audio returned")
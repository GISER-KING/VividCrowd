import React, { useState, useRef, useEffect } from 'react';
import { MediaRecorder as ExtendableMediaRecorder, register } from 'extendable-media-recorder';
import { connect } from 'extendable-media-recorder-wav-encoder';
import { IconButton, CircularProgress } from '@mui/material';
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import { CONFIG } from '../../config';

const AudioInput = ({ onTextRecognized }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    const startTimeRef = useRef(0);

    // Initialize Wav Encoder
    useEffect(() => {
        const initWavEncoder = async () => {
            try {
                await register(await connect());
                console.log("Wav encoder registered");
            } catch (e) {
                if (e.message && e.message.includes("already an encoder stored")) {
                    console.log("Wav encoder already registered, skipping.");
                } else {
                    console.error("Failed to register wav encoder", e);
                }
            }
        };
        initWavEncoder();
    }, []);

    const toggleRecording = async () => {
        if (isRecording) {
            // Stop
            if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                mediaRecorderRef.current.stop();
                setIsRecording(false);
            }
        } else {
            // Start
            try {
                chunksRef.current = [];
                const stream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    }
                });

                const mimeType = 'audio/wav';
                const recorder = new ExtendableMediaRecorder(stream, { mimeType });

                recorder.ondataavailable = (e) => {
                    if (e.data.size > 0) {
                        chunksRef.current.push(e.data);
                    }
                };

                recorder.onstop = async () => {
                    const duration = Date.now() - startTimeRef.current;
                    const blob = new Blob(chunksRef.current, { type: mimeType });
                    chunksRef.current = [];
                    stream.getTracks().forEach(track => track.stop());

                    if (duration < 500) {
                        return;
                    }

                    setIsProcessing(true);
                    try {
                        const formData = new FormData();
                        formData.append('file', blob, 'recording.wav');

                        const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/audio/transcribe`, {
                            method: 'POST',
                            body: formData
                        });

                        if (response.ok) {
                            const data = await response.json();
                            if (data.text) {
                                onTextRecognized(data.text);
                            }
                        } else {
                            console.error("Transcription failed", response.statusText);
                        }
                    } catch (err) {
                        console.error("Transcription failed details:", err);
                    } finally {
                        setIsProcessing(false);
                    }
                };

                mediaRecorderRef.current = recorder;
                recorder.start();
                startTimeRef.current = Date.now();
                setIsRecording(true);
            } catch (err) {
                console.error("Error accessing microphone", err);
                alert("无法访问麦克风，请检查权限");
            }
        }
    };

    return (
        <IconButton
            onClick={toggleRecording}
            disabled={isProcessing}
            color={isRecording ? "error" : "primary"}
            sx={{
                background: isRecording ? 'rgba(244, 67, 54, 0.1)' : 'rgba(102, 126, 234, 0.1)',
                border: `1px solid ${isRecording ? '#f44336' : 'rgba(102, 126, 234, 0.3)'}`,
                '&:hover': {
                     background: isRecording ? 'rgba(244, 67, 54, 0.2)' : 'rgba(102, 126, 234, 0.2)',
                }
            }}
        >
            {isProcessing ? <CircularProgress size={24} /> : (isRecording ? <StopIcon /> : <MicIcon />)}
        </IconButton>
    );
};

export default AudioInput;
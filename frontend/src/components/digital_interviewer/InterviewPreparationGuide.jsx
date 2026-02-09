import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  Button,
  Box,
  Alert,
  Checkbox,
  FormControlLabel,
  Typography,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  CameraAlt as CameraIcon,
  Mic as MicIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

/**
 * 面试准备指南组件
 * 帮助候选人在面试前进行设备检测和准备
 */
const InterviewPreparationGuide = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [cameraPermission, setCameraPermission] = useState(false);
  const [microphonePermission, setMicrophonePermission] = useState(false);
  const [checklist, setChecklist] = useState({
    environment: false,
    network: false,
    documents: false,
    time: false
  });

  const steps = ['设备检测', '环境准备', '开始面试'];

  // 检测摄像头权限
  const checkCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach(track => track.stop());
      setCameraPermission(true);
      return true;
    } catch (error) {
      setCameraPermission(false);
      return false;
    }
  };

  // 检测麦克风权限
  const checkMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      setMicrophonePermission(true);
      return true;
    } catch (error) {
      setMicrophonePermission(false);
      return false;
    }
  };

  return (
    <Card sx={{ maxWidth: 800, margin: '0 auto' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          面试准备指南
        </Typography>

        <Box display="flex" flexDirection="column" gap={3}>
          {/* 步骤指示器 */}
          <Stepper activeStep={currentStep}>
            {steps.map((label, index) => (
              <Step key={label}>
                <StepLabel
                  StepIconComponent={() => {
                    if (index === 0) return <CameraIcon />;
                    if (index === 1) return <SecurityIcon />;
                    return <CheckCircleIcon />;
                  }}
                >
                  {label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* 第一步：设备检测 */}
          {currentStep === 0 && (
            <Box display="flex" flexDirection="column" gap={2}>
              <Typography variant="subtitle1" fontWeight="bold">
                设备检测
              </Typography>

              <Alert severity="info">
                请确保您的摄像头和麦克风正常工作
              </Alert>

              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" flexDirection="column" gap={2}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <CameraIcon />
                        <Typography>摄像头</Typography>
                      </Box>
                      <Button variant="outlined" onClick={checkCamera}>
                        {cameraPermission ? '✓ 已授权' : '检测'}
                      </Button>
                    </Box>

                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={1}>
                        <MicIcon />
                        <Typography>麦克风</Typography>
                      </Box>
                      <Button variant="outlined" onClick={checkMicrophone}>
                        {microphonePermission ? '✓ 已授权' : '检测'}
                      </Button>
                    </Box>
                  </Box>
                </CardContent>
              </Card>

              <Button
                variant="contained"
                onClick={() => setCurrentStep(1)}
                disabled={!cameraPermission || !microphonePermission}
              >
                下一步
              </Button>
            </Box>
          )}

          {/* 第二步：环境准备 */}
          {currentStep === 1 && (
            <Box display="flex" flexDirection="column" gap={2}>
              <Typography variant="subtitle1" fontWeight="bold">
                环境准备
              </Typography>

              <Alert severity="info">
                请确保您的面试环境符合以下要求
              </Alert>

              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" flexDirection="column" gap={1}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={checklist.environment}
                          onChange={(e) => setChecklist({...checklist, environment: e.target.checked})}
                        />
                      }
                      label="选择安静、光线充足的环境"
                    />

                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={checklist.network}
                          onChange={(e) => setChecklist({...checklist, network: e.target.checked})}
                        />
                      }
                      label="确保网络连接稳定"
                    />

                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={checklist.documents}
                          onChange={(e) => setChecklist({...checklist, documents: e.target.checked})}
                        />
                      }
                      label="准备好相关资料（简历、作品集等）"
                    />

                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={checklist.time}
                          onChange={(e) => setChecklist({...checklist, time: e.target.checked})}
                        />
                      }
                      label="预留充足的时间（建议30-60分钟）"
                    />
                  </Box>
                </CardContent>
              </Card>

              <Box display="flex" gap={2}>
                <Button onClick={() => setCurrentStep(0)}>
                  上一步
                </Button>
                <Button
                  variant="contained"
                  onClick={() => setCurrentStep(2)}
                  disabled={!Object.values(checklist).every(v => v)}
                >
                  下一步
                </Button>
              </Box>
            </Box>
          )}

          {/* 第三步：开始面试 */}
          {currentStep === 2 && (
            <Box display="flex" flexDirection="column" gap={2}>
              <Typography variant="subtitle1" fontWeight="bold">
                准备完成
              </Typography>

              <Alert severity="success" icon={<CheckCircleIcon />}>
                您已完成所有准备工作，可以开始面试了！
              </Alert>

              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                    面试提示：
                  </Typography>
                  <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                    <li>保持自信，放松心态</li>
                    <li>认真听题，思考后再回答</li>
                    <li>回答要有条理，突出重点</li>
                    <li>如遇技术问题，请及时联系技术支持</li>
                  </ul>
                </CardContent>
              </Card>

              <Box display="flex" gap={2}>
                <Button onClick={() => setCurrentStep(1)}>
                  上一步
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  onClick={onComplete}
                >
                  开始面试
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default InterviewPreparationGuide;

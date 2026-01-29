import React from 'react';
import { Box, Typography, Stepper, Step, StepLabel, StepConnector } from '@mui/material';
import { styled } from '@mui/material/styles';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';

const ColorlibConnector = styled(StepConnector)(({ theme }) => ({
  alternativeLabel: {
    top: 5,
  },
  active: {
    '& .MuiStepConnector-line': {
      backgroundImage: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
    },
  },
  completed: {
    '& .MuiStepConnector-line': {
      backgroundImage: 'linear-gradient(90deg, #43e97b 0%, #38f9d7 100%)',
    },
  },
  line: {
    height: 3,
    border: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 1,
  },
}));

const ColorlibStepIconRoot = styled('div')(({ ownerState }) => ({
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  zIndex: 1,
  width: 12,
  height: 12,
  borderRadius: '50%',
  ...(ownerState.active && {
    backgroundImage: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    boxShadow: '0 0 10px 0 rgba(102, 126, 234, 0.8)',
  }),
  ...(ownerState.completed && {
    backgroundImage: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
  }),
}));

function ColorlibStepIcon(props) {
  const { active, completed, className } = props;

  return (
    <ColorlibStepIconRoot ownerState={{ completed, active }} className={className} />
  );
}

const TRAINING_STAGES = [
  { id: 1, name: '信任与关系建立', description: '判断客户沟通意愿，建立基本沟通条件' },
  { id: 2, name: '信息探索与需求诊断', description: '收集客户信息，识别痛点和约束条件' },
  { id: 3, name: '价值呈现与方案链接', description: '介绍方案，建立需求与方案的对应关系' },
  { id: 4, name: '异议/顾虑处理', description: '识别并回应客户异议，澄清顾虑' },
  { id: 5, name: '收尾与成交', description: '总结要点，推进下一步行动' },
];

function StageIndicator({ currentStage, completedStages = [] }) {
  return (
    <Box
      sx={{
        p: 1.5,
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <Stepper
        alternativeLabel
        activeStep={currentStage - 1}
        connector={<ColorlibConnector />}
      >
        {TRAINING_STAGES.map((stage) => (
          <Step key={stage.id} completed={completedStages.includes(stage.id)}>
            <StepLabel
              StepIconComponent={ColorlibStepIcon}
              sx={{
                '& .MuiStepLabel-label': {
                  color: 'rgba(255, 255, 255, 0.5)',
                  fontWeight: 500,
                  mt: 0.5,
                },
                '& .MuiStepLabel-label.Mui-active': {
                  color: '#fff',
                  fontWeight: 700,
                },
                '& .MuiStepLabel-label.Mui-completed': {
                  color: '#43e97b',
                  fontWeight: 600,
                },
              }}
            >
              <Box>
                <Typography
                  sx={{
                    fontSize: '0.875rem',
                    fontWeight: currentStage === stage.id ? 700 : 500,
                    color:
                      currentStage === stage.id
                        ? '#fff'
                        : completedStages.includes(stage.id)
                        ? '#43e97b'
                        : 'rgba(255, 255, 255, 0.5)',
                  }}
                >
                  {stage.name}
                </Typography>
              </Box>
            </StepLabel>
          </Step>
        ))}
      </Stepper>
    </Box>
  );
}

export default StageIndicator;

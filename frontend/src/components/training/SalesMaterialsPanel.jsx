import React, { useRef } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider, Chip, IconButton, Tooltip } from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import TableChartIcon from '@mui/icons-material/TableChart';
import HelpIcon from '@mui/icons-material/Help';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import ArticleIcon from '@mui/icons-material/Article';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { CONFIG } from '../../config';

const MATERIALS_DATA = {
  1: [ // 信任与关系建立
    { id: 'm1_1', type: 'sop', title: '电话邀约 SOP', desc: '标准化的电话邀约流程与关键节点' },
    { id: 'm1_2', type: 'script', title: '破冰与开场白话术', desc: '针对不同客户类型的开场技巧' },
  ],
  2: [ // 信息探索与需求诊断
    { id: 'm2_1', type: 'qa', title: '客户常见痛点知识库', desc: '行业常见问题与痛点分析' },
    { id: 'm2_2', type: 'script', title: 'SPIN 提问话术', desc: '背景、难点、暗示、需求-效益提问法' },
  ],
  3: [ // 价值呈现与方案链接
    { id: 'm3_1', type: 'table', title: '检测项目价格表', desc: '各套餐详细项目与价格明细' },
    { id: 'm3_2', type: 'article', title: '产品优势与案例', desc: '核心卖点与成功案例分享' },
  ],
  4: [ // 异议/顾虑处理
    { id: 'm4_1', type: 'qa', title: '常见异议应答库', desc: '价格、效果、售后等常见异议处理' },
    { id: 'm4_2', type: 'table', title: '竞品对比分析表', desc: '我方与主要竞品的优劣势对比' },
  ],
  5: [ // 收尾与成交
    { id: 'm5_1', type: 'script', title: '成交促单话术', desc: '假设成交法、选择成交法等技巧' },
    { id: 'm5_2', type: 'sop', title: '签约与付款流程', desc: '合同签署注意事项与付款指引' },
  ]
};

const getIconByType = (type) => {
  switch (type) {
    case 'table': return <TableChartIcon sx={{ color: '#43e97b' }} />;
    case 'qa': return <HelpIcon sx={{ color: '#ffa726' }} />;
    case 'script': return <PhoneInTalkIcon sx={{ color: '#667eea' }} />;
    case 'sop': return <FormatListBulletedIcon sx={{ color: '#38f9d7' }} />;
    default: return <DescriptionIcon sx={{ color: '#fff' }} />;
  }
};

const getTypeLabel = (type) => {
    switch (type) {
        case 'table': return '表格';
        case 'qa': return '知识库';
        case 'script': return '话术';
        case 'sop': return 'SOP';
        default: return '文档';
    }
}

function SalesMaterialsPanel({ currentStage }) {
  const materials = MATERIALS_DATA[currentStage] || [];
  const fileInputRef = useRef(null);

  const handleUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/digital-customer/knowledge/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        alert(`知识库上传成功！\n解析了 ${data.count} 条知识点。`);
      } else {
        const errorData = await response.json();
        alert(`上传失败: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('上传出错，请检查网络或联系管理员。');
    } finally {
      // Clear input
      event.target.value = null;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".xlsx,.pdf"
        onChange={handleFileChange}
      />
      <Paper
        sx={{
          p: 2,
          background: 'rgba(255, 255, 255, 0.03)',
          backdropFilter: 'blur(20px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 1 }}>
            <ArticleIcon sx={{ color: '#667eea' }} />
            销售物料支持
          </Typography>
          <Tooltip title="上传知识库文件 (xlsx/pdf)">
            <IconButton 
              size="small" 
              onClick={handleUploadClick}
              sx={{ color: 'rgba(255,255,255,0.7)', '&:hover': { color: '#fff', background: 'rgba(255,255,255,0.1)' } }}
            >
              <CloudUploadIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto' }}>
            {materials.length > 0 ? (
                <List>
                    {materials.map((item, index) => (
                        <React.Fragment key={item.id}>
                            {index > 0 && <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.05)', my: 1 }} />}
                            <ListItem
                                disablePadding
                                sx={{
                                    flexDirection: 'column',
                                    alignItems: 'flex-start',
                                    p: 1.5,
                                    borderRadius: '12px',
                                    transition: 'all 0.2s',
                                    cursor: 'pointer',
                                    '&:hover': {
                                        background: 'rgba(255, 255, 255, 0.05)',
                                    }
                                }}
                            >
                                <Box sx={{ display: 'flex', width: '100%', alignItems: 'center', mb: 0.5 }}>
                                    <ListItemIcon sx={{ minWidth: 36 }}>
                                        {getIconByType(item.type)}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.title}
                                        primaryTypographyProps={{
                                            sx: { color: '#fff', fontWeight: 600, fontSize: '0.95rem' }
                                        }}
                                    />
                                    <Chip 
                                        label={getTypeLabel(item.type)} 
                                        size="small" 
                                        sx={{ 
                                            height: 20, 
                                            fontSize: '0.7rem', 
                                            background: 'rgba(255,255,255,0.1)',
                                            color: 'rgba(255,255,255,0.7)',
                                            ml: 1
                                        }} 
                                    />
                                </Box>
                                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', ml: 4.5, fontSize: '0.8rem' }}>
                                    {item.desc}
                                </Typography>
                            </ListItem>
                        </React.Fragment>
                    ))}
                </List>
            ) : (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', opacity: 0.5 }}>
                    <Typography variant="body2">暂无推荐物料</Typography>
                </Box>
            )}
        </Box>
      </Paper>
    </Box>
  );
}

export default SalesMaterialsPanel;
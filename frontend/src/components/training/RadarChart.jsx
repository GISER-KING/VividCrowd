import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Box, Paper, Typography } from '@mui/material';

function RadarChart({ scores, title = '销售能力雷达图' }) {
  const option = {
    title: {
      text: title,
      left: 'center',
      top: 10,
      textStyle: {
        color: '#fff',
        fontSize: 18,
        fontWeight: 700,
      },
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: '#667eea',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
      },
      formatter: function (params) {
        const indicators = [
          '信任与关系建立',
          '信息探索与需求诊断',
          '价值呈现与方案链接',
          '异议/顾虑处理',
          '进程推进与节奏管理',
        ];
        let result = `<div style="padding: 8px;">`;
        result += `<div style="font-weight: bold; margin-bottom: 8px;">${params.name}</div>`;
        params.value.forEach((val, idx) => {
          result += `<div style="margin: 4px 0;">
            <span style="color: #667eea;">●</span>
            ${indicators[idx]}: <span style="font-weight: bold; color: #43e97b;">${val}/5</span>
          </div>`;
        });
        result += `</div>`;
        return result;
      },
    },
    radar: {
      indicator: [
        { name: '信任与\n关系建立', max: 5 },
        { name: '信息探索与\n需求诊断', max: 5 },
        { name: '价值呈现与\n方案链接', max: 5 },
        { name: '异议/顾虑\n处理', max: 5 },
        { name: '进程推进与\n节奏管理', max: 5 },
      ],
      shape: 'polygon',
      splitNumber: 5,
      center: ['50%', '55%'],
      radius: '65%',
      axisName: {
        color: '#fff',
        fontSize: 12,
        fontWeight: 600,
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderRadius: 8,
        padding: [8, 12],
      },
      splitLine: {
        lineStyle: {
          color: ['rgba(102, 126, 234, 0.3)', 'rgba(102, 126, 234, 0.2)', 'rgba(102, 126, 234, 0.15)', 'rgba(102, 126, 234, 0.1)', 'rgba(102, 126, 234, 0.05)'],
          width: 2,
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(102, 126, 234, 0.05)', 'rgba(102, 126, 234, 0.03)'],
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(102, 126, 234, 0.4)',
          width: 2,
        },
      },
    },
    series: [
      {
        name: '能力评分',
        type: 'radar',
        symbol: 'circle',
        symbolSize: 8,
        data: [
          {
            value: [
              scores?.trust_building_score || 0,
              scores?.needs_diagnosis_score || 0,
              scores?.value_presentation_score || 0,
              scores?.objection_handling_score || 0,
              scores?.progress_management_score || 0,
            ],
            name: '本次培训',
            areaStyle: {
              color: {
                type: 'radial',
                x: 0.5,
                y: 0.5,
                r: 0.5,
                colorStops: [
                  { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
                  { offset: 1, color: 'rgba(118, 75, 162, 0.2)' },
                ],
              },
            },
            lineStyle: {
              color: '#667eea',
              width: 3,
              shadowColor: 'rgba(102, 126, 234, 0.5)',
              shadowBlur: 10,
            },
            itemStyle: {
              color: '#667eea',
              borderColor: '#fff',
              borderWidth: 2,
              shadowColor: 'rgba(102, 126, 234, 0.8)',
              shadowBlur: 10,
            },
            label: {
              show: true,
              formatter: function (params) {
                return params.value;
              },
              color: '#43e97b',
              fontSize: 14,
              fontWeight: 700,
              distance: 10,
            },
          },
        ],
      },
    ],
  };

  return (
    <Paper
      sx={{
        p: 3,
        background: 'rgba(255, 255, 255, 0.03)',
        backdropFilter: 'blur(20px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
      }}
    >
      <ReactECharts
        option={option}
        style={{ height: '450px', width: '100%' }}
        opts={{ renderer: 'canvas' }}
      />

      {/* 评分说明 */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 3, flexWrap: 'wrap' }}>
        {[
          { score: 5, label: '优秀', color: '#43e97b' },
          { score: 4, label: '良好', color: '#38f9d7' },
          { score: 3, label: '一般', color: '#ffa726' },
          { score: 2, label: '需改进', color: '#ff7043' },
          { score: 1, label: '较差', color: '#f44336' },
        ].map((item) => (
          <Box key={item.score} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                background: item.color,
              }}
            />
            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              {item.score}分 - {item.label}
            </Typography>
          </Box>
        ))}
      </Box>
    </Paper>
  );
}

export default RadarChart;

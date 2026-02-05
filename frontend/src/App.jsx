import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';
import Sidebar from './components/Sidebar';
import GroupChatPage from './pages/GroupChatPage';
import CelebrityPage from './pages/CelebrityPage';
import CustomerServicePage from './pages/CustomerServicePage';
import DigitalCustomerPage from './pages/DigitalCustomerPage';
import EvaluationReportPage from './pages/Training/EvaluationReportPage';
import DigitalInterviewerPage from './pages/DigitalInterviewerPage';
import InterviewReportPage from './pages/InterviewReportPage';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Box sx={{ display: 'flex', height: '100%', overflow: 'hidden' }}>
        <Sidebar />
        <Box sx={{ flex: 1, height: '100%', overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<GroupChatPage />} />
            <Route path="/celebrity" element={<CelebrityPage />} />
            <Route path="/customer-service" element={<CustomerServicePage />} />
            <Route path="/digital-customer" element={<DigitalCustomerPage />} />
            <Route path="/training/evaluation" element={<EvaluationReportPage />} />
            <Route path="/digital-interviewer" element={<DigitalInterviewerPage />} />
            <Route path="/interview/report/:sessionId" element={<InterviewReportPage />} />
          </Routes>
        </Box>
      </Box>
    </ErrorBoundary>
  );
}

export default App;

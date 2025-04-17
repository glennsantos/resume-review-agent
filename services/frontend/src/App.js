import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ResumeUpload from './pages/ResumeUpload';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<ResumeUpload />} />
      </Routes>
    </div>
  );
}

export default App;

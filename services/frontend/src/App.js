import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ResumeUpload from './pages/ResumeUpload';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>CV&lt;&gt;JD</h1>
        <p className="subtitle">Compare CVs against Job Descriptions</p>
      </header>
      <Routes>
        <Route path="/" element={<ResumeUpload />} />
      </Routes>
    </div>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import { uploadResume, saveJobDescription, getJobDescriptions } from '../api/api';
import LoadingSpinner from '../components/LoadingSpinner';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [jdContent, setJdContent] = useState('');
  const [jdTitle, setJdTitle] = useState('');
  const [jdLoading, setJdLoading] = useState(false);
  const [jdResult, setJdResult] = useState(null);
  const [jdError, setJdError] = useState('');
  const [jdList, setJdList] = useState([]);
  const [selectedJdId, setSelectedJdId] = useState('');

  useEffect(() => {
    getJobDescriptions()
      .then(res => setJdList(res.data))
      .catch(err => console.error('Failed to fetch JDs', err));
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedJdId) {
      setError('Please select a job description.');
      return;
    }
    if (!file) {
      setError('Please select a resume file.');
      return;
    }
    setLoading(true);
    try {
      const response = await uploadResume(file, selectedJdId);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleJDChange = (e) => {
    setJdContent(e.target.value);
    setJdError('');
    setJdResult(null);
  };

  const handleJDTitleChange = (e) => {
    setJdTitle(e.target.value);
    setJdError('');
    setJdResult(null);
  };

  const handleJDSubmit = async (e) => {
    e.preventDefault();
    if (!jdTitle.trim()) {
      setJdError('Please enter a title.');
      return;
    }
    if (!jdContent.trim()) {
      setJdError('Please enter a job description.');
      return;
    }
    setJdLoading(true);
    try {
      const response = await saveJobDescription(jdTitle, jdContent);
      setJdResult(response.data);
    } catch (err) {
      setJdError(err.response?.data?.detail || 'Failed to save JD.');
    } finally {
      setJdLoading(false);
    }
  };

  return (
    <div className="resume-upload">
      <h2>Upload Resume</h2>
      <form onSubmit={handleSubmit}>
        <select
          value={selectedJdId}
          onChange={(e) => setSelectedJdId(e.target.value)}
        >
          <option value="">Select JD</option>
          {jdList.map((jd) => (
            <option key={jd.id} value={jd.id}>
              {jd.title}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Submit'}
        </button>
      </form>

      {loading && <LoadingSpinner />}
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <h3>Score Result</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}

      <div className="job-description">
        <h2>Submit Job Description</h2>
        <form onSubmit={handleJDSubmit}>
          <input
            type="text"
            placeholder="Title"
            value={jdTitle}
            onChange={handleJDTitleChange}
          />
          <textarea
            value={jdContent}
            onChange={handleJDChange}
            placeholder="Paste job description here..."
            rows={5}
          />
          <button type="submit" disabled={jdLoading}>
            {jdLoading ? 'Saving...' : 'Save JD'}
          </button>
        </form>
        {jdError && <div className="error">{jdError}</div>}
        {jdResult && (
          <div className="jd-result">
            <p>Saved JD id: {jdResult.id}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload;

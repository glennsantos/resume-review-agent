import React, { useState, useEffect } from 'react';
import { compareResume, saveJobDescription, getJobDescriptions, getJobDescription, updateJobDescription } from '../api/api';
import LoadingSpinner from '../components/LoadingSpinner';

const ResumeUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [compareResult, setCompareResult] = useState(null);
  const [jdContent, setJdContent] = useState('');
  const [jdTitle, setJdTitle] = useState('');
  const [jdLoading, setJdLoading] = useState(false);
  const [jdResult, setJdResult] = useState(null);
  const [jdError, setJdError] = useState('');
  const [jdList, setJdList] = useState([]);
  const [selectedJdId, setSelectedJdId] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    getJobDescriptions()
      .then(res => setJdList(res.data))
      .catch(err => console.error('Failed to fetch JDs', err));
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setCompareResult(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedJdId) {
      setError('Please select a job description.');
      return;
    }
    if (!file) {
      setError('Please select a CV file.');
      return;
    }
    setLoading(true);
    try {
      const response = await compareResume(file, selectedJdId);
      setCompareResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed.');
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
      let response;
      if (isEditing && editingId) {
        response = await updateJobDescription(editingId, jdTitle, jdContent);
        setJdResult({ ...response.data, message: 'Job description updated successfully!' });
      } else {
        response = await saveJobDescription(jdTitle, jdContent);
        setJdResult({ ...response.data, message: 'Job description saved successfully!' });
      }
      
      // Refresh JD list and auto-select new/updated JD
      const newJd = response.data;
      try {
        const listRes = await getJobDescriptions();
        setJdList(listRes.data);
        setSelectedJdId(newJd.id);
      } catch (err) {
        console.error('Failed to refresh JD list', err);
      }
      
      // Clear form and reset editing state
      setJdTitle('');
      setJdContent('');
      setIsEditing(false);
      setEditingId(null);
    } catch (err) {
      setJdError(err.response?.data?.detail || 'Failed to save JD.');
    } finally {
      setJdLoading(false);
    }
  };

  const handleEditJD = async (id) => {
    try {
      setJdLoading(true);
      const response = await getJobDescription(id);
      const jd = response.data;
      setJdTitle(jd.title);
      setJdContent(jd.content);
      setIsEditing(true);
      setEditingId(id);
      setJdError('');
      setJdResult(null);
    } catch (err) {
      setJdError(err.response?.data?.detail || 'Failed to load job description for editing.');
    } finally {
      setJdLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setJdTitle('');
    setJdContent('');
    setIsEditing(false);
    setEditingId(null);
    setJdError('');
    setJdResult(null);
  };

  return (
    <div className="cv-upload">
      <h2>Upload CV</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="jd-select">Select Job Description:</label>
          <select
            id="jd-select"
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
          {selectedJdId && (
            <button 
              type="button" 
              className="edit-button"
              onClick={() => handleEditJD(selectedJdId)}
            >
              Edit
            </button>
          )}
        </div>
        <div className="form-group">
          <label htmlFor="cv-file">Upload CV:</label>
          <input
            id="cv-file"
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileChange}
          />
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Comparing...' : 'Compare'}
        </button>
      </form>

      {loading && <LoadingSpinner />}
      {error && <div className="error">{error}</div>}
      {compareResult && (
        <div className="result">
          <h3>CV-JD Comparison Result</h3>
          {compareResult.criteria?.map((c) => (
            <div key={c.name}>
              <strong>{c.name}:</strong> <span>{c.score_description}</span>
            </div>
          ))}
          <h4>Summary</h4>
          <p>{compareResult.summary}</p>
        </div>
      )}

      <div className="job-description">
        <h2>{isEditing ? 'Edit Job Description' : 'Add New Job Description'}</h2>
        <form onSubmit={handleJDSubmit}>
          <div className="form-group">
            <label htmlFor="jd-title">Title:</label>
            <input
              id="jd-title"
              type="text"
              placeholder="Title"
              value={jdTitle}
              onChange={handleJDTitleChange}
            />
          </div>
          <div className="form-group">
            <label htmlFor="jd-content">Content:</label>
            <textarea
              id="jd-content"
              value={jdContent}
              onChange={handleJDChange}
              placeholder="Paste job description here..."
              rows={10}
            />
          </div>
          <div className="button-group">
            <button type="submit" disabled={jdLoading}>
              {jdLoading ? 'Saving...' : isEditing ? 'Update JD' : 'Save JD'}
            </button>
            {isEditing && (
              <button type="button" onClick={handleCancelEdit}>
                Cancel
              </button>
            )}
          </div>
        </form>
        {jdError && <div className="error">{jdError}</div>}
        {jdResult && (
          <div className="jd-result success">
            <p>{jdResult.message || `Saved JD id: ${jdResult.id}`}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeUpload;

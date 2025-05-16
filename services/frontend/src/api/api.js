import axios from 'axios';

// Get the current hostname and port
const { hostname, protocol } = window.location;
const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';

// If we're running locally, use the environment variable or default to localhost:8000
// Otherwise, use the current hostname with port 8000 for the API
const API_URL = isLocalhost 
  ? (process.env.REACT_APP_API_URL || 'http://localhost:8000')
  : `${protocol}//${hostname}:8000`;

console.log('Using API URL:', API_URL);

export const uploadResume = (file, jdId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('jd_id', jdId);
  return axios.post(`${API_URL}/resumes/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const compareResume = (file, jdId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('jd_id', jdId);
  return axios.post(`${API_URL}/resumes/compare`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const saveJobDescription = (title, content) => {
  return axios.post(`${API_URL}/job_descriptions`, { title, content });
};

export const getJobDescriptions = () => {
  return axios.get(`${API_URL}/job_descriptions`);
};

export const getJobDescription = (id) => {
  return axios.get(`${API_URL}/job_descriptions/${id}`);
};

export const updateJobDescription = (id, title, content) => {
  return axios.put(`${API_URL}/job_descriptions/${id}`, { title, content });
};

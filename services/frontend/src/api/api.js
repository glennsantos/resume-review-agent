import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

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

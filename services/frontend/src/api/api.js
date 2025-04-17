import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${API_URL}/resumes/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

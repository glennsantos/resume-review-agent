import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ResumeUpload from '../src/pages/ResumeUpload';
import { uploadResume } from '../src/api/api';

jest.mock('../src/api/api');

describe('ResumeUpload', () => {
  beforeEach(() => {
    uploadResume.mockReset();
  });

  it('renders form elements', () => {
    render(<ResumeUpload />);
    expect(screen.getByText(/Upload Resume/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit/i })).toBeEnabled();
    const fileInput = document.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
  });

  it('shows error when submitting without file', async () => {
    render(<ResumeUpload />);
    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));
    expect(await screen.findByText(/Please select a resume file./i)).toBeInTheDocument();
  });

  it('uploads file and displays result', async () => {
    const mockResponse = { data: { score: 85 } };
    uploadResume.mockResolvedValue(mockResponse);

    render(<ResumeUpload />);
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });
    const input = document.querySelector('input[type="file"]');
    fireEvent.change(input, { target: { files: [file] } });

    fireEvent.click(screen.getByRole('button', { name: /Submit/i }));

    expect(uploadResume).toHaveBeenCalledWith(file);
    expect(await screen.findByText(/Score Result/i)).toBeInTheDocument();
    expect(screen.getByText(/"score": 85/)).toBeInTheDocument();
  });
});

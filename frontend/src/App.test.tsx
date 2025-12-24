import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as any;

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the header', () => {
      render(<App />);
      expect(screen.getByText(/GraphML Visualizer/i)).toBeInTheDocument();
    });

    it('should render upload section', () => {
      render(<App />);
      expect(screen.getByText(/Upload GraphML File/i)).toBeInTheDocument();
      expect(screen.getByText(/Choose File/i)).toBeInTheDocument();
    });

    it('should render empty state when no graph is loaded', () => {
      render(<App />);
      expect(screen.getByText(/No Graph Loaded/i)).toBeInTheDocument();
    });
  });

  describe('File Upload', () => {
    it('should handle successful file upload', async () => {
      const mockGraphData = {
        nodes: [
          { id: 'n1', label: 'Service A', type: 'service', env: 'prod', tags: [], x: null, y: null },
          { id: 'n2', label: 'Database', type: 'db', env: 'prod', tags: [], x: null, y: null },
        ],
        edges: [
          {
            id: 'e1',
            source: 'n1',
            target: 'n2',
            label: 'Query',
            kind: 'sync',
            criticality: 'high',
            protocol: undefined,
            weight: 1.0,
            env: 'prod',
            tags: [],
          },
        ],
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockGraphData });

      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByText(/Loaded: test.graphml/i)).toBeInTheDocument();
      });
    });

    it('should display error message on upload failure', async () => {
      const errorMessage = 'Invalid GraphML file';
      mockedAxios.post.mockRejectedValueOnce({
        response: { data: { detail: errorMessage } },
      });

      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>invalid</graphml>'], 'invalid.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByText(new RegExp(errorMessage))).toBeInTheDocument();
      });
    });

    it('should show loading state during upload', async () => {
      mockedAxios.post.mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({ data: { nodes: [], edges: [] } }), 100))
      );

      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      expect(screen.getByText(/Loading/i)).toBeInTheDocument();
    });
  });

  describe('Filters', () => {
    beforeEach(() => {
      const mockGraphData = {
        nodes: [
          { id: 'n1', label: 'Service A', type: 'service', env: 'prod', tags: [], x: null, y: null },
          { id: 'n2', label: 'Service B', type: 'service', env: 'dev', tags: [], x: null, y: null },
          { id: 'n3', label: 'Database', type: 'db', env: 'prod', tags: [], x: null, y: null },
        ],
        edges: [
          {
            id: 'e1',
            source: 'n1',
            target: 'n3',
            label: 'Query',
            kind: 'sync',
            criticality: 'high',
            protocol: undefined,
            weight: 1.0,
            env: 'prod',
            tags: [],
          },
        ],
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockGraphData });
    });

    it('should display filter section after graph loads', async () => {
      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByLabelText(/Environment/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Node Type/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Edge Criticality/i)).toBeInTheDocument();
      });
    });

    it('should filter by environment', async () => {
      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByLabelText(/Environment/i)).toBeInTheDocument();
      });

      const envFilter = screen.getByLabelText(/Environment/i) as HTMLSelectElement;
      await userEvent.selectOptions(envFilter, 'prod');

      // After filtering, should still show nodes with env='prod'
      expect(screen.getByText(/Service A|Database/)).toBeInTheDocument();
    });

    it('should filter by node type', async () => {
      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByLabelText(/Node Type/i)).toBeInTheDocument();
      });

      const typeFilter = screen.getByLabelText(/Node Type/i) as HTMLSelectElement;
      await userEvent.selectOptions(typeFilter, 'service');

      // After filtering, should show nodes with type='service'
      expect(screen.getByText(/Service A|Service B/)).toBeInTheDocument();
    });

    it('should filter by criticality', async () => {
      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByLabelText(/Edge Criticality/i)).toBeInTheDocument();
      });

      const criticalityFilter = screen.getByLabelText(/Edge Criticality/i) as HTMLSelectElement;
      await userEvent.selectOptions(criticalityFilter, 'high');

      // Filter applied
      expect(criticalityFilter.value).toBe('high');
    });
  });

  describe('Tag Search', () => {
    beforeEach(() => {
      const mockGraphData = {
        nodes: [
          { id: 'n1', label: 'Service A', type: 'service', env: 'prod', tags: ['critical', 'api'], x: null, y: null },
          { id: 'n2', label: 'Service B', type: 'service', env: 'dev', tags: ['debug'], x: null, y: null },
        ],
        edges: [],
      };

      mockedAxios.post.mockResolvedValueOnce({ data: mockGraphData });
    });

    it('should filter nodes by tags', async () => {
      render(<App />);

      const fileInput = screen.getByLabelText(/Choose File/i) as HTMLInputElement;
      const file = new File(['<graphml>test</graphml>'], 'test.graphml', { type: 'text/xml' });

      await userEvent.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Search by tag/i)).toBeInTheDocument();
      });

      const tagInput = screen.getByPlaceholderText(/Search by tag/i) as HTMLInputElement;
      await userEvent.type(tagInput, 'critical');

      // Tag filter applied
      expect(tagInput.value).toBe('critical');
    });
  });
});

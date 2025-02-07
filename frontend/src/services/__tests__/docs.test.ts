import { describe, it, expect, beforeAll } from 'vitest';
import { listDocuments, getDocumentContent } from '../docs';
import { checkApiHealth } from '../../utils/test-utils';

describe('Documentation Service Integration Tests', () => {
  beforeAll(async () => {
    // Check if API is available
    const isHealthy = await checkApiHealth();
    if (!isHealthy) {
      throw new Error('API is not available. Please start the backend server.');
    }
  });

  it('should list available documents', async () => {
    const documents = await listDocuments();
    expect(Array.isArray(documents)).toBe(true);
    if (documents.length > 0) {
      const doc = documents[0];
      expect(doc.path).toBeDefined();
      expect(doc.title).toBeDefined();
      expect(doc.category).toBeDefined();
      expect(Array.isArray(doc.tags)).toBe(true);
    }
  });

  it('should get document content', async () => {
    // First get the list of documents
    const documents = await listDocuments();
    if (documents.length === 0) {
      console.warn('No documents available for testing');
      return;
    }

    // Get content of the first document
    const doc = documents[0];
    const content = await getDocumentContent(doc.path);
    expect(content.metadata).toBeDefined();
    expect(content.content).toBeDefined();
    expect(content.html_content).toBeDefined();
    expect(content.metadata.title).toBe(doc.title);
  });

  it('should handle non-existent documents', async () => {
    await expect(
      getDocumentContent('non-existent-doc.md')
    ).rejects.toThrow('Document not found');
  });

  it('should handle malformed document paths', async () => {
    await expect(
      getDocumentContent('../../../etc/passwd')
    ).rejects.toThrow();
  });

  it('should validate document metadata', async () => {
    const documents = await listDocuments();
    if (documents.length === 0) return;

    const doc = documents[0];
    expect(doc).toMatchObject({
      path: expect.any(String),
      title: expect.any(String),
      category: expect.any(String),
      tags: expect.any(Array),
      last_updated: expect.any(String),
    });
  });
}); 
import { UrlReaderService } from '@backstage/backend-plugin-api';
import { readImageTags } from './readImageTags';

const BASE = 'https://github.com/o/gitops/blob/main';

function mockReader(files: Record<string, string>): UrlReaderService {
  return {
    readUrl: jest.fn(async (url: string) => {
      if (!(url in files)) throw new Error('NotFoundError');
      return { buffer: async () => Buffer.from(files[url]) } as any;
    }),
    readTree: jest.fn(),
    search: jest.fn(),
  };
}

describe('readImageTags', () => {
  it('reads image.tag for every service', async () => {
    const reader = mockReader({
      [`${BASE}/envs/dev/users-svc/values.yaml`]:
        'image:\n  tag: abc123\nreplicaCount: 1\n',
      [`${BASE}/envs/dev/orders-svc/values.yaml`]:
        'image:\n  # c\n  tag: def456\n',
    });
    await expect(
      readImageTags(reader, `${BASE}/`, ['users-svc', 'orders-svc'], 'dev'),
    ).resolves.toEqual({ 'users-svc': 'abc123', 'orders-svc': 'def456' });
  });

  it('accepts entity refs', async () => {
    const reader = mockReader({
      [`${BASE}/envs/dev/users-svc/values.yaml`]: 'image:\n  tag: abc\n',
    });
    await expect(
      readImageTags(reader, BASE, ['component:default/users-svc'], 'dev'),
    ).resolves.toEqual({ 'users-svc': 'abc' });
  });

  it('fails clearly when the service is not in the env', async () => {
    await expect(
      readImageTags(mockReader({}), BASE, ['nope-svc'], 'dev'),
    ).rejects.toThrow('nope-svc is not deployed in dev');
  });

  it('fails when image.tag is missing', async () => {
    const reader = mockReader({
      [`${BASE}/envs/dev/x-svc/values.yaml`]: 'replicaCount: 1\n',
    });
    await expect(readImageTags(reader, BASE, ['x-svc'], 'dev')).rejects.toThrow(
      'has no image.tag',
    );
  });

  it('rejects names that could change the path', async () => {
    await expect(
      readImageTags(mockReader({}), BASE, ['../secrets'], 'dev'),
    ).rejects.toThrow('Invalid service name');
    await expect(
      readImageTags(mockReader({}), BASE, ['a'], 'dev/..'),
    ).rejects.toThrow('Invalid environment name');
  });
});

import { UrlReaderService } from '@backstage/backend-plugin-api';
import { createTemplateAction } from '@backstage/plugin-scaffolder-node';
import { parse } from 'yaml';

// Names end up in a URL path, so only allow plain k8s-style names.
const NAME = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/;
// A plain name, or a Component entity ref from EntityPicker: component:<namespace>/<name>.
const REF = /^(?:component:[a-z0-9-]+\/)?([a-z0-9]([a-z0-9-]*[a-z0-9])?)$/;

/**
 * Reads `image.tag` from `<baseUrl>/envs/<fromEnv>/<svc>/values.yaml` for each service.
 * Read-only: it never writes to GitHub, the cluster or Terraform.
 */
export async function readImageTags(
  reader: UrlReaderService,
  baseUrl: string,
  services: string[],
  fromEnv: string,
): Promise<Record<string, string>> {
  if (!NAME.test(fromEnv)) {
    throw new Error(`Invalid environment name "${fromEnv}"`);
  }
  const tags: Record<string, string> = {};
  for (const ref of services) {
    const svc = REF.exec(ref)?.[1];
    if (!svc) {
      throw new Error(`Invalid service name "${ref}"`);
    }
    const url = `${baseUrl.replace(
      /\/+$/,
      '',
    )}/envs/${fromEnv}/${svc}/values.yaml`;
    let text: string;
    try {
      const res = await reader.readUrl(url);
      text = (await res.buffer()).toString('utf8');
    } catch (e) {
      throw new Error(
        `${svc} is not deployed in ${fromEnv}: could not read ${url} (${
          (e as Error).message
        })`,
      );
    }
    const tag = parse(text)?.image?.tag;
    if (typeof tag !== 'string' || tag === '') {
      throw new Error(`${url} has no image.tag`);
    }
    tags[svc] = tag;
  }
  return tags;
}

export function createReadImageTagsAction(reader: UrlReaderService) {
  return createTemplateAction({
    id: 'gitops:read-image-tags',
    description:
      'Reads image.tag for each service from envs/<fromEnv>/<svc>/values.yaml in a gitops repo (read-only).',
    supportsDryRun: true,
    schema: {
      input: {
        repoUrl: z =>
          z
            .string()
            .describe(
              'Browse URL of the gitops repo at a branch, e.g. https://github.com/<owner>/gitops/blob/main',
            ),
        services: z =>
          z
            .array(z.string())
            .min(1)
            .describe(
              'Service names or entity refs, e.g. ["users-svc"] or ["component:default/users-svc"]',
            ),
        fromEnv: z =>
          z
            .string()
            .default('dev')
            .describe('Environment to copy the tags from'),
      },
      output: {
        tags: z =>
          z
            .record(z.string(), z.string())
            .describe('Map of service name to image tag'),
        services: z => z.array(z.string()).describe('Plain service names'),
      },
    },
    async handler(ctx) {
      const { repoUrl, services, fromEnv } = ctx.input;
      const tags = await readImageTags(
        reader,
        repoUrl,
        services,
        fromEnv ?? 'dev',
      );
      for (const [svc, tag] of Object.entries(tags)) {
        ctx.logger.info(`${svc}: ${fromEnv ?? 'dev'} image.tag = ${tag}`);
      }
      ctx.output('tags', tags);
      ctx.output('services', Object.keys(tags));
    },
  });
}

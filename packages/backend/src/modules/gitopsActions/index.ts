import {
  coreServices,
  createBackendModule,
} from '@backstage/backend-plugin-api';
import { scaffolderActionsExtensionPoint } from '@backstage/plugin-scaffolder-node';
import { createReadImageTagsAction } from './readImageTags';

/** Read-only scaffolder actions for the gitops repo (used by the New environment template). */
export default createBackendModule({
  pluginId: 'scaffolder',
  moduleId: 'gitops-actions',
  register(env) {
    env.registerInit({
      deps: {
        scaffolder: scaffolderActionsExtensionPoint,
        urlReader: coreServices.urlReader,
      },
      async init({ scaffolder, urlReader }) {
        scaffolder.addActions(createReadImageTagsAction(urlReader));
      },
    });
  },
});

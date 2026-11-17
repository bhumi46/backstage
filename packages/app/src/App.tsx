import { createApp } from '@backstage/frontend-defaults';
import catalogPlugin from '@backstage/plugin-catalog/alpha';
import githubActionsPlugin from '@backstage-community/plugin-github-actions/alpha';
import argocdPlugin from '@roadiehq/backstage-plugin-argo-cd/alpha';
import { navModule } from './modules/nav';
import { homeModule } from './modules/home';
import { signInModule } from './modules/signIn';

export default createApp({
  features: [
    catalogPlugin,
    githubActionsPlugin,
    argocdPlugin,
    navModule,
    homeModule,
    signInModule,
  ],
});

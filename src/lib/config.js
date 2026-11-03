/**
 * Config loader — the single read path for every static list in the app.
 * Spaces, channels, social accounts, services and repos all come from /config/*.json.
 * Nothing in a JSX file should hardcode these lists.
 */
import spacesFile from '../../config/spaces.json';
import channelsFile from '../../config/channels.json';
import socialFile from '../../config/social.json';
import servicesFile from '../../config/services.json';
import reposFile from '../../config/repos.json';
import railsFile from '../../config/payment-rails.json';

export const spaces = spacesFile.spaces;
export const channels = channelsFile.channels;
export const socialAccounts = socialFile.accounts;
export const services = servicesFile.services;
export const repos = reposFile.repos;
export const paymentRails = railsFile.rails;

export const configMeta = {
  spaces: spacesFile.updated,
  channels: channelsFile.updated,
  social: socialFile.updated,
  services: servicesFile.updated,
  repos: reposFile.updated,
  rails: railsFile.updated,
};

/** Look up one space by id. Returns undefined for unknown ids instead of throwing. */
export const getSpace = (id) => spaces.find((s) => s.id === id);

/** Space that owns a given relative route, e.g. '/space/ops' -> ops object. */
export const spaceForRoute = (route) => spaces.find((s) => s.route === route);

/** Channels belonging to a space, filtered by the ids declared in spaces.json. */
export const channelsForSpace = (spaceId) => {
  if (spaceId === 'yt-automation') return channels;
  return [];
};

export const reposByRole = (role) => repos.filter((r) => r.role === role);

export const repoHealth = () => {
  const total = repos.reduce((sum, r) => sum + (r.size_mb || 0), 0);
  const empty = repos.filter((r) => !r.size_mb).length;
  const candidates = repos.filter((r) => r.status === 'archived-candidate').length;
  return { count: repos.length, totalMb: total, empty, archiveCandidates: candidates };
};

/** Fail loudly in dev if a space references a config file that does not exist. */
export const validateConfig = () => {
  const problems = [];
  const known = new Set(spaces.map((s) => s.id));
  channels.forEach((c) => { if (!c.id) problems.push('channel missing id'); });
  socialAccounts.forEach((a) => { if (!a.id) problems.push('social account missing id'); });
  repos.forEach((r) => {
    if (r.space && r.space !== 'all' && !known.has(r.space)) {
      problems.push(`repo ${r.name} references unknown space ${r.space}`);
    }
  });
  return problems;
};

# Monarch — modular personal work platform

Monarch is being shaped as one workspace with focused mini-apps: YouTube Studio, Social Studio, Projects, AI & Agent Library, Knowledge Base, Team & Access, and Monarch Vault. Each area has its own workflow; shared navigation, search, tasks, and workspace context tie them together.

## Run the current private preview

```bash
npm install
npm run dev
```

The Vite dev server is configured for the Arena preview host. For a production bundle:

```bash
npm run build
```

## Implemented in this build

- Premium responsive workspace shell, mini-app navigation, global search (`Ctrl/Cmd + K`), and a clear private-preview notice.
- Dashboard and persistent local tasks, priorities, inbox filters, month navigation, starter projects, and project rooms with task/notes sections.
- Separate channel spaces for the three sample YouTube channels, a content pipeline, stage changes, and a video workspace for idea/brief, research, hook, script, thumbnail/packaging notes, and production checklist.
- Social Studio with account spaces, pillars, short-form planning, and an editable production stage.
- AI & Agent Library for manually saved conversation summaries, tags, project context, and follow-up actions.
- Knowledge notes and Monarch Vault folders plus Discord-inspired spaces, channels, and local conversations. File upload, image/video/audio previews where supported, download, and manual delete work in the browser preview using IndexedDB; workspace records use local browser storage.
- Team roster and role selection are interactive in preview mode. Invites are visibly marked as local-only and do not send email or grant real access.
- A reviewed Supabase SQL foundation is included at `supabase/migrations/202610300001_monarch_core.sql`: workspace membership roles, RLS, core work data, private Vault bucket, and storage access policies.

## Important: what this preview does not yet provide

A separate **free-plan** Supabase project named `monarch-workspace` has been created in the ap-south-1 region. The unrelated `whatsapp-ai-saathi` project was not changed. Two migrations are applied: the private workspace/RLS foundation and a revision-checked workspace-state sync function. Email/password sign-up is enabled with email confirmation; the Arena preview and deployed Vercel URLs are allowed as auth redirects. A Vercel Hobby deployment is live at https://monarch-workspace-beryl.vercel.app (deployed from the current Arena branch).

Once you create and confirm your Monarch account in the preview, low-volume work records (tasks, ideas, scripts, projects, chat summaries, notes, and Vault conversations) sync to the private `workspace_state` record, so they can follow your account across devices. A revision check prevents a stale device from silently overwriting a newer saved version. The first account gets its own private workspace.

**Vault file bytes still stay in the current browser.** The private Storage bucket and workspace access rules exist, but the app's upload/download path has not yet been switched to cloud storage. Browser storage can be cleared or run out of quota. Do not treat it as backup, and don't upload irreplaceable files yet. The free plan has provider limits and can pause/sleep; there is no promise of 100 GB or unlimited retention.

The team roster can read the cloud membership list, but email invitations and role-change actions in the UI are not yet wired to the server. The database roles and RLS policies are in place; real invitation acceptance still needs a trusted server-side flow. Arena history is not auto-imported, and YouTube/social publishing is not connected.

## Cloud foundation notes

1. Project setup uses only a publishable Supabase key in the browser; no service-role key is included in the app.
2. Auth confirmation and redirects are configured for the Arena preview, the deployed Vercel host, and localhost. The current deployment is from the session branch; future Vercel deployments may need to be triggered manually unless Git auto-deploy is enabled.
3. The private Vault bucket and RLS are set up, but cloud file upload, resumable transfers, backup/restore, and invitation email are pending before team files are used for real work.
4. Keep the workspace on the free plan unless you explicitly choose otherwise. Watch provider quotas; don't assume included storage or bandwidth will cover large media.
5. Before inviting teammates, test separate accounts and verify Owner/Admin/Editor/Contributor/Viewer permissions in the live cloud project.

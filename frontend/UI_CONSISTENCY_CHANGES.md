# BuildTrack UI Consistency Pass

This revision is frontend-only. No backend files or API contracts were changed.

## What was standardized
- All role dashboards now use the shared BuildTrack sidebar component instead of maintaining separate sidebar copies.
- Authenticated screens now share the same page background, content spacing, typography, card radius, shadows and border system.
- Forms now use consistent input/select/textarea sizing, hover states and focus rings.
- Tables now share header styling, spacing, row hover behavior and responsive horizontal scrolling.
- Primary, secondary and danger actions now use a common interaction language.
- Stat cards, panels, notifications and dashboard sections share one card style.
- Login, registration, forgot-password and reset-password pages now use the same authentication visual identity.

## Interactivity added
- Subtle page entrance animation.
- Card lift/shadow on hover.
- Button hover/press feedback.
- Animated loading spinner using the existing `.loading` state.
- Smooth progress-bar width transitions.
- Improved tab active/hover states.
- Interactive sidebar hover and active markers.
- Better form focus feedback for keyboard/mouse users.
- Reduced-motion support for accessibility.

## Files intentionally changed
- `src/styles.css`
- `src/app/shared/app-sidebar.component.css`
- `src/app/shared/app-sidebar.component.html`
- `src/app/pages/dashboards/admin-dashboard/admin-dashboard.html`
- `src/app/pages/dashboards/admin-dashboard/admin-dashboard.ts`
- `src/app/pages/dashboards/client-dashboard/client-dashboard.html`
- `src/app/pages/dashboards/client-dashboard/client-dashboard.ts`
- `src/app/pages/dashboards/contractor-dashboard/contractor-dashboard.html`
- `src/app/pages/dashboards/contractor-dashboard/contractor-dashboard.ts`
- `src/app/pages/dashboards/site-engineer-dashboard/site-engineer-dashboard.html`
- `src/app/pages/dashboards/site-engineer-dashboard/site-engineer-dashboard.ts`
- `src/app/pages/dashboards/worker-dashboard/worker-dashboard.html`
- `src/app/pages/dashboards/worker-dashboard/worker-dashboard.ts`
- `src/app/pages/resources/resource-operations/resource-operations.html`

Generated folders such as `node_modules`, `.angular`, and `dist` should not be copied between computers. Run `npm install`/`npm ci` locally after extracting the project.

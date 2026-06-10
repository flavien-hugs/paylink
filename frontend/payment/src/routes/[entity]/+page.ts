import { error } from '@sveltejs/kit';
import { fetchEntity } from '$lib/api';
import type { PageLoad } from './$types';

// Render client-side: the entity branding is fetched from the browser (where
// PUBLIC_API_URL / localhost is reachable), and the Kkiapay widget is
// browser-only anyway. This avoids the SSR container resolving localhost to itself.
export const ssr = false;

export const load: PageLoad = async ({ params, fetch }) => {
	try {
		const entity = await fetchEntity(params.entity, fetch);
		return { entity };
	} catch {
		throw error(404, `Entité « ${params.entity} » introuvable`);
	}
};

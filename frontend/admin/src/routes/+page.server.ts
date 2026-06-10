import { api } from '$lib/server/api';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const token = locals.token!;
	const [stats, recent] = await Promise.all([
		api.stats(token),
		api.transactions(token, 'limit=8&offset=0')
	]);
	return { stats, recent: recent.items };
};

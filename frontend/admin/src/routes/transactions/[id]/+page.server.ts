import { error } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
	try {
		const transaction = await api.transaction(locals.token!, params.id);
		return { transaction };
	} catch (e) {
		if (e instanceof ApiError && e.status === 404) throw error(404, 'Transaction introuvable');
		throw e;
	}
};

export const actions: Actions = {
	reverify: async ({ locals, params }) => {
		try {
			const transaction = await api.reverify(locals.token!, params.id);
			return { transaction };
		} catch (e) {
			const message = e instanceof ApiError ? e.message : 'Échec de la re-vérification.';
			return { error: message };
		}
	}
};

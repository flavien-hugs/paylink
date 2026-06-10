import { fail } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	return { me: await api.me(locals.token!) };
};

export const actions: Actions = {
	password: async ({ locals, request }) => {
		const form = await request.formData();
		const current = String(form.get('current_password') ?? '');
		const next = String(form.get('new_password') ?? '');
		const confirm = String(form.get('confirm_password') ?? '');

		if (next.length < 6) return fail(400, { error: 'Le nouveau mot de passe doit faire au moins 6 caractères.' });
		if (next !== confirm) return fail(400, { error: 'La confirmation ne correspond pas.' });

		try {
			await api.changePassword(locals.token!, current, next);
			return { ok: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Changement impossible.' });
		}
	}
};

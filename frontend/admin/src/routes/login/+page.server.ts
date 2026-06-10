import { fail, redirect } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request, cookies }) => {
		const form = await request.formData();
		const email = String(form.get('email') ?? '');
		const password = String(form.get('password') ?? '');

		if (!email || !password) {
			return fail(400, { error: 'Email et mot de passe requis.' });
		}

		try {
			const { access_token } = await api.login(email, password);
			cookies.set('admin_token', access_token, {
				path: '/',
				httpOnly: true,
				sameSite: 'lax',
				secure: process.env.NODE_ENV === 'production',
				maxAge: 60 * 60 * 12
			});
		} catch (e) {
			const message = e instanceof ApiError ? e.message : 'Connexion impossible.';
			return fail(401, { error: message, email });
		}

		throw redirect(303, '/');
	}
};

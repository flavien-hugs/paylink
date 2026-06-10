import { fail, redirect } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	const me = await api.me(locals.token!);
	if (!me.is_superadmin) throw redirect(303, '/');
	return { users: await api.users(locals.token!), me };
};

export const actions: Actions = {
	create: async ({ locals, request }) => {
		const form = await request.formData();
		const email = String(form.get('email') ?? '').trim();
		const password = String(form.get('password') ?? '');
		const is_active = form.get('is_active') === 'on';
		if (!email || password.length < 6) {
			return fail(400, { error: 'Email requis et mot de passe d’au moins 6 caractères.' });
		}
		try {
			await api.createUser(locals.token!, { email, password, is_active });
			return { ok: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Création impossible.' });
		}
	},

	update: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		const email = String(form.get('email') ?? '').trim();
		const password = String(form.get('password') ?? '');
		const body: { email?: string; password?: string; is_active?: boolean } = {
			email,
			is_active: form.get('is_active') === 'on'
		};
		if (password) body.password = password;
		try {
			await api.updateUser(locals.token!, id, body);
			return { ok: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Mise à jour impossible.' });
		}
	},

	toggle: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		const activate = form.get('activate') === 'true';
		try {
			await api.setUserActive(locals.token!, id, activate);
			return { ok: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Action impossible.' });
		}
	},

	remove: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		try {
			await api.deleteUser(locals.token!, id);
			return { ok: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Suppression impossible.' });
		}
	}
};

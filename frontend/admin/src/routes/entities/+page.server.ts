import { fail } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	return { entities: await api.entities(locals.token!) };
};

function readEntity(form: FormData) {
	return {
		slug: String(form.get('slug') ?? '').trim(),
		name: String(form.get('name') ?? '').trim(),
		description: String(form.get('description') ?? '').trim() || null,
		kkiapay_public_key: String(form.get('kkiapay_public_key') ?? '').trim(),
		kkiapay_private_key: String(form.get('kkiapay_private_key') ?? '').trim(),
		kkiapay_secret: String(form.get('kkiapay_secret') ?? '').trim(),
		logo_url: String(form.get('logo_url') ?? '').trim() || null,
		primary_color: String(form.get('primary_color') ?? '#2563eb'),
		secondary_color: String(form.get('secondary_color') ?? '#1e293b'),
		currency: String(form.get('currency') ?? 'XOF'),
		sandbox: form.get('sandbox') === 'on',
		is_active: form.get('is_active') === 'on'
	};
}

export const actions: Actions = {
	create: async ({ locals, request }) => {
		const body = readEntity(await request.formData());
		try {
			await api.createEntity(locals.token!, body);
			return { created: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Création impossible.' });
		}
	},

	update: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		const body = readEntity(form);
		try {
			await api.updateEntity(locals.token!, id, body);
			return { updated: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Mise à jour impossible.' });
		}
	},

	delete: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		try {
			await api.deleteEntity(locals.token!, id);
			return { deleted: true };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Suppression impossible.' });
		}
	}
};

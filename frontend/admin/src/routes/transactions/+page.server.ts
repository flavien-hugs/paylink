import { fail } from '@sveltejs/kit';
import { api, ApiError } from '$lib/server/api';
import type { Actions, PageServerLoad } from './$types';

const PAGE_SIZE = 25;

export const load: PageServerLoad = async ({ locals, url }) => {
	const token = locals.token!;
	const status = url.searchParams.get('status') ?? '';
	const entityId = url.searchParams.get('entity_id') ?? '';
	const q = url.searchParams.get('q') ?? '';
	const sort = url.searchParams.get('sort') === 'asc' ? 'asc' : 'desc';
	const page = Math.max(1, Number(url.searchParams.get('page') ?? '1'));
	const offset = (page - 1) * PAGE_SIZE;

	const params = new URLSearchParams({ limit: String(PAGE_SIZE), offset: String(offset) });
	if (status) params.set('status', status);
	if (entityId) params.set('entity_id', entityId);
	if (q) params.set('search', q);
	params.set('sort', sort);

	const [data, entities] = await Promise.all([
		api.transactions(token, params.toString()),
		api.entities(token)
	]);

	return {
		transactions: data.items,
		total: data.total,
		page,
		pageSize: PAGE_SIZE,
		filters: { status, entityId, q, sort },
		entities: entities.map((e) => ({ id: e.id, name: e.name }))
	};
};

export const actions: Actions = {
	reverify: async ({ locals, request }) => {
		const form = await request.formData();
		const id = String(form.get('id') ?? '');
		const kkiapayId = String(form.get('kkiapay_transaction_id') ?? '').trim();
		try {
			const transaction = await api.reverify(locals.token!, id, kkiapayId || undefined);
			return { transaction };
		} catch (e) {
			return fail(400, { error: e instanceof ApiError ? e.message : 'Re-vérification impossible.' });
		}
	}
};

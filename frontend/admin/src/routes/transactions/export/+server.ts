import { error } from '@sveltejs/kit';
import { apiBaseUrl } from '$lib/server/api';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ locals, url, fetch }) => {
	const token = locals.token;
	if (!token) throw error(401, 'Non autorisé');

	const params = new URLSearchParams();
	const status = url.searchParams.get('status');
	const entityId = url.searchParams.get('entity_id');
	const q = url.searchParams.get('q');
	if (status) params.set('status', status);
	if (entityId) params.set('entity_id', entityId);
	if (q) params.set('search', q);

	const res = await fetch(`${apiBaseUrl}/admin/transactions/export?${params.toString()}`, {
		headers: { Authorization: `Bearer ${token}` }
	});
	if (!res.ok) throw error(res.status, 'Export impossible');

	const body = await res.text();
	return new Response(body, {
		headers: {
			'Content-Type': 'text/csv; charset=utf-8',
			'Content-Disposition':
				res.headers.get('content-disposition') ?? 'attachment; filename="transactions.csv"'
		}
	});
};

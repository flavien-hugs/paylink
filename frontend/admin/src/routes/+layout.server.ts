import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import { api, ApiError } from '$lib/server/api';
import type { AdminUser } from '$lib/types';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url, cookies }) => {
	let me: AdminUser | null = null;
	if (locals.token) {
		try {
			me = await api.me(locals.token);
		} catch (e) {
			// Token rejected by the API (expired / invalid) → force a clean logout.
			if (e instanceof ApiError && e.status === 401) {
				cookies.delete('admin_token', { path: '/' });
				throw redirect(303, '/login?expired=1');
			}
			me = null;
		}
	}
	return {
		authenticated: Boolean(locals.token),
		me,
		pathname: url.pathname,
		// Public base URL of the payment app, used to build shareable entity links.
		paymentBaseUrl: env.PAYMENT_WEB_URL ?? 'http://localhost:5173'
	};
};

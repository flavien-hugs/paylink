import { redirect } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ cookies }) => {
		cookies.delete('admin_token', { path: '/' });
		throw redirect(303, '/login');
	}
};

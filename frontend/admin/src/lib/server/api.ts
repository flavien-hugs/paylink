import { env } from '$env/dynamic/private';
import type { AdminUser, Entity, Paginated, Stats, StatsReport, Transaction } from '$lib/types';

export type { AdminUser, Entity, Paginated, Stats, StatsReport, Transaction };

const API_URL = env.API_URL ?? 'http://localhost:8000/api';

export class ApiError extends Error {
	constructor(
		public status: number,
		message: string
	) {
		super(message);
	}
}

/**
 * Turn a FastAPI error body into a human-readable message.
 * `detail` is a string for HTTPException, but an array of {loc, msg} for 422
 * validation errors — which must be flattened, not stringified to "[object Object]".
 */
function extractDetail(body: unknown, fallback: string): string {
	const detail = (body as { detail?: unknown })?.detail;
	if (!detail) return fallback;
	if (typeof detail === 'string') return detail;
	if (Array.isArray(detail)) {
		const parts = detail.map((e) => {
			const loc = Array.isArray(e?.loc) ? e.loc.filter((p: unknown) => p !== 'body') : [];
			const field = loc.join('.');
			return field ? `${field} : ${e?.msg}` : String(e?.msg ?? '');
		});
		return parts.filter(Boolean).join(' · ') || fallback;
	}
	if (typeof detail === 'object' && detail !== null && 'msg' in detail) {
		return String((detail as { msg: unknown }).msg);
	}
	return fallback;
}

async function request<T>(
	path: string,
	token: string | null,
	init: RequestInit = {}
): Promise<T> {
	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(init.headers as Record<string, string>)
	};
	if (token) headers.Authorization = `Bearer ${token}`;

	const res = await fetch(`${API_URL}${path}`, { ...init, headers });
	if (!res.ok) {
		let message = res.statusText;
		try {
			message = extractDetail(await res.json(), res.statusText);
		} catch {
			/* non-JSON body → keep statusText */
		}
		throw new ApiError(res.status, message);
	}
	if (res.status === 204) return undefined as T;
	return res.json();
}

export const api = {
	login: (email: string, password: string) =>
		request<{ access_token: string }>('/admin/login', null, {
			method: 'POST',
			body: JSON.stringify({ email, password })
		}),

	stats: (token: string) => request<Stats>('/admin/stats', token),

	transactions: (token: string, query: string) =>
		request<Paginated<Transaction>>(`/admin/transactions?${query}`, token),

	transaction: (token: string, id: string) =>
		request<Transaction>(`/admin/transactions/${id}`, token),

	reverify: (token: string, id: string, kkiapayTransactionId?: string) =>
		request<Transaction>(`/admin/transactions/${id}/reverify`, token, {
			method: 'POST',
			body: JSON.stringify(
				kkiapayTransactionId ? { kkiapay_transaction_id: kkiapayTransactionId } : {}
			)
		}),

	entities: (token: string) => request<Entity[]>('/admin/entities', token),

	createEntity: (token: string, body: Partial<Entity>) =>
		request<Entity>('/admin/entities', token, { method: 'POST', body: JSON.stringify(body) }),

	updateEntity: (token: string, id: string, body: Partial<Entity>) =>
		request<Entity>(`/admin/entities/${id}`, token, {
			method: 'PUT',
			body: JSON.stringify(body)
		}),

	deleteEntity: (token: string, id: string) =>
		request<void>(`/admin/entities/${id}`, token, { method: 'DELETE' }),

	// Reporting
	statsReport: (token: string, days = 14) =>
		request<StatsReport>(`/admin/stats/report?days=${days}`, token),

	// Admin users
	users: (token: string) => request<AdminUser[]>('/admin/users', token),

	createUser: (token: string, body: { email: string; password: string; is_active: boolean }) =>
		request<AdminUser>('/admin/users', token, { method: 'POST', body: JSON.stringify(body) }),

	updateUser: (
		token: string,
		id: string,
		body: { email?: string; password?: string; is_active?: boolean }
	) => request<AdminUser>(`/admin/users/${id}`, token, { method: 'PUT', body: JSON.stringify(body) }),

	setUserActive: (token: string, id: string, active: boolean) =>
		request<AdminUser>(`/admin/users/${id}/${active ? 'activate' : 'deactivate'}`, token, {
			method: 'POST'
		}),

	deleteUser: (token: string, id: string) =>
		request<void>(`/admin/users/${id}`, token, { method: 'DELETE' }),

	// Current account
	me: (token: string) => request<AdminUser>('/admin/me', token),

	changePassword: (token: string, current_password: string, new_password: string) =>
		request<void>('/admin/me/password', token, {
			method: 'PUT',
			body: JSON.stringify({ current_password, new_password })
		}),

	// Raw CSV export (returns text)
	exportTransactionsUrl: (query: string) => `/admin/transactions/export?${query}`
};

/** Base API URL — exported so server routes can stream the CSV export. */
export const apiBaseUrl = API_URL;

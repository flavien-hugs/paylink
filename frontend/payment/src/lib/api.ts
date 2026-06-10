import { API_URL } from './config';

/** Flatten a FastAPI error body (string detail, or 422 validation array) to text. */
async function errorMessage(res: Response, fallback: string): Promise<string> {
	const detail = (await res.json().catch(() => ({})))?.detail;
	if (typeof detail === 'string') return detail;
	if (Array.isArray(detail)) {
		const msg = detail
			.map((e) => {
				const field = Array.isArray(e?.loc)
					? e.loc.filter((p: unknown) => p !== 'body').join('.')
					: '';
				return field ? `${field} : ${e?.msg}` : String(e?.msg ?? '');
			})
			.filter(Boolean)
			.join(' · ');
		if (msg) return msg;
	}
	return fallback;
}

export interface EntityBranding {
	slug: string;
	name: string;
	description: string | null;
	logo_url: string | null;
	primary_color: string;
	secondary_color: string;
	currency: string;
	public_key: string;
	sandbox: boolean;
}

export interface InitiatePaymentResult {
	reference: string;
	amount: number;
	currency: string;
	public_key: string;
	sandbox: boolean;
	entity_name: string;
}

export interface TransactionView {
	reference: string;
	amount: number;
	currency: string;
	status: 'PENDING' | 'SUCCESS' | 'FAILED';
}

export async function fetchEntity(slug: string, fetchFn: typeof fetch = fetch): Promise<EntityBranding> {
	const res = await fetchFn(`${API_URL}/entities/${slug}`);
	if (!res.ok) throw new Error(`Entity '${slug}' introuvable`);
	return res.json();
}

export async function initiatePayment(
	slug: string,
	body: {
		amount: number;
		customer_name?: string;
		customer_email?: string;
		customer_phone?: string;
	}
): Promise<InitiatePaymentResult> {
	const res = await fetch(`${API_URL}/payments/${slug}/initiate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});
	if (!res.ok) {
		throw new Error(await errorMessage(res, 'Échec de l’initialisation du paiement'));
	}
	return res.json();
}

export async function verifyPayment(
	reference: string,
	kkiapayTransactionId: string
): Promise<TransactionView> {
	const res = await fetch(`${API_URL}/payments/${reference}/verify`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ kkiapay_transaction_id: kkiapayTransactionId })
	});
	if (!res.ok) {
		throw new Error(await errorMessage(res, 'Échec de la vérification du paiement'));
	}
	return res.json();
}

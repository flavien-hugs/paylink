const SCRIPT_SRC = 'https://cdn.kkiapay.me/k.js';

let loader: Promise<void> | null = null;

/** Lazily inject the Kkiapay widget script once per page. */
export function loadKkiapay(): Promise<void> {
	if (typeof window === 'undefined') return Promise.resolve();
	if (window.openKkiapayWidget) return Promise.resolve();
	if (loader) return loader;

	loader = new Promise((resolve, reject) => {
		const script = document.createElement('script');
		script.src = SCRIPT_SRC;
		script.async = true;
		script.onload = () => resolve();
		script.onerror = () => reject(new Error('Impossible de charger le widget Kkiapay'));
		document.head.appendChild(script);
	});
	return loader;
}

export interface KkiapayOpenOptions {
	amount: number;
	key: string;
	sandbox: boolean;
	reference: string;
	name?: string;
	email?: string;
	phone?: string;
	theme?: string;
	onSuccess: (transactionId: string) => void;
	onFailed: (reason: unknown, transactionId: string) => void;
}

/** Read the Kkiapay transaction id from any of the shapes its SDK may emit. */
function extractTransactionId(response: unknown): string {
	if (typeof response === 'string') return response;
	if (response && typeof response === 'object') {
		const r = response as Record<string, unknown>;
		const candidate =
			r.transactionId ??
			r.transaction_id ??
			(r.data as Record<string, unknown> | undefined)?.transactionId ??
			(r.response as Record<string, unknown> | undefined)?.transactionId;
		// Kkiapay sends transactionId as a number — coerce it to a string.
		if (typeof candidate === 'string' || typeof candidate === 'number') {
			return String(candidate);
		}
	}
	return '';
}

export async function openPayment(options: KkiapayOpenOptions): Promise<void> {
	await loadKkiapay();
	if (!window.openKkiapayWidget) throw new Error('Widget Kkiapay indisponible');

	// Kkiapay passes the transaction id either as a bare string or wrapped in an
	// object ({ transactionId } / { transaction_id }) depending on the SDK build.
	window.addSuccessListener?.((response) => {
		options.onSuccess(extractTransactionId(response));
	});
	// On failure Kkiapay may still provide a transaction id — pass it through so
	// the backend can reconcile the attempt (record it as FAILED) server-side.
	window.addFailedListener?.((reason) => {
		options.onFailed(reason, extractTransactionId(reason));
	});

	window.openKkiapayWidget({
		amount: options.amount,
		key: options.key,
		sandbox: options.sandbox,
		position: 'center',
		theme: options.theme ?? '#2563eb',
		name: options.name,
		email: options.email,
		phone: options.phone,
		// Echoed back to us in the webhook payload so we can match the transaction.
		data: JSON.stringify({ reference: options.reference })
	});
}

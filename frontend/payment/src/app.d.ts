declare global {
	namespace App {}

	type KkiapaySuccess = string | { transactionId?: string; transaction_id?: string };

	interface Window {
		openKkiapayWidget?: (options: Record<string, unknown>) => void;
		addSuccessListener?: (cb: (response: KkiapaySuccess) => void) => void;
		addFailedListener?: (cb: (response: unknown) => void) => void;
	}
}

export {};

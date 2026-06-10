export function money(amount: number, currency = 'XOF'): string {
	return `${new Intl.NumberFormat('fr-FR').format(amount)} ${currency}`;
}

export function datetime(iso: string): string {
	return new Date(iso).toLocaleString('fr-FR', {
		dateStyle: 'medium',
		timeStyle: 'short'
	});
}

export const STATUS_LABEL: Record<string, string> = {
	PENDING: 'En attente',
	SUCCESS: 'Réussi',
	FAILED: 'Échoué'
};

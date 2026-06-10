export type PaymentStatus = 'PENDING' | 'SUCCESS' | 'FAILED';

export interface Stats {
	total: number;
	pending: number;
	success: number;
	failed: number;
	success_amount: number;
}

export interface Transaction {
	id: string;
	reference: string;
	kkiapay_transaction_id: string | null;
	entity_id: string;
	amount: number;
	currency: string;
	status: PaymentStatus;
	customer_name: string | null;
	customer_email: string | null;
	customer_phone: string | null;
	metadata: Record<string, unknown>;
	created_at: string;
	updated_at: string;
}

export interface Paginated<T> {
	items: T[];
	total: number;
	limit: number;
	offset: number;
}

export interface AdminUser {
	id: string;
	email: string;
	is_active: boolean;
	is_superadmin: boolean;
	created_at: string;
}

export interface EntityStat {
	entity_id: string;
	name: string;
	total: number;
	success: number;
	pending: number;
	failed: number;
	success_amount: number;
}

export interface DailyPoint {
	date: string;
	count: number;
	success_amount: number;
}

export interface StatsReport {
	overall: Stats;
	by_entity: EntityStat[];
	daily: DailyPoint[];
}

export interface Entity {
	id: string;
	slug: string;
	name: string;
	description: string | null;
	logo_url: string | null;
	primary_color: string;
	secondary_color: string;
	currency: string;
	kkiapay_public_key: string;
	kkiapay_private_key: string;
	kkiapay_secret: string;
	sandbox: boolean;
	success_url: string | null;
	failure_url: string | null;
	is_active: boolean;
	created_at: string;
}

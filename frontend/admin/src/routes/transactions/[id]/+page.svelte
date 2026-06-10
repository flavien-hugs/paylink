<script lang="ts">
	import { enhance } from '$app/forms';
	import StatusBadge from '$lib/StatusBadge.svelte';
	import { datetime, money } from '$lib/format';
	import { ArrowLeft, Check, Loader2, RefreshCw } from '@lucide/svelte';
	let { data, form } = $props();

	const txn = $derived(form?.transaction ?? data.transaction);
	let verifying = $state(false);

	const fields = $derived([
		{ label: 'Référence', value: txn.reference, mono: true },
		{ label: 'ID Kkiapay', value: txn.kkiapay_transaction_id ?? '—', mono: true },
		{ label: 'Créée le', value: datetime(txn.created_at) },
		{ label: 'Mise à jour', value: datetime(txn.updated_at) },
		{ label: 'Client', value: txn.customer_name ?? '—' },
		{ label: 'Email', value: txn.customer_email ?? '—' },
		{ label: 'Téléphone', value: txn.customer_phone ?? '—' },
		{ label: 'Devise', value: txn.currency }
	]);
</script>

<svelte:head><title>Transaction {txn.reference.slice(0, 8)}</title></svelte:head>

<a href="/transactions" class="flex items-center gap-1 text-sm text-slate-400 hover:text-slate-600">
	<ArrowLeft class="size-4" /> Transactions
</a>

<div class="mt-4 mb-6 flex items-start justify-between">
	<div>
		<h1 class="mb-1 text-2xl font-bold">{money(txn.amount, txn.currency)}</h1>
		<StatusBadge status={txn.status} />
	</div>
	{#if txn.status === 'SUCCESS'}
		<span class="flex items-center gap-2 text-sm font-medium text-green-700">
			<Check class="size-4" /> Paiement confirmé
		</span>
	{:else}
		<form
			method="POST"
			action="?/reverify"
			use:enhance={() => {
				verifying = true;
				return async ({ update }) => {
					await update();
					verifying = false;
				};
			}}
		>
			<button
				type="submit"
				disabled={verifying}
				class="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
			>
				{#if verifying}
					<Loader2 class="size-4 animate-spin" /> Vérification…
				{:else}
					<RefreshCw class="size-4" /> Re-vérifier le statut
				{/if}
			</button>
		</form>
	{/if}
</div>

{#if form?.error}
	<p class="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-600">{form.error}</p>
{/if}

<div class="grid grid-cols-1 gap-4 rounded-2xl border border-slate-200 bg-white p-6 sm:grid-cols-2 lg:grid-cols-3">
	{#each fields as f}
		<div class="flex flex-col gap-1">
			<span class="text-xs uppercase text-slate-400">{f.label}</span>
			<span class="text-sm break-all {f.mono ? 'font-mono text-xs' : ''}">{f.value}</span>
		</div>
	{/each}
</div>

{#if Object.keys(txn.metadata ?? {}).length > 0}
	<h2 class="mt-8 mb-3 text-base font-semibold">Métadonnées</h2>
	<pre class="overflow-x-auto rounded-2xl bg-slate-900 p-4 text-xs text-slate-200">{JSON.stringify(
			txn.metadata,
			null,
			2
		)}</pre>
{/if}

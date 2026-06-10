<script lang="ts">
	import { goto } from '$app/navigation';
	import StatusBadge from '$lib/StatusBadge.svelte';
	import { datetime, money } from '$lib/format';
	import { ArrowRight, CheckCircle2, Clock, Receipt, Wallet, XCircle } from '@lucide/svelte';
	let { data } = $props();
	const { stats, recent } = data;

	const cards = [
		{ label: 'Total transactions', value: stats.total, icon: Receipt, tone: 'text-slate-900' },
		{ label: 'Réussies', value: stats.success, icon: CheckCircle2, tone: 'text-green-600' },
		{ label: 'En attente', value: stats.pending, icon: Clock, tone: 'text-amber-600' },
		{ label: 'Échouées', value: stats.failed, icon: XCircle, tone: 'text-red-600' }
	];
</script>

<svelte:head><title>Tableau de bord</title></svelte:head>

<h1 class="mb-6 text-2xl font-bold">Tableau de bord</h1>

<section class="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-5">
	{#each cards as c}
		<div class="rounded-2xl border border-slate-200 bg-white p-5">
			<div class="flex items-center justify-between text-slate-400">
				<span class="text-xs">{c.label}</span>
				<c.icon class="size-4" />
			</div>
			<span class="mt-2 block text-2xl font-extrabold {c.tone}">{c.value}</span>
		</div>
	{/each}
	<div class="rounded-2xl border border-slate-200 bg-white p-5">
		<div class="flex items-center justify-between text-slate-400">
			<span class="text-xs">Montant encaissé</span>
			<Wallet class="size-4" />
		</div>
		<span class="mt-2 block text-xl font-extrabold text-blue-600">
			{money(stats.success_amount)}
		</span>
	</div>
</section>

<div class="rounded-2xl border border-slate-200 bg-white p-6">
	<div class="mb-4 flex items-center justify-between">
		<h2 class="text-lg font-semibold">Transactions récentes</h2>
		<a href="/transactions" class="flex items-center gap-1 text-sm font-semibold text-blue-600 hover:underline">
			Voir tout <ArrowRight class="size-4" />
		</a>
	</div>
	{#if recent.length === 0}
		<p class="py-8 text-center text-slate-400">Aucune transaction pour le moment.</p>
	{:else}
		<div class="overflow-x-auto">
		<table class="w-full min-w-[560px]">
			<thead>
				<tr class="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
					<th class="px-3 py-2 font-medium">Date</th>
					<th class="px-3 py-2 font-medium">Client</th>
					<th class="px-3 py-2 font-medium">Montant</th>
					<th class="px-3 py-2 font-medium">Statut</th>
				</tr>
			</thead>
			<tbody>
				{#each recent as t}
					<tr
						class="cursor-pointer border-b border-slate-100 text-sm hover:bg-slate-50"
						onclick={() => goto(`/transactions/${t.id}`)}
					>
						<td class="px-3 py-3">{datetime(t.created_at)}</td>
						<td class="px-3 py-3">{t.customer_name ?? '—'}</td>
						<td class="px-3 py-3 font-medium">{money(t.amount, t.currency)}</td>
						<td class="px-3 py-3"><StatusBadge status={t.status} /></td>
					</tr>
				{/each}
			</tbody>
		</table>
		</div>
	{/if}
</div>

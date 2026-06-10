<script lang="ts">
	import { money } from '$lib/format';
	import { CheckCircle2, Clock, Receipt, Wallet, XCircle } from '@lucide/svelte';
	let { data } = $props();
	const { overall, by_entity, daily } = data.report;

	const successRate = $derived(
		overall.total ? Math.round((overall.success / overall.total) * 100) : 0
	);

	const maxDaily = $derived(Math.max(1, ...daily.map((d) => d.count)));
	const maxEntity = $derived(Math.max(1, ...by_entity.map((e) => e.success_amount)));

	function dayLabel(iso: string) {
		return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
	}

	const cards = [
		{ label: 'Total', value: overall.total, icon: Receipt, tone: 'text-slate-900' },
		{ label: 'Réussies', value: overall.success, icon: CheckCircle2, tone: 'text-green-600' },
		{ label: 'En attente', value: overall.pending, icon: Clock, tone: 'text-amber-600' },
		{ label: 'Échouées', value: overall.failed, icon: XCircle, tone: 'text-red-600' }
	];
</script>

<svelte:head><title>Statistiques</title></svelte:head>

<h1 class="mb-6 text-2xl font-bold">Statistiques</h1>

<section class="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
	{#each cards as c}
		<div class="rounded-2xl border border-slate-200 bg-white p-5">
			<div class="flex items-center justify-between text-slate-400">
				<span class="text-xs">{c.label}</span>
				<c.icon class="size-4" />
			</div>
			<span class="mt-2 block text-2xl font-extrabold {c.tone}">{c.value}</span>
		</div>
	{/each}
</section>

<section class="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
	<div class="rounded-2xl border border-slate-200 bg-white p-5">
		<span class="text-xs text-slate-400">Montant encaissé</span>
		<div class="mt-2 flex items-center gap-2 text-2xl font-extrabold text-blue-600">
			<Wallet class="size-5" />{money(overall.success_amount)}
		</div>
	</div>
	<div class="rounded-2xl border border-slate-200 bg-white p-5">
		<span class="text-xs text-slate-400">Taux de réussite</span>
		<div class="mt-2 text-2xl font-extrabold text-green-600">{successRate}%</div>
		<div class="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
			<div class="h-full rounded-full bg-green-500" style="width: {successRate}%"></div>
		</div>
	</div>
	<div class="rounded-2xl border border-slate-200 bg-white p-5">
		<span class="text-xs text-slate-400">Panier moyen (réussi)</span>
		<div class="mt-2 text-2xl font-extrabold text-slate-900">
			{money(overall.success ? Math.round(overall.success_amount / overall.success) : 0)}
		</div>
	</div>
</section>

<!-- 14-day activity -->
<div class="mb-6 rounded-2xl border border-slate-200 bg-white p-6">
	<h2 class="mb-4 text-lg font-semibold">Activité (14 derniers jours)</h2>
	{#if daily.length === 0}
		<p class="py-6 text-center text-slate-400">Aucune donnée sur la période.</p>
	{:else}
		<div class="flex h-44 items-end gap-2">
			{#each daily as d}
				<div class="flex flex-1 flex-col items-center gap-1">
					<div
						class="w-full rounded-t bg-blue-500/80 transition-all hover:bg-blue-600"
						style="height: {(d.count / maxDaily) * 100}%"
						title="{d.count} transaction(s) — {money(d.success_amount)}"
					></div>
					<span class="text-[10px] text-slate-400">{dayLabel(d.date)}</span>
				</div>
			{/each}
		</div>
	{/if}
</div>

<!-- Per-entity breakdown -->
<div class="rounded-2xl border border-slate-200 bg-white p-6">
	<h2 class="mb-4 text-lg font-semibold">Répartition par entité</h2>
	{#if by_entity.length === 0}
		<p class="py-6 text-center text-slate-400">Aucune entité.</p>
	{:else}
		<table class="w-full">
			<thead>
				<tr class="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
					<th class="px-3 py-2 font-medium">Entité</th>
					<th class="px-3 py-2 font-medium">Total</th>
					<th class="px-3 py-2 font-medium">Réussies</th>
					<th class="px-3 py-2 font-medium">Encaissé</th>
					<th class="px-3 py-2 font-medium"></th>
				</tr>
			</thead>
			<tbody>
				{#each by_entity as e}
					<tr class="border-b border-slate-100 text-sm">
						<td class="px-3 py-3 font-medium">{e.name}</td>
						<td class="px-3 py-3">{e.total}</td>
						<td class="px-3 py-3 text-green-600">{e.success}</td>
						<td class="px-3 py-3 font-semibold">{money(e.success_amount)}</td>
						<td class="px-3 py-3" style="width: 40%">
							<div class="h-2 overflow-hidden rounded-full bg-slate-100">
								<div
									class="h-full rounded-full bg-blue-500"
									style="width: {(e.success_amount / maxEntity) * 100}%"
								></div>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

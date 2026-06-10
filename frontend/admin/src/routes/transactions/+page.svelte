<script lang="ts">
	import { enhance } from "$app/forms";
	import { goto, invalidateAll } from "$app/navigation";
	import { page } from "$app/stores";
	import SearchableSelect from "$lib/SearchableSelect.svelte";
	import StatusBadge from "$lib/StatusBadge.svelte";
	import { datetime, money } from "$lib/format";
	import type { Transaction } from "$lib/types";
	import {
		ArrowDownWideNarrow,
		ArrowUpWideNarrow,
		Building2,
		Check,
		ChevronLeft,
		ChevronRight,
		Copy,
		Download,
		ListFilter,
		RefreshCw,
		RotateCw,
		Search,
		X,
	} from "@lucide/svelte";
	let { data, form } = $props();

	const totalPages = $derived(
		Math.max(1, Math.ceil(data.total / data.pageSize)),
	);

	// CSV export link carrying the current filters.
	const exportHref = $derived.by(() => {
		const p = new URLSearchParams();
		if (data.filters.status) p.set("status", data.filters.status);
		if (data.filters.entityId) p.set("entity_id", data.filters.entityId);
		if (data.filters.q) p.set("q", data.filters.q);
		const qs = p.toString();
		return `/transactions/export${qs ? `?${qs}` : ""}`;
	});

	let selected = $state<Transaction | null>(null);
	let reconciling = $state(false);
	let searchValue = $state(data.filters.q);
	let searchTimer: ReturnType<typeof setTimeout>;

	// After a reconcile, refresh the drawer from the action result (the table
	// itself is refreshed via invalidateAll in the form's enhance handler).
	$effect(() => {
		if (form?.transaction && selected?.id === form.transaction.id) {
			selected = form.transaction;
		}
	});

	function setParam(key: string, value: string) {
		const url = new URL($page.url);
		if (value) url.searchParams.set(key, value);
		else url.searchParams.delete(key);
		url.searchParams.set("page", "1");
		goto(url, { keepFocus: true });
	}

	function onSearch(value: string) {
		searchValue = value;
		clearTimeout(searchTimer);
		searchTimer = setTimeout(() => setParam("q", value.trim()), 350);
	}

	function gotoPage(p: number) {
		const url = new URL($page.url);
		url.searchParams.set("page", String(p));
		goto(url);
	}

	const sortAsc = $derived(data.filters.sort === "asc");
	function toggleSort() {
		setParam("sort", sortAsc ? "desc" : "asc");
	}

	let refreshing = $state(false);
	async function refresh() {
		refreshing = true;
		await invalidateAll();
		refreshing = false;
	}

	function open(t: Transaction) {
		selected = t;
	}

	async function copy(text: string) {
		try {
			await navigator.clipboard.writeText(text);
		} catch {
			/* ignore */
		}
	}

</script>

<svelte:head><title>Transactions</title></svelte:head>

<h1 class="mb-6 text-2xl font-bold">Transactions</h1>

<div class="mb-4 flex flex-wrap items-center gap-3">
	<div class="relative flex-1 sm:min-w-72 sm:flex-none">
		<Search
			class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400"
		/>
		<input
			type="search"
			placeholder="Rechercher (client, email, référence, ID Kkiapay)…"
			value={searchValue}
			oninput={(e) => onSearch(e.currentTarget.value)}
			class="w-full rounded-xl border border-slate-200 bg-white py-2 pr-3 pl-9 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
		/>
	</div>

	<SearchableSelect
		value={data.filters.status}
		options={[
			{ value: 'PENDING', label: 'En attente' },
			{ value: 'SUCCESS', label: 'Réussi' },
			{ value: 'FAILED', label: 'Échoué' }
		]}
		allLabel="Tous les statuts"
		placeholder="Rechercher un statut…"
		icon={ListFilter}
		onChange={(v) => setParam('status', v)}
	/>

	<SearchableSelect
		value={data.filters.entityId}
		options={data.entities.map((e) => ({ value: e.id, label: e.name }))}
		allLabel="Toutes les entités"
		placeholder="Rechercher une entité…"
		icon={Building2}
		onChange={(v) => setParam("entity_id", v)}
	/>

	<div class="ml-auto flex items-center gap-2">
		<span class="mr-1 text-sm text-slate-400">
			{data.total} résultat{data.total > 1 ? "s" : ""}
		</span>

		<button
			type="button"
			onclick={toggleSort}
			title={sortAsc ? "Plus ancien d’abord" : "Plus récent d’abord"}
			class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
		>
			{#if sortAsc}
				<ArrowUpWideNarrow class="size-4" /> Ancien
			{:else}
				<ArrowDownWideNarrow class="size-4" /> Récent
			{/if}
		</button>

		<button
			type="button"
			onclick={refresh}
			disabled={refreshing}
			title="Actualiser"
			class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60"
		>
			<RotateCw class="size-4 {refreshing ? 'animate-spin' : ''}" /> Actualiser
		</button>

		<a
			href={exportHref}
			data-sveltekit-reload
			class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
		>
			<Download class="size-4" /> Exporter
		</a>
	</div>
</div>

<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
	{#if data.transactions.length === 0}
		<p class="py-8 text-center text-slate-400">Aucune transaction.</p>
	{:else}
		<table class="w-full">
			<thead>
				<tr
					class="border-b border-slate-200 text-left text-xs uppercase text-slate-400"
				>
					<th class="px-4 py-3 font-medium">Date</th>
					<th class="px-4 py-3 font-medium">Référence</th>
					<th class="px-4 py-3 font-medium">Client</th>
					<th class="px-4 py-3 font-medium">Montant</th>
					<th class="px-4 py-3 font-medium">Statut</th>
					<th class="px-4 py-3 font-medium"></th>
				</tr>
			</thead>
			<tbody>
				{#each data.transactions as t}
					<tr
						class="cursor-pointer border-b border-slate-100 text-sm hover:bg-slate-50"
						onclick={() => open(t)}
					>
						<td class="px-4 py-3.5">{datetime(t.created_at)}</td>
						<td class="px-4 py-3.5 font-mono text-slate-400"
							>{t.reference.slice(0, 8)}…</td
						>
						<td class="px-4 py-3.5">{t.customer_name ?? "—"}</td>
						<td class="px-4 py-3.5 font-medium"
							>{money(t.amount, t.currency)}</td
						>
						<td class="px-4 py-3.5"
							><StatusBadge status={t.status} /></td
						>
						<td class="px-4 py-3.5 text-right">
							{#if t.status === "PENDING"}
								<button
									class="inline-flex items-center gap-1.5 rounded-lg border border-blue-200 px-2.5 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50"
									onclick={(e) => {
										e.stopPropagation();
										open(t);
									}}
								>
									<RefreshCw class="size-3.5" /> Réconcilier
								</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

{#if totalPages > 1}
	<div class="mt-5 flex items-center justify-center gap-4">
		<button
			class="flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-sm disabled:opacity-50"
			disabled={data.page <= 1}
			onclick={() => gotoPage(data.page - 1)}
		>
			<ChevronLeft class="size-4" /> Précédent
		</button>
		<span class="text-sm text-slate-500"
			>Page {data.page} / {totalPages}</span
		>
		<button
			class="flex items-center gap-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-sm disabled:opacity-50"
			disabled={data.page >= totalPages}
			onclick={() => gotoPage(data.page + 1)}
		>
			Suivant <ChevronRight class="size-4" />
		</button>
	</div>
{/if}

<!-- Right-side detail drawer -->
{#if selected}
	<div
		class="fixed inset-0 z-20 bg-slate-900/40"
		role="presentation"
		onclick={() => (selected = null)}
	></div>
	<aside
		class="fixed top-0 right-0 z-30 flex h-full w-full max-w-md flex-col overflow-y-auto bg-white shadow-2xl"
	>
		<header
			class="flex items-start justify-between border-b border-slate-200 p-6"
		>
			<div>
				<div class="text-2xl font-bold">
					{money(selected.amount, selected.currency)}
				</div>
				<div class="mt-1"><StatusBadge status={selected.status} /></div>
			</div>
			<button
				class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100"
				onclick={() => (selected = null)}
				aria-label="Fermer"
			>
				<X class="size-5" />
			</button>
		</header>

		<div class="grid grid-cols-1 gap-4 p-6 sm:grid-cols-2">
			{#each [{ label: "Référence", value: selected.reference, mono: true, copyable: true }, { label: "ID Kkiapay", value: selected.kkiapay_transaction_id ?? "—", mono: true }, { label: "Créée le", value: datetime(selected.created_at) }, { label: "Mise à jour", value: datetime(selected.updated_at) }, { label: "Client", value: selected.customer_name ?? "—" }, { label: "Email", value: selected.customer_email ?? "—" }, { label: "Téléphone", value: selected.customer_phone ?? "—" }, { label: "Devise", value: selected.currency }] as f}
				<div class="flex flex-col gap-1">
					<span class="text-xs uppercase text-slate-400"
						>{f.label}</span
					>
					<span
						class="flex items-center gap-1.5 text-sm break-all {f.mono
							? 'font-mono text-xs'
							: ''}"
					>
						{f.value}
						{#if f.copyable}
							<button
								class="text-slate-400 hover:text-blue-600"
								onclick={() => copy(String(f.value))}
								aria-label="Copier"
							>
								<Copy class="size-3.5" />
							</button>
						{/if}
					</span>
				</div>
			{/each}
		</div>

		<!-- Reconciliation: only relevant while the payment is not yet confirmed.
		     A SUCCESS transaction is final, so nothing left to reconcile. -->
		{#if selected.status === "SUCCESS"}
			<div
				class="flex items-center gap-2 border-t border-slate-200 p-6 text-sm text-green-700"
			>
				<Check class="size-4" /> Paiement confirmé — aucune réconciliation
				nécessaire.
			</div>
		{:else}
			<div class="border-t border-slate-200 p-6">
				<h3 class="mb-1 flex items-center gap-2 font-semibold">
					<RefreshCw class="size-4" /> Réconciliation
				</h3>
				<p class="mb-3 text-xs text-slate-500">
					Re-vérifie le statut auprès de Kkiapay. Pour une transaction
					orpheline, renseignez son identifiant de transaction
					Kkiapay.
				</p>

				{#if form?.error}
					<p
						class="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600"
					>
						{form.error}
					</p>
				{/if}

				<form
					method="POST"
					action="?/reverify"
					use:enhance={() => {
						reconciling = true;
						return async ({ update }) => {
							await update({ reset: false });
							reconciling = false;
							await invalidateAll();
						};
					}}
				>
					<input type="hidden" name="id" value={selected.id} />
					<label
						class="mb-3 flex flex-col gap-1.5 text-xs font-semibold text-slate-700"
					>
						ID transaction Kkiapay
						<input
							name="kkiapay_transaction_id"
							value={selected.kkiapay_transaction_id ?? ""}
							placeholder="ex. 1104473908194860"
							class="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
						/>
					</label>
					<button
						type="submit"
						disabled={reconciling}
						class="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
					>
						<RefreshCw
							class="size-4 {reconciling ? 'animate-spin' : ''}"
						/>
						{reconciling
							? "Vérification…"
							: "Réconcilier maintenant"}
					</button>
				</form>
			</div>
		{/if}

		{#if Object.keys(selected.metadata ?? {}).length > 0}
			<div class="border-t border-slate-200 p-6">
				<h3 class="mb-3 font-semibold">Métadonnées</h3>
				<pre
					class="overflow-x-auto rounded-xl bg-slate-900 p-4 text-xs text-slate-200">{JSON.stringify(
						selected.metadata,
						null,
						2,
					)}</pre>
			</div>
		{/if}
	</aside>
{/if}

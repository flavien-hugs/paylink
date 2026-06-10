<script lang="ts">
	import { goto } from '$app/navigation';
	import { initiatePayment, verifyPayment } from '$lib/api';
	import { openPayment } from '$lib/kkiapay';
	import { Loader2, Lock, ShieldCheck } from '@lucide/svelte';
	import type { PageData } from './$types';

	let { data }: { data: PageData } = $props();
	const entity = data.entity;

	let amount = $state<number | null>(null);
	let customerName = $state('');
	let customerEmail = $state('');
	let customerPhone = $state('');
	let processing = $state(false);
	let errorMsg = $state('');

	const fmt = new Intl.NumberFormat('fr-FR');

	async function pay(event: SubmitEvent) {
		event.preventDefault();
		errorMsg = '';
		if (!amount || amount <= 0) {
			errorMsg = 'Veuillez saisir un montant valide.';
			return;
		}
		processing = true;
		try {
			const init = await initiatePayment(entity.slug, {
				amount,
				customer_name: customerName || undefined,
				customer_email: customerEmail || undefined,
				customer_phone: customerPhone || undefined
			});

			await openPayment({
				amount: init.amount,
				key: init.public_key,
				sandbox: init.sandbox,
				reference: init.reference,
				name: customerName || undefined,
				email: customerEmail || undefined,
				phone: customerPhone || undefined,
				theme: entity.primary_color,
				onSuccess: async (transactionId) => {
					try {
						const txn = await verifyPayment(init.reference, transactionId);
						const target = txn.status === 'SUCCESS' ? 'success' : 'failure';
						await goto(`/${entity.slug}/${target}?ref=${txn.reference}&amount=${txn.amount}`);
					} catch {
						await goto(`/${entity.slug}/failure?ref=${init.reference}`);
					}
				},
				onFailed: async (_reason, transactionId) => {
					// Reconcile the failed attempt server-side when Kkiapay gave us an id.
					if (transactionId) {
						try {
							await verifyPayment(init.reference, transactionId);
						} catch {
							/* webhook will reconcile if this fails */
						}
					}
					await goto(`/${entity.slug}/failure?ref=${init.reference}`);
				}
			});
		} catch (e) {
			errorMsg = e instanceof Error ? e.message : 'Une erreur est survenue.';
		} finally {
			processing = false;
		}
	}
</script>

<svelte:head>
	<title>Paiement — {entity.name}</title>
</svelte:head>

<div
	class="grid min-h-screen w-full bg-white md:grid-cols-2"
	style="--brand-primary: {entity.primary_color}; --brand-secondary: {entity.secondary_color};"
>
	<!-- Left: entity branding -->
	<aside
		class="relative flex flex-col justify-between gap-8 p-8 text-white md:p-12 lg:p-16"
		style="background: linear-gradient(160deg, var(--brand-primary), var(--brand-secondary));"
	>
		<div class="flex items-center gap-3">
			{#if entity.logo_url}
				<img
					class="size-12 rounded-xl bg-white/10 object-contain p-1 backdrop-blur"
					src={entity.logo_url}
					alt={entity.name}
				/>
			{:else}
				<div class="grid size-12 place-items-center rounded-xl bg-white/15 text-xl font-bold">
					{entity.name.charAt(0)}
				</div>
			{/if}
			<span class="text-lg font-bold">{entity.name}</span>
		</div>

		<div>
			<h1 class="text-2xl leading-tight font-extrabold md:text-3xl">
				Effectuez votre paiement
			</h1>
			{#if entity.description}
				<p class="mt-3 text-sm leading-relaxed text-white/85">{entity.description}</p>
			{:else}
				<p class="mt-3 text-sm leading-relaxed text-white/85">
					Réglez le montant de votre choix en toute sécurité auprès de {entity.name}.
				</p>
			{/if}
		</div>

		<div class="flex items-center gap-2 text-sm text-white/80">
			<ShieldCheck class="size-4" /> Paiement sécurisé via Kkiapay
		</div>

		{#if entity.sandbox}
			<span
				class="absolute top-4 right-4 rounded-full bg-white/15 px-2.5 py-0.5 text-xs font-medium backdrop-blur"
			>
				Mode test
			</span>
		{/if}
	</aside>

	<!-- Right: payment form -->
	<div class="flex items-center justify-center p-8 md:p-12">
		<div class="w-full max-w-md">
			<h2 class="mb-6 text-lg font-bold text-slate-900">Détails du paiement</h2>
			<form class="flex flex-col gap-4" onsubmit={pay}>
		<label class="flex flex-col gap-1.5">
			<span class="text-sm font-semibold text-slate-700">
				Montant à payer ({entity.currency})
			</span>
			<div
				class="flex items-center overflow-hidden rounded-xl border border-slate-200 focus-within:border-[var(--brand-primary)] focus-within:ring-2 focus-within:ring-[var(--brand-primary)]/20"
			>
				<input
					class="w-full bg-transparent px-3.5 py-2.5 text-2xl font-bold outline-none"
					type="number"
					min="1"
					step="1"
					inputmode="numeric"
					placeholder="0"
					bind:value={amount}
					required
				/>
				<span class="px-3.5 font-semibold text-slate-400">{entity.currency}</span>
			</div>
		</label>

		<label class="flex flex-col gap-1.5">
			<span class="text-sm font-semibold text-slate-700">Nom complet</span>
			<input
				class="rounded-xl border border-slate-200 px-3.5 py-2.5 outline-none focus:border-[var(--brand-primary)] focus:ring-2 focus:ring-[var(--brand-primary)]/20"
				type="text"
				bind:value={customerName}
				placeholder="Votre nom"
			/>
		</label>

		<div class="grid grid-cols-2 gap-3">
			<label class="flex flex-col gap-1.5">
				<span class="text-sm font-semibold text-slate-700">Email</span>
				<input
					class="rounded-xl border border-slate-200 px-3.5 py-2.5 outline-none focus:border-[var(--brand-primary)] focus:ring-2 focus:ring-[var(--brand-primary)]/20"
					type="email"
					bind:value={customerEmail}
					placeholder="vous@email.com"
				/>
			</label>
			<label class="flex flex-col gap-1.5">
				<span class="text-sm font-semibold text-slate-700">Téléphone</span>
				<input
					class="rounded-xl border border-slate-200 px-3.5 py-2.5 outline-none focus:border-[var(--brand-primary)] focus:ring-2 focus:ring-[var(--brand-primary)]/20"
					type="tel"
					bind:value={customerPhone}
					placeholder="+229..."
				/>
			</label>
		</div>

		{#if errorMsg}
			<p class="text-sm text-red-600">{errorMsg}</p>
		{/if}

		<button
			class="mt-1 flex items-center justify-center gap-2 rounded-xl px-4 py-3 font-bold text-white transition disabled:cursor-not-allowed disabled:opacity-60"
			style="background: var(--brand-primary)"
			type="submit"
			disabled={processing}
		>
			{#if processing}
				<Loader2 class="size-5 animate-spin" /> Traitement…
			{:else}
				<Lock class="size-4" />
				Payer {amount ? fmt.format(amount) + ' ' + entity.currency : ''}
			{/if}
		</button>
		</form>
		</div>
	</div>
</div>

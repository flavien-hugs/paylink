<script lang="ts">
	import { page } from '$app/stores';
	import { CheckCircle2 } from '@lucide/svelte';

	const reference = $derived($page.url.searchParams.get('ref'));
	const amount = $derived($page.url.searchParams.get('amount'));
	const slug = $derived($page.params.entity);
</script>

<svelte:head><title>Paiement réussi</title></svelte:head>

<div class="grid min-h-screen place-items-center p-6">
<div class="w-full max-w-md rounded-2xl bg-white p-12 text-center shadow-xl shadow-slate-900/10">
	<div class="mx-auto mb-5 grid size-18 place-items-center rounded-full bg-green-100 text-green-600">
		<CheckCircle2 class="size-10" />
	</div>
	<h1 class="mb-1 text-2xl font-bold text-green-600">Paiement réussi</h1>
	<p class="text-slate-500">Votre transaction a bien été confirmée.</p>
	{#if amount}
		<p class="my-4 text-3xl font-extrabold text-slate-900">
			{Number(amount).toLocaleString('fr-FR')} F
		</p>
	{/if}
	{#if reference}
		<p class="text-xs break-all text-slate-400">Référence : {reference}</p>
	{/if}
	<a
		href="/{slug}"
		class="mt-6 inline-block font-semibold text-blue-600 hover:underline"
	>
		Nouveau paiement
	</a>
</div>
</div>

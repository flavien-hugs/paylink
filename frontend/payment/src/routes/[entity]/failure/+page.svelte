<script lang="ts">
	import { page } from '$app/stores';
	import { XCircle } from '@lucide/svelte';

	const reference = $derived($page.url.searchParams.get('ref'));
	const slug = $derived($page.params.entity);
</script>

<svelte:head><title>Paiement échoué</title></svelte:head>

<div class="grid min-h-screen place-items-center p-6">
<div class="w-full max-w-md rounded-2xl bg-white p-12 text-center shadow-xl shadow-slate-900/10">
	<div class="mx-auto mb-5 grid size-18 place-items-center rounded-full bg-red-100 text-red-600">
		<XCircle class="size-10" />
	</div>
	<h1 class="mb-1 text-2xl font-bold text-red-600">Paiement échoué</h1>
	<p class="text-slate-500">
		Votre paiement n’a pas pu être confirmé. Aucun montant n’a été débité.
	</p>
	{#if reference}
		<p class="mt-3 text-xs break-all text-slate-400">Référence : {reference}</p>
	{/if}
	<a
		href="/{slug}"
		class="mt-6 inline-block font-semibold text-blue-600 hover:underline"
	>
		Réessayer
	</a>
</div>
</div>

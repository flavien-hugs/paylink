<script lang="ts">
	import { page } from '$app/stores';
	import { enhance } from '$app/forms';
	import IconInput from '$lib/IconInput.svelte';
	import SecretInput from '$lib/SecretInput.svelte';
	import { Clock, KeyRound, Loader2, Lock, Mail } from '@lucide/svelte';
	let { form } = $props();
	let loading = $state(false);
	const expired = $derived($page.url.searchParams.get('expired') === '1');
</script>

<svelte:head><title>Connexion — Admin Payment</title></svelte:head>

<div class="grid min-h-screen place-items-center p-6">
	<form
		method="POST"
		class="flex w-full max-w-sm flex-col gap-4 rounded-2xl bg-white p-8 shadow-xl shadow-slate-900/10"
		use:enhance={() => {
			loading = true;
			return async ({ update }) => {
				await update();
				loading = false;
			};
		}}
	>
		<div class="text-xl font-extrabold">SBBS <span class="font-medium text-blue-600">Payment</span></div>
		<h1 class="-mt-2 mb-2 text-base font-medium text-slate-500">Espace administrateur</h1>

		{#if expired}
			<p class="flex items-center gap-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-700">
				<Clock class="size-4 shrink-0" /> Votre session a expiré, veuillez vous reconnecter.
			</p>
		{/if}

		<label class="flex flex-col gap-1.5">
			<span class="text-sm font-semibold text-slate-700">Email</span>
			<IconInput type="email" name="email" value={form?.email ?? ''} icon={Mail} required />
		</label>
		<label class="flex flex-col gap-1.5">
			<span class="text-sm font-semibold text-slate-700">Mot de passe</span>
			<SecretInput name="password" icon={KeyRound} required />
		</label>

		{#if form?.error}
			<p class="text-sm text-red-600">{form.error}</p>
		{/if}

		<button
			class="mt-1 flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-3 font-bold text-white transition hover:bg-blue-700 disabled:opacity-60"
			type="submit"
			disabled={loading}
		>
			{#if loading}
				<Loader2 class="size-5 animate-spin" /> Connexion…
			{:else}
				<Lock class="size-4" /> Se connecter
			{/if}
		</button>
	</form>
</div>

<script lang="ts">
	import { enhance } from '$app/forms';
	import SecretInput from '$lib/SecretInput.svelte';
	import { datetime } from '$lib/format';
	import { KeyRound, Loader2, Mail, UserCircle } from '@lucide/svelte';
	let { data, form } = $props();
	let saving = $state(false);

	const labelClass = 'flex flex-col gap-1.5 text-xs font-semibold text-slate-700';
</script>

<svelte:head><title>Paramètres</title></svelte:head>

<h1 class="mb-6 text-2xl font-bold">Paramètres</h1>

<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
	<!-- Account -->
	<div class="rounded-2xl border border-slate-200 bg-white p-6">
		<h2 class="mb-4 flex items-center gap-2 text-lg font-semibold">
			<UserCircle class="size-5" /> Mon compte
		</h2>
		<div class="flex items-center gap-2 text-sm text-slate-600">
			<Mail class="size-4 text-slate-400" /> {data.me.email}
		</div>
		<div class="mt-2 text-xs text-slate-400">Compte créé le {datetime(data.me.created_at)}</div>
		<div class="mt-3">
			<span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-700">
				{data.me.is_active ? 'Actif' : 'Inactif'}
			</span>
		</div>
	</div>

	<!-- Change password -->
	<div class="rounded-2xl border border-slate-200 bg-white p-6">
		<h2 class="mb-4 flex items-center gap-2 text-lg font-semibold">
			<KeyRound class="size-5" /> Changer mon mot de passe
		</h2>

		{#if form?.ok}
			<p class="mb-3 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">
				Mot de passe mis à jour.
			</p>
		{/if}
		{#if form?.error}
			<p class="mb-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{form.error}</p>
		{/if}

		<form
			method="POST"
			action="?/password"
			class="flex flex-col gap-3.5"
			use:enhance={() => {
				saving = true;
				return async ({ update }) => {
					await update();
					saving = false;
				};
			}}
		>
			<label class={labelClass}>
				Mot de passe actuel
				<SecretInput name="current_password" icon={KeyRound} required />
			</label>
			<label class={labelClass}>
				Nouveau mot de passe
				<SecretInput name="new_password" icon={KeyRound} required />
			</label>
			<label class={labelClass}>
				Confirmer le nouveau mot de passe
				<SecretInput name="confirm_password" icon={KeyRound} required />
			</label>
			<button
				type="submit"
				disabled={saving}
				class="mt-1 flex items-center justify-center gap-2 rounded-xl bg-blue-600 py-2.5 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
			>
				{#if saving}<Loader2 class="size-4 animate-spin" /> Enregistrement…{:else}Mettre à jour{/if}
			</button>
		</form>
	</div>
</div>

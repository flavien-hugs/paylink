<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import IconInput from '$lib/IconInput.svelte';
	import SecretInput from '$lib/SecretInput.svelte';
	import { datetime } from '$lib/format';
	import type { AdminUser } from '$lib/types';
	import {
		KeyRound,
		Mail,
		Pencil,
		Plus,
		Power,
		PowerOff,
		Search,
		ShieldCheck,
		Trash2,
		UserPlus
	} from '@lucide/svelte';
	let { data, form } = $props();

	let editing = $state<AdminUser | null>(null);
	let showForm = $state(false);
	let search = $state('');

	const filteredUsers = $derived(
		search.trim()
			? data.users.filter((u) => u.email.toLowerCase().includes(search.trim().toLowerCase()))
			: data.users
	);

	function openCreate() {
		editing = null;
		showForm = true;
	}
	function openEdit(u: AdminUser) {
		editing = u;
		showForm = true;
	}
	function close() {
		showForm = false;
		editing = null;
	}

	const inputClass =
		'rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20';
	const labelClass = 'flex flex-col gap-1.5 text-xs font-semibold text-slate-700';
</script>

<svelte:head><title>Utilisateurs</title></svelte:head>

<div class="mb-6 flex items-center justify-between">
	<h1 class="text-2xl font-bold">Utilisateurs</h1>
	<button
		class="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 font-semibold text-white transition hover:bg-blue-700"
		onclick={openCreate}
	>
		<UserPlus class="size-4" /> Nouvel utilisateur
	</button>
</div>

{#if form?.error}
	<p class="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-600">{form.error}</p>
{/if}

<div class="mb-4 flex items-center gap-3">
	<div class="relative sm:min-w-72">
		<Search class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
		<input
			type="search"
			placeholder="Rechercher un utilisateur (email)…"
			bind:value={search}
			class="w-full rounded-xl border border-slate-200 bg-white py-2 pr-3 pl-9 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
		/>
	</div>
	<span class="ml-auto text-sm text-slate-400">
		{filteredUsers.length} utilisateur{filteredUsers.length > 1 ? 's' : ''}
	</span>
</div>

<div class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
	<table class="w-full">
		<thead>
			<tr class="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
				<th class="px-4 py-3 font-medium">Email</th>
				<th class="px-4 py-3 font-medium">Statut</th>
				<th class="px-4 py-3 font-medium">Créé le</th>
				<th class="px-4 py-3 text-right font-medium">Actions</th>
			</tr>
		</thead>
		<tbody>
			{#each filteredUsers as u}
				<tr class="border-b border-slate-100 text-sm">
					<td class="px-4 py-3.5 font-medium">
						<div class="flex items-center gap-2">
							{u.email}
							{#if u.is_superadmin}
								<span
									class="flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-semibold text-blue-700"
								>
									<ShieldCheck class="size-3" /> Super admin
								</span>
							{/if}
						</div>
					</td>
					<td class="px-4 py-3.5">
						{#if u.is_active}
							<span class="rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-semibold text-green-700">
								Actif
							</span>
						{:else}
							<span class="rounded-full bg-slate-200 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
								Inactif
							</span>
						{/if}
					</td>
					<td class="px-4 py-3.5 text-slate-500">{datetime(u.created_at)}</td>
					<td class="px-4 py-3.5">
						<div class="flex justify-end gap-2">
							<button
								class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold hover:bg-slate-50"
								onclick={() => openEdit(u)}
							>
								<Pencil class="size-3.5" /> Modifier
							</button>
							{#if !u.is_superadmin}
							<form
								method="POST"
								action="?/toggle"
								use:enhance={() => async ({ update }) => {
									await update();
									await invalidateAll();
								}}
							>
								<input type="hidden" name="id" value={u.id} />
								<input type="hidden" name="activate" value={u.is_active ? 'false' : 'true'} />
								{#if u.is_active}
									<button
										type="submit"
										class="flex items-center gap-1.5 rounded-lg border border-amber-200 px-2.5 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-50"
									>
										<PowerOff class="size-3.5" /> Désactiver
									</button>
								{:else}
									<button
										type="submit"
										class="flex items-center gap-1.5 rounded-lg border border-green-200 px-2.5 py-1.5 text-xs font-semibold text-green-700 hover:bg-green-50"
									>
										<Power class="size-3.5" /> Activer
									</button>
								{/if}
							</form>
							<form
								method="POST"
								action="?/remove"
								use:enhance={() => async ({ update }) => {
									await update();
									await invalidateAll();
								}}
							>
								<input type="hidden" name="id" value={u.id} />
								<button
									type="submit"
									class="flex items-center gap-1.5 rounded-lg border border-red-200 px-2.5 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50"
									onclick={(e) => {
										if (!confirm(`Supprimer « ${u.email} » ?`)) e.preventDefault();
									}}
								>
									<Trash2 class="size-3.5" /> Supprimer
								</button>
							</form>
							{/if}
						</div>
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

{#if showForm}
	<div
		class="fixed inset-0 z-10 grid place-items-center bg-slate-900/50 p-6"
		role="presentation"
		onclick={(e) => {
			if (e.target === e.currentTarget) close();
		}}
	>
		<form
			method="POST"
			action={editing ? '?/update' : '?/create'}
			class="flex w-full max-w-md flex-col gap-3.5 rounded-2xl bg-white p-7"
			use:enhance={() =>
				async ({ update, result }) => {
					await update();
					if (result.type === 'success') {
						close();
						await invalidateAll();
					}
				}}
		>
			<h2 class="flex items-center gap-2 text-lg font-bold">
				<Plus class="size-5" />
				{editing ? 'Modifier' : 'Nouvel'} utilisateur
			</h2>
			{#if editing}<input type="hidden" name="id" value={editing.id} />{/if}

			<label class={labelClass}>
				Email
				<IconInput type="email" name="email" value={editing?.email ?? ''} icon={Mail} required />
			</label>
			<label class={labelClass}>
				Mot de passe {editing ? '(laisser vide pour ne pas changer)' : ''}
				<SecretInput name="password" placeholder="••••••" icon={KeyRound} required={!editing} />
			</label>
			<label class="flex items-center gap-2 text-sm font-medium">
				<input type="checkbox" name="is_active" checked={editing ? editing.is_active : true} />
				Compte actif
			</label>

			<div class="mt-1 flex justify-end gap-3">
				<button
					type="button"
					class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm hover:bg-slate-50"
					onclick={close}
				>
					Annuler
				</button>
				<button
					type="submit"
					class="rounded-xl bg-blue-600 px-4 py-2.5 font-semibold text-white hover:bg-blue-700"
				>
					{editing ? 'Enregistrer' : 'Créer'}
				</button>
			</div>
		</form>
	</div>
{/if}

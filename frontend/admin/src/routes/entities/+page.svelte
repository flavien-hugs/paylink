<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import SearchableSelect from '$lib/SearchableSelect.svelte';
	import SecretInput from '$lib/SecretInput.svelte';
	import { slugify } from '$lib/slug';
	import type { Entity } from '$lib/types';
	import {
		ArrowDownAZ,
		ArrowUpAZ,
		Check,
		CircleCheck,
		Copy,
		ExternalLink,
		ImagePlus,
		KeyRound,
		Link2,
		Pencil,
		Plus,
		RotateCw,
		Search,
		Share2,
		SlidersHorizontal,
		Trash2,
		Upload,
		X
	} from '@lucide/svelte';
	let { data, form } = $props();

	const base = $derived(data.paymentBaseUrl);

	let editing = $state<Entity | null>(null);
	let showForm = $state(false);

	// Client-side search / filters / sort over the loaded entities.
	let search = $state('');
	let statusFilter = $state('');
	let modeFilter = $state('');
	let sortAsc = $state(true);
	let refreshing = $state(false);

	const filteredEntities = $derived.by(() => {
		const q = search.trim().toLowerCase();
		let list = data.entities.filter((e) => {
			if (q && !e.name.toLowerCase().includes(q) && !e.slug.toLowerCase().includes(q)) return false;
			if (statusFilter === 'active' && !e.is_active) return false;
			if (statusFilter === 'inactive' && e.is_active) return false;
			if (modeFilter === 'sandbox' && !e.sandbox) return false;
			if (modeFilter === 'live' && e.sandbox) return false;
			return true;
		});
		list = [...list].sort((a, b) =>
			sortAsc ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name)
		);
		return list;
	});

	async function refresh() {
		refreshing = true;
		await invalidateAll();
		refreshing = false;
	}

	// Form state so the slug can auto-follow the name yet stay customizable.
	let fName = $state('');
	let fSlug = $state('');
	let fLogo = $state('');
	let logoError = $state('');
	let slugTouched = $state(false);
	let copiedId = $state<string | null>(null);

	const MAX_LOGO_BYTES = 512 * 1024;

	function openCreate() {
		editing = null;
		fName = '';
		fSlug = '';
		fLogo = '';
		logoError = '';
		slugTouched = false;
		showForm = true;
	}
	function openEdit(entity: Entity) {
		editing = entity;
		fName = entity.name;
		fSlug = entity.slug;
		fLogo = entity.logo_url ?? '';
		logoError = '';
		slugTouched = true; // existing slug: don't silently rewrite it
		showForm = true;
	}

	function onLogoFile(e: Event) {
		logoError = '';
		const file = (e.currentTarget as HTMLInputElement).files?.[0];
		if (!file) return;
		if (!file.type.startsWith('image/')) {
			logoError = 'Veuillez choisir une image.';
			return;
		}
		if (file.size > MAX_LOGO_BYTES) {
			logoError = 'Image trop lourde (max 512 Ko).';
			return;
		}
		const reader = new FileReader();
		reader.onload = () => (fLogo = String(reader.result));
		reader.readAsDataURL(file);
	}
	function close() {
		showForm = false;
		editing = null;
	}

	function onName(value: string) {
		fName = value;
		if (!slugTouched) fSlug = slugify(value);
	}
	function onSlug(value: string) {
		slugTouched = true;
		fSlug = slugify(value);
	}

	function linkFor(slug: string) {
		return `${base}/${slug}`;
	}

	async function copyLink(entity: Entity) {
		try {
			await navigator.clipboard.writeText(linkFor(entity.slug));
			copiedId = entity.id;
			setTimeout(() => (copiedId = copiedId === entity.id ? null : copiedId), 1500);
		} catch {
			/* ignore */
		}
	}

	async function shareLink(entity: Entity) {
		const url = linkFor(entity.slug);
		if (navigator.share) {
			try {
				await navigator.share({ title: `Payer ${entity.name}`, url });
			} catch {
				/* user cancelled */
			}
		} else {
			await copyLink(entity);
		}
	}

	const inputClass =
		'rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20';
	const labelClass = 'flex flex-col gap-1.5 text-xs font-semibold text-slate-700';
</script>

<svelte:head><title>Entités</title></svelte:head>

<div class="mb-6 flex items-center justify-between">
	<h1 class="text-2xl font-bold">Entités</h1>
	<button
		class="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 font-semibold text-white transition hover:bg-blue-700"
		onclick={openCreate}
	>
		<Plus class="size-4" /> Nouvelle entité
	</button>
</div>

{#if form?.error}
	<p class="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-600">{form.error}</p>
{/if}

<div class="mb-4 flex flex-wrap items-center gap-3">
	<div class="relative flex-1 sm:min-w-72 sm:flex-none">
		<Search class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
		<input
			type="search"
			placeholder="Rechercher (nom, slug)…"
			bind:value={search}
			class="w-full rounded-xl border border-slate-200 bg-white py-2 pr-3 pl-9 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
		/>
	</div>

	<SearchableSelect
		value={statusFilter}
		options={[
			{ value: 'active', label: 'Actives' },
			{ value: 'inactive', label: 'Inactives' }
		]}
		allLabel="Tous les états"
		placeholder="Filtrer par état…"
		icon={CircleCheck}
		onChange={(v) => (statusFilter = v)}
	/>

	<SearchableSelect
		value={modeFilter}
		options={[
			{ value: 'sandbox', label: 'Sandbox' },
			{ value: 'live', label: 'Production' }
		]}
		allLabel="Tous les modes"
		placeholder="Filtrer par mode…"
		icon={SlidersHorizontal}
		onChange={(v) => (modeFilter = v)}
	/>

	<div class="ml-auto flex items-center gap-2">
		<span class="mr-1 text-sm text-slate-400">
			{filteredEntities.length} entité{filteredEntities.length > 1 ? 's' : ''}
		</span>
		<button
			type="button"
			onclick={() => (sortAsc = !sortAsc)}
			title={sortAsc ? 'Nom A→Z' : 'Nom Z→A'}
			class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50"
		>
			{#if sortAsc}<ArrowDownAZ class="size-4" /> A–Z{:else}<ArrowUpAZ class="size-4" /> Z–A{/if}
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
	</div>
</div>

<div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
	{#if filteredEntities.length === 0}
		<p class="py-8 text-center text-slate-400">Aucune entité.</p>
	{:else}
		<table class="w-full min-w-[720px]">
			<thead>
				<tr class="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
					<th class="px-4 py-3 font-medium">Entité</th>
					<th class="px-4 py-3 font-medium">Devise</th>
					<th class="px-4 py-3 font-medium">État</th>
					<th class="px-4 py-3 font-medium">Lien</th>
					<th class="px-4 py-3 text-right font-medium">Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each filteredEntities as entity}
					<tr class="border-b border-slate-100 text-sm">
						<td class="px-4 py-3">
							<div class="flex items-center gap-3">
								{#if entity.logo_url}
									<img class="size-9 rounded-lg object-contain" src={entity.logo_url} alt={entity.name} />
								{:else}
									<div class="grid size-9 place-items-center rounded-lg text-sm font-bold text-white" style="background: {entity.primary_color}">{entity.name.charAt(0)}</div>
								{/if}
								<div>
									<strong class="block">{entity.name}</strong>
									<span class="font-mono text-xs text-slate-400">/{entity.slug}</span>
								</div>
							</div>
						</td>
						<td class="px-4 py-3 font-medium">{entity.currency}</td>
						<td class="px-4 py-3">
							<div class="flex flex-wrap gap-1.5">
								{#if entity.sandbox}<span class="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-700">Sandbox</span>{:else}<span class="rounded-full bg-green-100 px-2 py-0.5 text-xs font-semibold text-green-700">Production</span>{/if}
								{#if !entity.is_active}<span class="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-semibold text-slate-600">Inactive</span>{/if}
							</div>
						</td>
						<td class="px-4 py-3">
							<div class="flex items-center gap-1">
								<button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700" title="Copier le lien" onclick={() => copyLink(entity)}>
									{#if copiedId === entity.id}<Check class="size-4 text-green-600" />{:else}<Copy class="size-4" />{/if}
								</button>
								<button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700" title="Partager" onclick={() => shareLink(entity)}><Share2 class="size-4" /></button>
								<a class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700" title="Ouvrir la page" href={linkFor(entity.slug)} target="_blank" rel="noreferrer"><ExternalLink class="size-4" /></a>
							</div>
						</td>
						<td class="px-4 py-3">
							<div class="flex justify-end gap-2">
								<button class="flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs font-semibold hover:bg-slate-50" onclick={() => openEdit(entity)}><Pencil class="size-3.5" /> Modifier</button>
								<form method="POST" action="?/delete" use:enhance={() => async ({ update }) => { await update(); await invalidateAll(); }}>
									<input type="hidden" name="id" value={entity.id} />
									<button type="submit" class="flex items-center gap-1.5 rounded-lg border border-red-200 px-2.5 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50" onclick={(e) => { if (!confirm(`Supprimer « ${entity.name} » ?`)) e.preventDefault(); }}><Trash2 class="size-3.5" /> Supprimer</button>
								</form>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
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
			class="flex max-h-[90vh] w-full max-w-xl flex-col gap-3.5 overflow-y-auto rounded-2xl bg-white p-7"
			use:enhance={() =>
				async ({ update, result }) => {
					await update();
					if (result.type === 'success') {
						close();
						await invalidateAll();
					}
				}}
		>
			<h2 class="text-lg font-bold">{editing ? 'Modifier' : 'Nouvelle'} entité</h2>
			{#if editing}<input type="hidden" name="id" value={editing.id} />{/if}

			<div class="grid grid-cols-2 gap-3">
				<label class={labelClass}>
					Nom
					<input
						class={inputClass}
						name="name"
						value={fName}
						oninput={(e) => onName(e.currentTarget.value)}
						required
					/>
				</label>
				<label class={labelClass}>
					Slug (lien)
					<input
						class={inputClass}
						name="slug"
						value={fSlug}
						oninput={(e) => onSlug(e.currentTarget.value)}
						placeholder="mon-entite"
						required
					/>
				</label>
			</div>

			<div class="-mt-1 flex items-center gap-1.5 text-xs text-slate-400">
				<Link2 class="size-3.5" />
				<span class="font-mono">{linkFor(fSlug || 'mon-entite')}</span>
			</div>

			<label class={labelClass}>
				Description (affichée sur la page de paiement)
				<textarea
					class="{inputClass} min-h-20 resize-y"
					name="description"
					value={editing?.description ?? ''}
					placeholder="Quelques mots présentant l’entité, le service ou les paiements acceptés…"
				></textarea>
			</label>

			<div class={labelClass}>
				Logo
				<input type="hidden" name="logo_url" value={fLogo} />
				<div class="flex items-center gap-3">
					<div class="grid size-14 shrink-0 place-items-center overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
						{#if fLogo}
							<img src={fLogo} alt="Logo" class="size-full object-contain" />
						{:else}
							<ImagePlus class="size-5 text-slate-300" />
						{/if}
					</div>
					<label
						class="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium hover:bg-slate-50"
					>
						<Upload class="size-4" /> Téléverser
						<input type="file" accept="image/*" class="hidden" onchange={onLogoFile} />
					</label>
					{#if fLogo}
						<button
							type="button"
							class="flex items-center gap-1 text-sm text-red-600 hover:underline"
							onclick={() => (fLogo = '')}
						>
							<X class="size-4" /> Retirer
						</button>
					{/if}
				</div>
				{#if logoError}<span class="text-xs font-normal text-red-600">{logoError}</span>{/if}
				<input
					class="{inputClass} mt-1"
					value={fLogo.startsWith('data:') ? '' : fLogo}
					oninput={(e) => (fLogo = e.currentTarget.value)}
					placeholder="…ou collez une URL https://"
				/>
			</div>

			<div class="grid grid-cols-3 gap-3">
				<label class={labelClass}>
					Couleur primaire
					<input
						class="h-10 rounded-lg border border-slate-200 p-1"
						type="color"
						name="primary_color"
						value={editing?.primary_color ?? '#2563eb'}
					/>
				</label>
				<label class={labelClass}>
					Couleur secondaire
					<input
						class="h-10 rounded-lg border border-slate-200 p-1"
						type="color"
						name="secondary_color"
						value={editing?.secondary_color ?? '#1e293b'}
					/>
				</label>
				<label class={labelClass}>
					Devise
					<input class={inputClass} name="currency" value={editing?.currency ?? 'XOF'} />
				</label>
			</div>

			<label class={labelClass}>
				Clé publique Kkiapay
				<SecretInput name="kkiapay_public_key" value={editing?.kkiapay_public_key ?? ''} icon={KeyRound} required />
			</label>
			<div class="grid grid-cols-2 gap-3">
				<label class={labelClass}>
					Clé privée Kkiapay
					<SecretInput name="kkiapay_private_key" value={editing?.kkiapay_private_key ?? ''} icon={KeyRound} required />
				</label>
				<label class={labelClass}>
					Secret Kkiapay
					<SecretInput name="kkiapay_secret" value={editing?.kkiapay_secret ?? ''} icon={KeyRound} required />
				</label>
			</div>

			<div class="flex gap-6">
				<label class="flex items-center gap-2 text-sm font-medium">
					<input type="checkbox" name="sandbox" checked={editing ? editing.sandbox : true} />
					Mode sandbox
				</label>
				<label class="flex items-center gap-2 text-sm font-medium">
					<input type="checkbox" name="is_active" checked={editing ? editing.is_active : true} />
					Active
				</label>
			</div>

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

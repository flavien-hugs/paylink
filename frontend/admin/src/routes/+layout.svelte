<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import {
		Building2,
		ChartColumn,
		LayoutDashboard,
		LogOut,
		Menu,
		PanelLeftClose,
		PanelLeftOpen,
		Receipt,
		Settings,
		Users,
		X
	} from '@lucide/svelte';
	let { children, data } = $props();

	// Desktop: collapse to an icon rail. Mobile: off-canvas drawer.
	let collapsed = $state(false);
	let mobileOpen = $state(false);

	$effect(() => {
		const saved = localStorage.getItem('admin:sidebar-collapsed');
		if (saved !== null) collapsed = saved === '1';
	});

	function toggle() {
		collapsed = !collapsed;
		localStorage.setItem('admin:sidebar-collapsed', collapsed ? '1' : '0');
	}

	// Close the mobile drawer whenever the route changes.
	$effect(() => {
		$page.url.pathname;
		mobileOpen = false;
	});

	const isSuperadmin = $derived(data.me?.is_superadmin ?? false);

	const navGroups = $derived([
		{
			title: 'Aperçu',
			items: [
				{ href: '/', label: 'Tableau de bord', icon: LayoutDashboard },
				{ href: '/stats', label: 'Statistiques', icon: ChartColumn }
			]
		},
		{
			title: 'Paiements',
			items: [
				{ href: '/transactions', label: 'Transactions', icon: Receipt },
				{ href: '/entities', label: 'Entités', icon: Building2 }
			]
		},
		{
			title: 'Administration',
			items: [
				...(isSuperadmin ? [{ href: '/users', label: 'Utilisateurs', icon: Users }] : []),
				{ href: '/settings', label: 'Paramètres', icon: Settings }
			]
		}
	]);

	function isActive(href: string) {
		return href === '/' ? $page.url.pathname === '/' : $page.url.pathname.startsWith(href);
	}

	// `collapsed` only applies on desktop (md+); the mobile drawer always shows labels.
	const labelHidden = $derived(collapsed ? 'md:hidden' : '');
</script>

{#if data.authenticated}
	<div class="flex min-h-screen">
		<!-- Mobile backdrop -->
		{#if mobileOpen}
			<button
				class="fixed inset-0 z-30 bg-slate-900/50 md:hidden"
				aria-label="Fermer le menu"
				onclick={() => (mobileOpen = false)}
			></button>
		{/if}

		<aside
			class="fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-slate-900 p-3 text-slate-300 transition-transform duration-200
				md:static md:z-auto md:translate-x-0
				{mobileOpen ? 'translate-x-0' : '-translate-x-full'}
				{collapsed ? 'md:w-[76px]' : 'md:w-60'}"
		>
			<div class="mb-4 flex items-center justify-between px-1">
				<div class="px-1 text-lg font-extrabold text-white {labelHidden}">
					Pay<span class="font-medium text-blue-400">Link</span>
				</div>
				<!-- Desktop collapse toggle -->
				<button
					onclick={toggle}
					class="hidden rounded-lg p-2 text-slate-400 transition hover:bg-white/5 hover:text-white md:block {collapsed
						? 'md:mx-auto'
						: ''}"
					aria-label={collapsed ? 'Déplier' : 'Replier'}
					title={collapsed ? 'Déplier' : 'Replier'}
				>
					{#if collapsed}<PanelLeftOpen class="size-5" />{:else}<PanelLeftClose class="size-5" />{/if}
				</button>
				<!-- Mobile close -->
				<button
					onclick={() => (mobileOpen = false)}
					class="rounded-lg p-2 text-slate-400 hover:bg-white/5 hover:text-white md:hidden"
					aria-label="Fermer"
				>
					<X class="size-5" />
				</button>
			</div>

			<nav class="flex flex-1 flex-col gap-1 overflow-y-auto">
				{#each navGroups as group}
					<div
						class="px-3 pt-3 pb-1 text-[11px] font-semibold tracking-wider text-slate-500 uppercase {labelHidden}"
					>
						{group.title}
					</div>
					{#each group.items as item}
						<a
							href={item.href}
							title={item.label}
							class="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition
								{collapsed ? 'md:justify-center' : ''}
								{isActive(item.href) ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/5'}"
						>
							<item.icon class="size-4.5 shrink-0" />
							<span class="truncate {labelHidden}">{item.label}</span>
						</a>
					{/each}
				{/each}
			</nav>

			<form method="POST" action="/logout">
				<button
					type="submit"
					title="Se déconnecter"
					class="flex w-full items-center justify-center gap-2 rounded-xl border border-white/15 py-2.5 text-sm text-slate-300 transition hover:bg-white/5"
				>
					<LogOut class="size-4 shrink-0" />
					<span class={labelHidden}>Se déconnecter</span>
				</button>
			</form>
		</aside>

		<div class="flex min-w-0 flex-1 flex-col">
			<!-- Mobile top bar -->
			<header
				class="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3 md:hidden"
			>
				<button
					onclick={() => (mobileOpen = true)}
					class="rounded-lg p-2 text-slate-600 hover:bg-slate-100"
					aria-label="Ouvrir le menu"
				>
					<Menu class="size-5" />
				</button>
				<span class="text-lg font-extrabold">Pay<span class="font-medium text-blue-600">Link</span></span>
			</header>

			<main class="min-w-0 flex-1 overflow-x-auto px-4 py-6 md:px-10 md:py-8">
				{@render children()}
			</main>
		</div>
	</div>
{:else}
	{@render children()}
{/if}

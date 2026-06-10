<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import {
		Building2,
		ChartColumn,
		LayoutDashboard,
		LogOut,
		PanelLeftClose,
		PanelLeftOpen,
		Receipt,
		Settings,
		Users
	} from '@lucide/svelte';
	let { children, data } = $props();

	let collapsed = $state(false);

	$effect(() => {
		// Restore persisted preference on mount.
		const saved = localStorage.getItem('admin:sidebar-collapsed');
		if (saved !== null) collapsed = saved === '1';
	});

	function toggle() {
		collapsed = !collapsed;
		localStorage.setItem('admin:sidebar-collapsed', collapsed ? '1' : '0');
	}

	// Only the super administrator manages other accounts.
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
				...(isSuperadmin
					? [{ href: '/users', label: 'Utilisateurs', icon: Users }]
					: []),
				{ href: '/settings', label: 'Paramètres', icon: Settings }
			]
		}
	]);

	function isActive(href: string) {
		return href === '/' ? $page.url.pathname === '/' : $page.url.pathname.startsWith(href);
	}
</script>

{#if data.authenticated}
	<div
		class="grid min-h-screen transition-[grid-template-columns] duration-200"
		style="grid-template-columns: {collapsed ? '72px' : '240px'} 1fr"
	>
		<aside class="flex flex-col bg-slate-900 p-3 text-slate-300">
			<div class="mb-4 flex items-center justify-between px-1">
				{#if !collapsed}
					<div class="px-1 text-lg font-extrabold text-white">
						SBBS <span class="font-medium text-blue-400">Payment</span>
					</div>
				{/if}
				<button
					onclick={toggle}
					class="rounded-lg p-2 text-slate-400 transition hover:bg-white/5 hover:text-white {collapsed
						? 'mx-auto'
						: ''}"
					aria-label={collapsed ? 'Déplier' : 'Replier'}
					title={collapsed ? 'Déplier' : 'Replier'}
				>
					{#if collapsed}<PanelLeftOpen class="size-5" />{:else}<PanelLeftClose class="size-5" />{/if}
				</button>
			</div>

			<nav class="flex flex-1 flex-col gap-1 overflow-y-auto">
				{#each navGroups as group, i}
					{#if collapsed}
						{#if i > 0}<div class="my-2 border-t border-white/10"></div>{/if}
					{:else}
						<div class="px-3 pt-3 pb-1 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
							{group.title}
						</div>
					{/if}
					{#each group.items as item}
						<a
							href={item.href}
							title={item.label}
							class="flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition
								{collapsed ? 'justify-center' : ''}
								{isActive(item.href) ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-white/5'}"
						>
							<item.icon class="size-4.5 shrink-0" />
							{#if !collapsed}<span class="truncate">{item.label}</span>{/if}
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
					{#if !collapsed}Se déconnecter{/if}
				</button>
			</form>
		</aside>
		<main class="overflow-x-auto px-10 py-8">{@render children()}</main>
	</div>
{:else}
	{@render children()}
{/if}

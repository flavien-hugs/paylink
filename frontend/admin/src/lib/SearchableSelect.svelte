<script lang="ts">
	import { Building2, Check, ChevronDown, Search } from "@lucide/svelte";
	import type { Component } from "svelte";

	let {
		value = "",
		options,
		allLabel = "Tout",
		placeholder = "Rechercher…",
		icon = Building2,
		onChange,
	}: {
		value?: string;
		options: { value: string; label: string }[];
		allLabel?: string;
		placeholder?: string;
		icon?: Component;
		onChange: (value: string) => void;
	} = $props();

	let open = $state(false);
	let query = $state("");
	let inputEl = $state<HTMLInputElement | null>(null);

	const active = $derived(!!value);
	const selectedLabel = $derived(
		options.find((o) => o.value === value)?.label ?? allLabel,
	);
	const filtered = $derived(
		query.trim()
			? options.filter((o) =>
					o.label.toLowerCase().includes(query.trim().toLowerCase()),
				)
			: options,
	);
	const Icon = $derived(icon);

	function toggle() {
		open = !open;
		if (open) {
			query = "";
			queueMicrotask(() => inputEl?.focus());
		}
	}

	function choose(v: string) {
		onChange(v);
		open = false;
	}
</script>

<div class="relative">
	<button
		type="button"
		onclick={toggle}
		class="flex w-full min-w-52 cursor-pointer items-center gap-2 rounded-lg border py-2.5 pr-3.5 pl-3.5 text-sm font-semibold shadow-sm transition focus:ring-2 focus:ring-blue-500/25 focus:outline-none
			{active
			? 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100'
			: 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'}"
	>
		<Icon
			class="size-4 shrink-0 {active
				? 'text-blue-500'
				: 'text-slate-400'}"
		/>
		<span class="flex-1 truncate text-left">{selectedLabel}</span>
		<ChevronDown
			class="size-4 shrink-0 {active
				? 'text-blue-500'
				: 'text-slate-400'}"
		/>
	</button>

	{#if open}
		<button
			type="button"
			class="fixed inset-0 z-20 cursor-default"
			aria-label="Fermer"
			onclick={() => (open = false)}
		></button>
		<div
			class="absolute z-30 mt-2 w-72 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl"
		>
			<div class="relative border-b border-slate-100 p-2">
				<Search
					class="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-slate-400"
				/>
				<input
					bind:this={inputEl}
					bind:value={query}
					type="search"
					{placeholder}
					class="w-full rounded-lg bg-slate-50 py-2 pr-3 pl-9 text-sm outline-none focus:bg-white focus:ring-2 focus:ring-blue-500/20"
				/>
			</div>
			<ul class="max-h-64 overflow-y-auto p-1.5">
				<li>
					<button
						type="button"
						onclick={() => choose("")}
						class="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-slate-50"
					>
						<span
							class={value === ""
								? "font-semibold text-blue-600"
								: "text-slate-600"}
						>
							{allLabel}
						</span>
						{#if value === ""}<Check
								class="size-4 text-blue-600"
							/>{/if}
					</button>
				</li>
				{#each filtered as o}
					<li>
						<button
							type="button"
							onclick={() => choose(o.value)}
							class="flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-slate-50"
						>
							<span
								class="truncate {value === o.value
									? 'font-semibold text-blue-600'
									: 'text-slate-700'}"
							>
								{o.label}
							</span>
							{#if value === o.value}<Check
									class="size-4 shrink-0 text-blue-600"
								/>{/if}
						</button>
					</li>
				{/each}
				{#if filtered.length === 0}
					<li class="px-3 py-4 text-center text-sm text-slate-400">
						Aucun résultat
					</li>
				{/if}
			</ul>
		</div>
	{/if}
</div>

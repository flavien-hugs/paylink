<script lang="ts">
	import { Eye, EyeOff } from '@lucide/svelte';
	import type { Component } from 'svelte';

	let {
		name,
		value = '',
		placeholder = '',
		required = false,
		icon
	}: {
		name: string;
		value?: string;
		placeholder?: string;
		required?: boolean;
		icon?: Component;
	} = $props();

	let visible = $state(false);
	const Icon = $derived(icon);
</script>

<div class="relative">
	{#if Icon}
		<Icon class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
	{/if}
	<input
		{name}
		{placeholder}
		{required}
		{value}
		type={visible ? 'text' : 'password'}
		autocomplete="off"
		spellcheck="false"
		class="w-full rounded-lg border border-slate-200 py-2 pr-10 font-mono text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 {Icon
			? 'pl-9'
			: 'pl-3'}"
	/>
	<button
		type="button"
		onclick={() => (visible = !visible)}
		class="absolute top-1/2 right-2 -translate-y-1/2 rounded p-1 text-slate-400 hover:text-slate-600"
		aria-label={visible ? 'Masquer' : 'Afficher'}
		title={visible ? 'Masquer' : 'Afficher'}
	>
		{#if visible}
			<EyeOff class="size-4" />
		{:else}
			<Eye class="size-4" />
		{/if}
	</button>
</div>

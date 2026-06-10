<script lang="ts">
	import type { Component } from 'svelte';

	let {
		name,
		type = 'text',
		value = '',
		placeholder = '',
		required = false,
		icon
	}: {
		name: string;
		type?: string;
		value?: string;
		placeholder?: string;
		required?: boolean;
		icon?: Component;
	} = $props();

	const Icon = $derived(icon);
</script>

<div class="relative">
	{#if Icon}
		<Icon class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400" />
	{/if}
	<input
		{name}
		{type}
		{placeholder}
		{required}
		{value}
		class="w-full rounded-lg border border-slate-200 py-2 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 {Icon
			? 'pl-9'
			: 'pl-3'}"
	/>
</div>

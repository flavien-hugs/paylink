<script lang="ts">
	import { STATUS_LABEL } from './format';
	let { status }: { status: 'PENDING' | 'SUCCESS' | 'FAILED' } = $props();

	const styles: Record<string, string> = {
		PENDING: 'bg-amber-100 text-amber-700',
		SUCCESS: 'bg-green-100 text-green-700',
		FAILED: 'bg-red-100 text-red-700'
	};
</script>

<span class="inline-block rounded-full px-2.5 py-0.5 text-xs font-semibold {styles[status]}">
	{STATUS_LABEL[status] ?? status}
</span>

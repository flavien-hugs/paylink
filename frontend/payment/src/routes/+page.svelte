<script lang="ts">
	import { CreditCard } from "@lucide/svelte";
</script>

<div class="grid min-h-screen place-items-center p-6">
	<div
		class="w-full max-w-md rounded-2xl bg-white p-10 text-center shadow-xl shadow-slate-900/5"
	>
		<div
			class="mx-auto mb-5 grid size-14 place-items-center rounded-2xl bg-blue-600 text-white"
		>
			<CreditCard class="size-7" />
		</div>
		<h1 class="mb-2 text-xl font-bold text-slate-900">Page de paiement</h1>
		<p class="text-sm text-slate-500">
			Accédez à la page d’une entité via son identifiant :
			<code class="rounded bg-slate-100 px-1.5 py-0.5 text-slate-700"
				>/&lt;slug&gt;</code
			>
			— par exemple
			<a
				href="/paylink"
				class="font-semibold text-blue-600 hover:underline">/paylink</a
			>.
		</p>
	</div>
</div>

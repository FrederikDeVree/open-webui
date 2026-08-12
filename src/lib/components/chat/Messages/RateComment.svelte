<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { createEventDispatcher, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';

	const i18n = getContext<Writable<i18nType>>('i18n');

	const dispatch = createEventDispatcher();

	export let message;
	export let show = false;

	let comment = '';

	$: if (message) {
		comment = message?.annotation?.comment ?? '';
	}

	const saveHandler = () => {
		if (!comment.trim()) {
			toast.error($i18n.t('Please provide feedback details'));
			return;
		}

		dispatch('save', {
			reason: null,
			comment: comment,
			tags: [],
			details: {}
		});

		toast.success($i18n.t('Thanks for your feedback!'));
		show = false;
	};
</script>

<div
	class="my-2.5 rounded-xl px-4 py-3 border border-gray-100/30 dark:border-gray-850/30"
	id="message-feedback-{message.id}"
>
	<div class="flex justify-between items-center">
		<div class="text-sm font-normal italic">
			{$i18n.t('Feedback will be emailed directly to the AI Server Development team')}
		</div>
		<button
			aria-label={$i18n.t('Close feedback')}
			on:click={() => {
				show = false;
			}}
		>
			<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="size-4">
				<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
			</svg>
		</button>
	</div>

	<div class="mt-2">
		<textarea
			bind:value={comment}
			class="w-full text-sm px-1 py-2 bg-transparent outline-hidden resize-none rounded-xl"
			placeholder={$i18n.t('Please provide your feedback details (required)')}
			aria-label={$i18n.t('Additional feedback comments')}
			rows="3"
		></textarea>
	</div>

	<div class="mt-2 flex justify-end">
		<button
			class="px-3.5 py-1.5 text-sm font-normal bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			on:click={() => {
				saveHandler();
			}}
		>
			{$i18n.t('Send')}
		</button>
	</div>
</div>

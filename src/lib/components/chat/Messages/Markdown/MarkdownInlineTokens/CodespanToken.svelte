<script lang="ts">
	import { copyToClipboard, unescapeHtml } from '$lib/utils';
	import { toast } from 'svelte-sonner';
	import { downloadPyodideFile } from '$lib/utils/pyodide';
	import { downloadTerminalFile, TERMINAL_PATH_RE } from '$lib/utils/terminal';

	import { getContext } from 'svelte';

	import { settings } from '$lib/stores';

	const i18n = getContext('i18n');

	export let token;
	export let done = true;

	$: text = unescapeHtml(token.text ?? '');
	$: isPyodidePath = /^\/mnt\/uploads\//.test(text);
	$: isTerminalPath = !isPyodidePath && TERMINAL_PATH_RE.test(text);
</script>

{#if isPyodidePath}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<span
		class="inline-flex items-center gap-0.5 cursor-pointer text-blue-500 dark:text-blue-400 hover:underline"
		title={text}
		on:click={() =>
			downloadPyodideFile(text).then((ok) => {
				if (!ok) toast.error($i18n.t('Failed to download file'));
			})}
	>
		<code class="{!done && ($settings?.chatFadeStreamingText ?? true) ? 'fade-in-token' : ''}">{text.split('/').pop()}</code>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			viewBox="0 0 16 16"
			fill="currentColor"
			class="size-3 shrink-0 opacity-70"
		>
			<path
				d="M8.75 2.75a.75.75 0 0 0-1.5 0v5.69L5.03 6.22a.75.75 0 0 0-1.06 1.06l3.5 3.5a.75.75 0 0 0 1.06 0l3.5-3.5a.75.75 0 0 0-1.06-1.06L8.75 8.44V2.75Z"
			/>
			<path
				d="M3.5 9.75a.75.75 0 0 0-1.5 0v1.5A2.75 2.75 0 0 0 4.75 14h6.5A2.75 2.75 0 0 0 14 11.25v-1.5a.75.75 0 0 0-1.5 0v1.5c0 .69-.56 1.25-1.25 1.25h-6.5c-.69 0-1.25-.56-1.25-1.25v-1.5Z"
			/>
		</svg>
	</span>
{:else if isTerminalPath}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<span
		class="inline-flex items-center gap-0.5 cursor-pointer text-blue-500 dark:text-blue-400 hover:underline"
		title={text}
		on:click={() =>
			downloadTerminalFile(text).then((ok) => {
				if (!ok) toast.error($i18n.t('Failed to download file'));
			})}
	>
		<code class="{!done && ($settings?.chatFadeStreamingText ?? true) ? 'fade-in-token' : ''}">{text.split('/').pop()}</code>
		<svg
			xmlns="http://www.w3.org/2000/svg"
			viewBox="0 0 16 16"
			fill="currentColor"
			class="size-3 shrink-0 opacity-70"
		>
			<path
				d="M8.75 2.75a.75.75 0 0 0-1.5 0v5.69L5.03 6.22a.75.75 0 0 0-1.06 1.06l3.5 3.5a.75.75 0 0 0 1.06 0l3.5-3.5a.75.75 0 0 0-1.06-1.06L8.75 8.44V2.75Z"
			/>
			<path
				d="M3.5 9.75a.75.75 0 0 0-1.5 0v1.5A2.75 2.75 0 0 0 4.75 14h6.5A2.75 2.75 0 0 0 14 11.25v-1.5a.75.75 0 0 0-1.5 0v1.5c0 .69-.56 1.25-1.25 1.25h-6.5c-.69 0-1.25-.56-1.25-1.25v-1.5Z"
			/>
		</svg>
	</span>
{:else}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
	<code
		class="codespan cursor-pointer {!done && ($settings?.chatFadeStreamingText ?? true)
			? 'fade-in-token'
			: ''}"
		on:click={() => {
			copyToClipboard(text);
			toast.success($i18n.t('Copied to clipboard'));
		}}>{text}</code
	>
{/if}

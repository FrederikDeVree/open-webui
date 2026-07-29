<script lang="ts">
	import DOMPurify from 'dompurify';
	import { toast } from 'svelte-sonner';

	import type { Token } from 'marked';
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	import { WEBUI_BASE_URL } from '$lib/constants';
	import { copyToClipboard, unescapeHtml } from '$lib/utils';
	import { downloadPyodideFile, PYODIDE_DOWNLOAD_SCHEME } from '$lib/utils/pyodide';
	import { downloadTerminalFile, TERMINAL_DOWNLOAD_SCHEME, TERMINAL_PATH_RE } from '$lib/utils/terminal';
	import { terminalServers } from '$lib/stores';

	import Image from '$lib/components/common/Image.svelte';
	import KatexRenderer from './KatexRenderer.svelte';
	import Source from './Source.svelte';
	import HtmlToken from './HTMLToken.svelte';
	import TextToken from './MarkdownInlineTokens/TextToken.svelte';
	import CodespanToken from './MarkdownInlineTokens/CodespanToken.svelte';
	import MentionToken from './MarkdownInlineTokens/MentionToken.svelte';
	import NoteLinkToken from './MarkdownInlineTokens/NoteLinkToken.svelte';
	import SourceToken from './SourceToken.svelte';

	export let id: string;
	export let done = true;
	export let tokens: Token[];
	export let sourceIds = [];
	export let onSourceClick: Function = () => {};

	/**
	 * Check if a URL is a same-origin note link and return the note ID if so.
	 */
	const getNoteIdFromHref = (href: string): string | null => {
		try {
			const url = new URL(href, window.location.origin);
			if (url.origin === window.location.origin) {
				const match = url.pathname.match(/^\/notes\/([^/]+)$/);
				if (match) {
					return match[1];
				}
			}
		} catch {
			// Invalid URL
		}
		return null;
	};

	/**
	 * Handle link clicks - intercept same-origin app URLs for in-app navigation
	 */
	const handleLinkClick = (e: MouseEvent, href: string) => {
		if (href.startsWith(PYODIDE_DOWNLOAD_SCHEME)) {
			e.preventDefault();
			const filePath = href.slice(PYODIDE_DOWNLOAD_SCHEME.length);
			downloadPyodideFile(filePath).then((ok) => {
				if (!ok) toast.error($i18n.t('Failed to download file'));
			});
			return;
		}
		if (href.startsWith(TERMINAL_DOWNLOAD_SCHEME)) {
			e.preventDefault();
			const filePath = href.slice(TERMINAL_DOWNLOAD_SCHEME.length);
			downloadTerminalFile(filePath).then((ok) => {
				if (!ok) toast.error($i18n.t('Failed to download file'));
			});
			return;
		}
		try {
			const url = new URL(href, window.location.origin);
			// Check if the link points to a terminal file path:
			// - same-origin URL whose pathname looks like a terminal file path, or
			// - a URL whose origin matches a known terminal server
			const servers = $terminalServers as Array<{ id: string; url: string; key: string }>;
			const isTerminalServerOrigin = servers.some((s) => {
				try {
					return new URL(s.url).origin === url.origin;
				} catch {
					return false;
				}
			});
			if (
				(url.origin === window.location.origin || isTerminalServerOrigin) &&
				TERMINAL_PATH_RE.test(url.pathname)
			) {
				e.preventDefault();
				downloadTerminalFile(url.pathname).then((ok) => {
					if (!ok) toast.error($i18n.t('Failed to download file'));
				});
				return;
			}
			// Check if same origin and an in-app route
			if (
				url.origin === window.location.origin &&
				(url.pathname.startsWith('/notes/') ||
					url.pathname.startsWith('/c/') ||
					url.pathname.startsWith('/channels/'))
			) {
				e.preventDefault();
				goto(url.pathname + url.search + url.hash);
			}
		} catch {
			// Invalid URL, let browser handle it
		}
	};
</script>

{#each tokens as token, tokenIdx (tokenIdx)}
	{#if token.type === 'escape'}
		{unescapeHtml(token.text)}
	{:else if token.type === 'html'}
		<HtmlToken {id} {token} {onSourceClick} />
	{:else if token.type === 'link'}
		{@const noteId = getNoteIdFromHref(token.href)}
		{@const isPyodideDownload = token.href.startsWith(PYODIDE_DOWNLOAD_SCHEME)}
		{@const isTerminalDownload = token.href.startsWith(TERMINAL_DOWNLOAD_SCHEME)}
		{#if isPyodideDownload}
			{@const filePath = token.href.slice(PYODIDE_DOWNLOAD_SCHEME.length)}
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<span
				class="inline-flex items-center gap-0.5 cursor-pointer text-blue-500 dark:text-blue-400 hover:underline"
				title={filePath}
				on:click={() =>
					downloadPyodideFile(filePath).then((ok) => {
						if (!ok) toast.error($i18n.t('Failed to download file'));
					})}
			>
				{#if token.tokens}
					<svelte:self id={`${id}-a`} tokens={token.tokens} {onSourceClick} {done} />
				{:else}
					{token.text ?? filePath.split('/').pop()}
				{/if}
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
		{:else if isTerminalDownload}
			{@const filePath = token.href.slice(TERMINAL_DOWNLOAD_SCHEME.length)}
			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<!-- svelte-ignore a11y-no-static-element-interactions -->
			<span
				class="inline-flex items-center gap-0.5 cursor-pointer text-blue-500 dark:text-blue-400 hover:underline"
				title={filePath}
				on:click={() =>
					downloadTerminalFile(filePath).then((ok) => {
						if (!ok) toast.error($i18n.t('Failed to download file'));
					})}
			>
				{#if token.tokens}
					<svelte:self id={`${id}-a`} tokens={token.tokens} {onSourceClick} {done} />
				{:else}
					{token.text ?? filePath.split('/').pop()}
				{/if}
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
		{:else if noteId}
			<NoteLinkToken {noteId} href={token.href} />
		{:else if token.tokens}
			<a
				href={token.href}
				target="_blank"
				rel="nofollow"
				title={token.title}
				on:click={(e) => handleLinkClick(e, token.href)}
			>
				<svelte:self id={`${id}-a`} tokens={token.tokens} {onSourceClick} {done} />
			</a>
		{:else}
			<a
				href={token.href}
				target="_blank"
				rel="nofollow"
				title={token.title}
				on:click={(e) => handleLinkClick(e, token.href)}>{token.text}</a
			>
		{/if}
	{:else if token.type === 'image'}
		<Image src={token.href} alt={token.text} allowExternal={true} />
	{:else if token.type === 'strong'}
		<strong><svelte:self id={`${id}-strong`} tokens={token.tokens} {onSourceClick} /></strong>
	{:else if token.type === 'em'}
		<em><svelte:self id={`${id}-em`} tokens={token.tokens} {onSourceClick} /></em>
	{:else if token.type === 'codespan'}
		<CodespanToken {token} {done} />
	{:else if token.type === 'br'}
		<br />
	{:else if token.type === 'del'}
		<del><svelte:self id={`${id}-del`} tokens={token.tokens} {onSourceClick} /></del>
	{:else if token.type === 'inlineKatex'}
		{#if token.text}
			<KatexRenderer content={token.text} displayMode={token?.displayMode ?? false} />
		{/if}
	{:else if token.type === 'iframe'}
		<iframe
			src="{WEBUI_BASE_URL}/api/v1/files/{token.fileId}/content"
			title={token.fileId}
			width="100%"
			frameborder="0"
			on:load={(e) => {
				try {
					e.currentTarget.style.height =
						e.currentTarget.contentWindow.document.body.scrollHeight + 20 + 'px';
				} catch {}
			}}
		></iframe>
	{:else if token.type === 'mention'}
		<MentionToken {token} />
	{:else if token.type === 'footnote'}
		{@html DOMPurify.sanitize(
			`<sup class="footnote-ref footnote-ref-text">${token.escapedText}</sup>`
		) || ''}
	{:else if token.type === 'citation'}
		{#if (sourceIds ?? []).length > 0}
			<SourceToken {id} {token} {sourceIds} onClick={onSourceClick} />
		{:else}
			<TextToken {token} {done} />
		{/if}
	{:else if token.type === 'text'}
		<TextToken {token} {done} />
	{/if}
{/each}

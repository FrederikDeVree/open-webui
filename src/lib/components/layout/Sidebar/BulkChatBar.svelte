<script>
	import { getContext } from 'svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import Bookmark from '$lib/components/icons/Bookmark.svelte';
	import BookmarkSlash from '$lib/components/icons/BookmarkSlash.svelte';
	import Folder from '$lib/components/icons/Folder.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { folders } from '$lib/stores';

	const i18n = getContext('i18n');

	export let count = 0;
	export let allPinned = false;
	export let onDelete = () => {};
	export let onArchive = () => {};
	export let onPin = () => {};
	export let onMove = (folderId) => {};
	export let onClear = () => {};
	export let onSelectAll = () => {};

	function stopClick(event) {
		event.stopPropagation();
	}

	let showFolderMenu = false;
</script>

<div
	class="flex items-center gap-1 px-2 py-1.5 bg-gray-100 dark:bg-gray-900 rounded-xl shrink-0 mx-0.5 border border-gray-200/60 dark:border-gray-800/60"
>
	<span class="text-xs font-medium text-gray-500 dark:text-gray-400 flex-1 truncate select-none cursor-pointer" on:click={onSelectAll}>
		{count} {count === 1 ? $i18n.t('chat selected') : $i18n.t('chats selected')}
	</span>

	<Tooltip content={$i18n.t('Delete selected')}>
		<button
			class="p-1 rounded transition text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-gray-200/60 dark:hover:bg-gray-800"
			on:click={onDelete}
		>
			<GarbageBin className="size-3.5" strokeWidth="2" />
		</button>
	</Tooltip>

	<Tooltip content={$i18n.t('Archive selected')}>
		<button
			class="p-1 rounded transition text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200/60 dark:hover:bg-gray-800"
			on:click={onArchive}
		>
			<ArchiveBox className="size-3.5" strokeWidth="2" />
		</button>
	</Tooltip>

	<Tooltip content={$i18n.t(allPinned ? 'Unpin selected' : 'Pin selected')}>
		<button
			class="p-1 rounded transition text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200/60 dark:hover:bg-gray-800"
			on:click={onPin}
		>
			{#if allPinned}
				<BookmarkSlash className="size-3.5" strokeWidth="2" />
			{:else}
				<Bookmark className="size-3.5" strokeWidth="2" />
			{/if}
		</button>
	</Tooltip>

	{#if $folders && $folders.length > 0}
		<div class="relative z-10">
			<Tooltip content={$i18n.t('Move selected')}>
				<button
					class="p-1 rounded transition text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200/60 dark:hover:bg-gray-800"
					on:click={() => { showFolderMenu = !showFolderMenu; }}
					aria-label={$i18n.t('Move selected')}
				>
					<Folder className="size-3.5" strokeWidth="2" />
				</button>
			</Tooltip>

			{#if showFolderMenu && count > 0}
				<div
					class="absolute right-0 top-8 z-[60] w-48 rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-gray-900 shadow-lg py-0.5 overflow-hidden"
					on:click={stopClick}
				>
					<button
						class="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
						on:click={() => {
							onMove(null);
							showFolderMenu = false;
						}}
					>
						<Folder className="size-3.5" />
						<span>{$i18n.t('No Folder')}</span>
					</button>
					{#each $folders as folder}
						<button
							class="flex items-center gap-2 w-full px-3 py-1.5 text-xs text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
							on:click={() => {
								onMove(folder.id);
								showFolderMenu = false;
							}}
						>
							<Folder className="size-3.5" />
							{folder.name}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	{/if}

	<Tooltip content={$i18n.t('Deselect all')}>
		<div
			class="flex items-center justify-center size-4 rounded-full text-gray-400 dark:text-gray-500 hover:bg-gray-200/60 dark:hover:bg-gray-800 transition shrink-0 cursor-pointer"
			on:click={onClear}
		>
			<svg class="size-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12" fill="currentColor">
				<path d="M3 1l6 6M9 1L3 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
			</svg>
		</div>
	</Tooltip>
</div>

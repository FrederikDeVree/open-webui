<script lang="ts">
	import { getContext, createEventDispatcher, onMount } from 'svelte';
	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	import { toast } from 'svelte-sonner';

	import { bulkArchiveChats, bulkDeleteChats, bulkMoveChats } from '$lib/apis/chats';
	import {
		chats,
		pinnedChats,
		currentChatPage,
		folders as foldersStore,
		selectedFolder
	} from '$lib/stores';
	import { getChatList, getPinnedChatList } from '$lib/apis/chats';

	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Folder from '$lib/components/icons/Folder.svelte';
	import XMark from '$lib/components/icons/XMark.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	export let chatIds: Set<string> = new Set();
	export let onClear: () => void = () => {};

	let showDeleteConfirm = false;
	let showFolderPicker = false;
	let deleting = false;
	let archiving = false;
	let allFolders: Record<string, unknown>[] = [];

	const t = (key: string, params?: Record<string, unknown>) => i18n.t(key, params);

	const archiveHandler = async () => {
		if (archiving || chatIds.size === 0) return;
		archiving = true;

		const ids = Array.from(chatIds);
		try {
			await bulkArchiveChats(localStorage.token, ids);
			toast.success(t('{{COUNT}} chats archived.', { COUNT: ids.length }));
			await refreshChats();
			onClear();
		} catch (error) {
			console.error('Error archiving chats:', error);
			toast.error(t('Failed to archive chats.'));
		} finally {
			archiving = false;
		}
	};

	const deleteHandler = async () => {
		if (deleting || chatIds.size === 0) return;
		deleting = true;

		const ids = Array.from(chatIds);
		try {
			await bulkDeleteChats(localStorage.token, ids);
			toast.success(t('{{COUNT}} chats deleted.', { COUNT: ids.length }));
			await refreshChats();
			onClear();
		} catch (error) {
			console.error('Error deleting chats:', error);
			toast.error(t('Failed to delete chats.'));
		} finally {
			deleting = false;
		}
	};

	const moveHandler = async (folderId: string | null) => {
		if (chatIds.size === 0) return;

		const ids = Array.from(chatIds);
		try {
			await bulkMoveChats(localStorage.token, ids, folderId);
			toast.success(t('{{COUNT}} chats moved.', { COUNT: ids.length }));
			await refreshChats();
			onClear();
		} catch (error) {
			console.error('Error moving chats:', error);
			toast.error(t('Failed to move chats.'));
		}
	};

	const refreshChats = async () => {
		await selectedFolder.set(null);
		currentChatPage.set(1);
		await chats.set(await getChatList(localStorage.token, 1));
		await pinnedChats.set(await getPinnedChatList(localStorage.token));
		dispatch('refresh');
	};

	const deleteCount = chatIds.size;

	onMount(() => {
		allFolders = $foldersStore ?? [];
		return foldersStore.subscribe((val) => {
			allFolders = val ?? [];
		});
	});
</script>

<ConfirmDialog
	bind:show={showDeleteConfirm}
	title={t('Delete {{COUNT}} chats?', { COUNT: deleteCount })}
	on:confirm={deleteHandler}
>
	<div class="text-sm text-gray-500">
		{t('Are you sure you want to delete {{COUNT}} chats? This action cannot be undone.', {
			COUNT: deleteCount
		})}
	</div>
</ConfirmDialog>

<!-- Batch action bar - visible when 1+ chats selected -->
{#if chatIds.size > 0}
	<div
		class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 rounded-2xl border border-gray-200 dark:border-gray-700 bg-white/90 dark:bg-gray-850/90 backdrop-blur-xl shadow-xl px-3 py-2 text-sm"
	>
		<!-- Selection count badge -->
		<div class="flex items-center gap-1.5 px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-lg">
			<span class="font-semibold text-gray-800 dark:text-gray-200">{chatIds.size}</span>
			<span class="text-gray-500 dark:text-gray-400 text-xs">{t('selected')}</span>
		</div>

		<!-- Divider -->
		<div class="w-px h-5 bg-gray-200 dark:bg-gray-700"></div>

		<!-- Archive button -->
		<Tooltip content={t('Archive')}>
			<button
				class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition disabled:opacity-50 text-gray-600 dark:text-gray-300"
				on:click={archiveHandler}
				disabled={archiving}
				type="button"
			>
				<ArchiveBox className="size-4" strokeWidth="2" />
			</button>
		</Tooltip>

		<!-- Delete button -->
		<Tooltip content={t('Delete')}>
			<button
				class="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition disabled:opacity-50 text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
				on:click={() => {
					showDeleteConfirm = true;
				}}
				disabled={deleting}
				type="button"
			>
				<GarbageBin className="size-4" strokeWidth="2" />
			</button>
		</Tooltip>

		<!-- Move to folder button -->
		<Tooltip content={t('Move to folder')}>
			<button
				class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition disabled:opacity-50 text-gray-600 dark:text-gray-300"
				on:click={() => {
					showFolderPicker = !showFolderPicker;
				}}
				type="button"
			>
				<Folder className="size-4" strokeWidth="2" />
			</button>
		</Tooltip>

		<!-- Move dropdown -->
		{#if showFolderPicker}
			<div
				class="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-50 py-1"
			>
				<button
					class="w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-200"
					on:click={() => {
						moveHandler(null);
						showFolderPicker = false;
					}}
				>
					<Folder className="size-3.5 shrink-0" strokeWidth="2" />
					<span>{t('Clear folder')}</span>
				</button>
				{#each allFolders as folder}
					<button
						class="w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-700 dark:text-gray-200 truncate"
						on:click={() => {
							moveHandler(folder.id as string);
							showFolderPicker = false;
						}}
					>
						<Folder className="size-3.5 shrink-0" strokeWidth="2" />
						<span class="truncate">{folder.name}</span>
					</button>
				{/each}
			</div>
		{/if}

		<!-- Clear selection button -->
		<Tooltip content={t('Clear selection')} className="ml-1">
			<button
				class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
				on:click={onClear}
				type="button"
			>
				<XMark className="size-4" strokeWidth="2" />
			</button>
		</Tooltip>
	</div>
{/if}

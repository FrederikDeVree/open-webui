<script context="module" lang="ts">
	const invisibleDragImage = new Image();
	invisibleDragImage.src =
		'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
</script>

<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { goto } from '$app/navigation';
	import { onMount, getContext, createEventDispatcher, tick } from 'svelte';
	const i18n = getContext('i18n');

	const dispatch = createEventDispatcher();

	import {
		archiveChatById,
		cloneChatById,
		deleteChatById,
		getAllTags,
		getChatById,
		getChatList,
		getPinnedChatList,
		updateChatById,
		updateChatFolderIdById
	} from '$lib/apis/chats';
	import {
		chatId,
		chatTitle as _chatTitle,
		chats,
		mobile,
		pinnedChats,
		showSidebar,
		currentChatPage,
		tags,
		selectedFolder,
		activeChatIds
	} from '$lib/stores';

	import ChatMenu from './ChatMenu.svelte';
	import DeleteConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import ShareChatModal from '$lib/components/chat/ShareChatModal.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ArchiveBox from '$lib/components/icons/ArchiveBox.svelte';
	import DragGhost from '$lib/components/common/DragGhost.svelte';
	import Check from '$lib/components/icons/Check.svelte';
	import Document from '$lib/components/icons/Document.svelte';
	import Sparkles from '$lib/components/icons/Sparkles.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { generateTitle } from '$lib/apis';
	import { createMessagesList } from '$lib/utils';

	export let className = '';
	export let id;
	export let title;
	export let createdAt: number | null = null;
	export let updatedAt: number | null = null;
	export let lastReadAt: number | null = null;
	export let selected = false;
	export let shiftKey = false;
	export let checkboxMode = false;
	export let isSelected = false;
	export let onDragEnd = () => {};

	function formatTimeAgo(timestamp: number): string {
		const now = Date.now();
		const diff = now - timestamp * 1000;
		const seconds = Math.floor(diff / 1000);
		const minutes = Math.floor(seconds / 60);
		const hours = Math.floor(minutes / 60);
		const days = Math.floor(hours / 24);
		const weeks = Math.floor(days / 7);
		const years = Math.floor(days / 365);
		if (years > 0) return $i18n.t('{{COUNT}}y', { COUNT: years, context: 'time_ago' });
		if (weeks > 0) return $i18n.t('{{COUNT}}w', { COUNT: weeks, context: 'time_ago' });
		if (days > 0) return $i18n.t('{{COUNT}}d', { COUNT: days, context: 'time_ago' });
		if (hours > 0) return $i18n.t('{{COUNT}}h', { COUNT: hours, context: 'time_ago' });
		if (minutes > 0) return $i18n.t('{{COUNT}}m', { COUNT: minutes, context: 'time_ago' });
		return $i18n.t('1m', { context: 'time_ago' });
	}

	let chat = null;
	let mouseOver = false;
	let viewedAt: number | null = null;
	let checkboxClicked = false;

	$: if (id === $chatId) {
		viewedAt = updatedAt ?? Date.now() / 1000;
	}
	$: effectiveReadAt = Math.max(lastReadAt ?? 0, viewedAt ?? 0) || null;
	$: unread =
		id !== $chatId && !$activeChatIds.has(id) &&
		(effectiveReadAt === null || (updatedAt !== null && updatedAt > effectiveReadAt));

	let showShareChatModal = false;
	let confirmEdit = false;
	let chatTitle = title;

	const editChatTitle = async (id, newTitle) => {
		if (newTitle === '') { toast.error($i18n.t('Title cannot be an empty string.')); return; }
		await updateChatById(localStorage.token, id, { title: newTitle });
		if (id === $chatId) _chatTitle.set(newTitle);
		currentChatPage.set(1);
		await chats.set(await getChatList(localStorage.token, $currentChatPage));
		await pinnedChats.set(await getPinnedChatList(localStorage.token));
		dispatch('change');
	};

	const cloneChatHandler = async (id) => {
		const res = await cloneChatById(localStorage.token, id, $i18n.t('Clone of {{TITLE}}', { TITLE: title })).catch((e) => { toast.error(e); return null; });
		if (res) {
			goto(`/c/${res.id}`);
			currentChatPage.set(1);
			await chats.set(await getChatList(localStorage.token, $currentChatPage));
			await pinnedChats.set(await getPinnedChatList(localStorage.token));
		}
	};

	let deleting = false;
	const deleteChatHandler = async (id) => {
		if (deleting) return;
		deleting = true;
		const res = await deleteChatById(localStorage.token, id).catch((e) => { toast.error(e); return null; });
		if (res) {
			tags.set(await getAllTags(localStorage.token));
			if ($chatId === id) { await goto('/'); chatId.set(''); await tick(); }
			dispatch('change');
		}
		deleting = false;
	};

	let archiving = false;
	const archiveChatHandler = async (id) => {
		if (archiving) return;
		archiving = true;
		try {
			await archiveChatById(localStorage.token, id);
			if ($chatId === id) { await goto('/'); chatId.set(''); }
			dispatch('change');
			toast.success($i18n.t('Chat archived.'));
		} catch (e) { toast.error($i18n.t('Failed to archive chat.')); }
		finally { archiving = false; }
	};

	const moveChatHandler = async (cId, folderId) => {
		if (cId && folderId) {
			const res = await updateChatFolderIdById(localStorage.token, cId, folderId).catch((e) => { toast.error(e); return null; });
			if (res) {
				currentChatPage.set(1);
				await chats.set(await getChatList(localStorage.token, $currentChatPage));
				await pinnedChats.set(await getPinnedChatList(localStorage.token));
				dispatch('change');
				toast.success($i18n.t('Chat moved successfully'));
			}
		} else { toast.error($i18n.t('Failed to move chat')); }
	};

	let itemElement;
	let generating = false;
	let doubleClicked = false;
	let dragged = false;
	let x = 0, y = 0;

	const onDragStart = (event) => {
		event.stopPropagation();
		event.dataTransfer.setDragImage(invisibleDragImage, 0, 0);
		event.dataTransfer.setData('text/plain', JSON.stringify({ type: 'chat', id: id }));
		dragged = true;
		itemElement.style.opacity = '0.5';
	};
	const onDrag = (event) => { event.stopPropagation(); x = event.clientX; y = event.clientY; };
	const onDragEndHandler = (event) => { event.stopPropagation(); itemElement.style.opacity = '1'; dragged = false; onDragEnd(event); };

	const onClickOutside = (event) => {
		if (!itemElement.contains(event.target) && confirmEdit) {
			if (chatTitle !== title) editChatTitle(id, chatTitle);
			confirmEdit = false; chatTitle = '';
		}
	};

	onMount(() => {
		const el = itemElement; if (!el) return;
		document.addEventListener('click', onClickOutside, true);
		el.addEventListener('dragstart', onDragStart);
		el.addEventListener('drag', onDrag);
		el.addEventListener('dragend', onDragEndHandler);
		return () => {
			document.removeEventListener('click', onClickOutside, true);
			el.removeEventListener('dragstart', onDragStart);
			el.removeEventListener('drag', onDrag);
			el.removeEventListener('dragend', onDragEndHandler);
		};
	});

	let showDeleteConfirm = false;
	const chatTitleInputKeydownHandler = (e) => {
		if (e.key === 'Enter') { e.preventDefault(); setTimeout(() => { const input = document.getElementById(`chat-title-input-${id}`); input?.blur(); }, 0); }
		else if (e.key === 'Escape') { e.preventDefault(); confirmEdit = false; chatTitle = ''; }
	};

	const renameHandler = async () => {
		chatTitle = title; confirmEdit = true;
		await tick();
		setTimeout(() => { const input = document.getElementById(`chat-title-input-${id}`); input?.focus?.(); input?.select?.(); }, 0);
	};

	const generateTitleHandler = async () => {
		generating = true;
		chat = await getChatById(localStorage.token, id);
		const history = chat?.chat?.history;
		let messages = [];
		if (history?.messages && history?.currentId) {
			messages = createMessagesList(history, history.currentId).map((m) => ({ role: m.role, content: m.content }));
		} else {
			messages = (chat?.chat?.messages ?? []).map((m) => ({ role: m.role, content: m.content }));
		}
		let model = id === $chatId ? (JSON.parse(sessionStorage.selectedModels || '[]').find((m) => m) ?? '') : '';
		if (!model && history?.messages && history?.currentId) {
			let cid = history.currentId;
			while (cid) { const msg = history.messages[cid]; if (!msg) break; if (msg.role === 'assistant' && msg.model) { model = msg.model; break; } cid = msg.parentId; }
		}
		if (!model) model = chat?.chat?.models?.[0] ?? '';
		chatTitle = '';
		const generatedTitle = await generateTitle(localStorage.token, model, messages).catch((e) => { toast.error(e); return null; });
		if (generatedTitle) { if (generatedTitle !== title) editChatTitle(id, generatedTitle); confirmEdit = false; }
		else { chatTitle = title; }
		generating = false;
	};
</script>

<ShareChatModal bind:show={showShareChatModal} chatId={id} />
<DeleteConfirmDialog bind:show={showDeleteConfirm} title={$i18n.t('Delete chat?')} on:confirm={() => deleteChatHandler(id)}>
	<div class=" text-sm text-gray-500 flex-1 line-clamp-3">{$i18n.t('This will delete')} <span class=" font-semibold">{title}</span>.</div>
</DeleteConfirmDialog>

{#if dragged && x && y}
	<DragGhost {x} {y}>
		<div class=" bg-black/80 backdrop-blur-2xl px-2 py-1 rounded-lg w-fit max-w-40">
			<div class="flex items-center gap-1"><Document className=" size-[18px]" strokeWidth="2" /><div class=" text-xs text-white line-clamp-1">{title}</div></div>
		</div>
	</DragGhost>
{/if}

<div id="sidebar-chat-group" bind:this={itemElement} class=" w-full {className} relative group" draggable={!confirmEdit}>
	{#if confirmEdit}
		<div class=" w-full flex justify-between rounded-xl px-[11px] py-[6px] {id === $chatId || confirmEdit ? 'bg-gray-100 dark:bg-gray-900 selected' : selected ? 'bg-gray-100 dark:bg-gray-950 selected' : 'group-hover:bg-gray-100 dark:group-hover:bg-gray-950'} whitespace-nowrap text-ellipsis relative {generating ? 'cursor-not-allowed' : ''}">
			<input id="chat-title-input-{id}" bind:value={chatTitle} class=" bg-transparent w-full outline-hidden mr-10" placeholder={generating ? $i18n.t('Generating...') : ''} disabled={generating} on:keydown={chatTitleInputKeydownHandler} on:blur={async (e) => { if (doubleClicked) { e.preventDefault(); e.stopPropagation(); await tick(); setTimeout(() => { document.getElementById(`chat-title-input-${id}`)?.focus(); }, 0); doubleClicked = false; return; } }} />
		</div>
	{:else}
		<div class="w-full flex items-center">
			<!-- Checkbox -->
			<button
				class="flex items-center justify-center w-7 h-7 shrink-0 ml-1 mr-0.5 z-10 rounded hover:bg-gray-200 dark:hover:bg-gray-800 transition opacity-0 group-hover:opacity-100 focus:opacity-100 cursor-pointer"
				class:opacity-100={checkboxMode}
				on:click={(e) => {
					e.preventDefault();
					e.stopPropagation();
					checkboxClicked = true;
					dispatch('toggleSelect', { id });
				}}
				aria-label="Select chat"
				type="button"
			>
				<div class="w-4 h-4 rounded flex items-center justify-center border-2 transition-colors"
					class:border-gray-300 dark:border-gray-600={!isSelected}
					class:!border-blue-500={isSelected}
					class:bg-transparent={!isSelected}
					class:bg-blue-500={isSelected}
				>
					{#if isSelected}
						<Check className="w-3 h-3 text-white" strokeWidth="3" />
					{/if}
				</div>
			</button>

			<a
				id="sidebar-chat-item"
				class="w-full flex justify-between rounded-xl px-[11px] py-[6px] {id === $chatId || confirmEdit ? 'bg-gray-100 dark:bg-gray-900 selected' : selected ? 'bg-gray-100 dark:bg-gray-950 selected' : ' group-hover:bg-gray-100 dark:group-hover:bg-gray-950'} whitespace-nowrap text-ellipsis"
				href="/c/{id}"
				on:click={(e) => {
					if (checkboxMode && checkboxClicked) { checkboxClicked = false; return; }
					if (checkboxMode) {
						e.preventDefault();
						if (e.shiftKey) { dispatch('shiftClick', { id }); }
						else { dispatch('toggleSelect', { id }); }
						return;
					}
					dispatch('select');
					if ($selectedFolder) selectedFolder.set(null);
					if ($mobile) showSidebar.set(false);
					unread = false;
					lastReadAt = Date.now() / 1000;
				}}
				on:dblclick={async (e) => {
					if (checkboxMode) return;
					e.preventDefault(); e.stopPropagation(); doubleClicked = true; renameHandler();
				}}
				on:mouseenter={() => { mouseOver = true; }}
				on:mouseleave={() => { mouseOver = false; }}
				on:focus={() => {}}
				draggable="false"
			>
				{#if $activeChatIds.has(id)}
					<div class="shrink-0 self-center pr-2"><Spinner className="size-3" /></div>
				{/if}
				<div class="flex self-center flex-1 w-full min-w-0">
					{#if unread}
						<div class="shrink-0 self-center pr-2.5 flex transition-opacity duration-300"><div class="size-1.5 bg-sky-500 rounded-full" /></div>
					{/if}
					<div dir="auto" class="text-left self-center overflow-hidden w-full h-[20px] truncate {unread ? 'font-medium text-gray-900 dark:text-gray-100' : ''}">{title}</div>
				</div>
				{#if createdAt && !mouseOver}
					<div class="shrink-0 self-center text-[10px] text-gray-400 dark:text-gray-500 pl-2">{formatTimeAgo(createdAt)}</div>
				{/if}
			</a>
		</div>
	{/if}

	<!-- Menu button (right side) -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		id="sidebar-chat-item-menu"
		class="
        {id === $chatId || confirmEdit ? 'from-gray-100 dark:from-gray-900 selected' : selected ? 'from-gray-100 dark:from-gray-950 selected' : 'invisible group-hover:visible from-gray-100 dark:from-gray-950'}
            absolute {className === 'pr-2' ? 'right-[8px]' : 'right-1'} top-[4px] py-1 pr-0.5 mr-1.5 pl-5 bg-linear-to-l from-80% to-transparent"
		on:mouseenter={() => { mouseOver = true; }}
		on:mouseleave={() => { mouseOver = false; }}
	>
		{#if confirmEdit}
			<div class="flex self-center items-center space-x-1.5 z-10 translate-y-[0.5px] -translate-x-[0.5px]">
				<Tooltip content={$i18n.t('Generate')}><button class=" self-center dark:hover:text-white transition disabled:cursor-not-allowed" id="generate-title-button" disabled={generating} on:click={() => generateTitleHandler()}><Sparkles strokeWidth="2" /></button></Tooltip>
			</div>
		{:else if shiftKey && mouseOver && !checkboxMode}
			<div class=" flex items-center self-center space-x-1.5">
				<Tooltip content={$i18n.t('Archive')} className="flex items-center">
					<button class=" self-center dark:hover:text-white transition disabled:cursor-not-allowed" disabled={archiving} on:click={() => archiveChatHandler(id)} type="button"><ArchiveBox className="size-4  translate-y-[0.5px]" strokeWidth="2" /></button>
				</Tooltip>
				<Tooltip content={$i18n.t('Delete')}>
					<button class=" self-center dark:hover:text-white transition disabled:cursor-not-allowed" disabled={deleting} on:click={() => deleteChatHandler(id)} type="button"><GarbageBin strokeWidth="2" /></button>
				</Tooltip>
			</div>
		{:else}
			<div class="flex self-center z-10 items-end">
				<ChatMenu chatId={id} cloneChatHandler={() => cloneChatHandler(id)} shareHandler={() => { showShareChatModal = true; }} {moveChatHandler} archiveChatHandler={() => archiveChatHandler(id)} {renameHandler} deleteHandler={() => { showDeleteConfirm = true; }} onClose={() => dispatch('unselect')} onPinChange={async () => dispatch('change')}>
					<button aria-label="Chat Menu" class=" self-center dark:hover:text-white transition m-0" on:click={() => dispatch('select')}>
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4"><path d="M2 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM6.5 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM12.5 6.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z"/></svg>
					</button>
				</ChatMenu>
				{#if id === $chatId}
					<button id="delete-chat-button" class="hidden" on:click={() => { showDeleteConfirm = true; }}>
						<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4"><path d="M2 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM6.5 8a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0ZM12.5 6.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3Z"/></svg>
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>

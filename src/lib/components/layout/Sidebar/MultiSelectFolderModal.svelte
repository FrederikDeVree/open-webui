<script lang="ts">
	import { getContext } from 'svelte';
	import { folders } from '$lib/stores';
	import Modal from '$lib/components/common/Modal.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let chatIds: string[] = [];
	export let onSubmit: (folderId: string | null) => void = () => {};

	let selectedFolderId: string | null = null;

	const submitHandler = () => {
		onSubmit(selectedFolderId);
	};
</script>

<Modal
	{show}
	onClose={() => {
		show = false;
		selectedFolderId = null;
	}}
>
	<div class="p-4 w-full max-w-sm">
		<h2 class="text-lg font-semibold mb-3">{$i18n.t('Move to folder')}</h2>
		<p class="text-sm text-gray-500 mb-3">
			{chatIds.length + ' ' + $i18n.t('chats selected')}
		</p>

		<!-- "No folder" option -->
		<label
			class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition"
		>
			<input
				type="radio"
				name="folder"
				checked={selectedFolderId === null}
				on:change={() => {
					selectedFolderId = null;
				}}
				class="accent-sky-500"
			/>
			<span class="text-sm">{$i18n.t('No folder (root)')}</span>
		</label>

		<!-- Folder options -->
		{#each $folders as folder (folder.id)}
			<label
				class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition"
			>
				<input
					type="radio"
					name="folder"
					checked={selectedFolderId === folder.id}
					on:change={() => {
						selectedFolderId = folder.id;
					}}
					class="accent-sky-500"
				/>
				<span class="text-sm truncate">{folder.name}</span>
			</label>
		{/each}

		<div class="flex gap-2 mt-4 justify-end">
			<button
				class="px-4 py-2 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
				on:click={() => {
					show = false;
					selectedFolderId = null;
				}}
			>
				{$i18n.t('Cancel')}
			</button>
			<button
				class="px-4 py-2 rounded-lg text-sm font-medium bg-sky-500 text-white hover:bg-sky-600 transition"
				on:click={submitHandler}
			>
				{$i18n.t('Move')}
			</button>
		</div>
	</div>
</Modal>

<script lang="ts">
	import { decode } from 'html-entities';
	import Collapsible from '$lib/components/common/Collapsible.svelte';
	import ToolCallDisplay from '$lib/components/common/ToolCallDisplay.svelte';
	import SvgPanZoom from '$lib/components/common/SVGPanZoom.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import { settings } from '$lib/stores';
	import { getContext } from 'svelte';

	const i18n = getContext('i18n');

	import Markdown from './Markdown.svelte';
	import ConsecutiveDetailsGroup from './Markdown/ConsecutiveDetailsGroup.svelte';
	import {
		buildOutputDisplayItems,
		type OutputDetailToken,
		type OutputDisplayItem,
		type OutputItem
	} from './structuredOutput';

	export let id = '';
	export let output: OutputItem[] = [];
	export let done = true;
	export let model = null;
	export let save = false;
	export let preview = false;
	export let compactPreview = false;
	export let renderMarkdown = true;
	export let editCodeBlock = true;
	export let topPadding = false;
	export let sourceIds: string[] = [];
	export let formatMessageContent: (content: string) => string = (content) => content;
	export let onSave: any = () => {};
	export let onSourceClick: any = () => {};
	export let onTaskClick: any = () => {};
	export let onUpdate: any = () => {};
	export let onPreview: any = () => {};

	const getDetailTitle = (detailToken: OutputDetailToken): any => detailToken.summary;
	const getDetailAttributes = (detailToken: OutputDetailToken): any => detailToken.attributes;

	$: detailButtonClassName = `w-fit py-0.5 ${
		compactPreview ? 'text-xs' : 'text-[0.9375rem]'
	} text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition`;

	$: displayItems = buildOutputDisplayItems(output) as OutputDisplayItem[];
</script>

{#each displayItems as displayItem (displayItem.id)}
	{#if displayItem.type === 'message'}
		{#if renderMarkdown}
			<div class="markdown-prose">
				<Markdown
					id={`${id}-${displayItem.id}`}
					content={formatMessageContent(displayItem.text)}
					{model}
					{save}
					{preview}
					{compactPreview}
					{done}
					{editCodeBlock}
					{topPadding}
					{sourceIds}
					{onSourceClick}
					{onTaskClick}
					{onSave}
					{onUpdate}
					{onPreview}
				/>
			</div>
		{:else}
			<div class="whitespace-pre-wrap text-[0.9375rem]">{displayItem.text}</div>
		{/if}
	{:else if displayItem.type === 'detail_group'}
		<ConsecutiveDetailsGroup
			id={`${id}-${displayItem.id}`}
			tokens={displayItem.tokens}
			messageDone={done}
			{compactPreview}
		>
			<div slot="content">
				{#each displayItem.tokens as detailToken, detailIndex}
					{#if detailToken.attributes?.type === 'tool_calls'}
						<ToolCallDisplay
							id={`${id}-${displayItem.id}-${detailIndex}-tool-call`}
							attributes={detailToken.attributes}
							resultContent={detailToken.text}
							grouped={true}
							open={$settings?.expandDetails ?? false}
							className="w-full"
							buttonClassName={detailButtonClassName}
						/>
					{:else if detailToken.attributes?.type === 'diagram_renderer'}
						{@const drDone = detailToken.attributes?.done === 'true'}
						{@const drSvg = decode(detailToken.attributes?.svg ?? '')}
						{@const drError = decode(detailToken.attributes?.error ?? '')}
						<div class="w-full">
							{#if !drDone}
								<div class="flex items-center gap-2 text-gray-500 py-1">
									<Spinner className="size-4" />
									<span class="text-sm shimmer">{$i18n.t('Drawing diagram…')}</span>
								</div>
							{:else if drSvg}
								<SvgPanZoom className="rounded-2xl max-h-fit overflow-hidden" svg={drSvg} />
							{:else if drError}
								<div
									class="flex gap-2.5 border px-4 py-3 border-red-600/10 bg-red-600/10 rounded-2xl"
								>
									{$i18n.t('Failed to render diagram')}: {drError}
								</div>
							{/if}
						</div>
					{:else if detailToken.text?.length > 0}
						<Collapsible
							title={getDetailTitle(detailToken)}
							open={$settings?.expandDetails ?? false}
							attributes={getDetailAttributes(detailToken)}
							messageDone={done}
							className="w-full"
							buttonClassName={detailButtonClassName}
						>
							<div class="mb-1.5" slot="content">
								<div class="markdown-prose">
									<Markdown
										id={`${id}-${displayItem.id}-${detailIndex}-detail`}
										content={detailToken.text}
										{done}
										{preview}
										{compactPreview}
										{editCodeBlock}
									/>
								</div>
							</div>
						</Collapsible>
					{:else}
						<Collapsible
							title={getDetailTitle(detailToken)}
							open={false}
							disabled={true}
							attributes={getDetailAttributes(detailToken)}
							messageDone={done}
							className="w-full"
							buttonClassName={detailButtonClassName}
						/>
					{/if}
				{/each}
			</div>
		</ConsecutiveDetailsGroup>
	{:else}
		{@const detailToken = displayItem.token}
		{#if detailToken.attributes?.type === 'tool_calls'}
			<ToolCallDisplay
				id={`${id}-${displayItem.id}-tool-call`}
				attributes={detailToken.attributes}
				resultContent={detailToken.text}
				open={$settings?.expandDetails ?? false}
				className="w-full space-y-2"
				buttonClassName={detailButtonClassName}
			/>
		{:else if detailToken.attributes?.type === 'diagram_renderer'}
			{@const drDone = detailToken.attributes?.done === 'true'}
			{@const drSvg = decode(detailToken.attributes?.svg ?? '')}
			{@const drError = decode(detailToken.attributes?.error ?? '')}
			<div class="w-full">
				{#if !drDone}
					<div class="flex items-center gap-2 text-gray-500 py-1">
						<Spinner className="size-4" />
						<span class="text-sm shimmer">{$i18n.t('Drawing diagram…')}</span>
					</div>
				{:else if drSvg}
					<SvgPanZoom className="rounded-2xl max-h-fit overflow-hidden" svg={drSvg} />
				{:else if drError}
					<div class="flex gap-2.5 border px-4 py-3 border-red-600/10 bg-red-600/10 rounded-2xl">
						{$i18n.t('Failed to render diagram')}: {drError}
					</div>
				{/if}
			</div>
		{:else if detailToken.text?.length > 0}
			<Collapsible
				title={getDetailTitle(detailToken)}
				open={$settings?.expandDetails ?? false}
				attributes={getDetailAttributes(detailToken)}
				messageDone={done}
				className="w-full space-y-2"
				buttonClassName={detailButtonClassName}
			>
				<div class="mb-1.5" slot="content">
					<div class="markdown-prose">
						<Markdown
							id={`${id}-${displayItem.id}-detail`}
							content={detailToken.text}
							{done}
							{preview}
							{compactPreview}
							{editCodeBlock}
						/>
					</div>
				</div>
			</Collapsible>
		{:else}
			<Collapsible
				title={getDetailTitle(detailToken)}
				open={false}
				disabled={true}
				attributes={getDetailAttributes(detailToken)}
				messageDone={done}
				className="w-full space-y-2"
				buttonClassName={detailButtonClassName}
			/>
		{/if}
	{/if}
{/each}

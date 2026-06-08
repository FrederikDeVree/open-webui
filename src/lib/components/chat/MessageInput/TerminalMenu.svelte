<script lang="ts">
	import { getContext } from 'svelte';

	import { settings, terminalServers, selectedTerminalId, user } from '$lib/stores';
	import { getToolServersData } from '$lib/apis';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Cloud from '$lib/components/icons/Cloud.svelte';

	const i18n = getContext('i18n');

	$: systemTerminals = ($terminalServers ?? []).filter((t) => t.id);
	$: directTerminals = ($settings?.terminalServers ?? []).filter((s) => s.url);

	const refreshTerminalServersStore = async (servers: typeof directTerminals) => {
		// Preserve system terminals (those with an `id`) — only refresh direct ones
		const existingSystemTerminals = ($terminalServers ?? []).filter((t) => t.id);

		const activeTerminals = servers.filter((s) => s.enabled);
		if (activeTerminals.length > 0) {
			let data = await getToolServersData(
				activeTerminals.map((t) => ({
					url: t.url,
					auth_type: t.auth_type ?? 'bearer',
					key: t.key ?? '',
					path: t.path ?? '/openapi.json',
					config: { enable: true }
				}))
			);
			data = data.filter((d) => d && !d.error);
			terminalServers.set([...data, ...existingSystemTerminals]);
		} else {
			terminalServers.set(existingSystemTerminals);
		}
	};

	const toggleTerminal = () => {
		if ($selectedTerminalId) {
			// Disable terminal
			selectedTerminalId.set(null);

			// If we were using a direct terminal, disable it in settings
			const isDirect = directTerminals.some((t) => t.url === $selectedTerminalId);
			if (isDirect && $settings?.terminalServers) {
				const updatedServers = $settings.terminalServers.map((s) => ({
					...s,
					enabled: false
				}));
				settings.set({
					...$settings,
					terminalServers: updatedServers
				});
				refreshTerminalServersStore(updatedServers);
			}
		} else {
			// Enable terminal: prefer system terminal first, then direct
			if (systemTerminals.length > 0) {
				selectedTerminalId.set(systemTerminals[0].id);
			} else if (
				directTerminals.length > 0 &&
				($user?.role === 'admin' || ($user?.permissions?.features?.direct_tool_servers ?? true))
			) {
				const terminal = directTerminals[0];
				selectedTerminalId.set(terminal.url);

				// Enable the selected direct terminal, disable all others
				const updatedServers = ($settings?.terminalServers ?? []).map((s) => ({
					...s,
					enabled: s.url === terminal.url
				}));

				settings.set({
					...$settings,
					terminalServers: updatedServers
				});

				refreshTerminalServersStore(updatedServers);
			}
		}
	};
</script>

<div class="flex items-center translate-x-0.5">
	<Tooltip content={$i18n.t('Terminal')} placement="top">
		<button
			type="button"
			class="flex items-center gap-1.5 translate-y-[1px] hover:bg-gray-50 dark:hover:bg-gray-850 text-sm transition rounded-lg cursor-pointer px-2.5 py-1
				{$selectedTerminalId ? 'text-black dark:text-gray-100' : 'opacity-50'}"
			on:click={toggleTerminal}
		>
			<Cloud className="size-3.5" strokeWidth="2" />
			<span class="text-[13px] whitespace-nowrap">{$i18n.t('Terminal')}</span>
		</button>
	</Tooltip>
</div>

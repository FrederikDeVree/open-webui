import { get } from 'svelte/store';
import { terminalServers, selectedTerminalId } from '$lib/stores';
import { downloadFileBlob } from '$lib/apis/terminal';

/** Scheme prefix used for terminal download links generated in markdown. */
export const TERMINAL_DOWNLOAD_SCHEME = 'terminal-download://';

/**
 * Regex that matches an absolute POSIX file path with at least one directory
 * component and a file extension. Used to detect terminal file paths in code
 * spans so they can be rendered as clickable download buttons.
 *
 * Examples that match: /workspace/output.csv, /home/user/results.json, /tmp/report.pdf
 * Examples that don't: /bin/bash (no extension), /mnt/uploads/... (handled by Pyodide)
 */
export const TERMINAL_PATH_RE = /^\/(?:[^\s/]+\/)+[^\s/]+\.[a-zA-Z0-9]{1,10}$/;

/**
 * Download a file from the currently selected terminal server.
 * Returns true on success, false if no terminal is available or the file is missing.
 */
export async function downloadTerminalFile(filePath: string): Promise<boolean> {
	const servers = get(terminalServers) as Array<{ id: string; url: string; key: string }>;
	const selectedId = get(selectedTerminalId) as string | null;

	const terminal = selectedId
		? (servers.find((t) => t.id === selectedId) ?? servers[0] ?? null)
		: (servers[0] ?? null);

	if (!terminal) return false;

	try {
		const result = await downloadFileBlob(terminal.url, terminal.key, filePath);
		if (!result) return false;

		const url = URL.createObjectURL(result.blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = result.filename;
		a.click();
		URL.revokeObjectURL(url);
		return true;
	} catch {
		return false;
	}
}

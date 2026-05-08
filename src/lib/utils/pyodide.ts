import { get } from 'svelte/store';
import { pyodideWorker } from '$lib/stores';

let _reqId = 0;

/**
 * Send a message to the shared Pyodide worker and wait for the response.
 */
export function sendPyodideWorkerMessage(msg: Record<string, unknown>): Promise<any> {
	const worker = get(pyodideWorker);
	if (!worker) return Promise.reject(new Error('Pyodide worker not available'));

	const id = `pyodide-util-${++_reqId}`;
	return new Promise((resolve, reject) => {
		const timeout = setTimeout(() => {
			worker.removeEventListener('message', handler);
			reject(new Error('Timeout'));
		}, 30000);

		function handler(event: MessageEvent) {
			if (event.data?.id !== id) return;
			clearTimeout(timeout);
			worker.removeEventListener('message', handler);
			resolve(event.data);
		}

		worker.addEventListener('message', handler);
		worker.postMessage({ ...msg, id });
	});
}

/**
 * Download a file from the Pyodide virtual filesystem.
 * Returns true on success, false if the worker is unavailable or the file is missing.
 */
export async function downloadPyodideFile(filePath: string): Promise<boolean> {
	try {
		const res = await sendPyodideWorkerMessage({ type: 'fs:read', path: filePath });
		if (!res.data) return false;

		const blob = new Blob([res.data]);
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filePath.split('/').pop() ?? 'file';
		a.click();
		URL.revokeObjectURL(url);
		return true;
	} catch {
		return false;
	}
}

/** Scheme prefix used for Pyodide download links generated during markdown preprocessing. */
export const PYODIDE_DOWNLOAD_SCHEME = 'pyodide-download://';

/**
 * Pre-process markdown content: convert bare `/mnt/uploads/...` paths that appear
 * as plain text into markdown download links so the renderer can turn them into
 * clickable download buttons.
 *
 * Paths that are already inside a markdown link target `(...)` or inside code
 * spans / fences are left untouched.
 */
export function linkifyPyodidePaths(content: string): string {
	// Split on code fences and inline code so we don't touch those segments.
	const segments = content.split(/(```[\s\S]*?```|`[^`\n]+`)/g);
	return segments
		.map((seg, i) => {
			if (i % 2 === 1) return seg; // inside a code block / inline code – skip
			// Replace bare /mnt/uploads/... paths not already inside a markdown link target
			return seg.replace(/(?<!\()\/mnt\/uploads\/([^\s"'`<>\)\]]+)/g, (match) => {
				const filename = match.split('/').pop() ?? match;
				return `[${filename}](${PYODIDE_DOWNLOAD_SCHEME}${match})`;
			});
		})
		.join('');
}

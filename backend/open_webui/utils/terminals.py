"""Shared routing helpers for admin-configured terminal servers."""

import logging
from urllib.parse import quote

import aiohttp
from open_webui.env import AIOHTTP_CLIENT_SESSION_SSL
from open_webui.utils.chat_id import is_saved_chat_id
from open_webui.utils.headers import bearer_auth_header

log = logging.getLogger(__name__)

TERMINAL_CONTEXT_HEADER = 'X-Terminal-Context-Id'
TERMINAL_CONTEXT_DEFAULT = 'default'
TERMINAL_CONTEXT_TYPES = {'chat', 'automation'}
TERMINAL_CONTEXT_ID_SOURCES = {'chat': 'chat_id', 'automation': 'automation_id'}
TERMINAL_CHAT_UPLOAD_MODES = {'default', 'filesystem', 'both'}


def is_terminal_orchestrator(connection: dict) -> bool:
    """Return whether this connection points at Terminals, not raw Open Terminal."""
    return connection.get('server_type') == 'orchestrator' or bool(connection.get('policy_id'))


def get_terminal_server_url(connection: dict) -> str:
    """Return the upstream base URL for a terminal connection.

    An explicit policy uses the named-policy route. Connections without one
    keep their existing root route.
    """
    base_url = str(connection.get('url') or '').rstrip('/')
    policy_id = str(connection.get('policy_id') or '').strip()
    if policy_id:
        return f'{base_url}/p/{quote(policy_id, safe="")}'
    return base_url


def terminal_context_config(connection: dict, context: str) -> dict | bool:
    """Return config for an OpenWebUI terminal context.

    Missing config is legacy behavior: available, shared default terminal.
    """
    if not is_terminal_orchestrator(connection):
        return {}

    contexts = (connection.get('config') or {}).get('contexts')
    if not isinstance(contexts, dict):
        return {}

    value = contexts.get(context, {})
    if value is False:
        return False
    return value if isinstance(value, dict) else {}


def terminal_context_available(connection: dict, context: str) -> bool:
    """Return whether this terminal is exposed in an OpenWebUI context."""
    if context not in TERMINAL_CONTEXT_TYPES:
        return False
    return terminal_context_config(connection, context) is not False


def terminal_context_id(
    connection: dict,
    metadata: dict | None = None,
    context: str = 'chat',
) -> str | None:
    """Return the terminal runtime context for trusted request metadata."""
    if not is_terminal_orchestrator(connection) or not terminal_context_available(connection, context):
        return None

    config = terminal_context_config(connection, context)
    context_id_source = config.get('context_id') if isinstance(config, dict) else None
    if not context_id_source or context_id_source == TERMINAL_CONTEXT_DEFAULT:
        return None

    if context_id_source != TERMINAL_CONTEXT_ID_SOURCES.get(context):
        return None

    metadata = metadata or {}

    if context == 'automation':
        automation_id = metadata.get('automation_id')
        return f'automation:{automation_id}' if automation_id else None

    chat_id = metadata.get('chat_id')
    if context == 'chat' and chat_id and is_saved_chat_id(chat_id):
        return f'chat:{chat_id}'
    return None


def terminal_contexts(connection: dict) -> dict:
    """Return normalized sparse context config for clients."""
    if not is_terminal_orchestrator(connection):
        return {}

    contexts = (connection.get('config') or {}).get('contexts')
    if not isinstance(contexts, dict):
        return {}

    result = {}
    for context, value in contexts.items():
        if context not in TERMINAL_CONTEXT_TYPES:
            continue
        if value is False:
            result[context] = False
        elif isinstance(value, dict):
            context_id_source = value.get('context_id')
            if context_id_source in {TERMINAL_CONTEXT_DEFAULT, TERMINAL_CONTEXT_ID_SOURCES[context]}:
                result[context] = {'context_id': context_id_source}
            else:
                result[context] = {}
    return result


def terminal_chat_uploads(connection: dict) -> str:
    """Return normalized main-chat upload behavior for this connection."""
    value = (connection.get('config') or {}).get('chat_uploads')
    return value if value in TERMINAL_CHAT_UPLOAD_MODES else 'default'


async def delete_terminal_chat_attachments(connection: dict, chat_id: str, user_id: str) -> None:
    """Delete the per-chat attachments folder (``<home>/chat_attachments/<chat_id>``)
    on a terminal server.

    Best effort: any failure (unknown home dir, unreachable server, missing
    endpoint) is logged and swallowed so chat deletion is never blocked.
    """
    if not chat_id or not is_saved_chat_id(chat_id):
        return

    base_url = get_terminal_server_url(connection)
    if not base_url:
        return

    headers = {'Content-Type': 'application/json', 'X-User-Id': user_id, 'X-Session-Id': chat_id}
    auth_type = connection.get('auth_type', 'bearer')
    if auth_type == 'bearer':
        headers.update(bearer_auth_header(connection.get('key', '')))
    # 'session' / 'system_oauth' auth require a live request (cookies / OAuth
    # session); there is no user credential to call the server with here, so
    # skip cleanup for those rather than guess.
    if auth_type not in {'bearer', 'none'}:
        log.debug('Skipping terminal attachment cleanup for %s (auth_type=%s)', chat_id, auth_type)
        return

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            trust_env=True,
        ) as session:
            # Resolve the home dir; the attachments folder is anchored there.
            async with session.get(
                f'{base_url}/files/cwd', headers=headers, ssl=AIOHTTP_CLIENT_SESSION_SSL
            ) as resp:
                if resp.status != 200:
                    log.debug('Attachment cleanup: /files/cwd returned %s for chat %s', resp.status, chat_id)
                    return
                data = await resp.json()
            home = data.get('home') or data.get('cwd')
            if not home:
                return

            attachments_path = f'{home.rstrip("/")}/chat_attachments/{chat_id}'
            log.info('Deleting terminal attachments for chat %s: %s', chat_id, attachments_path)
            async with session.request(
                'DELETE',
                f'{base_url}/files/delete?path={quote(attachments_path, safe="")}',
                headers=headers,
                ssl=AIOHTTP_CLIENT_SESSION_SSL,
            ) as resp:
                if resp.status < 400:
                    log.info('Deleted terminal attachments for chat %s: %s', chat_id, attachments_path)
                if resp.status >= 500:
                    body = await resp.text()
                    log.warning(
                        'Failed to delete terminal attachments for chat %s: HTTP %s %s',
                        chat_id,
                        resp.status,
                        body[:200],
                    )
                elif resp.status >= 400:
                    # 404 is expected when the chat never uploaded any files.
                    log.debug('Terminal attachment delete for chat %s: HTTP %s', chat_id, resp.status)
    except Exception as e:
        log.warning('Failed to delete terminal attachments for chat %s: %s', chat_id, e)

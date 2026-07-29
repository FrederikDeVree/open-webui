<script lang="ts">
	import { getBackendConfig } from '$lib/apis';
	import {
		getAdminConfig,
		getLdapConfig,
		getLdapServers,
		getOAuthConfig,
		updateLdapConfig,
		updateLdapServers,
		updateOAuthConfig,
		updateAdminConfig
	} from '$lib/apis/auths';
	import { getGroups } from '$lib/apis/groups';
	import SensitiveInput from '$lib/components/common/SensitiveInput.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import Textarea from '$lib/components/common/Textarea.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import { config } from '$lib/stores';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import AdminSettingField from './AdminSettingField.svelte';
	import AdminSettingRow from './AdminSettingRow.svelte';
	import AdminSettingSection from './AdminSettingSection.svelte';
	import SettingsSelect from '$lib/components/common/SettingsSelect.svelte';

	const i18n: any = getContext('i18n');

	let adminConfig: any = null;
	let groups: any[] = [];

	let ENABLE_LDAP = false;
	let LDAP_SERVERS = [
		{
			label: '',
			host: '',
			port: '',
			attribute_for_mail: 'mail',
			attribute_for_username: 'uid',
			app_dn: '',
			app_dn_password: '',
			search_base: '',
			search_filters: '',
			use_tls: false,
			certificate_path: '',
			ciphers: ''
		}
	];

	let oauthConfig: any = null;
	const inputClass =
		'w-full h-7 rounded-lg border border-gray-100/50 bg-gray-50/40 px-2 text-xs text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';
	const textareaClass =
		'w-full rounded-lg border border-gray-100/50 bg-gray-50/40 px-2 py-1.5 text-xs text-gray-700 outline-hidden transition-colors placeholder:text-gray-300 focus:border-blue-400 dark:border-white/[0.04] dark:bg-white/[0.03] dark:text-gray-300 dark:placeholder:text-gray-700 dark:focus:border-blue-500';

	const updateOAuthHandler = async () => {
		if (!oauthConfig) return true;
		const res = await updateOAuthConfig(localStorage.token, oauthConfig).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (res) {
			oauthConfig = res;
		}
		return !!res;
	};

	const updateLdapServerHandler = async () => {
		await updateLdapConfig(localStorage.token, ENABLE_LDAP);
		if (!ENABLE_LDAP) return true;

		const res = await updateLdapServers(localStorage.token, { servers: LDAP_SERVERS }).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		return !!res;
	};

	const addLdapServer = () => {
		LDAP_SERVERS = [...LDAP_SERVERS, {
			label: '',
			host: '',
			port: '',
			attribute_for_mail: 'mail',
			attribute_for_username: 'uid',
			app_dn: '',
			app_dn_password: '',
			search_base: '',
			search_filters: '',
			use_tls: false,
			certificate_path: '',
			ciphers: ''
		}];
	};

	const removeLdapServer = (index: number) => {
		if (LDAP_SERVERS.length > 1) {
			LDAP_SERVERS = LDAP_SERVERS.filter((_, i) => i !== index);
		}
	};

	const moveLdapServer = (index: number, direction: 'up' | 'down') => {
		if (direction === 'up' && index > 0) {
			const copy = [...LDAP_SERVERS];
			const temp = copy[index - 1];
			copy[index - 1] = copy[index];
			copy[index] = temp;
			LDAP_SERVERS = copy;
		} else if (direction === 'down' && index < LDAP_SERVERS.length - 1) {
			const copy = [...LDAP_SERVERS];
			const temp = copy[index + 1];
			copy[index + 1] = copy[index];
			copy[index] = temp;
			LDAP_SERVERS = copy;
		}
	};

	const updateAdminHandler = async () => {
		if (!adminConfig) return true;
		const res = await updateAdminConfig(localStorage.token, adminConfig).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		return !!res;
	};

	const submitHandler = async () => {
		const adminSaved = await updateAdminHandler();
		const ldapSaved = await updateLdapServerHandler();
		const oauthSaved = await updateOAuthHandler();

		if (adminSaved && ldapSaved && oauthSaved) {
			toast.success($i18n.t('Settings saved successfully!'));
			await config.set(await getBackendConfig());
		}
	};

	onMount(async () => {
		await Promise.all([
			(async () => {
				adminConfig = await getAdminConfig(localStorage.token);
			})(),
			(async () => {
				groups = await getGroups(localStorage.token);
			})(),
			(async () => {
				const ldapServersResponse = await getLdapServers(localStorage.token).catch(() => ({ servers: [] }));
				LDAP_SERVERS = (ldapServersResponse?.servers || []).length
					? ldapServersResponse.servers
					: [
							{
								label: '',
								host: '',
								port: '',
								attribute_for_mail: 'mail',
								attribute_for_username: 'uid',
								app_dn: '',
								app_dn_password: '',
								search_base: '',
								search_filters: '',
								use_tls: false,
								certificate_path: '',
								ciphers: ''
							}
					  ];
			})(),
			(async () => {
				oauthConfig = await getOAuthConfig(localStorage.token).catch(() => null);
			})()
		]);

		const ldapConfig = await getLdapConfig(localStorage.token);
		ENABLE_LDAP = ldapConfig.ENABLE_LDAP;
	});
</script>

<form
	class="flex flex-col h-full justify-between space-y-3 text-sm"
	onsubmit={(e) => { e.preventDefault(); submitHandler(); }}
>
	<div class="space-y-3 overflow-y-scroll scrollbar-hidden h-full">
		{#if adminConfig !== null}
			<AdminSettingSection title={$i18n.t('User Access')} first>
				<AdminSettingRow
					label={$i18n.t('Default User Role')}
					description={$i18n.t('Role assigned to new users when they create an account.')}
				>
					<SettingsSelect
						bind:value={adminConfig.DEFAULT_USER_ROLE}
						placeholder={$i18n.t('Select a role')}
					>
						<option value="pending">{$i18n.t('pending')}</option>
						<option value="user">{$i18n.t('user')}</option>
						<option value="admin">{$i18n.t('admin')}</option>
					</SettingsSelect>
				</AdminSettingRow>

				<AdminSettingRow
					label={$i18n.t('Default Group')}
					description={$i18n.t('Group assigned to new users by default.')}
				>
					<SettingsSelect
						bind:value={adminConfig.DEFAULT_GROUP_ID}
						placeholder={$i18n.t('Select a group')}
					>
						<option value={''}>None</option>
						{#each groups as group}
							<option value={group.id}>{group.name}</option>
						{/each}
					</SettingsSelect>
				</AdminSettingRow>

				<AdminSettingRow
					label={$i18n.t('New Sign Ups')}
					description={$i18n.t('Allow new users to create accounts.')}
					let:labelId
				>
					<Switch bind:state={adminConfig.ENABLE_SIGNUP} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				<AdminSettingRow
					label={$i18n.t('API Keys')}
					description={$i18n.t('Allow users to create API keys for programmatic access.')}
					let:labelId
				>
					<Switch bind:state={adminConfig.ENABLE_API_KEYS} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				{#if adminConfig?.ENABLE_API_KEYS}
					<AdminSettingRow
						label={$i18n.t('API Key Endpoint Restrictions')}
						description={$i18n.t('Limit API keys to configured endpoints.')}
						let:labelId
					>
						<Switch
							bind:state={adminConfig.ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					{#if adminConfig?.ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS}
						<AdminSettingField
							label={$i18n.t('Allowed Endpoints')}
							description={$i18n.t('Comma-separated API paths that API keys can access.')}
						>
							<input
								class={inputClass}
								type="text"
								placeholder={`e.g.) /api/v1/messages, /api/v1/channels`}
								bind:value={adminConfig.API_KEYS_ALLOWED_ENDPOINTS}
							/>
							<a
								href="https://docs.openwebui.com/reference/api-endpoints"
								target="_blank"
								class="mt-1 block text-[0.6875rem] text-gray-400 underline hover:text-gray-700 dark:text-gray-600 dark:hover:text-gray-300"
							>
								{$i18n.t('To learn more about available endpoints, visit our documentation.')}
							</a>
						</AdminSettingField>
					{/if}
				{/if}

				<AdminSettingField
					label={$i18n.t('JWT Expiration')}
					description={$i18n.t(
						"Valid time units: 's', 'm', 'h', 'd', 'w' or '-1' for no expiration."
					)}
				>
					<input
						class={inputClass}
						type="text"
						placeholder={`e.g.) "30m","1h", "10d". `}
						bind:value={adminConfig.JWT_EXPIRES_IN}
					/>

					{#if adminConfig.JWT_EXPIRES_IN === '-1'}
						<a
							href="https://docs.openwebui.com/reference/env-configuration#jwt_expires_in"
							target="_blank"
							class="mt-1 block rounded-lg bg-yellow-500/10 px-2 py-1.5 text-[0.6875rem] text-yellow-700 underline dark:text-yellow-200"
						>
							{$i18n.t('No expiration can pose security risks.')}
						</a>
					{/if}
				</AdminSettingField>
			</AdminSettingSection>

			<AdminSettingSection title={$i18n.t('Pending Accounts')}>
				<AdminSettingRow
					label={$i18n.t('Admin Details')}
					description={$i18n.t('Show admin contact details while an account waits for approval.')}
					let:labelId
				>
					<Switch bind:state={adminConfig.SHOW_ADMIN_DETAILS} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				{#if adminConfig.SHOW_ADMIN_DETAILS}
					<AdminSettingField
						label={$i18n.t('Admin Contact Email')}
						description={$i18n.t('Email shown in the pending account overlay.')}
					>
						<input
							class={inputClass}
							type="email"
							placeholder={$i18n.t('Leave empty to use first admin user')}
							bind:value={adminConfig.ADMIN_EMAIL}
						/>
					</AdminSettingField>
				{/if}

				<AdminSettingField
					label={$i18n.t('Pending User Overlay Title')}
					description={$i18n.t('Custom title shown while an account waits for approval.')}
				>
					<Textarea
						className={textareaClass}
						placeholder={$i18n.t(
							'Enter a title for the pending user info overlay. Leave empty for default.'
						)}
						bind:value={adminConfig.PENDING_USER_OVERLAY_TITLE}
					/>
				</AdminSettingField>

				<AdminSettingField
					label={$i18n.t('Pending User Overlay Content')}
					description={$i18n.t('Custom message shown while an account waits for approval.')}
				>
					<Textarea
						className={textareaClass}
						placeholder={$i18n.t(
							'Enter content for the pending user info overlay. Leave empty for default.'
						)}
						bind:value={adminConfig.PENDING_USER_OVERLAY_CONTENT}
					/>
				</AdminSettingField>
			</AdminSettingSection>
		{/if}

		<AdminSettingSection title={$i18n.t('LDAP')}>
			<AdminSettingRow
				label={$i18n.t('LDAP')}
				description={$i18n.t('Allow users to authenticate with an LDAP directory.')}
				let:labelId
			>
				<Switch bind:state={ENABLE_LDAP} ariaLabelledbyId={labelId} />
			</AdminSettingRow>

			{#if ENABLE_LDAP}
				<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
					<AdminSettingField
						label={$i18n.t('Label')}
						description={$i18n.t('Display name for this LDAP connection.')}
					>
						<input
							class={inputClass}
							required
							placeholder={$i18n.t('Enter server label')}
							bind:value={LDAP_SERVER.label}
						/>
					</AdminSettingField>
				</div>

				{#if ENABLE_LDAP}
					<div class="flex flex-col gap-3">
						{#each LDAP_SERVERS as server, index}
							<div class="border border-gray-200 dark:border-gray-700 rounded-lg p-3 space-y-2">
								<div class="flex justify-between items-center">
									<div class="font-medium text-sm">{$i18n.t('Server')} {index + 1}</div>
									<div class="flex gap-1">
										<button
											type="button"
											class="px-2 py-1 text-xs rounded bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
											onclick={() => moveLdapServer(index, 'up')}
											disabled={index === 0}
										>
											{$i18n.t('Up')}
										</button>
										<button
											type="button"
											class="px-2 py-1 text-xs rounded bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
											onclick={() => moveLdapServer(index, 'down')}
											disabled={index === LDAP_SERVERS.length - 1}
										>
											{$i18n.t('Down')}
										</button>
										<button
											type="button"
											class="px-2 py-1 text-xs rounded bg-red-100 dark:bg-red-900 hover:bg-red-200 dark:hover:bg-red-800 text-red-700 dark:text-red-300"
											onclick={() => removeLdapServer(index)}
											disabled={LDAP_SERVERS.length === 1}
										>
											{$i18n.t('Remove')}
										</button>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Label')}
										</div>
										<input
											class="w-full bg-transparent outline-hidden py-0.5"
											required
											placeholder={$i18n.t('Enter server label')}
											bind:value={server.label}
										/>
									</div>
									<div class="w-full"></div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Host')}
										</div>
										<input
											class="w-full bg-transparent outline-hidden py-0.5"
											required
											placeholder={$i18n.t('Enter server host')}
											bind:value={server.host}
										/>
									</div>
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Port')}
										</div>
										<Tooltip
											placement="top-start"
											content={$i18n.t('Default to 389 or 636 if TLS is enabled')}
											className="w-full"
										>
											<input
												class="w-full bg-transparent outline-hidden py-0.5"
												type="number"
												placeholder={$i18n.t('Enter server port')}
												bind:value={server.port}
											/>
										</Tooltip>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Application DN')}
										</div>
										<Tooltip
											content={$i18n.t('The Application Account DN you bind with for search')}
											placement="top-start"
										>
											<input
												class="w-full bg-transparent outline-hidden py-0.5"
												placeholder={$i18n.t('Enter Application DN')}
												bind:value={server.app_dn}
											/>
										</Tooltip>
									</div>
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Application DN Password')}
										</div>
										<SensitiveInput
											placeholder={$i18n.t('Enter Application DN Password')}
											required={false}
											bind:value={server.app_dn_password}
										/>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Attribute for Mail')}
										</div>
										<Tooltip
											content={$i18n.t(
												'The LDAP attribute that maps to the mail that users use to sign in.'
											)}
											placement="top-start"
										>
											<input
												class="w-full bg-transparent outline-hidden py-0.5"
												required
												placeholder={$i18n.t('Example: mail')}
												bind:value={server.attribute_for_mail}
											/>
										</Tooltip>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Attribute for Username')}
										</div>
										<Tooltip
											content={$i18n.t(
												'The LDAP attribute that maps to the username that users use to sign in.'
											)}
											placement="top-start"
										>
											<input
												class="w-full bg-transparent outline-hidden py-0.5"
												required
												placeholder={$i18n.t('Example: sAMAccountName or uid or userPrincipalName')}
												bind:value={server.attribute_for_username}
											/>
										</Tooltip>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Search Base')}
										</div>
										<Tooltip content={$i18n.t('The base to search for users')} placement="top-start">
											<input
												class="w-full bg-transparent outline-hidden py-0.5"
												required
												placeholder={$i18n.t('Example: ou=users,dc=foo,dc=example')}
												bind:value={server.search_base}
											/>
										</Tooltip>
									</div>
								</div>
								<div class="flex w-full gap-2">
									<div class="w-full">
										<div class=" self-center text-xs font-medium min-w-fit mb-1">
											{$i18n.t('Search Filters')}
										</div>
										<input
											class="w-full bg-transparent outline-hidden py-0.5"
											placeholder={$i18n.t('Example: (&(objectClass=inetOrgPerson)(uid=%s))')}
											bind:value={server.search_filters}
										/>
									</div>
								</div>
								<div class="text-xs text-gray-400 dark:text-gray-500">
									<a
										class=" text-gray-300 font-medium underline"
										href="https://ldap.com/ldap-filters/"
										target="_blank"
									>
										{$i18n.t('Click here for filter guides.')}
									</a>
								</div>
								<div>
									<div class="flex justify-between items-center text-sm">
										<div class="  font-medium">{$i18n.t('TLS')}</div>

										<div class="mt-1">
											<Switch bind:state={server.use_tls} />
										</div>
									</div>
									{#if server.use_tls}
										<div class="flex w-full gap-2">
											<div class="w-full">
												<div class=" self-center text-xs font-medium min-w-fit mb-1 mt-1">
													{$i18n.t('Certificate Path')}
												</div>
												<input
													class="w-full bg-transparent outline-hidden py-0.5"
													placeholder={$i18n.t('Enter certificate path')}
													bind:value={server.certificate_path}
												/>
											</div>
										</div>
										<div class="flex justify-between items-center text-xs">
											<div class=" font-medium">{$i18n.t('Validate certificate')}</div>

											<div class="mt-1">
												<Switch bind:state={server.validate_cert} />
											</div>
										</div>
										<div class="flex w-full gap-2">
											<div class="w-full">
												<div class=" self-center text-xs font-medium min-w-fit mb-1">
													{$i18n.t('Ciphers')}
												</div>
												<Tooltip content={$i18n.t('Default to ALL')} placement="top-start">
													<input
														class="w-full bg-transparent outline-hidden py-0.5"
														placeholder={$i18n.t('Example: ALL')}
														bind:value={server.ciphers}
													/>
												</Tooltip>
											</div>
											<div class="w-full"></div>
										</div>
									{/if}
								</div>
							</div>
						{/each}
						<button
							type="button"
							class="px-3 py-1 text-xs rounded bg-blue-100 dark:bg-blue-900 hover:bg-blue-200 dark:hover:bg-blue-800 text-blue-700 dark:text-blue-300"
							onclick={addLdapServer}
						>
							{$i18n.t('Add Server')}
						</button>
					</div>
				{/if}
			</div>
		</div>
		{#if oauthConfig}
			<div class="mb-3">
				<div class="mt-0.5 mb-2.5 text-base font-medium">{$i18n.t('OAuth / OIDC')}</div>

				<hr class="border-gray-100/30 dark:border-gray-850/30 my-2" />

				<div class="pr-1.5">
					<div class="space-y-3">
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Provider Name')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="SSO"
									bind:value={oauthConfig.OAUTH_PROVIDER_NAME}
								/>
							</div>
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Provider URL')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="https://accounts.google.com/.well-known/openid-configuration"
									bind:value={oauthConfig.OPENID_PROVIDER_URL}
								/>
							</div>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Client ID')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder={$i18n.t('Enter Client ID')}
									bind:value={oauthConfig.OAUTH_CLIENT_ID}
								/>
							</div>
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Client Secret')}
								</div>
								<SensitiveInput
									placeholder={$i18n.t('Enter Client Secret')}
									required={false}
									outerClassName="flex flex-1 bg-transparent"
									inputClassName="w-full text-sm py-0.5 bg-transparent"
									bind:value={oauthConfig.OAUTH_CLIENT_SECRET}
								/>
							</div>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Redirect URI')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder={$i18n.t('Enter Redirect URI')}
									bind:value={oauthConfig.OPENID_REDIRECT_URI}
								/>
							</div>
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Scopes')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="openid email profile"
									bind:value={oauthConfig.OAUTH_SCOPES}
								/>
							</div>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Email Claim')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="email"
									bind:value={oauthConfig.OAUTH_EMAIL_CLAIM}
								/>
							</div>
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Username Claim')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="name"
									bind:value={oauthConfig.OAUTH_USERNAME_CLAIM}
								/>
							</div>
						</div>

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Picture Claim')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="picture"
									bind:value={oauthConfig.OAUTH_PICTURE_CLAIM}
								/>
							</div>
							<div class="w-full">
								<div class="self-center text-xs font-medium min-w-fit mb-1">
									{$i18n.t('Sub Claim')}
								</div>
								<input
									class="w-full bg-transparent outline-hidden py-0.5"
									placeholder="sub"
									bind:value={oauthConfig.OAUTH_SUB_CLAIM}
								/>
							</div>
						</div>

						<div class="flex w-full justify-between pr-2">
							<div class="self-center text-xs font-medium">
								{$i18n.t('Enable OAuth Signup')}
							</div>
							<Switch bind:state={oauthConfig.ENABLE_OAUTH_SIGNUP} />
						</div>

						<div class="flex w-full justify-between pr-2">
							<div class="self-center text-xs font-medium">
								{$i18n.t('Merge Accounts by Email')}
							</div>
							<Switch bind:state={oauthConfig.OAUTH_MERGE_ACCOUNTS_BY_EMAIL} />
						</div>

						<div class="flex w-full justify-between pr-2">
							<div class="self-center text-xs font-medium">
								{$i18n.t('Auto Redirect')}
							</div>
							<Switch bind:state={oauthConfig.OAUTH_AUTO_REDIRECT} />
						</div>

						<div class="w-full">
							<div class="self-center text-xs font-medium min-w-fit mb-1">
								{$i18n.t('Allowed Domains')}
							</div>
							<input
								class={inputClass}
								type="number"
								placeholder={$i18n.t('Enter server port')}
								bind:value={LDAP_SERVER.port}
							/>
						</Tooltip>
					</AdminSettingField>
				</div>

				<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
					<AdminSettingField
						label={$i18n.t('Application DN')}
						description={$i18n.t('Bind DN used for directory search.')}
					>
						<Tooltip
							content={$i18n.t('The Application Account DN you bind with for search')}
							placement="top-start"
						>
							<input
								class={inputClass}
								placeholder={$i18n.t('Enter Application DN')}
								bind:value={LDAP_SERVER.app_dn}
							/>
						</Tooltip>
					</AdminSettingField>

					<AdminSettingField
						label={$i18n.t('Application DN Password')}
						description={$i18n.t('Password for the bind DN.')}
					>
						<SensitiveInput
							variant="settings"
							placeholder={$i18n.t('Enter Application DN Password')}
							required={false}
							bind:value={LDAP_SERVER.app_dn_password}
						/>
					</AdminSettingField>
				</div>

				<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
					<AdminSettingField
						label={$i18n.t('Attribute for Mail')}
						description={$i18n.t('LDAP attribute used as the user email address.')}
					>
						<Tooltip
							content={$i18n.t(
								'The LDAP attribute that maps to the mail that users use to sign in.'
							)}
							placement="top-start"
						>
							<input
								class={inputClass}
								required
								placeholder={$i18n.t('Example: mail')}
								bind:value={LDAP_SERVER.attribute_for_mail}
							/>
						</Tooltip>
					</AdminSettingField>

					<AdminSettingField
						label={$i18n.t('Attribute for Username')}
						description={$i18n.t('LDAP attribute used as the username.')}
					>
						<Tooltip
							content={$i18n.t(
								'The LDAP attribute that maps to the username that users use to sign in.'
							)}
							placement="top-start"
						>
							<input
								class={inputClass}
								required
								placeholder={$i18n.t('Example: sAMAccountName or uid or userPrincipalName')}
								bind:value={LDAP_SERVER.attribute_for_username}
							/>
						</Tooltip>
					</AdminSettingField>
				</div>

				<AdminSettingField
					label={$i18n.t('Search Base')}
					description={$i18n.t('Base DN used when searching for users.')}
				>
					<Tooltip content={$i18n.t('The base to search for users')} placement="top-start">
						<input
							class={inputClass}
							required
							placeholder={$i18n.t('Example: ou=users,dc=foo,dc=example')}
							bind:value={LDAP_SERVER.search_base}
						/>
					</Tooltip>
				</AdminSettingField>

				<AdminSettingField
					label={$i18n.t('Search Filters')}
					description={$i18n.t('LDAP filter used to match signing-in users.')}
				>
					<input
						class={inputClass}
						placeholder={$i18n.t('Example: (&(objectClass=inetOrgPerson)(uid=%s))')}
						bind:value={LDAP_SERVER.search_filters}
					/>
					<a
						class="mt-1 block text-[0.6875rem] text-gray-400 underline hover:text-gray-700 dark:text-gray-600 dark:hover:text-gray-300"
						href="https://ldap.com/ldap-filters/"
						target="_blank"
					>
						{$i18n.t('Click here for filter guides.')}
					</a>
				</AdminSettingField>

				<AdminSettingRow
					label={$i18n.t('TLS')}
					description={$i18n.t('Use TLS when connecting to the LDAP server.')}
					let:labelId
				>
					<Switch bind:state={LDAP_SERVER.use_tls} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				{#if LDAP_SERVER.use_tls}
					<AdminSettingField
						label={$i18n.t('Certificate Path')}
						description={$i18n.t('Certificate file used for TLS verification.')}
					>
						<input
							class={inputClass}
							placeholder={$i18n.t('Enter certificate path')}
							bind:value={LDAP_SERVER.certificate_path}
						/>
					</AdminSettingField>

					<AdminSettingRow
						label={$i18n.t('Validate Certificate')}
						description={$i18n.t('Verify the LDAP server certificate when TLS is enabled.')}
						let:labelId
					>
						<Switch bind:state={LDAP_SERVER.validate_cert} ariaLabelledbyId={labelId} />
					</AdminSettingRow>

					<AdminSettingField
						label={$i18n.t('Ciphers')}
						description={$i18n.t('TLS cipher list for LDAP connections.')}
					>
						<Tooltip content={$i18n.t('Default to ALL')} placement="top-start">
							<input
								class={inputClass}
								placeholder={$i18n.t('Example: ALL')}
								bind:value={LDAP_SERVER.ciphers}
							/>
						</Tooltip>
					</AdminSettingField>
				{/if}

				<!-- LICENSE covers this Open WebUI wordmark.
					Do not alter, remove, obscure, or replace it except as LICENSE permits:
					https://docs.openwebui.com/license. -->
				<AdminSettingRow
					label={$i18n.t('Group Mapping')}
					description={$i18n.t('Map LDAP groups to Open WebUI groups.')}
					let:labelId
				>
					<Switch bind:state={LDAP_SERVER.enable_group_management} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				{#if LDAP_SERVER.enable_group_management}
					<AdminSettingRow
						label={$i18n.t('Auto-Create Groups')}
						description={$i18n.t('Create missing groups from LDAP groups.')}
						let:labelId
					>
						<Switch bind:state={LDAP_SERVER.enable_group_creation} ariaLabelledbyId={labelId} />
					</AdminSettingRow>

					<AdminSettingField
						label={$i18n.t('Group Attribute')}
						description={$i18n.t('LDAP attribute containing the user group memberships.')}
					>
						<Tooltip content={$i18n.t('Default to memberOf')} placement="top-start">
							<input
								class={inputClass}
								placeholder="memberOf"
								bind:value={LDAP_SERVER.attribute_for_groups}
							/>
						</Tooltip>
					</AdminSettingField>
				{/if}
			{/if}
		</AdminSettingSection>

		{#if oauthConfig}
			<AdminSettingSection title={$i18n.t('OAuth / OIDC')}>
				<AdminSettingRow
					label={$i18n.t('OAuth / OIDC')}
					description={$i18n.t('Allow users to authenticate with an OAuth / OIDC provider.')}
					let:labelId
				>
					<Switch bind:state={oauthConfig.ENABLE_OAUTH} ariaLabelledbyId={labelId} />
				</AdminSettingRow>

				{#if oauthConfig.ENABLE_OAUTH}
					<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
						<AdminSettingField
							label={$i18n.t('Provider Name')}
							description={$i18n.t('Display name shown for the OAuth provider.')}
						>
							<input
								class={inputClass}
								placeholder="SSO"
								bind:value={oauthConfig.OAUTH_PROVIDER_NAME}
							/>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('Provider URL')}
							description={$i18n.t('OpenID discovery URL for this provider.')}
						>
							<input
								class={inputClass}
								placeholder="https://accounts.google.com/.well-known/openid-configuration"
								bind:value={oauthConfig.OPENID_PROVIDER_URL}
							/>
						</AdminSettingField>
					</div>

					<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
						<AdminSettingField
							label={$i18n.t('Client ID')}
							description={$i18n.t('OAuth client identifier from the provider.')}
						>
							<input
								class={inputClass}
								placeholder={$i18n.t('Enter Client ID')}
								bind:value={oauthConfig.OAUTH_CLIENT_ID}
							/>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('Client Secret')}
							description={$i18n.t('OAuth client secret from the provider.')}
						>
							<SensitiveInput
								variant="settings"
								placeholder={$i18n.t('Enter Client Secret')}
								required={false}
								bind:value={oauthConfig.OAUTH_CLIENT_SECRET}
							/>
						</AdminSettingField>
					</div>

					<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
						<AdminSettingField
							label={$i18n.t('Redirect URI')}
							description={$i18n.t('Callback URI registered with the provider.')}
						>
							<input
								class={inputClass}
								placeholder={$i18n.t('Enter Redirect URI')}
								bind:value={oauthConfig.OPENID_REDIRECT_URI}
							/>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('Scopes')}
							description={$i18n.t('OAuth scopes requested during sign-in.')}
						>
							<input
								class={inputClass}
								placeholder="openid email profile"
								bind:value={oauthConfig.OAUTH_SCOPES}
							/>
						</AdminSettingField>
					</div>

					<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
						<AdminSettingField
							label={$i18n.t('Email Claim')}
							description={$i18n.t('Claim used as the user email address.')}
						>
							<input
								class={inputClass}
								placeholder="email"
								bind:value={oauthConfig.OAUTH_EMAIL_CLAIM}
							/>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('Username Claim')}
							description={$i18n.t('Claim used as the display name.')}
						>
							<input
								class={inputClass}
								placeholder="name"
								bind:value={oauthConfig.OAUTH_USERNAME_CLAIM}
							/>
						</AdminSettingField>
					</div>

					<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
						<AdminSettingField
							label={$i18n.t('Picture Claim')}
							description={$i18n.t('Claim used as the profile picture URL.')}
						>
							<input
								class={inputClass}
								placeholder="picture"
								bind:value={oauthConfig.OAUTH_PICTURE_CLAIM}
							/>
						</AdminSettingField>

						<AdminSettingField
							label={$i18n.t('Sub Claim')}
							description={$i18n.t('Claim used as the stable user identifier.')}
						>
							<input
								class={inputClass}
								placeholder="sub"
								bind:value={oauthConfig.OAUTH_SUB_CLAIM}
							/>
						</AdminSettingField>
					</div>

					<AdminSettingRow
						label={$i18n.t('OAuth Signup')}
						description={$i18n.t('Allow users to create accounts through OAuth.')}
						let:labelId
					>
						<Switch bind:state={oauthConfig.ENABLE_OAUTH_SIGNUP} ariaLabelledbyId={labelId} />
					</AdminSettingRow>

					<AdminSettingRow
						label={$i18n.t('Merge Accounts by Email')}
						description={$i18n.t('Link OAuth sign-ins to existing accounts with the same email.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.OAUTH_MERGE_ACCOUNTS_BY_EMAIL}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					<AdminSettingRow
						label={$i18n.t('Auto Redirect')}
						description={$i18n.t(
							'Send users directly to the OAuth provider from the sign-in page.'
						)}
						let:labelId
					>
						<Switch bind:state={oauthConfig.OAUTH_AUTO_REDIRECT} ariaLabelledbyId={labelId} />
					</AdminSettingRow>

					<AdminSettingField
						label={$i18n.t('Allowed Domains')}
						description={$i18n.t('Email domains allowed to sign in with OAuth.')}
					>
						<input
							class={inputClass}
							placeholder="* (all domains)"
							bind:value={oauthConfig.OAUTH_ALLOWED_DOMAINS}
						/>
					</AdminSettingField>

					<!-- LICENSE covers this Open WebUI wordmark.
						Do not alter, remove, obscure, or replace it except as LICENSE permits:
						https://docs.openwebui.com/license. -->
					<AdminSettingRow
						label={$i18n.t('Role Mapping')}
						description={$i18n.t('Map OAuth claims to Open WebUI roles.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.ENABLE_OAUTH_ROLE_MANAGEMENT}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					{#if oauthConfig.ENABLE_OAUTH_ROLE_MANAGEMENT}
						<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
							<AdminSettingField
								label={$i18n.t('Roles Claim')}
								description={$i18n.t('Claim containing provider roles.')}
							>
								<input
									class={inputClass}
									placeholder="roles"
									bind:value={oauthConfig.OAUTH_ROLES_CLAIM}
								/>
							</AdminSettingField>

							<AdminSettingField
								label={$i18n.t('Admin Roles')}
								description={$i18n.t('Provider roles that grant admin access.')}
							>
								<input
									class={inputClass}
									placeholder="admin"
									bind:value={oauthConfig.OAUTH_ADMIN_ROLES}
								/>
							</AdminSettingField>
						</div>

						<AdminSettingField
							label={$i18n.t('Allowed Roles')}
							description={$i18n.t('Provider roles allowed to sign in.')}
						>
							<input
								class={inputClass}
								placeholder="*"
								bind:value={oauthConfig.OAUTH_ALLOWED_ROLES}
							/>
						</AdminSettingField>
					{/if}

					<!-- LICENSE covers this Open WebUI wordmark.
						Do not alter, remove, obscure, or replace it except as LICENSE permits:
						https://docs.openwebui.com/license. -->
					<AdminSettingRow
						label={$i18n.t('Group Mapping')}
						description={$i18n.t('Map OAuth claims to Open WebUI groups.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.ENABLE_OAUTH_GROUP_MANAGEMENT}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					{#if oauthConfig.ENABLE_OAUTH_GROUP_MANAGEMENT}
						<AdminSettingRow
							label={$i18n.t('Auto-Create Groups')}
							description={$i18n.t('Create missing groups from OAuth claims.')}
							let:labelId
						>
							<Switch
								bind:state={oauthConfig.ENABLE_OAUTH_GROUP_CREATION}
								ariaLabelledbyId={labelId}
							/>
						</AdminSettingRow>

						<div class="grid grid-cols-1 gap-x-3 gap-y-2.5 sm:grid-cols-2">
							<AdminSettingField
								label={$i18n.t('Group Claim')}
								description={$i18n.t('Claim containing provider groups.')}
							>
								<input
									class={inputClass}
									placeholder="groups"
									bind:value={oauthConfig.OAUTH_GROUP_CLAIM}
								/>
							</AdminSettingField>

							<AdminSettingField
								label={$i18n.t('Blocked Groups')}
								description={$i18n.t('Provider groups blocked from signing in.')}
							>
								<input
									class={inputClass}
									placeholder={$i18n.t('Comma-separated group names')}
									bind:value={oauthConfig.OAUTH_BLOCKED_GROUPS}
								/>
							</AdminSettingField>
						</div>
					{/if}

					<AdminSettingRow
						label={$i18n.t('Update Email')}
						description={$i18n.t('Refresh the account email from OAuth on sign-in.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.OAUTH_UPDATE_EMAIL_ON_LOGIN}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					<AdminSettingRow
						label={$i18n.t('Update Name')}
						description={$i18n.t('Refresh the account name from OAuth on sign-in.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.OAUTH_UPDATE_NAME_ON_LOGIN}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>

					<AdminSettingRow
						label={$i18n.t('Update Picture')}
						description={$i18n.t('Refresh the profile picture from OAuth on sign-in.')}
						let:labelId
					>
						<Switch
							bind:state={oauthConfig.OAUTH_UPDATE_PICTURE_ON_LOGIN}
							ariaLabelledbyId={labelId}
						/>
					</AdminSettingRow>
				{/if}
			</AdminSettingSection>
		{/if}
	</div>

	<div class="flex justify-end pt-6 text-sm font-normal">
		<button
			class="px-3.5 py-1.5 text-sm font-normal bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
			type="submit"
		>
			{$i18n.t('Save')}
		</button>
	</div>
</form>

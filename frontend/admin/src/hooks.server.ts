import { redirect, type Handle } from '@sveltejs/kit';

const PUBLIC_PATHS = ['/login'];

/** Decode the JWT `exp` claim (no signature check) to detect expiry locally. */
function isExpired(token: string): boolean {
	try {
		const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64url').toString());
		if (typeof payload.exp !== 'number') return false;
		return payload.exp * 1000 <= Date.now();
	} catch {
		return true; // malformed token → treat as invalid
	}
}

export const handle: Handle = async ({ event, resolve }) => {
	let token = event.cookies.get('admin_token') ?? null;

	// Proactively log out when the token is expired (or malformed).
	let expired = false;
	if (token && isExpired(token)) {
		event.cookies.delete('admin_token', { path: '/' });
		token = null;
		expired = true;
	}
	event.locals.token = token;

	const isPublic = PUBLIC_PATHS.some((p) => event.url.pathname.startsWith(p));
	if (!token && !isPublic) {
		throw redirect(303, expired ? '/login?expired=1' : '/login');
	}
	if (token && event.url.pathname === '/login') {
		throw redirect(303, '/');
	}

	return resolve(event);
};

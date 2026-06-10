import { env } from '$env/dynamic/public';

/** Base URL of the payment API. Overridable at runtime via PUBLIC_API_URL. */
export const API_URL = env.PUBLIC_API_URL ?? 'http://localhost:8000/api';

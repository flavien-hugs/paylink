/** Turn a free-text label into a URL-safe slug (matches the API pattern). */
export function slugify(value: string): string {
	return value
		.normalize('NFD')
		.replace(/[̀-ͯ]/g, '') // strip accents
		.toLowerCase()
		.trim()
		.replace(/[^a-z0-9]+/g, '-') // non-alphanumerics → hyphen
		.replace(/^-+|-+$/g, '') // trim leading/trailing hyphens
		.slice(0, 63);
}

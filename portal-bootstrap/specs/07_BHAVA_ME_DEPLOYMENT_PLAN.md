# bhava.me Deployment Plan

The domain is owned in IONOS. Local development comes first.

## Do not change DNS now

The current implementation must not modify:
- destination settings
- nameservers
- DNS records
- SSL settings
- mail settings

## Future deployment options

Preferred:
1. Deploy the public Next.js frontend to a managed platform.
2. Deploy the public read API separately.
3. Keep all factory-control endpoints off the public deployment.
4. Add the provider-required DNS records in IONOS.
5. Verify HTTPS before changing the domain destination.
6. Preserve current IONOS mail service records.

## Domain layout

```text
bhava.me              Public devotional library
www.bhava.me          Redirect to bhava.me
api.bhava.me          Public read-only API, if needed
studio.localhost      Local factory only; never public
```

## Contact

Use configuration rather than hard-coded personal details:

```text
Project steward: Swapnil Patil
Website: https://swapnilpatil.tech
Contact: https://swapnilpatil.tech/contact
LinkedIn: https://linkedin.com/in/swapnil-patil-ai-architect
GitHub: https://github.com/swap2you
```

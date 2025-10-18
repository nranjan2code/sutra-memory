# Archived Deployment Scripts

These files are **deprecated** and kept for reference only.

## Do NOT Use These Files

All deployment operations should now use the single source of truth:

```bash
../sutra-deploy.sh
```

## Archived Files

- **build-images.sh** - Old image build script → Use `./sutra-deploy.sh build`
- **deploy-optimized.sh** - Old deployment script → Use `./sutra-deploy.sh up`
- **deploy-docker-grid.sh** - Old Grid deployment → Use `./sutra-deploy.sh install`
- **docker-compose.yml** - Original compose file → Use `docker-compose-grid.yml`
- **docker-compose-v2.yml** - Version 2 compose → Use `docker-compose-grid.yml`

## Migration

If you were using any of these files, migrate to the new single deployment script:

```bash
# Old way
./build-images.sh
./deploy-optimized.sh

# New way
./sutra-deploy.sh install
```

See `../DEPLOYMENT.md` for complete documentation.

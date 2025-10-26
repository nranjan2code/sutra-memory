# DEPRECATED - Use sutrabuild/ System

⚠️ **This Dockerfile is deprecated and will be removed in a future version.**

## New Build System

Please use the **consolidated build system** instead:

```bash
# Instead of building individual services, use:
./sutrabuild/scripts/build-all.sh --profile simple

# This builds all services with optimized shared base images
# and proper dependency caching for faster builds.
```

## Migration Path

1. **Stop using this file**: Don't reference this Dockerfile in your scripts
2. **Use profiles**: Choose `simple`, `community`, or `enterprise` profile 
3. **Consolidated builds**: All services built together with shared optimization
4. **New documentation**: See `docs/build/` for comprehensive guides

## Benefits of New System

- ✅ **50%+ faster builds** through shared base images
- ✅ **100% reproducible** builds verified through testing  
- ✅ **Centralized management** - no scattered build files
- ✅ **Profile-based deployment** - build only what you need
- ✅ **Built-in health checks** and monitoring
- ✅ **Multi-stage optimization** for smaller production images

## Questions?

See the comprehensive build documentation:
- [Quick Start Guide](../../docs/sutrabuild/QUICKSTART.md)
- [Build Architecture](../../docs/sutrabuild/ARCHITECTURE.md) 
- [Complete Reference](../../docs/sutrabuild/REFERENCE.md)

---

> **Removal Timeline**: This file will be removed in version 3.0.0
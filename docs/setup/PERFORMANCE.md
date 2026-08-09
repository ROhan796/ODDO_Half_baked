# Performance Optimization Guide

## Overview

This guide covers database indexing, query optimization, caching strategies, and frontend performance tuning for Reprico.

## Problem Statement

The app is loading too slowly. Key bottlenecks:
1. Uncached database queries on every page load
2. Missing indexes on frequently queried columns
3. N+1 query patterns in list endpoints
4. Large payload sizes (no pagination limits)
5. No connection pooling optimization

## 1. Database Indexing

### High-Impact Indexes

```sql
-- ===========================================
-- USER TABLE INDEXES
-- ===========================================
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_phone ON users(phone);
CREATE INDEX CONCURRENTLY idx_users_role ON users(role);
CREATE INDEX CONCURRENTLY idx_users_kyc_status ON users(kyc_status);
CREATE INDEX CONCURRENTLY idx_users_trust_tier ON users(trust_tier);
CREATE INDEX CONCURRENTLY idx_users_created_at ON users(created_at);

-- ===========================================
-- PRODUCT TABLE INDEXES
-- ===========================================
CREATE INDEX CONCURRENTLY idx_products_category ON products(category_id);
CREATE INDEX CONCURRENTLY idx_products_status ON products(status);
CREATE INDEX CONCURRENTLY idx_products_slug ON products(slug);
CREATE INDEX CONCURRENTLY idx_products_daily_rate ON products(daily_rate);
CREATE INDEX CONCURRENTLY idx_products_condition ON products(condition_rating);

-- Composite index for catalog queries
CREATE INDEX CONCURRENTLY idx_products_cat_status ON products(category_id, status);
CREATE INDEX CONCURRENTLY idx_products_status_rate ON products(status, daily_rate);

-- ===========================================
-- RENTAL TABLE INDEXES
-- ===========================================
CREATE INDEX CONCURRENTLY idx_rentals_user ON rentals(user_id);
CREATE INDEX CONCURRENTLY idx_rentals_status ON rentals(status);
CREATE INDEX CONCURRENTLY idx_rentals_dates ON rentals(start_date, end_date);
CREATE INDEX CONCURRENTLY idx_rentals_created ON rentals(created_at);

-- Composite for dashboard queries
CREATE INDEX CONCURRENTLY idx_rentals_status_date ON rentals(status, created_at);
CREATE INDEX CONCURRENTLY idx_rentals_user_status ON rentals(user_id, status);

-- ===========================================
-- INVOICE TABLE INDEXES
-- ===========================================
CREATE INDEX CONCURRENTLY idx_invoices_rental ON invoices(rental_id);
CREATE INDEX CONCURRENTLY idx_invoices_status ON invoices(status);
CREATE INDEX CONCURRENTLY idx_invoices_user ON invoices(user_id);
CREATE INDEX CONCURRENTLY idx_invoices_due_date ON invoices(due_date);

-- ===========================================
-- PAYMENT TABLE INDEXES
-- ===========================================
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_razorpay_order ON payments(razorpay_order_id);

-- ===========================================
-- DEPOSIT TABLE INDEXES
-- ===========================================
CREATE INDEX idx_deposits_user ON security_deposits(user_id);
CREATE INDEX idx_deposits_rental ON security_deposits(rental_id);
CREATE INDEX idx_deposits_status ON security_deposits(status);

-- ===========================================
-- AUDIT LOG INDEXES (audit schema)
-- ===========================================
CREATE INDEX idx_audit_user ON audit.audit_logs(user_id);
CREATE INDEX idx_audit_entity ON audit.audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created ON audit.audit_logs(created_at);
CREATE INDEX idx_audit_action ON audit.audit_logs(action);

-- ===========================================
-- NOTIFICATION INDEXES
-- ===========================================
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created ON notifications(created_at);

-- ===========================================
-- CRM INDEXES
-- ===========================================
CREATE INDEX idx_crm_contacts_email ON crm_contacts(email);
CREATE INDEX idx_crm_contacts_phone ON crm_contacts(phone);
CREATE INDEX idx_crm_interactions_contact ON crm_interactions(contact_id);
CREATE INDEX idx_crm_interactions_created ON crm_interactions(created_at);

-- ===========================================
-- STOCK INDEXES
-- ===========================================
CREATE INDEX idx_stock_levels_product ON stock_levels(product_id);
CREATE INDEX idx_stock_levels_location ON stock_levels(location_id);
CREATE INDEX idx_stock_movements_product ON stock_movements(product_id);
CREATE INDEX idx_stock_movements_date ON stock_movements(created_at);
```

### Partial Indexes (For Status Filtering)

```sql
-- Only index active rentals (most queried)
CREATE INDEX idx_rentals_active ON rentals(created_at)
WHERE status IN ('active', 'overdue');

-- Only index unpaid invoices
CREATE INDEX idx_invoices_unpaid ON invoices(due_date)
WHERE status IN ('pending', 'overdue');

-- Only index unread notifications
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at)
WHERE is_read = false;
```

### Index Maintenance

```bash
# Find missing indexes (run monthly)
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE tablename IN ('users', 'products', 'rentals', 'invoices')
AND n_distinct > 100
ORDER BY n_distinct DESC;

# Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

# Reindex bloated indexes
REINDEX INDEX CONCURRENTLY idx_users_email;
```

## 2. Query Optimization

### Eliminate N+1 Queries

```python
# BAD: N+1 queries
for rental in rentals:
    user = await db.get(User, rental.user_id)      # Query per rental
    product = await db.get(Product, rental.product_id)  # Query per rental

# GOOD: Single join query
from sqlalchemy.orm import selectinload

stmt = (
    select(Rental)
    .options(selectinload(Rental.user))
    .options(selectinload(Rental.product))
    .where(Rental.status == "active")
)
result = await db.execute(stmt)
rentals = result.scalars().all()
```

### Use Read Replicas for Lists

```python
# Reads go to replica (less load on primary)
async def list_rentals(
    db: AsyncSession = Depends(get_read_db),  # ← Read replica
    skip: int = 0,
    limit: int = 20,
):
    stmt = select(Rental).offset(skip).limit(limit)
    return await db.execute(stmt)
```

### Pagination Everywhere

```python
# Always paginate list endpoints
@router.get("/")
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = None,
    status: str = "available",
):
    offset = (page - 1) * page_size

    # Count query (cached)
    total = await cache.get_or_set(
        f"products:count:{category}:{status}",
        lambda: count_products(db, category, status),
        ttl=300,
    )

    # Data query (cached)
    products = await cache.get_or_set(
        f"products:{page}:{page_size}:{category}:{status}",
        lambda: fetch_products(db, offset, page_size, category, status),
        ttl=300,
    )

    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size),
    }
```

## 3. Caching Strategy

### Cache Layers

```
┌─────────────────────────────────────┐
│        LAYER 1: Browser Cache       │
│  Static assets, API responses       │
│  TTL: 5-60 minutes                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        LAYER 2: CDN (Cloudflare)    │
│  Product images, static files       │
│  TTL: 24 hours                      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        LAYER 3: Redis Cache         │
│  API responses, sessions, queries   │
│  TTL: 5 minutes - 1 hour            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        LAYER 4: Database            │
│  Source of truth                    │
└─────────────────────────────────────┘
```

### Cache Patterns

```python
# Pattern 1: Cache-Aside (Lazy Loading)
async def get_product(product_id: str):
    # Check cache first
    cached = await cache.get(f"product:{product_id}")
    if cached:
        return cached

    # Cache miss - query DB
    product = await db.get(Product, product_id)
    await cache.set(f"product:{product_id}", product, ttl=3600)
    return product

# Pattern 2: @cached decorator
@cached(prefix="dashboard_stats", ttl=300)
async def get_dashboard_stats(db):
    # This result is cached for 5 minutes
    return await compute_stats(db)

# Pattern 3: Cache Invalidation
async def update_product(product_id: str, data: dict):
    product = await db.get(Product, product_id)
    # ... update logic ...
    await db.commit()

    # Invalidate related caches
    await cache.delete(f"product:{product_id}")
    await cache.invalidate_pattern("products:*")
    await cache.invalidate_pattern("catalog:*")
```

### Cache TTLs

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Product catalog | 1 hour | Changes rarely |
| Dashboard stats | 5 minutes | Needs freshness |
| Rental listings | 5 minutes | User-specific |
| User sessions | 15 minutes | Security balance |
| OTP codes | 5 minutes | Security requirement |
| Rate limits | 1 minute | Sliding window |
| Search results | 10 minutes | Expensive to compute |

## 4. Frontend Performance

### Next.js Optimizations

```typescript
// 1. Use React Server Components (default in Next.js 15)
// app/catalog/page.tsx
export default async function CatalogPage() {
  const products = await fetchProducts(); // Server-side
  return <ProductGrid products={products} />;
}

// 2. Use dynamic imports for heavy components
import dynamic from 'next/dynamic';
const MapView = dynamic(() => import('@/components/common/MapView'), {
  loading: () => <MapSkeleton />,
  ssr: false,
});

// 3. Image optimization
import Image from 'next/image';
<Image
  src={product.image_url}
  alt={product.name}
  width={400}
  height={300}
  placeholder="blur"
  blurDataURL={product.blur_hash}
/>

// 4. Prefetch routes
<Link href={`/product/${id}`} prefetch={true}>View</Link>
```

### API Query Optimization

```typescript
// 1. Debounce search
const debouncedSearch = useDebouncedCallback(
  (query: string) => searchProducts(query),
  300
);

// 2. Infinite scroll for large lists
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['products'],
  queryFn: ({ pageParam }) => fetchProducts(pageParam),
  getNextPageParam: (lastPage) => lastPage.nextCursor,
});

// 3. Optimistic updates
const mutation = useMutation({
  mutationFn: updateRental,
  onMutate: async (newData) => {
    await queryClient.cancelQueries(['rentals']);
    const previous = queryClient.getQueryData(['rentals']);
    queryClient.setQueryData(['rentals'], old => [...old, newData]);
    return { previous };
  },
  onError: (err, newData, context) => {
    queryClient.setQueryData(['rentals'], context.previous);
  },
});
```

### Bundle Size Optimization

```bash
# Analyze bundle
ANALYZE=true npm run build

# Check for large dependencies
npx next-bundle-analyzer
```

## 5. Connection Pool Tuning

### NeonDB Optimized Settings

```python
# app/utils/database.py
primary_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,              # NeonDB handles pooling server-side
    max_overflow=20,           # Burst capacity
    pool_timeout=30,           # Wait time
    pool_pre_ping=True,        # Validate before use
    pool_recycle=3600,         # Recycle connections hourly
    echo=False,                # Disable in production
)
```

### NeonDB Serverless Tips

1. **Use `pool_pre_ping=True`** - NeonDB suspends compute, connections may be stale
2. **Set `pool_recycle=3600`** - Recycle connections before NeonDB timeout
3. **Keep pool small** - NeonDB has its own pooling; duplicate pooling wastes resources
4. **Use prepared_statement_cache_size=0** - In connection string for serverless

## 6. Monitoring Performance

### Slow Query Detection

```python
# Add to database.py
import logging

slow_query_logger = logging.getLogger("sqlalchemy.slow")
slow_query_logger.setLevel(logging.WARNING)

# Log queries > 1 second
@event.listens_for(AsyncEngine, "before_cursor_execute")
def log_slow_queries(conn, cursor, statement, parameters, context, executemany):
    import time
    start = time.time()
    # ... after execution
    duration = time.time() - start
    if duration > 1.0:
        slow_query_logger.warning(f"Slow query ({duration:.2f}s): {statement}")
```

### Performance Metrics

```python
# app/middleware/performance.py
import time
from starlette.middleware.base import BaseHTTPMiddleware

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        response.headers["X-Response-Time"] = f"{duration:.4f}s"

        if duration > 2.0:
            # Log slow endpoint
            logger.warning(
                f"Slow endpoint: {request.method} {request.url.path} "
                f"took {duration:.2f}s"
            )

        return response
```

## Performance Checklist

- [ ] All list endpoints have pagination
- [ ] All frequently queried columns have indexes
- [ ] N+1 queries eliminated (use eager loading)
- [ ] Redis cache for dashboard stats (5min TTL)
- [ ] Redis cache for product listings (1hr TTL)
- [ ] Read replica for all GET endpoints
- [ ] Connection pool tuned for NeonDB
- [ ] Frontend uses React Server Components
- [ ] Images optimized with Next.js Image
- [ ] API responses compressed (gzip)
- [ ] Static assets served via CDN
- [ ] Database connections recycled
- [ ] Slow queries logged and optimized

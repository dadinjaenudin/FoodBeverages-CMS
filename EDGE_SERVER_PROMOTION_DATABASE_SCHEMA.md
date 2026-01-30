# Edge Server - Promotion Database Schema

## Overview
Database schema untuk Edge Server (POS) untuk menyimpan promotion data yang di-sync dari CMS.

**Design Principles:**
- ✅ Offline-capable (SQLite/PostgreSQL)
- ✅ Fast query performance
- ✅ Minimal storage footprint
- ✅ Easy to sync and update

---

## Table Structure

### 1. `promotions` (Main Table)

Stores all promotion data in denormalized format for fast querying.

```sql
CREATE TABLE promotions (
    -- Primary Key
    id VARCHAR(36) PRIMARY KEY,  -- UUID from CMS
    
    -- Basic Info
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    terms_conditions TEXT,
    
    -- Multi-tenant Context (CRITICAL for filtering)
    company_id VARCHAR(36) NOT NULL,
    brand_id VARCHAR(36) NOT NULL,
    store_id VARCHAR(36) NOT NULL,
    
    -- Type & Configuration
    promo_type VARCHAR(50) NOT NULL,  -- percent_discount, buy_x_get_y, etc.
    apply_to VARCHAR(20) NOT NULL,    -- all, category, product
    execution_stage VARCHAR(20) NOT NULL,  -- item_level, cart_level, payment_level
    execution_priority INTEGER DEFAULT 500,
    
    -- Flags
    is_active BOOLEAN DEFAULT TRUE,
    is_auto_apply BOOLEAN DEFAULT FALSE,
    require_voucher BOOLEAN DEFAULT FALSE,
    member_only BOOLEAN DEFAULT FALSE,
    is_stackable BOOLEAN DEFAULT FALSE,
    
    -- Validity (Denormalized for fast filtering)
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    time_start TIME,
    time_end TIME,
    valid_days TEXT,  -- JSON array: ["monday", "tuesday"]
    exclude_holidays BOOLEAN DEFAULT FALSE,
    
    -- Rules (JSON - Full promotion rules)
    rules_json TEXT NOT NULL,  -- JSON string of all rules
    
    -- Scope (JSON - Product/Category targeting)
    scope_json TEXT,  -- JSON string of scope rules
    
    -- Targeting (JSON - Store/Brand/Customer targeting)
    targeting_json TEXT,  -- JSON string of targeting rules
    
    -- Limits
    max_uses INTEGER,
    max_uses_per_customer INTEGER,
    max_uses_per_day INTEGER,
    current_uses INTEGER DEFAULT 0,
    
    -- Metadata
    compiled_at TIMESTAMP NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    
    -- Indexes for fast querying
    INDEX idx_company_store (company_id, store_id),
    INDEX idx_brand (brand_id),
    INDEX idx_active_dates (is_active, start_date, end_date),
    INDEX idx_promo_type (promo_type),
    INDEX idx_code (code)
);
```

---

### 2. `promotion_usage` (Usage Tracking)

Tracks promotion usage for limits enforcement.

```sql
CREATE TABLE promotion_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- References
    promotion_id VARCHAR(36) NOT NULL,
    promotion_code VARCHAR(50) NOT NULL,
    
    -- Transaction Info
    transaction_id VARCHAR(36) NOT NULL,
    order_number VARCHAR(50),
    
    -- Customer Info (if applicable)
    customer_id VARCHAR(36),
    customer_phone VARCHAR(20),
    member_tier VARCHAR(50),
    
    -- Usage Details
    discount_amount DECIMAL(15,2) NOT NULL,
    original_amount DECIMAL(15,2) NOT NULL,
    final_amount DECIMAL(15,2) NOT NULL,
    
    -- Context
    brand_id VARCHAR(36) NOT NULL,
    store_id VARCHAR(36) NOT NULL,
    
    -- Timestamp
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_date DATE NOT NULL,
    
    -- Indexes
    INDEX idx_promotion_usage (promotion_id, usage_date),
    INDEX idx_customer_usage (promotion_id, customer_id, usage_date),
    INDEX idx_transaction (transaction_id),
    
    FOREIGN KEY (promotion_id) REFERENCES promotions(id) ON DELETE CASCADE
);
```

---

### 3. `promotion_sync_log` (Sync History)

Tracks sync operations for debugging and monitoring.

```sql
CREATE TABLE promotion_sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Sync Info
    sync_type VARCHAR(20) NOT NULL,  -- full, incremental, manual
    sync_status VARCHAR(20) NOT NULL,  -- success, failed, partial
    
    -- Statistics
    promotions_received INTEGER DEFAULT 0,
    promotions_added INTEGER DEFAULT 0,
    promotions_updated INTEGER DEFAULT 0,
    promotions_deleted INTEGER DEFAULT 0,
    
    -- Context
    company_id VARCHAR(36) NOT NULL,
    store_id VARCHAR(36) NOT NULL,
    
    -- Error Info
    error_message TEXT,
    error_details TEXT,
    
    -- Timestamp
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    
    -- Metadata
    cms_version VARCHAR(20),
    edge_version VARCHAR(20),
    
    INDEX idx_sync_date (started_at),
    INDEX idx_sync_status (sync_status)
);
```

---

## Sample Data

### Example: Promotion Record

```sql
INSERT INTO promotions (
    id, code, name, description,
    company_id, brand_id, store_id,
    promo_type, apply_to, execution_stage, execution_priority,
    is_active, is_auto_apply, require_voucher, member_only, is_stackable,
    start_date, end_date, time_start, time_end, valid_days,
    rules_json, scope_json, targeting_json,
    max_uses, max_uses_per_customer, max_uses_per_day, current_uses,
    compiled_at, synced_at
) VALUES (
    '98c93090-79b3-45f9-84e7-f7b802e5405e',
    'DIC10',
    'Diskon 10%',
    'Diskon 10% untuk semua produk',
    '812e76b6-f235-4bb2-948a-cae58ee62b97',  -- company_id
    '4b4c6546-159b-4cd0-96d4-50a763ba12df',  -- brand_id
    'ee90b1f6-2ec2-4b46-8b4a-79d208b3c04c',  -- store_id
    'percent_discount',
    'all',
    'item_level',
    500,
    TRUE, TRUE, FALSE, FALSE, FALSE,
    '2026-01-28', '2026-01-31', NULL, NULL, '[]',
    '{"type":"percent","discount_percent":10,"max_discount_amount":null,"min_purchase":0}',
    '{"apply_to":"all","exclude_categories":[],"exclude_products":[]}',
    '{"stores":["ee90b1f6-2ec2-4b46-8b4a-79d208b3c04c"],"brands":"all","member_only":false,"customer_type":"all"}',
    NULL, NULL, NULL, 0,
    '2026-01-29 22:55:10', '2026-01-30 06:00:00'
);
```

---

## Query Examples

### 1. Get Active Promotions for Current Transaction

```sql
-- Get all active promotions for specific brand at current time
SELECT 
    id, code, name, promo_type, 
    rules_json, scope_json, targeting_json,
    execution_stage, execution_priority
FROM promotions
WHERE company_id = ?
  AND store_id = ?
  AND brand_id = ?
  AND is_active = TRUE
  AND start_date <= CURRENT_DATE
  AND end_date >= CURRENT_DATE
  AND (time_start IS NULL OR time_start <= CURRENT_TIME)
  AND (time_end IS NULL OR time_end >= CURRENT_TIME)
ORDER BY execution_priority ASC, execution_stage ASC;
```

### 2. Check Promotion Usage Limits

```sql
-- Check daily usage for promotion
SELECT COUNT(*) as usage_count
FROM promotion_usage
WHERE promotion_id = ?
  AND usage_date = CURRENT_DATE;

-- Check customer usage
SELECT COUNT(*) as customer_usage
FROM promotion_usage
WHERE promotion_id = ?
  AND customer_id = ?;
```

### 3. Get Promotions by Type

```sql
-- Get all auto-apply promotions
SELECT *
FROM promotions
WHERE company_id = ?
  AND store_id = ?
  AND is_active = TRUE
  AND is_auto_apply = TRUE
  AND start_date <= CURRENT_DATE
  AND end_date >= CURRENT_DATE;
```

### 4. Sync Statistics

```sql
-- Get last sync info
SELECT *
FROM promotion_sync_log
WHERE store_id = ?
ORDER BY started_at DESC
LIMIT 1;

-- Get sync success rate
SELECT 
    COUNT(*) as total_syncs,
    SUM(CASE WHEN sync_status = 'success' THEN 1 ELSE 0 END) as successful,
    AVG(duration_seconds) as avg_duration
FROM promotion_sync_log
WHERE store_id = ?
  AND started_at >= DATE('now', '-7 days');
```

---

## Sync Process Flow

### 1. Full Sync (Initial or Reset)

```python
def full_sync(company_id, store_id):
    """Full sync - replace all promotions"""
    
    # 1. Call CMS API
    response = requests.post(
        'https://cms.example.com/api/v1/sync/promotions/',
        json={
            'company_id': company_id,
            'store_id': store_id
        }
    )
    
    promotions_data = response.json()
    
    # 2. Start transaction
    conn.execute('BEGIN TRANSACTION')
    
    try:
        # 3. Delete old promotions
        conn.execute(
            'DELETE FROM promotions WHERE company_id = ? AND store_id = ?',
            (company_id, store_id)
        )
        
        # 4. Insert new promotions
        for store_id, store_data in promotions_data.items():
            for promo in store_data['promotions']:
                insert_promotion(promo)
        
        # 5. Log sync
        log_sync('full', 'success', len(promotions_data))
        
        conn.execute('COMMIT')
        
    except Exception as e:
        conn.execute('ROLLBACK')
        log_sync('full', 'failed', 0, error=str(e))
        raise
```

### 2. Incremental Sync (Updates Only)

```python
def incremental_sync(company_id, store_id, last_sync_time):
    """Incremental sync - only changed promotions"""
    
    response = requests.post(
        'https://cms.example.com/api/v1/sync/promotions/incremental/',
        json={
            'company_id': company_id,
            'store_id': store_id,
            'last_sync': last_sync_time
        }
    )
    
    changes = response.json()
    
    # Update/Insert changed promotions
    for promo in changes.get('updated', []):
        upsert_promotion(promo)
    
    # Delete removed promotions
    for promo_id in changes.get('deleted', []):
        delete_promotion(promo_id)
```

---

## Performance Optimization

### 1. Indexes

```sql
-- Critical indexes for fast querying
CREATE INDEX idx_active_lookup ON promotions(
    company_id, store_id, brand_id, is_active, start_date, end_date
);

CREATE INDEX idx_execution ON promotions(
    execution_stage, execution_priority
) WHERE is_active = TRUE;
```

### 2. Materialized View (Optional)

```sql
-- Pre-computed active promotions for ultra-fast access
CREATE VIEW active_promotions AS
SELECT *
FROM promotions
WHERE is_active = TRUE
  AND start_date <= CURRENT_DATE
  AND end_date >= CURRENT_DATE;
```

### 3. Caching Strategy

```python
# In-memory cache for frequently accessed promotions
promotion_cache = {
    'auto_apply': [],  # Auto-apply promotions
    'by_type': {},     # Grouped by type
    'by_brand': {}     # Grouped by brand
}

def refresh_cache():
    """Refresh in-memory cache from database"""
    promotion_cache['auto_apply'] = get_auto_apply_promotions()
    # ... refresh other caches
```

---

## Storage Estimates

### Per Promotion:
- Basic fields: ~500 bytes
- JSON fields: ~2-5 KB
- **Total per promotion: ~5-10 KB**

### For 100 Promotions:
- Promotions table: ~500 KB - 1 MB
- Usage tracking (1000 transactions): ~100 KB
- Sync logs (30 days): ~10 KB
- **Total: ~1-2 MB**

**Conclusion:** Very lightweight, suitable for embedded devices!

---

## Migration Script

```sql
-- SQLite Migration Script
-- Run this on Edge Server database

-- Create tables
CREATE TABLE IF NOT EXISTS promotions ( ... );
CREATE TABLE IF NOT EXISTS promotion_usage ( ... );
CREATE TABLE IF NOT EXISTS promotion_sync_log ( ... );

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_company_store ON promotions(company_id, store_id);
CREATE INDEX IF NOT EXISTS idx_brand ON promotions(brand_id);
CREATE INDEX IF NOT EXISTS idx_active_dates ON promotions(is_active, start_date, end_date);

-- Create views
CREATE VIEW IF NOT EXISTS active_promotions AS ...;
```

---

## API Integration Example

```python
# Edge Server - Sync Service

class PromotionSyncService:
    def __init__(self, db_path, cms_url, company_id, store_id):
        self.db = sqlite3.connect(db_path)
        self.cms_url = cms_url
        self.company_id = company_id
        self.store_id = store_id
    
    def sync_promotions(self):
        """Sync promotions from CMS"""
        try:
            # Call CMS API
            response = requests.post(
                f'{self.cms_url}/api/v1/sync/promotions/',
                json={
                    'company_id': self.company_id,
                    'store_id': self.store_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self._update_database(data)
                return True
            else:
                self._log_error(f'Sync failed: {response.status_code}')
                return False
                
        except Exception as e:
            self._log_error(f'Sync error: {str(e)}')
            return False
    
    def _update_database(self, data):
        """Update local database with synced data"""
        cursor = self.db.cursor()
        
        for store_id, store_data in data.items():
            for promo in store_data['promotions']:
                cursor.execute('''
                    INSERT OR REPLACE INTO promotions (
                        id, code, name, company_id, brand_id, store_id,
                        promo_type, rules_json, ...
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ...)
                ''', (
                    promo['id'],
                    promo['code'],
                    promo['name'],
                    promo['company_id'],
                    promo['brand_id'],
                    promo['store_id'],
                    promo['promo_type'],
                    json.dumps(promo['rules']),
                    # ... other fields
                ))
        
        self.db.commit()
```

---

## Summary

**Edge Server Database Design:**
- ✅ 3 main tables: `promotions`, `promotion_usage`, `promotion_sync_log`
- ✅ Denormalized for fast querying
- ✅ JSON fields for complex rules
- ✅ Indexed for performance
- ✅ Lightweight (~1-2 MB for 100 promotions)
- ✅ Offline-capable
- ✅ Easy to sync and update

**Ready for production deployment!** 🚀

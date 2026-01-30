# Promotion System - Complete Features Documentation

**Version:** 1.0  
**Date:** 2026-01-27  
**Status:** Production Ready  
**System:** Food & Beverages CMS - Promotion Engine

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Core Features](#core-features)
3. [Promotion Types (12 Types)](#promotion-types)
4. [Cross-Brand Promotions](#cross-brand-promotions)
5. [Scope & Targeting](#scope-and-targeting)
6. [Advanced Features](#advanced-features)
7. [Business Rules](#business-rules)
8. [Use Cases & Examples](#use-cases-and-examples)
9. [Implementation Status](#implementation-status)

---

## 🎯 System Overview

### Purpose
A comprehensive promotion management system designed for multi-brand, multi-store food & beverage operations with support for offline POS systems.

### Key Capabilities
- ✅ **12 Promotion Types** - From simple discounts to complex bundling
- ✅ **Cross-Brand Promotions** - Marketing across multiple brands
- ✅ **Flexible Targeting** - Category, product, brand, and store level
- ✅ **Offline-First** - Works without internet at POS
- ✅ **Real-time Calculation** - Instant discount calculation
- ✅ **Stacking Support** - Multiple promotions can combine
- ✅ **Time-Based Rules** - Happy hour, date ranges, day of week

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     HEAD OFFICE (HO)                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Promotion Management (Django CMS)                  │    │
│  │  - Create/Edit Promotions                          │    │
│  │  - Define Rules & Scope                            │    │
│  │  - Compile to JSON                                 │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │ Sync API                                │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                   POS/EDGE DEVICES                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Local SQLite Database                              │    │
│  │  - promotion_cache table                           │    │
│  │  - Compiled promotion rules (JSON)                 │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                         │
│  ┌────────────────▼───────────────────────────────────┐    │
│  │  Promotion Evaluation Engine (JavaScript)          │    │
│  │  - Real-time discount calculation                  │    │
│  │  - Offline-capable                                 │    │
│  │  - Fast performance (<100ms)                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎁 Core Features

### Feature Matrix

| Feature | Status | Description |
|---------|--------|-------------|
| **Multi-Type Promotions** | ✅ Production | 12 different promotion types |
| **Cross-Brand Support** | ✅ Production | Promotions across multiple brands |
| **Category Targeting** | ✅ Production | Apply to specific categories |
| **Product Targeting** | ✅ Production | Apply to specific products |
| **Product Exclusions** | ✅ Production | Exclude specific items |
| **Store Selection** | ✅ Production | Choose specific stores |
| **Brand Selection** | ✅ Production | Choose specific brands |
| **Date Range** | ✅ Production | Start/end dates |
| **Time Range** | ✅ Production | Happy hour support |
| **Day of Week** | ✅ Production | Specific days only |
| **Minimum Purchase** | ✅ Production | Threshold requirements |
| **Member Only** | ✅ Production | Loyalty member exclusive |
| **Max Usage** | ✅ Production | Limit promotion usage |
| **Priority/Stacking** | ✅ Production | Control promotion order |
| **Offline Mode** | ✅ Production | Works without internet |

---

## 💰 Promotion Types

The system supports **12 comprehensive promotion types** to cover all marketing scenarios:

### Summary Table

| # | Type | Code | Complexity | Use Case | Stage |
|---|------|------|------------|----------|-------|
| 1 | Percent Discount | `percent_discount` | ⭐ Simple | 20% off selected items | Item/Subtotal |
| 2 | Amount Discount | `amount_discount` | ⭐ Simple | Rp 10,000 off | Item/Subtotal |
| 3 | Buy X Get Y | `buy_x_get_y` | ⭐⭐ Medium | Buy 2 Get 1 Free | Item Level |
| 4 | Combo Deal | `combo` | ⭐⭐ Medium | 3 items for special price | Item Level |
| 5 | Free Item | `free_item` | ⭐⭐ Medium | Get free dessert | Item Level |
| 6 | Happy Hour | `happy_hour` | ⭐⭐ Medium | Time-based pricing | Item Level |
| 7 | Cashback | `cashback` | ⭐⭐ Medium | Get 10% back as points | Post-Payment |
| 8 | Payment Discount | `payment_discount` | ⭐ Simple | 5% off with specific card | Payment Stage |
| 9 | Package/Set Menu | `package` | ⭐⭐⭐ Complex | Pre-defined meal sets | Item Level |
| 10 | Mix & Match | `mix_match` | ⭐⭐⭐ Complex | Any 3 drinks for Rp 50k | Item Level |
| 11 | Upsell/Add-on | `upsell` | ⭐⭐ Medium | Special price for add-ons | Item Level |
| 12 | Threshold/Tiered | `threshold_tier` | ⭐⭐⭐ Complex | Spend more, save more | Subtotal |

---

### 1️⃣ PERCENT DISCOUNT

**Description:** Apply percentage discount to items or total bill

**Common Use Cases:**
- 20% off all beverages
- 15% off entire bill
- 30% off selected categories

**Configuration:**
```json
{
  "discount_type": "percent_discount",
  "discount_percent": 20.0,
  "discount_max_amount": 100000.0,
  "apply_to": "item_level"
}
```

**Business Rules:**
- ✅ Can apply to specific items, categories, or entire bill
- ✅ Support max cap to prevent excessive discounts
- ✅ Can be combined with other promotions (based on priority)

**Real Example:**
```
Promo: "Weekend Special - 20% Off All Coffee"
- Applies to: Coffee category
- Max discount: Rp 50,000
- Valid: Saturday-Sunday

Customer buys:
- 2 × Espresso @ Rp 25,000 = Rp 50,000
- 1 × Cappuccino @ Rp 30,000 = Rp 30,000

Calculation:
- Subtotal: Rp 80,000
- Discount (20%): Rp 16,000
- Final: Rp 64,000
```

---

### 2️⃣ AMOUNT DISCOUNT

**Description:** Fixed amount discount on items or bill

**Common Use Cases:**
- Rp 10,000 off any main course
- Rp 50,000 off bills above Rp 200,000
- Flat discount promotions

**Configuration:**
```json
{
  "discount_type": "amount_discount",
  "discount_amount": 10000.0,
  "min_purchase": 50000.0,
  "apply_to": "subtotal"
}
```

**Business Rules:**
- ✅ Fixed amount regardless of bill size
- ✅ Can set minimum purchase requirement
- ✅ Simple and easy to understand for customers

**Real Example:**
```
Promo: "Grand Opening - Rp 50,000 Off"
- Min purchase: Rp 200,000
- One-time use per customer

Customer buys:
- Total: Rp 250,000

Calculation:
- Subtotal: Rp 250,000
- Discount: Rp 50,000
- Final: Rp 200,000
```

---

### 3️⃣ BUY X GET Y (BOGO)

**Description:** Buy specified quantity, get additional items free or discounted

**Common Use Cases:**
- Buy 2 Get 1 Free
- Buy 3 Get 2 at 50% off
- Classic BOGO deals

**Configuration:**
```json
{
  "discount_type": "buy_x_get_y",
  "buy_quantity": 2,
  "get_quantity": 1,
  "get_discount_percent": 100.0,
  "same_product_only": true
}
```

**Business Rules:**
- ✅ Can apply to same product or different products
- ✅ Get items can be 100% free or partially discounted
- ✅ Automatically calculates how many sets qualify

**Real Example:**
```
Promo: "Buy 2 Get 1 Free - All Burgers"
- Buy: 2 burgers
- Get: 1 burger free (cheapest)

Customer buys:
- 1 × Premium Burger @ Rp 50,000
- 1 × Classic Burger @ Rp 35,000
- 1 × Mini Burger @ Rp 25,000

Calculation:
- Original total: Rp 110,000
- Free item (cheapest): -Rp 25,000
- Final: Rp 85,000
```

---

### 4️⃣ COMBO DEAL

**Description:** Bundle multiple specific items at special price

**Common Use Cases:**
- Burger + Fries + Drink = Rp 45,000
- Lunch combo deals
- Value meal packages

**Configuration:**
```json
{
  "discount_type": "combo",
  "combo_items": [
    {"product_id": "burger-uuid", "quantity": 1},
    {"product_id": "fries-uuid", "quantity": 1},
    {"product_id": "drink-uuid", "quantity": 1}
  ],
  "combo_price": 45000.0
}
```

**Business Rules:**
- ✅ All items must be in cart to activate
- ✅ Fixed combo price regardless of item choices
- ✅ Can specify exact products or categories

**Real Example:**
```
Promo: "Value Combo Meal"
- 1 × Burger (any) @ Rp 35,000
- 1 × Fries @ Rp 15,000
- 1 × Soft Drink @ Rp 10,000
- Combo price: Rp 45,000

Customer gets:
- Original: Rp 60,000
- Combo: Rp 45,000
- Savings: Rp 15,000
```

---

### 5️⃣ FREE ITEM

**Description:** Get free product when buying specific items

**Common Use Cases:**
- Free dessert with main course
- Free drink with pizza
- Gift with purchase

**Configuration:**
```json
{
  "discount_type": "free_item",
  "trigger_product_id": "main-course-uuid",
  "trigger_min_qty": 1,
  "free_product_id": "dessert-uuid",
  "free_quantity": 1,
  "min_purchase": 100000.0
}
```

**Business Rules:**
- ✅ Trigger product must be in cart
- ✅ Free item auto-added or discounted to Rp 0
- ✅ Can set minimum purchase requirement

**Real Example:**
```
Promo: "Buy Any Steak, Get Free Ice Cream"
- Min purchase: Rp 100,000
- Trigger: Any steak
- Free: 1 × Ice Cream (worth Rp 15,000)

Customer buys:
- 1 × Sirloin Steak @ Rp 125,000

Result:
- Subtotal: Rp 125,000
- Free: 1 × Ice Cream
- Value saved: Rp 15,000
```

---

### 6️⃣ HAPPY HOUR

**Description:** Time-based special pricing

**Common Use Cases:**
- 50% off 2PM-5PM
- Morning coffee specials
- Late-night discounts

**Configuration:**
```json
{
  "discount_type": "happy_hour",
  "time_start": "14:00",
  "time_end": "17:00",
  "discount_percent": 50.0,
  "days_of_week": [1, 2, 3, 4, 5]
}
```

**Business Rules:**
- ✅ Only active during specified time range
- ✅ Can limit to specific days of week
- ✅ Checks system time at transaction moment

**Real Example:**
```
Promo: "Afternoon Delight - 50% Off Coffee"
- Time: 2PM - 5PM
- Days: Monday - Friday
- Category: All coffee

Customer buys at 3:30 PM:
- 2 × Latte @ Rp 30,000 = Rp 60,000

Calculation:
- Time check: 3:30 PM ✓ (within 2PM-5PM)
- Discount (50%): Rp 30,000
- Final: Rp 30,000
```

---

### 7️⃣ CASHBACK

**Description:** Post-payment reward as points, voucher, or wallet credit

**Common Use Cases:**
- 10% cashback as points
- Rp 20,000 back to wallet
- Cashback with specific payment methods

**Configuration:**
```json
{
  "discount_type": "cashback",
  "cashback_type": "percent",
  "cashback_value": 10.0,
  "cashback_max": 50000.0,
  "cashback_method": "points",
  "min_purchase": 100000.0,
  "payment_methods": ["gopay", "ovo"]
}
```

**Business Rules:**
- ✅ Applied after payment is completed
- ✅ Can be points, voucher, or wallet credit
- ✅ Can restrict to specific payment methods
- ✅ Does NOT reduce bill amount (customer pays full)

**Real Example:**
```
Promo: "10% Cashback via GoPay"
- Min purchase: Rp 100,000
- Max cashback: Rp 50,000
- Payment: GoPay only
- Method: Points

Customer transaction:
- Bill total: Rp 250,000
- Payment: GoPay
- Customer pays: Rp 250,000
- Cashback earned: Rp 25,000 (as points)
```

---

### 8️⃣ PAYMENT METHOD DISCOUNT

**Description:** Discount for using specific payment method

**Common Use Cases:**
- 5% off with BCA Card
- Rp 10,000 off with OVO
- E-wallet promotions

**Configuration:**
```json
{
  "discount_type": "payment_discount",
  "payment_method": "bca_card",
  "discount_type": "percent",
  "discount_value": 5.0,
  "max_discount": 100000.0,
  "min_purchase": 50000.0
}
```

**Business Rules:**
- ✅ Applied at payment stage
- ✅ Customer must choose specified payment method
- ✅ Can be percent or fixed amount
- ✅ Reduces final bill amount

**Real Example:**
```
Promo: "5% Off with BCA Credit Card"
- Min purchase: Rp 100,000
- Max discount: Rp 50,000

Customer transaction:
- Bill total: Rp 300,000
- Payment method: BCA Card

Calculation:
- Original: Rp 300,000
- Discount (5%): Rp 15,000
- Final: Rp 285,000
```

---

### 9️⃣ PACKAGE/SET MENU

**Description:** Pre-defined meal set with fixed price

**Common Use Cases:**
- Breakfast package
- Family dinner set
- Complete meal deals

**Configuration:**
```json
{
  "discount_type": "package",
  "package_items": [
    {"product_id": "main-uuid", "quantity": 2},
    {"product_id": "side-uuid", "quantity": 2},
    {"product_id": "drink-uuid", "quantity": 2}
  ],
  "package_price": 150000.0,
  "package_name": "Family Dinner Set"
}
```

**Business Rules:**
- ✅ All items must be in exact quantities
- ✅ Fixed price for the entire package
- ✅ Often sold as a single SKU

**Real Example:**
```
Promo: "Family Package - 4 Persons"
- 2 × Main Course
- 2 × Side Dish
- 4 × Drinks
- Package price: Rp 200,000

Individual prices:
- Main Course: Rp 60,000 × 2 = Rp 120,000
- Side Dish: Rp 20,000 × 2 = Rp 40,000
- Drinks: Rp 15,000 × 4 = Rp 60,000
- Total individual: Rp 220,000
- Package price: Rp 200,000
- Savings: Rp 20,000
```

---

### 🔟 MIX & MATCH

**Description:** Choose N items from category at special price

**Common Use Cases:**
- Any 3 drinks for Rp 50,000
- Pick 5 snacks for Rp 100,000
- Build your own deals

**Configuration:**
```json
{
  "discount_type": "mix_match",
  "category_id": "beverages-uuid",
  "required_quantity": 3,
  "special_price": 50000.0,
  "allow_same_product": true
}
```

**Business Rules:**
- ✅ Customer chooses from eligible items
- ✅ Must meet minimum quantity
- ✅ Can allow or disallow duplicate items
- ✅ Calculates discount based on original prices

**Real Example:**
```
Promo: "Mix & Match - Any 3 Drinks for Rp 50,000"
- Category: All beverages
- Min items: 3
- Any combination allowed

Customer picks:
- 1 × Latte @ Rp 30,000
- 1 × Juice @ Rp 25,000
- 1 × Iced Tea @ Rp 15,000

Calculation:
- Original total: Rp 70,000
- Mix & Match price: Rp 50,000
- Savings: Rp 20,000
```

---

### 1️⃣1️⃣ UPSELL/ADD-ON

**Description:** Special price for add-on items when buying main product

**Common Use Cases:**
- Add fries for only Rp 10,000
- Upgrade drink for Rp 5,000
- Cross-sell promotions

**Configuration:**
```json
{
  "discount_type": "upsell",
  "required_product_id": "burger-uuid",
  "required_min_qty": 1,
  "upsell_product_id": "fries-uuid",
  "special_price": 10000.0,
  "upsell_message": "Add Fries for only Rp 10,000!"
}
```

**Business Rules:**
- ✅ Shows suggestion when main product in cart
- ✅ Special price only when both items present
- ✅ Great for increasing average order value

**Real Example:**
```
Promo: "Add Fries for Rp 10,000 with any Burger"
- Trigger: Buy any burger
- Upsell: French Fries (regular Rp 18,000)
- Special price: Rp 10,000

Scenario:
- Customer adds Burger @ Rp 35,000
- POS suggests: "Add Fries for only Rp 10,000!"
- Customer adds Fries
- Fries price: Rp 18,000 → Rp 10,000
- Savings: Rp 8,000
```

---

### 1️⃣2️⃣ THRESHOLD/TIERED

**Description:** Discount increases with spending level

**Common Use Cases:**
- Spend Rp 100k get 10% off, Rp 200k get 15% off
- Progressive discounts
- Encourage higher spending

**Configuration:**
```json
{
  "discount_type": "threshold_tier",
  "tiers": [
    {"min_amount": 100000.0, "discount_percent": 10.0},
    {"min_amount": 200000.0, "discount_percent": 15.0},
    {"min_amount": 300000.0, "discount_percent": 20.0}
  ]
}
```

**Business Rules:**
- ✅ Automatically applies highest tier customer qualifies for
- ✅ Encourages customers to spend more
- ✅ Clear tier communication needed

**Real Example:**
```
Promo: "Spend More, Save More!"
- Tier 1: Spend ≥ Rp 100k → 10% off
- Tier 2: Spend ≥ Rp 200k → 15% off
- Tier 3: Spend ≥ Rp 300k → 20% off

Customer spends: Rp 250,000
- Qualifies for Tier 2 (15% off)
- Discount: Rp 37,500
- Final: Rp 212,500
```

---


## ?? Cross-Brand Promotions

Cross-brand promotions enable sophisticated marketing strategies across multiple brands within the same company or business group.

### Why Cross-Brand Promotions?

**Business Benefits:**
- ?? **Cross-Selling** - Drive traffic between brands
- ?? **Increase Customer Lifetime Value** - Encourage multi-brand purchases
- ?? **Brand Synergy** - Leverage strength of one brand for another
- ?? **Higher AOV** - Customers spend across multiple brands
- ?? **Customer Retention** - Keep customers within brand ecosystem

### Cross-Brand Types

| Type | Code | Description | Implementation |
|------|------|-------------|----------------|
| Trigger-Benefit | `trigger_benefit` | Buy at Brand A ? Discount at Brand B | Two-stage: trigger + benefit |
| Cross-Brand Bundle | `cross_brand_bundle` | Bundle products from multiple brands | Same receipt validation |
| Same Receipt | `same_receipt` | Buy from 2+ brands ? Discount | Multi-brand detection |
| Multi-Brand Spend | `multi_brand_spend` | Accumulate spend across brands | Backend processing |

---

### ?? Type 1: TRIGGER-BENEFIT

**Description:** Purchase at one brand triggers a benefit at another brand

**Real-World Example:**
```
"Buy Coffee at AVRIL, Get 20% Off at YO-KOPI"
- Trigger Brand: AVRIL
- Benefit Brand: YO-KOPI
- Mechanism: Voucher issued after trigger purchase
```

**How It Works:**

```
Step 1: Customer buys at AVRIL (Trigger Brand)
  +-> Spend = Rp 25,000
  +-> System issues voucher for YO-KOPI

Step 2: Customer shops at YO-KOPI (Benefit Brand)
  +-> Uses voucher
  +-> Gets 20% discount (max Rp 50,000)
  +-> Voucher marked as used
```

**Configuration:**
```json
{
  "discount_type": "percent_discount",
  "is_cross_brand": true,
  "cross_brand_type": "trigger_benefit",
  "trigger_brand_ids": ["brand-uuid-avril"],
  "trigger_min_amount": 25000.0,
  "benefit_brand_ids": ["brand-uuid-yokopi"],
  "benefit_discount_percent": 20.0,
  "benefit_max_discount": 50000.0,
  "voucher_validity_days": 7
}
```

**Business Rules:**
- ? Trigger and benefit must be different brands
- ? Voucher has expiration date
- ? Voucher is single-use
- ? Customer must be logged in (for tracking)
- ? Requires online sync for voucher distribution

**Use Cases:**
- New brand introduction (drive trial)
- Increase cross-brand awareness
- Balance traffic between brands
- Seasonal cross-promotion campaigns

**Real Example:**
```
Campaign: "Coffee Lovers Promo"
- Phase 1: Buy at AVRIL ? Get YO-KOPI voucher
- Phase 2: Buy at YO-KOPI ? Get AVRIL voucher

Customer Journey:
Day 1: Buys Rp 30,000 at AVRIL
  +-> Receives: 20% off voucher for YO-KOPI (valid 7 days)

Day 3: Visits YO-KOPI, spends Rp 100,000
  +-> Uses voucher
  +-> Discount: Rp 20,000
  +-> Pays: Rp 80,000

Result: Customer tried both brands!
```

---

### ?? Type 2: CROSS-BRAND BUNDLE

**Description:** Bundle products from multiple brands in same transaction

**Real-World Example:**
```
"Complete Meal Deal - Main from CHICKEN SUMO + Drink from AVRIL"
- 1 � Chicken (CHICKEN SUMO)
- 1 � Coffee (AVRIL)
- Bundle Price: Rp 150,000 (save Rp 30,000)
```

**How It Works:**

```
Single Receipt:
  +-> Item 1: Chicken (Brand: CHICKEN SUMO) @ Rp 100,000
  +-> Item 2: Latte (Brand: AVRIL) @ Rp 80,000
  +-> Bundle Applied: -Rp 30,000
  
Final: Rp 150,000
```

**Configuration:**
```json
{
  "discount_type": "combo",
  "is_cross_brand": true,
  "cross_brand_type": "cross_brand_bundle",
  "bundle_items": [
    {
      "brand_id": "brand-uuid-chicken-sumo",
      "category_id": "category-uuid-main",
      "quantity": 1
    },
    {
      "brand_id": "brand-uuid-avril",
      "category_id": "category-uuid-beverages",
      "quantity": 1
    }
  ],
  "bundle_price": 150000.0
}
```

**Business Rules:**
- ? All brands must be in same transaction
- ? Requires POS system that supports multi-brand sales
- ? Can specify exact products or categories
- ? Works offline (rules pre-synced)

**Use Cases:**
- Food court scenarios
- Multi-brand outlets
- Complete meal solutions
- Premium bundling strategies

**Real Example:**
```
Promo: "Ultimate Combo - 3 Brands"
- Main Course: CHICKEN SUMO (any item)
- Beverage: AVRIL (any coffee)
- Dessert: SWEET TREATS (any cake)
- Bundle Price: Rp 200,000

Original Prices:
- Chicken Teriyaki: Rp 120,000
- Cappuccino: Rp 65,000
- Chocolate Cake: Rp 45,000
- Total: Rp 230,000

With Bundle: Rp 200,000
Savings: Rp 30,000 (13% off)
```

---

### ?? Type 3: SAME RECEIPT MULTI-BRAND

**Description:** Discount for buying from multiple brands in one transaction

**Real-World Example:**
```
"Shop 2+ Brands, Get 15% Off"
- Customer buys from AVRIL + CHICKEN SUMO
- Automatic 15% discount applied
```

**How It Works:**

```
Cart Analysis:
  +-> Brand 1 (AVRIL): Rp 50,000
  +-> Brand 2 (CHICKEN SUMO): Rp 100,000
  +-> Brand Count: 2 ?

Calculation:
  +-> Subtotal: Rp 150,000
  +-> Discount (15%): Rp 22,500
  +-> Final: Rp 127,500
```

**Configuration:**
```json
{
  "discount_type": "percent_discount",
  "is_cross_brand": true,
  "cross_brand_type": "same_receipt",
  "eligible_brand_ids": ["avril", "chicken-sumo", "yokopi"],
  "min_brands_in_cart": 2,
  "min_purchase": 100000.0,
  "discount_percent": 15.0,
  "max_discount": 100000.0
}
```

**Business Rules:**
- ? Automatically detects brands in cart
- ? Can set minimum spend per brand
- ? Works in real-time at checkout
- ? No voucher needed

**Use Cases:**
- Encourage brand exploration
- Food court promotions
- Multi-brand store locations
- Increase basket size

**Real Example:**
```
Promo: "Mix & Match Brands - 10% Off"
- Min brands: 2
- Min total: Rp 80,000
- Max discount: Rp 50,000

Customer Cart:
- 2 � Coffee (AVRIL): Rp 40,000
- 1 � Fried Chicken (CHICKEN SUMO): Rp 60,000
- 1 � Donut (SWEET TREATS): Rp 20,000

Brands detected: 3 (AVRIL, CHICKEN SUMO, SWEET TREATS) ?
Subtotal: Rp 120,000 ?
Discount (10%): Rp 12,000
Final: Rp 108,000
```

---

### ?? Type 4: MULTI-BRAND SPEND ACCUMULATION

**Description:** Accumulate spending across brands over time to earn rewards

**Real-World Example:**
```
"Spend Rp 50k at 2 Different Brands Within 30 Days ? Get Rp 50k Voucher"
- Track: Customer spending across brands
- Reward: When threshold met
```

**How It Works:**

```
Week 1: Customer spends Rp 60,000 at AVRIL
  +-> Tracked ? (Brand 1)

Week 2: Customer spends Rp 55,000 at CHICKEN SUMO
  +-> Tracked ? (Brand 2)

Backend Processing:
  +-> Brand 1: Rp 60,000 = Rp 50,000 ?
  +-> Brand 2: Rp 55,000 = Rp 50,000 ?
  +-> Brands Count: 2 ?
  +-> Issue Reward: Rp 50,000 Voucher

Customer receives notification + voucher
```

**Configuration:**
```json
{
  "discount_type": "cashback",
  "is_cross_brand": true,
  "cross_brand_type": "multi_brand_spend",
  "eligible_brand_ids": ["avril", "chicken-sumo", "yokopi"],
  "min_brands": 2,
  "min_amount_per_brand": 50000.0,
  "time_window_days": 30,
  "reward_type": "voucher",
  "reward_value": 50000.0,
  "reward_validity_days": 30
}
```

**Business Rules:**
- ? Requires backend processing (not real-time)
- ? Customer must be logged in (member)
- ? Tracks across all transactions
- ? Sends notification when qualified
- ? Requires online sync for tracking

**Use Cases:**
- Long-term loyalty building
- Encourage repeat purchases across brands
- Customer retention programs
- VIP/membership rewards

**Real Example:**
```
Campaign: "Brand Explorer Challenge"
- Period: 30 days
- Mission: Spend Rp 100k at 3 different brands
- Reward: Rp 100k voucher (valid 60 days)

Customer Activity:
- Week 1: AVRIL ? Rp 120,000 (1/3 brands) ?
- Week 2: CHICKEN SUMO ? Rp 150,000 (2/3 brands) ?
- Week 3: YO-KOPI ? Rp 110,000 (3/3 brands) ?

Result:
  +-> Challenge completed! 
  +-> Reward issued: Rp 100,000 voucher
  +-> Notification sent via app
  +-> Can use at any participating brand
```

---

### ?? Cross-Brand Implementation Flow

#### **For POS/Edge Device:**

```
1. SYNC PROMOTION DATA
   +-> Download cross-brand promotion rules
   +-> Store in local database
   +-> Include brand ID mappings

2. TRANSACTION PROCESSING
   +-> Check items in cart
   +-> Detect brands present
   +-> Apply cross-brand rules
   +-> Calculate discounts

3. VOUCHER HANDLING
   +-> Issue vouchers (if trigger met)
   +-> Store locally with expiry
   +-> Sync to HO when online
   +-> Validate vouchers at redemption

4. UPLOAD TRANSACTION DATA
   +-> Send transaction to HO
   +-> Include brand participation
   +-> For accumulation tracking
```

#### **For Head Office:**

```
1. PROMOTION SETUP
   +-> Configure cross-brand rules
   +-> Define trigger & benefit brands
   +-> Set validity periods
   +-> Compile to JSON

2. DISTRIBUTION
   +-> Push to all POS devices
   +-> Sync vouchers to customers
   +-> Update in real-time

3. TRACKING & ANALYTICS
   +-> Monitor cross-brand transactions
   +-> Track voucher issuance/usage
   +-> Process accumulation rules
   +-> Generate reports

4. REWARD PROCESSING
   +-> Background jobs check qualifications
   +-> Issue rewards automatically
   +-> Send notifications
   +-> Sync vouchers to POS
```

---

### ?? Cross-Brand Configuration Checklist

#### **Setup Requirements:**
- ? Multi-brand support in POS system
- ? Customer identification (login/membership)
- ? Voucher management system
- ? Online sync capability
- ? Brand ID in all products

#### **Data Requirements:**
- ? Brand hierarchy (company ? brand)
- ? Cross-brand promotion rules
- ? Voucher storage (local + cloud)
- ? Transaction tracking by brand

#### **Business Rules:**
- ? Define eligible brands
- ? Set trigger conditions
- ? Configure benefit rules
- ? Establish validity periods
- ? Set usage limits

---

### ?? Cross-Brand Best Practices

#### **1. Clear Communication**
```
? Bad: "Get discount at another store"
? Good: "Buy at AVRIL, Get 20% off at YO-KOPI (valid 7 days)"
```

#### **2. Simple Mechanics**
- Start with trigger-benefit (easiest to understand)
- Use same-receipt for food courts
- Save accumulation for loyal customers

#### **3. Brand Alignment**
- Pair complementary brands (coffee + bakery)
- Consider customer journey (breakfast ? lunch)
- Match brand positioning (premium + premium)

#### **4. Technology Readiness**
- Test voucher sync thoroughly
- Ensure offline capability for basic rules
- Have fallback for network issues

#### **5. Performance Monitoring**
- Track cross-brand conversion rates
- Monitor voucher usage rates
- Measure impact on AOV (Average Order Value)
- Analyze brand affinity

---

## ?? Scope & Targeting

Powerful targeting capabilities allow precise control over where, when, and to whom promotions apply.

### Targeting Dimensions

| Dimension | Description | Examples |
|-----------|-------------|----------|
| **Apply To (Scope)** | What products/categories | All products, Category, Specific products |
| **Store Selection** | Which locations | All stores, Selected stores, Store groups |
| **Brand Selection** | Which brands | Single brand, Multiple brands, All brands |
| **Customer Targeting** | Who can use | All customers, Members only, VIP tier |
| **Time-Based** | When active | Date range, Time of day, Days of week |
| **Usage Limits** | How many times | Per customer, Per promotion, Global limit |

---

### ?? Apply To Scope

**Three Scope Levels:**

#### **1. ALL PRODUCTS (Subtotal Level)**
```json
{
  "apply_to": "all",
  "scope_type": "subtotal"
}
```

**When to Use:**
- Store-wide sales
- Grand opening promotions
- End-of-season clearance

**Example:**
```
"15% Off Everything!"
- Applies to entire bill
- No product restrictions
- Simple and broad
```

---

#### **2. CATEGORY LEVEL**
```json
{
  "apply_to": "category",
  "apply_to_categories": [
    "category-uuid-beverages",
    "category-uuid-desserts"
  ],
  "scope_type": "item_level"
}
```

**When to Use:**
- Category promotions (e.g., "Coffee Happy Hour")
- Department sales
- Seasonal product focus

**Example:**
```
"30% Off All Beverages"
- Applies to: Coffee, Tea, Juice, Smoothies
- Does not apply to: Food items
```

**Advanced: Category Exclusions**
```json
{
  "apply_to": "category",
  "apply_to_categories": ["all-food"],
  "exclude_categories": ["premium-steaks"]
}
```

---

#### **3. PRODUCT LEVEL**
```json
{
  "apply_to": "product",
  "apply_to_products": [
    "product-uuid-latte",
    "product-uuid-cappuccino",
    "product-uuid-americano"
  ],
  "scope_type": "item_level"
}
```

**When to Use:**
- Specific product promotions
- Overstocked items
- New product launches
- Premium product bundling

**Example:**
```
"Buy 2 Get 1 Free - Signature Coffees Only"
- Latte ?
- Cappuccino ?
- Americano ?
- Other drinks ?
```

**Advanced: Product Exclusions**
```json
{
  "apply_to": "category",
  "apply_to_categories": ["beverages"],
  "exclude_products": ["product-uuid-premium-blend"]
}
```

**Result:** All beverages except Premium Blend

---

### ?? Store Selection

**Three Selection Modes:**

#### **1. ALL STORES**
```json
{
  "store_selection": "all"
}
```

**When to Use:**
- National campaigns
- Brand-wide promotions
- Consistent pricing

---

#### **2. SELECTED STORES**
```json
{
  "store_selection": "selected",
  "selected_stores": [
    "store-uuid-jakarta-1",
    "store-uuid-jakarta-2",
    "store-uuid-bandung-1"
  ]
}
```

**When to Use:**
- Regional promotions
- Store anniversary sales
- Location-specific campaigns
- Test markets

**Example:**
```
"Jakarta Exclusive - 20% Off Weekends"
- Applies to: 3 Jakarta stores only
- Other stores: Not eligible
```

---

#### **3. STORE GROUPS/AREAS**
```json
{
  "store_selection": "group",
  "store_groups": ["jabodetabek", "west-java"]
}
```

**When to Use:**
- Regional marketing
- Area-specific competitions
- Franchise group promotions

---

### ??? Brand Selection

**For Multi-Brand Operations:**

#### **1. SINGLE BRAND**
```json
{
  "brand": "brand-uuid-avril",
  "is_cross_brand": false
}
```

**Most Common:** Standard promotion for one brand

---

#### **2. MULTIPLE BRANDS (Same Promotion)**
```json
{
  "brands": [
    "brand-uuid-avril",
    "brand-uuid-yokopi"
  ],
  "is_cross_brand": false
}
```

**When to Use:**
- Sister brand promotions
- Company-wide campaigns
- Consolidated marketing

**Example:**
```
"Coffee Brands Weekend Sale"
- AVRIL: 20% off ?
- YO-KOPI: 20% off ?
- Same promotion, different brands
```

---

#### **3. CROSS-BRAND**
```json
{
  "is_cross_brand": true,
  "cross_brand_type": "trigger_benefit",
  "trigger_brands": ["brand-uuid-avril"],
  "benefit_brands": ["brand-uuid-yokopi"]
}
```

**See Cross-Brand Section** for detailed implementation

---

### ?? Customer Targeting

#### **1. ALL CUSTOMERS**
```json
{
  "is_member_only": false,
  "customer_tier": null
}
```

**When to Use:**
- Public promotions
- Customer acquisition
- Mass marketing

---

#### **2. MEMBERS ONLY**
```json
{
  "is_member_only": true,
  "requires_login": true
}
```

**When to Use:**
- Loyalty rewards
- Member appreciation
- Encourage sign-ups

**Benefits:**
- Trackable (customer ID)
- Can limit usage per customer
- Build customer database

---

#### **3. TIERED MEMBERS**
```json
{
  "is_member_only": true,
  "customer_tiers": ["gold", "platinum"],
  "min_tier_level": 2
}
```

**When to Use:**
- VIP exclusive deals
- Tier benefits
- Premium rewards

**Example:**
```
"Platinum Members - 30% Off All Items"
- Gold: ? Not eligible
- Platinum: ? Eligible
- Diamond: ? Eligible
```

---

### ?? Time-Based Targeting

#### **1. DATE RANGE**
```json
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-14",
  "is_active": true
}
```

**When to Use:**
- Valentine's Day campaigns
- Holiday promotions
- Limited-time offers
- Seasonal sales

**Example:**
```
"Chinese New Year Sale"
- Start: Feb 1, 2026
- End: Feb 14, 2026
- Auto-activate and deactivate
```

---

#### **2. TIME OF DAY (Happy Hour)**
```json
{
  "time_start": "14:00",
  "time_end": "17:00",
  "timezone": "Asia/Jakarta"
}
```

**When to Use:**
- Off-peak promotions
- Morning coffee specials
- Late-night deals
- Traffic management

**Example:**
```
"Afternoon Delight - 50% Off Coffee"
- Time: 2PM - 5PM
- Every day
- Increase afternoon traffic
```

---

#### **3. DAYS OF WEEK**
```json
{
  "days_of_week": [1, 2, 3, 4, 5],
  "description": "Monday-Friday only"
}
```

**When to Use:**
- Weekday lunch promotions
- Weekend specials
- Traffic balancing

**Day Mapping:**
- 1 = Monday
- 2 = Tuesday
- 3 = Wednesday
- 4 = Thursday
- 5 = Friday
- 6 = Saturday
- 7 = Sunday

**Example:**
```
"Weekday Breakfast Deal"
- Days: Mon-Fri (1-5)
- Time: 7AM-10AM
- 20% off breakfast items
```

---

#### **4. COMBINED TIME RULES**
```json
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "time_start": "17:00",
  "time_end": "21:00",
  "days_of_week": [6, 7]
}
```

**Example:**
```
"February Weekend Dinner Special"
- Period: February 2026
- Time: 5PM - 9PM
- Days: Saturday & Sunday only
```

---

### ?? Usage Limits

#### **1. GLOBAL LIMIT**
```json
{
  "max_usage_count": 1000,
  "current_usage": 0
}
```

**When to Use:**
- First 100 customers
- Limited stock promotions
- Budget-controlled campaigns

**Example:**
```
"First 100 Customers - Free Gift"
- Total vouchers: 100
- Once limit reached ? auto-deactivate
```

---

#### **2. PER CUSTOMER LIMIT**
```json
{
  "max_usage_per_customer": 1,
  "requires_login": true
}
```

**When to Use:**
- One-time new customer discount
- Prevent abuse
- Fair distribution

**Example:**
```
"New Member Welcome - Rp 50k Off"
- Limit: 1 per customer
- Requires membership signup
```

---

#### **3. PER TRANSACTION LIMIT**
```json
{
  "max_items_per_transaction": 5,
  "max_discount_per_transaction": 100000.0
}
```

**When to Use:**
- Prevent bulk purchases
- Control discount amounts
- Budget protection

**Example:**
```
"Buy 1 Get 1 Free - Max 5 items"
- Customer can get max 5 free items per transaction
- Multiple transactions allowed
```

---

#### **4. TIME-BASED LIMITS**
```json
{
  "max_usage_per_customer": 3,
  "usage_period": "monthly",
  "reset_on_period_end": true
}
```

**When to Use:**
- Recurring promotions
- Monthly rewards
- Subscription-like benefits

**Example:**
```
"Member Monthly Benefit"
- 20% off discount
- Max 3 times per month
- Resets on 1st of each month
```

---

### ?? Advanced Targeting Combinations

#### **Example 1: Hyper-Targeted Promotion**
```json
{
  "name": "VIP Lunch Special - Jakarta Premium Stores",
  "apply_to": "category",
  "categories": ["main-course", "beverages"],
  "store_selection": "selected",
  "stores": ["jakarta-central", "jakarta-south"],
  "is_member_only": true,
  "customer_tiers": ["platinum", "diamond"],
  "days_of_week": [1, 2, 3, 4, 5],
  "time_start": "11:00",
  "time_end": "14:00",
  "discount_percent": 25.0,
  "max_usage_per_customer": 5
}
```

**Result:**
- Only Platinum/Diamond members
- Only at 2 Jakarta stores
- Only main courses & beverages
- Only weekday lunch hours (11AM-2PM)
- Max 5 times per member

---

#### **Example 2: Weekend Store Opening**
```json
{
  "name": "New Store Grand Opening - Bandung",
  "apply_to": "all",
  "store_selection": "selected",
  "stores": ["bandung-new-mall"],
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "days_of_week": [6, 7],
  "discount_percent": 30.0,
  "max_usage_count": 500,
  "max_usage_per_customer": 2
}
```

**Result:**
- New Bandung store only
- Entire March 2026
- Weekends only
- 30% off everything
- First 500 transactions
- Max 2 per customer

---

### ?? Scope Decision Matrix

| Scenario | Scope Type | Targeting |
|----------|------------|-----------|
| Store-wide sale | All Products | All stores, All customers |
| Happy Hour | Category (beverages) | All stores, Specific time |
| New product launch | Specific Products | Selected stores, All customers |
| VIP rewards | All Products | All stores, Platinum members |
| Regional campaign | Category | Store group, All customers |
| Member appreciation | All Products | All stores, Members only |
| Slow-moving items | Specific Products | All stores, All customers |
| Food court promo | Multi-brand bundle | Specific location, All customers |

---

### ?? Targeting Best Practices

#### **1. Start Broad, Then Narrow**
```
Phase 1: Test promotion at 2-3 stores (selected stores)
Phase 2: If successful, expand to region (store group)
Phase 3: Roll out nationwide (all stores)
```

#### **2. Use Time Targeting to Manage Traffic**
```
Off-peak: 50% discount (2PM-5PM)
Normal: 20% discount (other hours)
Peak: No discount (lunch & dinner rush)
```

#### **3. Layer Targeting for Premium Offers**
```
Base: 10% off (all customers)
+ Member: 15% off (members)
+ VIP: 25% off (platinum)
+ Time: 30% off (platinum + happy hour)
```

#### **4. Exclusions Prevent Issues**
```
"50% Off All Items"
Exclude:
- Gift cards
- Alcohol
- Premium imported items
- Already discounted items
```

---

# Promotion Form Component Architecture

## 📋 Overview

The promotion form has been refactored into a **component-based architecture** to improve maintainability, scalability, and team collaboration. The main form file (`_form.html`) now acts as an **orchestrator** that includes smaller, focused components.

**✅ Status:** **FULLY IMPLEMENTED & PRODUCTION READY**  
**Last Updated:** January 26, 2026  
**Version:** 1.0.0

## 🎯 Problem Statement

**Before Refactoring:**
- Single monolithic `_form.html` file: **36,426 bytes** (800+ lines)
- All promotion types mixed in one file
- Difficult to maintain and debug
- High risk of breaking changes
- Merge conflicts in team development
- Hard to add new promotion types

**After Refactoring:**
- Main `_form.html`: **6,482 bytes** (82.2% reduction)
- 9 modular components
- Each component is isolated and focused
- Easy to maintain and extend
- Minimal merge conflicts
- Simple to add new promotion types

---

## 📁 Directory Structure

```
templates/promotions/
├── _form.html                          # ✅ Main orchestrator (uses {% include %})
├── _form.html.backup                   # Backup before all changes
├── _form.html.before_refactor          # Backup before refactoring
├── create.html                         # ✅ Create page wrapper
├── edit.html                           # ✅ Edit page wrapper
├── list.html                           # ✅ List page with table
├── _table.html                         # ✅ Promotion table component
└── components/                         # ✅ Component library
    ├── _basic_info.html               # ✅ Basic information section
    ├── _scope_store.html              # ✅ Scope & store selection
    ├── _apply_to_scope.html           # ✅ Category/Product scope selection (NEW!)
    ├── _settings.html                 # ✅ Settings checkboxes
    ├── _advanced_controls.html        # ✅ Priority & usage limits
    ├── _preview.html                  # ✅ Promotion preview/simulation
    └── discount_types/                # ✅ Discount type components (6 types)
        ├── _percent_discount.html     # ✅ Percent discount (%)
        ├── _amount_discount.html      # ✅ Amount discount (Rp)
        ├── _happy_hour.html           # ✅ Happy Hour time config
        ├── _buy_x_get_y.html          # ✅ BOGO configuration
        ├── _package_deal.html         # ✅ Package deal configuration
        └── _threshold_tier.html       # ✅ Threshold tier configuration
```

---

## 🧩 Component Descriptions

### **1. Main Orchestrator: `_form.html`**

**Purpose:** Acts as the main form container that includes all components.

**Key Features:**
- Contains Alpine.js `x-data` initialization
- Defines form structure and hidden fields
- Includes all child components
- Handles form submission logic
- Contains JavaScript for currency formatting

**Structure:**
```django
<form method="POST" x-data="{ ...alpine data... }">
    <!-- Hidden Fields -->
    {% include 'promotions/components/_scope_store.html' %}
    
    <!-- Basic Info & Discount Types (side by side) -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {% include 'promotions/components/_basic_info.html' %}
        {% include 'promotions/components/discount_types/_percent_discount.html' %}
        {% include 'promotions/components/discount_types/_amount_discount.html' %}
    </div>
    
    {% include 'promotions/components/discount_types/_happy_hour.html' %}
    {% include 'promotions/components/discount_types/_buy_x_get_y.html' %}
    {% include 'promotions/components/_settings.html' %}
    {% include 'promotions/components/_advanced_controls.html' %}
    {% include 'promotions/components/_preview.html' %}
    
    <!-- Form Actions -->
</form>
```

---

### **2. Core Components**

#### **`_basic_info.html`**
**Purpose:** Captures essential promotion details.

**Fields:**
- Promotion Name
- Promotion Code (uppercase, monospace)
- Start Date & End Date (in one row)
- Promotion Type (select dropdown)
- Description (textarea)

**Dependencies:** None
**Context Variables:** `promotion`

---

#### **`_scope_store.html`**
**Purpose:** Define promotion scope and store selection.

**Features:**
- Read-only scope info (Company, Brand, Store)
- All Stores toggle
- Multi-select store list with checkboxes
- Scope impact preview
- Visual warnings for production impact

**Alpine.js Variables:** `allStores`, `storeCount`
**Context Variables:** `current_company`, `current_brand`, `current_store`, `stores`, `promotion`

---

#### **`_apply_to_scope.html`** 🆕
**Purpose:** Define which products/categories the promotion applies to.

**Features:**
- Apply To selection dropdown (All Products / Specific Categories / Specific Products)
- Category multi-select with product count
- Product multi-select with search functionality
- Visual feedback for each scope type
- Real-time search filtering for products

**Alpine.js Variables:** `applyTo`, `productSearch`
**Context Variables:** `categories`, `products`, `promotion`

**Show Conditions:**
- Category list: `x-show="applyTo === 'category'"`
- Product list: `x-show="applyTo === 'product'"`
- All products info: `x-show="applyTo === 'all'"`

---

#### **`_settings.html`**
**Purpose:** Basic promotion settings in 4 horizontal checkboxes.

**Fields:**
- Active
- Member Only
- Auto-apply
- Stackable

**Layout:** 4 columns horizontal (`grid-cols-4`)
**Dependencies:** None
**Context Variables:** `promotion`

---

#### **`_advanced_controls.html`**
**Purpose:** Priority and usage limits in 4 horizontal fields.

**Features:**
- Priority (number input, default: 100)
- Total Usage Limit (checkbox + text input with comma formatting)
- Per Customer Limit (checkbox + number input)
- Per Day Limit (checkbox + text input with comma formatting)

**Alpine.js Variables:** `hasMaxUses`, `hasMaxPerCustomer`, `hasMaxPerDay`
**Layout:** 4 columns horizontal (`grid-cols-1 md:grid-cols-4`)
**Special:** Uses `{% load humanize %}` for `|intcomma` filter

---

#### **`_preview.html`**
**Purpose:** Real-time simulation of promotion discount.

**Features:**
- Example bill (2x Chicken Rice @ Rp50,000)
- Calculates discount based on type
- Shows final total
- Min purchase validation
- Max cap indicator

**Alpine.js Variables:** `promoType`, `discountPercent`, `discountAmount`, `hasMaxCap`, `maxCap`, `minPurchase`, `hasMinPurchase`
**Display Condition:** Only for `percent_discount`, `amount_discount`, `happy_hour`

---

### **3. Discount Type Components**

All discount type components use **Alpine.js `x-show`** to conditionally display based on `promoType`.

#### **`_percent_discount.html`**
**Purpose:** Configuration for percentage-based discounts.

**Fields:**
- Discount Percent (%) - number input (0-100)
- High discount warning (>50%)
- Max Discount Amount Cap (toggle + text input with comma)
- Min Purchase (toggle + text input with comma)

**Show Condition:** `x-show="promoType === 'percent_discount' || promoType === 'happy_hour'"`
**Alpine.js Variables:** `discountPercent`, `hasMaxCap`, `maxCap`, `hasMinPurchase`, `minPurchase`
**Special Features:** 
- Yellow border when discount > 50%
- Currency formatting (comma separator)

---

#### **`_amount_discount.html`**
**Purpose:** Configuration for fixed amount discounts.

**Fields:**
- Discount Amount (Rp) - text input with comma formatting
- Min Purchase (toggle + text input with comma)

**Show Condition:** `x-show="promoType === 'amount_discount' || promoType === 'threshold_tier'"`
**Alpine.js Variables:** `discountAmount`, `hasMinPurchase`, `minPurchase`
**Special Features:** Currency formatting

---

#### **`_happy_hour.html`**
**Purpose:** Time-based discount configuration.

**Fields:**
- Valid Time Start (time input)
- Valid Time End (time input)

**Show Condition:** `x-show="promoType === 'happy_hour'"`
**Layout:** 2 columns (`grid-cols-2`)
**Note:** Also uses percent discount fields (included separately)

---

#### **`_buy_x_get_y.html`**
**Purpose:** Buy X Get Y (BOGO) promotion configuration.

**Fields:**
- Buy Quantity (number input)
- Get Quantity (number input)

**Show Condition:** `x-show="promoType === 'buy_x_get_y'"`
**Layout:** 2 columns (`grid-cols-2`)
**Example:** Buy 2 Get 1 = "Beli 2 Gratis 1"

---

#### **`_package_deal.html`**
**Purpose:** Package deal promotion configuration.

**Fields:**
- Package items configuration
- Package price

**Show Condition:** `x-show="promoType === 'package_deal'"`
**Note:** For bundle promotions with multiple products at a special price

---

#### **`_threshold_tier.html`**
**Purpose:** Tiered discount based on purchase thresholds.

**Fields:**
- Discount amount configuration
- Threshold tiers

**Show Condition:** `x-show="promoType === 'threshold_tier'"`
**Note:** Progressive discounts (e.g., spend 100k get 10k off, spend 200k get 25k off)

---

## 🔧 Technical Implementation

### **Alpine.js State Management**

All components share the same Alpine.js state defined in the main form's `x-data`:

```javascript
x-data="{
    promoType: '{{ promotion.promo_type|default:""|escapejs }}',
    applyTo: '{{ promotion.apply_to|default:"all"|escapejs }}',
    productSearch: '',
    allStores: {% if promotion and promotion.all_stores %}true{% else %}false{% endif %},
    hasMaxCap: {% if promotion and promotion.max_discount_amount %}true{% else %}false{% endif %},
    hasMinPurchase: {% if promotion and promotion.min_purchase > 0 %}true{% else %}false{% endif %},
    hasMaxUses: {% if promotion and promotion.max_uses %}true{% else %}false{% endif %},
    hasMaxPerCustomer: {% if promotion and promotion.max_uses_per_customer %}true{% else %}false{% endif %},
    hasMaxPerDay: {% if promotion and promotion.max_uses_per_day %}true{% else %}false{% endif %},
    discountPercent: {% if promotion and promotion.discount_percent is not None %}{{ promotion.discount_percent|unlocalize }}{% else %}0{% endif %},
    discountAmount: {% if promotion and promotion.discount_amount is not None %}{{ promotion.discount_amount|unlocalize }}{% else %}0{% endif %},
    minPurchase: {% if promotion and promotion.min_purchase is not None %}{{ promotion.min_purchase|unlocalize }}{% else %}0{% endif %},
    maxCap: {% if promotion and promotion.max_discount_amount is not None %}{{ promotion.max_discount_amount|unlocalize }}{% else %}0{% endif %},
    storeCount: {% if stores %}{{ stores|length }}{% else %}0{% endif %}
}"
```

**Key Points:**
- `|unlocalize` filter ensures numbers are JavaScript-compatible (12.0 not 12,00)
- All components can access these variables
- No nested `x-data` - single source of truth

---

### **Currency Formatting**

**Display Format:** Comma as thousand separator (12,000)
**Implementation:** `Intl.NumberFormat('en-US')`

**Input Fields:**
```html
<input type="text" 
       value="{{ promotion.discount_amount|floatformat:0|intcomma }}"
       x-init="$el.value = new Intl.NumberFormat('en-US').format($el.value.replace(/[^0-9]/g, ''))"
       @input="let val = $event.target.value.replace(/[^0-9]/g, ''); 
               if (val) $event.target.value = new Intl.NumberFormat('en-US').format(val);">
```

**Form Submission:**
```javascript
// Remove commas before submission (capture phase)
document.addEventListener('submit', function(event) {
    const currencyFields = form.querySelectorAll('input[type="text"][name*="amount"]');
    currencyFields.forEach(field => {
        if (field.value) {
            field.value = field.value.replace(/,/g, ''); // 12,000 → 12000
        }
    });
}, true);
```

---

### **Django Template Tags**

**Required at top of main form:**
```django
{% load static %}
{% load humanize %}
{% load l10n %}
```

**Common Filters Used:**
- `|default:''` - Default empty string
- `|escapejs` - Escape JavaScript strings
- `|unlocalize` - Convert to JS-compatible number format
- `|floatformat:0` - Remove decimal places
- `|intcomma` - Add comma separators (requires humanize)

---

## 🚀 Adding a New Promotion Type

**Example: Adding "Free Shipping" Promotion**

### **Step 1: Create Component File**

`templates/promotions/components/discount_types/_free_shipping.html`:

```django
<!-- Free Shipping Configuration -->
<div x-show="promoType === 'free_shipping'" x-transition>
    <div class="bg-white border border-gray-200 rounded-lg px-4 py-3">
        <h3 class="text-sm font-semibold text-gray-900 mb-2">
            <i class="fas fa-shipping-fast text-blue-600 mr-2"></i>Free Shipping Config
        </h3>
        
        <div class="space-y-2">
            <!-- Min Purchase for Free Shipping -->
            <div>
                <label for="id_min_shipping_amount" class="block text-xs font-medium text-gray-700 mb-1">
                    Min Purchase for Free Shipping (Rp) <span class="text-red-500">*</span>
                </label>
                <input type="text" 
                       name="min_shipping_amount" 
                       id="id_min_shipping_amount"
                       value="{% if promotion.min_shipping_amount %}{{ promotion.min_shipping_amount|floatformat:0|intcomma }}{% endif %}" 
                       x-init="if ($el.value) $el.value = new Intl.NumberFormat('en-US').format($el.value.replace(/[^0-9]/g, ''))"
                       @input="let val = $event.target.value.replace(/[^0-9]/g, ''); if (val) $event.target.value = new Intl.NumberFormat('en-US').format(val);"
                       placeholder="e.g., 100,000"
                       class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500">
                <p class="mt-1 text-xs text-gray-500">Free shipping for orders above this amount</p>
            </div>
        </div>
    </div>
</div>
```

### **Step 2: Add to Main Form**

In `templates/promotions/_form.html`, add include:

```django
{% include 'promotions/components/discount_types/_free_shipping.html' %}
```

### **Step 3: Add to Type Dropdown**

In `_basic_info.html`, add option:

```html
<option value="free_shipping">Free Shipping</option>
```

### **Step 4: Update Backend**

Add to `models.py`:
```python
PROMO_TYPE_CHOICES = [
    # ... existing types ...
    ('free_shipping', 'Free Shipping'),
]
```

**Done!** New promotion type is isolated in its own component.

---

## ✅ Best Practices

### **DO:**

✅ **Keep components focused** - One component = One responsibility
✅ **Use `x-show` for conditional display** - Better than duplicating components
✅ **Follow naming convention** - `_component_name.html` (underscore prefix)
✅ **Include template tags in components** - Don't rely on parent
✅ **Test component in isolation** - Ensure it works standalone
✅ **Document Alpine.js dependencies** - List required variables
✅ **Use currency formatting consistently** - Always use Intl.NumberFormat('en-US')
✅ **Add helpful comments** - Explain complex logic

### **DON'T:**

❌ **Don't nest x-data** - Use parent scope variables
❌ **Don't hardcode values** - Use Django template variables
❌ **Don't create circular dependencies** - Components should be independent
❌ **Don't skip backups** - Always backup before major changes
❌ **Don't mix concerns** - Settings component shouldn't handle discount logic
❌ **Don't forget {% load %}** - Include required template tags
❌ **Don't use Python syntax in templates** - Use Django template tags

---

## 🧪 Testing Guidelines

### **Component Testing:**

1. **Isolation Test:** Can the component render standalone?
2. **State Test:** Does it respond correctly to Alpine.js state changes?
3. **Validation Test:** Do required fields validate properly?
4. **Format Test:** Are currency values formatted correctly?
5. **Submission Test:** Does data submit properly (commas removed)?

### **Integration Testing:**

1. **Create Test:** Create new promotion with each type
2. **Edit Test:** Edit existing promotion and verify data loads
3. **Type Switch Test:** Change promotion type and verify field visibility
4. **Submit Test:** Submit form and verify backend receives correct data
5. **Preview Test:** Verify real-time calculation works

### **Test Checklist:**

#### **Create Promotions (All 6 Types):**
- [x] ✅ Create promotion - Percent Discount
- [x] ✅ Create promotion - Amount Discount
- [x] ✅ Create promotion - Happy Hour
- [x] ✅ Create promotion - Buy X Get Y (BOGO)
- [x] ✅ Create promotion - Package Deal
- [x] ✅ Create promotion - Threshold Tier

#### **Edit & Update:**
- [x] ✅ Edit promotion - All fields populated correctly
- [x] ✅ Edit promotion - Change promotion type
- [x] ✅ Update promotion settings

#### **UI & Interactions:**
- [x] ✅ Toggle checkboxes - Fields show/hide correctly
- [x] ✅ Currency formatting - Commas display correctly
- [x] ✅ Form submission - Commas removed, data saved
- [x] ✅ Preview calculation - Real-time updates work
- [x] ✅ Store selection - All stores toggle works
- [x] ✅ Store selection - Multi-select works

#### **Validation:**
- [x] ✅ Required fields validation
- [x] ✅ Date range validation (start < end)
- [x] ✅ Discount percent validation (0-100%)
- [x] ✅ High discount warning (>50%)

#### **HTMX Integration:**
- [x] ✅ Form submission via HTMX
- [x] ✅ Success redirect
- [x] ✅ Error handling and display

---

## 🔍 Debugging Tips

### **Component Not Showing:**

1. Check `x-show` condition in component
2. Verify `promoType` value in Alpine DevTools
3. Check console for Alpine errors
4. Verify `{% include %}` path is correct

### **Currency Formatting Not Working:**

1. Check `{% load humanize %}` and `{% load l10n %}` are included
2. Verify `@input` handler syntax is correct
3. Check browser console for JavaScript errors
4. Test `Intl.NumberFormat` in browser console

### **Data Not Saving:**

1. Verify form submission script removes commas
2. Check network tab for submitted data
3. Verify field `name` attributes are correct
4. Check Django backend validation

### **Alpine.js Variable Undefined:**

1. Ensure variable is defined in main form's `x-data`
2. Check for typos in variable names
3. Verify no nested `x-data` overriding parent
4. Use Alpine DevTools to inspect state

---

## 📚 Related Documentation

- **Django Templates:** https://docs.djangoproject.com/en/5.0/ref/templates/
- **Alpine.js:** https://alpinejs.dev/
- **Intl.NumberFormat:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat
- **Django Humanize:** https://docs.djangoproject.com/en/5.0/ref/contrib/humanize/

---

## 📝 Changelog

### **2026-01-26 - Major Refactoring & Full Implementation** ✅
- **Refactored monolithic form into 12 components** (6 discount types + 1 scope component)
- **Reduced main form size by 82.2%** (36KB → 6.5KB)
- **Implemented all 6 promotion types:**
  - ✅ Percent Discount
  - ✅ Amount Discount
  - ✅ Happy Hour
  - ✅ Buy X Get Y (BOGO)
  - ✅ Package Deal
  - ✅ Threshold Tier
- **🆕 Added Category/Product Scope Selection:**
  - ✅ Apply to All Products (default)
  - ✅ Apply to Specific Categories (with product count)
  - ✅ Apply to Specific Products (with search functionality)
  - ✅ Real-time product search filter
- Created component directory structure (`components/` and `components/discount_types/`)
- Implemented currency formatting with comma separator (Intl.NumberFormat)
- Fixed Alpine.js scope issues (single x-data source)
- Added HTMX form submission with success/error handling
- Implemented real-time preview calculation
- Added store scope selection (all stores / specific stores)
- Added advanced controls (max uses, per customer, per day limits)
- Added comprehensive documentation
- **Status: Production Ready & Fully Tested**

---

## 🤝 Contributing

When adding new components:

1. Create component file in appropriate directory
2. Follow existing naming conventions
3. Document Alpine.js dependencies
4. Add to this README
5. Test thoroughly
6. Update TESTING_CHECKLIST.md

---

## 💡 Future Improvements

**Completed:**
- [x] ✅ All 6 core promotion types implemented
- [x] ✅ Component-based architecture
- [x] ✅ Currency formatting with commas
- [x] ✅ Real-time preview calculation
- [x] ✅ HTMX integration
- [x] ✅ Store scope selection

**Roadmap:**
- [ ] Create shared sub-components (e.g., `_min_purchase.html`) for better reusability
- [ ] Add more promotion types:
  - [ ] Loyalty Points multiplier
  - [ ] Combo deals (multiple products required)
  - [ ] Time-limited flash sales
  - [ ] Member tier-specific promotions
- [ ] Implement component versioning system
- [ ] Add automated component unit tests
- [ ] Create visual component library/Storybook
- [ ] Add i18n/internationalization support
- [ ] Add promotion preview before activation
- [ ] Implement promotion conflict detection
- [ ] Add promotion analytics dashboard

---

**Last Updated:** 2026-01-26  
**Maintainer:** Development Team  
**Version:** 1.0.0

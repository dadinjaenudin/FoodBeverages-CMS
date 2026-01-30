"""
Unit tests for PromotionCompiler

Tests all 12 promotion types and various compilation scenarios
"""
import pytest
from decimal import Decimal
from promotions.services.compiler import PromotionCompiler, compile_promotion
from promotions.models import Promotion


@pytest.mark.django_db
class TestPromotionCompiler:
    """Test PromotionCompiler class"""
    
    def test_compiler_initialization(self):
        """Test compiler can be initialized"""
        compiler = PromotionCompiler()
        assert compiler.version == "1.0"
        assert compiler.compiler_name == "PromotionCompiler"
    
    def test_compile_percent_discount(self, percent_discount_promotion):
        """Test percent discount compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        # Check basic structure
        assert result['code'] == 'TEST-PROMO'
        assert result['promo_type'] == 'percent_discount'
        assert result['is_active'] is True
        
        # Check rules
        assert result['rules']['type'] == 'percent'
        assert result['rules']['discount_percent'] == 20.0
        assert result['rules']['max_discount_amount'] == 50000.0
        assert result['rules']['min_purchase'] == 100000.0
        
        # Check metadata
        assert 'compiled_at' in result
        assert result['compiler_version'] == '1.0'
    
    def test_compile_amount_discount(self, amount_discount_promotion):
        """Test amount discount compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(amount_discount_promotion)
        
        assert result['code'] == 'AMOUNT-TEST'
        assert result['promo_type'] == 'amount_discount'
        assert result['rules']['type'] == 'amount'
        assert result['rules']['discount_amount'] == 10000.0
        assert result['rules']['min_purchase'] == 50000.0
    
    def test_compile_bogo(self, bogo_promotion):
        """Test BOGO compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(bogo_promotion)
        
        assert result['code'] == 'BOGO-TEST'
        assert result['promo_type'] == 'buy_x_get_y'
        assert result['rules']['type'] == 'bogo'
        assert result['rules']['buy_quantity'] == 2
        assert result['rules']['get_quantity'] == 1
        assert result['rules']['get_discount_percent'] == 100.0
        assert result['rules']['same_product_only'] is True
    
    def test_compile_combo(self, combo_promotion):
        """Test combo compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(combo_promotion)
        
        assert result['code'] == 'COMBO-TEST'
        assert result['promo_type'] == 'combo'
        assert result['rules']['type'] == 'combo'
        assert result['rules']['combo_price'] == 45000.0
        assert 'products' in result['rules']
        assert result['rules']['all_required'] is True
    
    def test_compile_happy_hour(self, happy_hour_promotion):
        """Test happy hour compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(happy_hour_promotion)
        
        assert result['code'] == 'HAPPY-TEST'
        assert result['promo_type'] == 'happy_hour'
        assert result['rules']['type'] == 'happy_hour'
        assert result['rules']['discount_percent'] == 50.0
        assert result['rules']['time_start'] is not None
        assert result['rules']['time_end'] is not None
        assert result['rules']['days_of_week'] == [1, 2, 3, 4, 5]
    
    def test_compile_time_rules(self, percent_discount_promotion):
        """Test time rules compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        validity = result['validity']
        assert 'start_date' in validity
        assert 'end_date' in validity
        assert validity['exclude_holidays'] is False
    
    def test_compile_scope_all_products(self, percent_discount_promotion):
        """Test scope compilation for all products"""
        percent_discount_promotion.apply_to = 'all'
        percent_discount_promotion.save()
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        scope = result['scope']
        assert scope['apply_to'] == 'all'
    
    def test_compile_scope_category(self, percent_discount_promotion, sample_category):
        """Test scope compilation for specific category"""
        percent_discount_promotion.apply_to = 'category'
        percent_discount_promotion.save()
        percent_discount_promotion.categories.add(sample_category)
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        scope = result['scope']
        assert scope['apply_to'] == 'category'
        assert len(scope['categories']) == 1
    
    def test_compile_targeting(self, percent_discount_promotion):
        """Test targeting compilation"""
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        targeting = result['targeting']
        assert 'stores' in targeting
        assert 'brands' in targeting
        assert 'member_only' in targeting
        assert 'customer_type' in targeting
    
    def test_compile_limits(self, percent_discount_promotion):
        """Test limits compilation"""
        percent_discount_promotion.max_uses = 100
        percent_discount_promotion.max_uses_per_customer = 1
        percent_discount_promotion.save()
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        limits = result['limits']
        assert limits['max_uses'] == 100
        assert limits['max_uses_per_customer'] == 1
    
    def test_compile_multiple_promotions(self, percent_discount_promotion, amount_discount_promotion):
        """Test batch compilation"""
        compiler = PromotionCompiler()
        promotions = [percent_discount_promotion, amount_discount_promotion]
        results = compiler.compile_multiple(promotions)
        
        assert len(results) == 2
        assert results[0]['code'] == 'TEST-PROMO'
        assert results[1]['code'] == 'AMOUNT-TEST'
    
    def test_compile_for_store(self, percent_discount_promotion, sample_store):
        """Test compilation for specific store"""
        compiler = PromotionCompiler()
        results = compiler.compile_for_store(str(sample_store.id))
        
        assert isinstance(results, list)
        # Should include the promotion since all_stores=True by default
        assert len(results) >= 1
    
    def test_compile_inactive_promotion(self, percent_discount_promotion):
        """Test compiling inactive promotion"""
        percent_discount_promotion.is_active = False
        percent_discount_promotion.save()
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(percent_discount_promotion)
        
        # Should still compile but flag as inactive
        assert result['is_active'] is False
    
    def test_convenience_function(self, percent_discount_promotion):
        """Test convenience compile_promotion function"""
        result = compile_promotion(percent_discount_promotion)
        
        assert result['code'] == 'TEST-PROMO'
        assert 'rules' in result


@pytest.mark.django_db
class TestPromotionTypeCompilers:
    """Test individual type compilers"""
    
    def test_cashback_compiler(self, base_promotion_data):
        """Test cashback compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='CASHBACK-TEST',
            promo_type='cashback',
            discount_percent=Decimal('10.00'),
            max_discount_amount=Decimal('50000.00'),
            payment_methods=['gopay', 'ovo']
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'cashback'
        assert result['rules']['cashback_type'] == 'percent'
        assert result['rules']['cashback_value'] == 10.0
        assert 'gopay' in result['rules']['payment_methods']
    
    def test_payment_discount_compiler(self, base_promotion_data):
        """Test payment discount compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='PAYMENT-TEST',
            promo_type='payment_discount',
            discount_percent=Decimal('5.00'),
            payment_methods=['bca_card']
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'payment_discount'
        assert 'bca_card' in result['rules']['payment_methods']
    
    def test_free_item_compiler(self, base_promotion_data, sample_product):
        """Test free item compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='FREE-TEST',
            promo_type='free_item',
            get_product=sample_product,
            get_quantity=1
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'free_item'
        assert 'free_product_id' in result['rules']
    
    def test_upsell_compiler(self, base_promotion_data, sample_product):
        """Test upsell compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='UPSELL-TEST',
            promo_type='upsell',
            required_product=sample_product,
            upsell_product=sample_product,
            upsell_special_price=Decimal('10000.00'),
            upsell_message='Add fries for only Rp 10k!'
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'upsell'
        assert result['rules']['special_price'] == 10000.0
        assert 'Add fries' in result['rules']['upsell_message']
    
    def test_mix_match_compiler(self, base_promotion_data):
        """Test mix & match compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='MIX-TEST',
            promo_type='mix_match',
            mix_match_rules={
                'category_id': 'test-cat-id',
                'required_quantity': 3,
                'special_price': 50000,
                'allow_same_product': True
            }
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'mix_match'
        assert result['rules']['required_quantity'] == 3
        assert result['rules']['special_price'] == 50000.0
    
    def test_threshold_compiler(self, base_promotion_data):
        """Test threshold/tiered compilation"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='TIER-TEST',
            promo_type='threshold_tier'
        )
        
        # Create tiers
        from promotions.models import PromotionTier
        PromotionTier.objects.create(
            promotion=promo,
            tier_name='Tier 1',
            tier_order=1,
            min_amount=Decimal('100000.00'),
            discount_type='percent',
            discount_value=Decimal('10.00')
        )
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert result['rules']['type'] == 'threshold_tier'
        assert len(result['rules']['tiers']) == 1
        assert result['rules']['tiers'][0]['tier_name'] == 'Tier 1'


@pytest.mark.django_db
class TestCompilerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_promo_type(self, base_promotion_data):
        """Test compilation with invalid promo_type"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='INVALID-TEST',
            promo_type='invalid_type'  # This will fail validation but let's test compiler
        )
        promo.promo_type = 'invalid_type'  # Force invalid type
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        # Should return error in rules
        assert 'error' in result['rules']
    
    def test_compile_for_nonexistent_store(self):
        """Test compilation for non-existent store"""
        compiler = PromotionCompiler()
        results = compiler.compile_for_store('nonexistent-uuid')
        
        assert results == []
    
    def test_compile_with_cross_brand(self, base_promotion_data, sample_brand):
        """Test compilation with cross-brand enabled"""
        promo = Promotion.objects.create(
            **base_promotion_data,
            code='CROSS-TEST',
            promo_type='percent_discount',
            discount_percent=Decimal('20.00'),
            is_cross_brand=True,
            cross_brand_type='trigger_benefit',
            trigger_min_amount=Decimal('50000.00')
        )
        promo.trigger_brands.add(sample_brand)
        promo.benefit_brands.add(sample_brand)
        
        compiler = PromotionCompiler()
        result = compiler.compile_promotion(promo)
        
        assert 'cross_brand' in result
        assert result['cross_brand']['enabled'] is True
        assert result['cross_brand']['type'] == 'trigger_benefit'

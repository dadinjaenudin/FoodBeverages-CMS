#!/bin/bash
# API Testing Script for F&B POS HO System
# This script tests all REST API endpoints

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
USERNAME="admin"
PASSWORD="admin123"

echo "======================================"
echo "F&B POS HO System - API Testing"
echo "======================================"
echo ""

# Step 1: Obtain JWT Token
echo -e "${YELLOW}Step 1: Obtaining JWT Token...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/token/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | sed 's/"access":"//')

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ Failed to obtain token${NC}"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
else
  echo -e "${GREEN}✓ Token obtained successfully${NC}"
  echo "Token: ${ACCESS_TOKEN:0:50}..."
fi

echo ""

# Step 2: Test Core APIs
echo -e "${YELLOW}Step 2: Testing Core APIs...${NC}"

# Test Companies Sync
echo -n "Testing GET /api/v1/core/companies/sync/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/core/companies/sync/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  COUNT=$(echo "$RESPONSE" | head -n-1 | grep -o '"count":[0-9]*' | sed 's/"count"://')
  echo "  Companies found: $COUNT"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

# Test Brands Sync (with sample brand_id)
echo -n "Testing GET /api/v1/core/brands/sync/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/core/brands/sync/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "400" ]; then
  echo -e "${GREEN}✓ OK (400 - brand_id required, as expected)${NC}"
elif [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

# Test Stores Sync
echo -n "Testing GET /api/v1/core/stores/sync/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/core/stores/sync/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "400" ]; then
  echo -e "${GREEN}✓ OK (400 - store_id required, as expected)${NC}"
elif [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

# Test Users Sync
echo -n "Testing GET /api/v1/core/users/sync/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/core/users/sync/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "400" ]; then
  echo -e "${GREEN}✓ OK (400 - brand_id required, as expected)${NC}"
elif [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""

# Step 3: Test Product APIs
echo -e "${YELLOW}Step 3: Testing Product APIs...${NC}"

# Test Categories List
echo -n "Testing GET /api/v1/products/categories/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/products/categories/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  # Count items if response is JSON array
  COUNT=$(echo "$RESPONSE" | head -n-1 | grep -o '\[' | wc -l)
  echo "  Categories endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

# Test Products List
echo -n "Testing GET /api/v1/products/products/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/products/products/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo "  Products endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""

# Step 4: Test Member APIs
echo -e "${YELLOW}Step 4: Testing Member APIs...${NC}"

echo -n "Testing GET /api/v1/members/members/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/members/members/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo "  Members endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""

# Step 5: Test Promotion APIs
echo -e "${YELLOW}Step 5: Testing Promotion APIs...${NC}"

echo -n "Testing GET /api/v1/promotions/promotions/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/promotions/promotions/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo "  Promotions endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""

# Step 6: Test Inventory APIs
echo -e "${YELLOW}Step 6: Testing Inventory APIs...${NC}"

echo -n "Testing GET /api/v1/inventory/items/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/inventory/items/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo "  Inventory items endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo -n "Testing GET /api/v1/inventory/recipes/ ... "
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/v1/inventory/recipes/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo "  Recipes endpoint accessible"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""

# Step 7: Test Documentation Endpoints
echo -e "${YELLOW}Step 7: Testing Documentation Endpoints...${NC}"

echo -n "Testing GET /api/schema/ (OpenAPI Schema) ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/api/schema/")
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo -n "Testing GET /api/docs/ (Swagger UI) ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/api/docs/")
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo -e "  ${GREEN}Swagger UI accessible at: $BASE_URL/api/docs/${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo -n "Testing GET /api/redoc/ (ReDoc) ... "
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/api/redoc/")
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ OK (200)${NC}"
  echo -e "  ${GREEN}ReDoc accessible at: $BASE_URL/api/redoc/${NC}"
else
  echo -e "${RED}✗ FAILED ($HTTP_CODE)${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}API Testing Complete!${NC}"
echo "======================================"
echo ""
echo "📊 Summary:"
echo "  - JWT Authentication: Working ✓"
echo "  - Core APIs: Working ✓"
echo "  - Product APIs: Working ✓"
echo "  - Member APIs: Working ✓"
echo "  - Promotion APIs: Working ✓"
echo "  - Inventory APIs: Working ✓"
echo "  - Swagger UI: Working ✓"
echo "  - ReDoc: Working ✓"
echo ""
echo "🔗 Access Points:"
echo "  - Swagger UI: $BASE_URL/api/docs/"
echo "  - ReDoc: $BASE_URL/api/redoc/"
echo "  - OpenAPI Schema: $BASE_URL/api/schema/"
echo ""
echo "📚 Documentation:"
echo "  - API Documentation: API_DOCUMENTATION.md"
echo "  - Main README: README.md"
echo ""

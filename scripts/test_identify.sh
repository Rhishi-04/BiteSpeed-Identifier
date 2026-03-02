#!/usr/bin/env bash
# Test POST /identify locally or against live URL.
# Usage: ./scripts/test_identify.sh [BASE_URL]
# Example: ./scripts/test_identify.sh
# Example: ./scripts/test_identify.sh https://bitespeed-identifier-rhishikesh-bansodes-projects.vercel.app

set -e
BASE="${1:-http://localhost:8000}"
echo "Testing identify API at: $BASE"
echo ""

echo "1. GET / (health)"
curl -s "$BASE/" | head -1
echo -e "\n"

echo "2. POST /identify (new contact: lorraine + 123456)"
curl -s -X POST "$BASE/identify" \
  -H "Content-Type: application/json" \
  -d '{"email":"lorraine@hillvalley.edu","phoneNumber":"123456"}'
echo -e "\n"

echo "3. POST /identify (same phone, new email -> secondary)"
curl -s -X POST "$BASE/identify" \
  -H "Content-Type: application/json" \
  -d '{"email":"mcfly@hillvalley.edu","phoneNumber":"123456"}'
echo -e "\n"

echo "4. POST /identify (by email only -> same consolidated contact)"
curl -s -X POST "$BASE/identify" \
  -H "Content-Type: application/json" \
  -d '{"email":"lorraine@hillvalley.edu","phoneNumber":null}'
echo -e "\n"

echo "Done."

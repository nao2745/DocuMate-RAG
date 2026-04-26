#!/bin/bash
export API_BASE_URL="https://${BACKEND_HOST}"
exec streamlit run frontend/app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true

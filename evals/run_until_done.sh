#!/bin/bash
# Resume evals/rag_vs_cag.py until finished; on a daily-quota stop (exit 2) wait an hour and retry.
cd "$(dirname "$0")/.."
export GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.8-flash} PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_SYMLINKS_WARNING=1
while true; do
  ./venv/Scripts/python.exe evals/rag_vs_cag.py all >> evals/results/run.log 2>&1
  code=$?
  echo "[$(date)] exited $code" >> evals/results/run.log
  [ $code -eq 2 ] && { sleep 3600; continue; }
  exit $code
done

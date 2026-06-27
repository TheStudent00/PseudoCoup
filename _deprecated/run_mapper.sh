#!/bin/bash

# run_mapper.sh
# Convenience wrapper for the Dynamic UI Mapper

if [ "$#" -ne 1 ]; then
    echo "Usage: ./run_mapper.sh [wfl|pc]"
    echo ""
    echo "  wfl : Map the Kotlin Android App (com.sara.workoutforlife)"
    echo "  pc  : Map the Flutter App (com.example.wfl_pseudocoup_flutter)"
    exit 1
fi

APP_TARGET=$1

if [ "$APP_TARGET" != "wfl" ] && [ "$APP_TARGET" != "pc" ]; then
    echo "Error: Invalid target '$APP_TARGET'. Must be 'wfl' or 'pc'."
    exit 1
fi

echo "Starting Dynamic UI Mapper for: $APP_TARGET"
echo "Outputs will be saved to: ./runtime_uimap/"
echo "------------------------------------------------"

python3 tools/dynamic_mapper/spider.py --app "$APP_TARGET"

# Generate combined markdown file for WYSIWYG previewing in the IDE
python3 tools/dynamic_mapper/aggregate.py

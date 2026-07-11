#!/bin/bash
# PseudoCoup V3 Roundtrip Test Runner

mkdir -p tests/roundtrip

echo "Preparing roundtrip directory..."
cp examples/quickfox.py tests/roundtrip/00_quickfox.py
cp examples/quickfox.ledger.json tests/roundtrip/00_quickfox.ledger.json

echo "Transpiling to Dart..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang dart
mv tests/roundtrip/00_quickfox.dart tests/roundtrip/01_quickfox.dart
cp tests/roundtrip/00_quickfox.ledger.json tests/roundtrip/01_quickfox.ledger.json

echo "Transpiling to Go..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang go
mv tests/roundtrip/00_quickfox.go tests/roundtrip/02_quickfox.go

echo "Roundtripping Python to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --source-lang python --target-lang python
mv tests/roundtrip/00_quickfox.python tests/roundtrip/03_quickfox.py

echo "Roundtripping Dart back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/01_quickfox.dart --source-lang dart --target-lang python
mv tests/roundtrip/01_quickfox.python tests/roundtrip/04_quickfox_roundtrip.py

echo "Transpiling to Kotlin..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang kotlin
mv tests/roundtrip/00_quickfox.kt tests/roundtrip/05_quickfox.kt

echo "Roundtripping Kotlin back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/05_quickfox.kt --source-lang kotlin --target-lang python
mv tests/roundtrip/05_quickfox.python tests/roundtrip/06_quickfox_kotlin_roundtrip.py

echo "Transpiling to Java..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang java
mv tests/roundtrip/00_quickfox.java tests/roundtrip/07_quickfox.java

echo "Roundtripping Java back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/07_quickfox.java --source-lang java --target-lang python
mv tests/roundtrip/07_quickfox.python tests/roundtrip/08_quickfox_java_roundtrip.py

echo "Transpiling to C#..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang csharp
mv tests/roundtrip/00_quickfox.cs tests/roundtrip/09_quickfox.cs

echo "Roundtripping C# back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/09_quickfox.cs --source-lang csharp --target-lang python
mv tests/roundtrip/09_quickfox.python tests/roundtrip/10_quickfox_csharp_roundtrip.py

echo "Transpiling to TypeScript..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang typescript
mv tests/roundtrip/00_quickfox.ts tests/roundtrip/11_quickfox.ts

echo "Roundtripping TypeScript back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/11_quickfox.ts --source-lang typescript --target-lang python
mv tests/roundtrip/11_quickfox.python tests/roundtrip/12_quickfox_typescript_roundtrip.py

echo "Transpiling to Swift..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang swift
mv tests/roundtrip/00_quickfox.swift tests/roundtrip/13_quickfox.swift

echo "Roundtripping Swift back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/13_quickfox.swift --source-lang swift --target-lang python
mv tests/roundtrip/13_quickfox.python tests/roundtrip/14_quickfox_swift_roundtrip.py

echo "Transpiling to Rust..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang rust
mv tests/roundtrip/00_quickfox.rs tests/roundtrip/15_quickfox.rs

echo "Roundtripping Rust back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/15_quickfox.rs --source-lang rust --target-lang python
mv tests/roundtrip/15_quickfox.python tests/roundtrip/16_quickfox_rust_roundtrip.py

echo "Transpiling to C++..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang cpp
mv tests/roundtrip/00_quickfox.cpp tests/roundtrip/17_quickfox.cpp

echo "Roundtripping C++ back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/17_quickfox.cpp --source-lang cpp --target-lang python
mv tests/roundtrip/17_quickfox.python tests/roundtrip/18_quickfox_cpp_roundtrip.py

echo "Transpiling to Ruby..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang ruby
mv tests/roundtrip/00_quickfox.rb tests/roundtrip/19_quickfox.rb

echo "Roundtripping Ruby back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/19_quickfox.rb --source-lang ruby --target-lang python
mv tests/roundtrip/19_quickfox.python tests/roundtrip/20_quickfox_ruby_roundtrip.py

echo "Transpiling to PHP..."
python3 -m pseudocoup.cli --source tests/roundtrip/00_quickfox.py --target-lang php
mv tests/roundtrip/00_quickfox.php tests/roundtrip/21_quickfox.php

echo "Roundtripping PHP back to Python..."
python3 -m pseudocoup.cli --source tests/roundtrip/21_quickfox.php --source-lang php --target-lang python
mv tests/roundtrip/21_quickfox.python tests/roundtrip/22_quickfox_php_roundtrip.py

echo "------------------------------------------------"
echo "Roundtrip tests completed in tests/roundtrip/"
ls -la tests/roundtrip/

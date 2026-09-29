# RecordBridge — Validated CSV-to-JSON Migration

**Category:** Legacy Software Modernization — supporting data-migration tooling  
**Status:** New independent working project; not a historical customer application migration.

## Description

RecordBridge turns legacy CSV exports into typed JSON through an explicit, reviewable migration workflow. Users open or paste source data, map field names and types, validate records and inspect the generated output before downloading it. A compiled C++17 engine handles quoted commas, multiline fields, escaped quotes and Unicode.

Invalid input blocks the complete export with actionable diagnostics. Required values and declared types are checked, while the command-line engine protects original files and existing destinations. Sixteen behavioral tests cover parsing, conversion, malformed input and file preservation.

This independent project demonstrates supporting tooling for software modernization. Screenshots show disclosed verification data processed by the actual engine. Compilation and execution were verified on macOS; Windows behavior remains unverified. Validation covers declared structure and types, so destination-specific business rules still require separate checks.

**Skills:** C++17, legacy data migration, CSV parsing, JSON, type validation, debugging, Python integration, automated testing, HTML/CSS/JavaScript.

**Screenshot captions:** See `screenshots/CAPTIONS.md`.

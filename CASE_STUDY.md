# RecordBridge — Validated CSV-to-JSON Migration

**Category:** Legacy Software Modernization — supporting data-migration tooling  
**Project type:** New independent software project for Ismail Habib  
**Stack:** C++17, Python standard library, HTML, CSS, JavaScript  
**Delivery:** Working local application, command-line engine, source code, verification fixtures, and tests

## The challenge

CSV exports often sit between an existing application and a newer system. A migration needs to preserve real values while making field names, data types, and invalid records explicit. Quoted commas, multiline notes, duplicate headers, and inconsistent row widths make a naive split-on-comma approach unreliable.

## What was built

RecordBridge is a complete local migration workflow: open or paste a CSV file, discover its fields, map names and types, validate every record, inspect the JSON preview, and download the complete export. A C++17 engine performs parsing and conversion. The Python adapter invokes the compiled engine with argument lists, and the interface presents its real results.

The engine supports quoted fields, escaped quotes, embedded newlines, Unicode, and several line-ending conventions. A mapping specifies required values and string, integer, number, or boolean types. Invalid input blocks the complete export and identifies the affected source field and line when available. Existing destinations cannot be overwritten, and source files are preserved.

## Verified outcomes

- The supplied fixture produced three JSON records with typed identifiers, booleans, and numbers.
- Quoted commas, a multiline note, Unicode characters, and escaped quote characters were preserved in the expected values.
- Sixteen behavioral tests passed against the compiled engine and Python adapter, including invalid types, malformed CSV, duplicate names, absent fields, invalid UTF-8, and preservation of existing input/output files.
- C++ compilation completed using Apple Clang 17 on macOS 15.7.8. Python and browser-script syntax checks passed.

These are reproducible software-verification results, not customer productivity or commercial-impact claims. The supplied data is a labeled verification fixture.

## Scope and limits

This is a newly built migration tool, not a historical customer C++ application migration. Windows compilation and runtime behavior have not been verified. Input size, row count, and dashboard execution limits are documented. Validation checks the declared types and structure; it does not infer business rules, email validity, unique customer identifiers, or requirements of a destination system.

## Portfolio screenshot captions

1. **Migration workspace:** local CSV input beside explicit field-to-JSON mappings; the displayed source is a verification fixture.
2. **Verified export:** the engine-generated validation report and JSON preview after a successful fixture run.
3. **Actionable diagnostics:** a deliberately invalid fixture edit blocks export and identifies the rejected value.

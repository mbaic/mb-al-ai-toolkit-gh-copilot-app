---
name: al-best-practices
description: AL language best practices, code style, naming conventions, performance rules (SetLoadFields, early filtering, set-based operations, temp tables), error handling with ErrorInfo/TryFunction, and a code-quality checklist for Microsoft Dynamics 365 Business Central. Use whenever editing, reviewing, or generating AL code (`*.al` files) — especially in PTE projects.
---

# AL Best Practices & Performance

## Code Style & Format

- **Indentation**: 4 spaces (no tabs)
- **Keywords**: Lowercase (`table`, `page`, `procedure`, `begin`, `end`)
- **Variables**: PascalCase (`CustomerNo`, `TotalAmount`)
- **Constants**: UPPERCASE
- **Brackets**: Curly brackets on new lines for blocks

## Naming Conventions

### File Naming
Pattern: `<ObjectName>.<ObjectType>.al`

Examples: `CustomerCard.Page.al`, `SalesPostingMgt.Codeunit.al`

### Object Naming
- **PTE Prefix**: 3-character customer prefix
- **Max Length**: 30 characters total
- **Interfaces**: Prefix with `I` (e.g., `IDataProcessor`)
- **Implementations**: Suffix with `Impl` (e.g., `DataProcessorImpl`)
- **Handlers**: Suffix with `Handler` for event subscriber codeunits

### Variable & Procedure Naming
```al
Customer: Record Customer;          // Record type as name
IsValidTransaction: Boolean;        // Boolean: Is, Has, Can prefix
TotalAmount: Decimal;               // Descriptive purpose
i: Integer;                         // Loop counter exception

procedure CalculateBalance()        // Action verb + subject
procedure ValidateSalesDocument()   // Clear intent
procedure GetDefaultPaymentTerms()  // Get for retrieval
```

## Performance Rules

### Rule 1: SetLoadFields BEFORE SetRange
Order matters — always specify fields first:

```al
// CORRECT
Customer.SetLoadFields("No.", Name, "Balance (LCY)");
Customer.SetRange("Country/Region Code", 'US');
if Customer.FindSet() then

// WRONG - SetLoadFields after filter
Customer.SetRange("Country/Region Code", 'US');
Customer.SetLoadFields("No.", Name);  // Too late!
```

### Rule 2: Filter Early
Apply filters before processing:

```al
// Good - filter first
CustLedgerEntry.SetRange("Customer No.", CustomerNo);
CustLedgerEntry.SetRange(Open, true);
CustLedgerEntry.CalcSums("Amount (LCY)");

// Avoid - filtering in loops
if CustLedgerEntry.FindSet() then
    repeat
        if CustLedgerEntry.Open then  // Too late!
            TotalAmount += CustLedgerEntry."Amount (LCY)";
    until CustLedgerEntry.Next() = 0;
```

### Rule 3: Use Set-Based Operations
Prefer aggregation over manual loops:

```al
// Use CalcSums
SalesLine.SetRange("Document No.", DocNo);
SalesLine.CalcSums(Amount);
exit(SalesLine.Amount);

// Avoid manual loops
```

### Rule 4: Temporary Tables for Processing
Use temporary tables for in-memory processing:

```al
procedure ProcessData(var TempBuffer: Record "Buffer" temporary)
begin
    // Process in memory, write once to database
end;
```

### Rule 5: Efficient Record Iteration
```al
// Use FindSet for loops
if Customer.FindSet() then
    repeat
        ProcessCustomer(Customer);
    until Customer.Next() = 0;

// Use FindFirst for single records
if Customer.FindFirst() then
```

## Error Handling

### Modern ErrorInfo Pattern
```al
procedure ValidateCreditLimit(Customer: Record Customer; Amount: Decimal)
var
    ErrorInfo: ErrorInfo;
begin
    if Amount > Customer."Credit Limit (LCY)" then begin
        ErrorInfo.Title := 'Credit Limit Exceeded';
        ErrorInfo.Message := StrSubstNo('Amount %1 exceeds limit %2.',
            Amount, Customer."Credit Limit (LCY)");
        ErrorInfo.DetailedMessage := 'Reduce order or request limit increase.';
        ErrorInfo.PageNo := Page::"Customer Card";
        ErrorInfo.RecordId := Customer.RecordId;
        Error(ErrorInfo);
    end;
end;
```

### TryFunction Pattern
Use `[TryFunction]` only for operations that do **not** perform any database writes (no Insert, Modify, Delete, or codeunit runs that trigger CRUD). TryFunctions catch runtime errors and return `false` — they do not roll back any partial writes.

Valid use cases: parsing/conversion, external service calls, validation logic with no side effects.

```al
// CORRECT - TryFunction for parsing/validation only (no CRUD)
[TryFunction]
local procedure TryParseAmount(RawText: Text; var ParsedAmount: Decimal)
begin
    // Pure evaluation - no database writes
    ParsedAmount := ParseDecimal(RawText);  // throws on invalid input
end;

procedure ImportAmount(RawText: Text): Decimal
var
    ParsedAmount: Decimal;
begin
    if not TryParseAmount(RawText, ParsedAmount) then
        Error('Invalid amount format: %1', RawText);
    exit(ParsedAmount);
end;

// WRONG - TryFunction wrapping CRUD or posting operations
[TryFunction]
local procedure TryPostDocument(var SalesHeader: Record "Sales Header")
var
    SalesPost: Codeunit "Sales-Post";
begin
    SalesPost.Run(SalesHeader);  // NOT allowed - triggers database writes
end;
```

## Events & Extensibility

- Use event subscribers and integration events, never modify standard objects directly
- Name event handler codeunits with `Handler` suffix
- Design event parameters to provide sufficient context

## Documentation

Use XML documentation for global procedures:

```al
/// <summary>
/// Calculates customer balance including pending orders.
/// </summary>
/// <param name="CustomerNo">The customer number</param>
/// <returns>Total balance in LCY</returns>
procedure CalculateBalance(CustomerNo: Code[20]): Decimal
```

## Code Quality Checklist

- [ ] No hardcoded user messages (use labels)
- [ ] SetLoadFields before SetRange
- [ ] Filters applied before loops
- [ ] No cognitive complexity >= 15
- [ ] TryFunctions used only for read/validation logic — never wrapping CRUD operations
- [ ] Error messages are user-friendly
- [ ] No compilation warnings or errors

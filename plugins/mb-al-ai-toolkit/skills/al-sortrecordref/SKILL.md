---
name: al-sortrecordref
description: Expert guidance on sorting records dynamically using RecordRef in Microsoft Dynamics 365 Business Central — covers the SortRecordRef procedure from the Type Helper codeunit, SetView, ascending/descending order, and best practices for generic, table-agnostic record handling. Use when working with RecordRef, FieldRef, dynamic sorting, or generic data utilities in AL.
---

# AL RecordRef Sorting & SortRecordRef Skill

## Purpose

This skill provides expert guidance on sorting records dynamically using **RecordRef** in Dynamics 365 Business Central. It covers:

- **SortRecordRef procedure** from the Type Helper codeunit (Codeunit 10)
- **RecordRef sorting strategies** for dynamic, table-agnostic code
- **SetView method** for combining sorting, ordering, and filtering
- **Ascending/Descending order** control via the Ascending() method
- **Best practices** for generic code that works across multiple tables
- **Key selection strategies** for reliable sorting without hardcoding

## When to Use This Skill

Use this skill when you need to:

- Sort records dynamically using a **RecordRef** variable (not tied to a specific table type)
- Implement the **SortRecordRef** procedure in your codeunits
- Handle sorting for **multiple table types** in a single code path
- Control sort order programmatically (ascending vs. descending)
- Combine **sorting, filtering, and key selection** in generic code
- Understand the **SetView method** and its impact on record iteration
- Apply **field-based sorting** when the primary key is not suitable
- Make **language-independent** sorting code that works across locales

## Core Concepts: RecordRef Sorting

### What is RecordRef?

**RecordRef** is a data type that acts as a **generic runtime pointer to any table**. Unlike a typed `Record` variable (which is bound to a specific table at compile time), a RecordRef can reference any table by its ID.

**Key Differences**:
| Aspect | Record (Typed) | RecordRef (Dynamic) |
|--------|----------------|-------------------|
| **Table Binding** | Compile-time, specific table | Runtime, any table |
| **Syntax** | `Record Customer` | `RecordRef` + `Open(Integer)` |
| **Use Case** | Normal AL code | Generic utilities, Type Helpers |
| **Sorting** | `SetCurrentKey()` | `CurrentKeyIndex()` or `SetView()` |

### Why Sort RecordRef?

RecordRef defaults to the **primary key**. When you need:
- A different sort order (by Name instead of ID)
- **Descending order** instead of ascending
- Multi-table generic code that applies the same sort to different tables
- **Dynamic sort specifications** at runtime

…you need explicit sorting.

## The SortRecordRef Procedure

### Syntax

```al
procedure SortRecordRef(var RecRef: RecordRef; CommaSeparatedFieldsToSort: Text; Ascending: Boolean)
```

### What It Does

The **SortRecordRef** procedure (from Codeunit 10 "Type Helper") sets up a sorting view on a RecordRef by:

1. **Accepting field names** as a comma-separated text string
2. **Applying sort direction** (ascending or descending)
3. **Building a SORTING clause** using the **SetView** method
4. **Initializing the record set** with **FindSet()** (optional behavior)

### Implementation

```al
procedure SortRecordRef(var RecRef: RecordRef; CommaSeparatedFieldsToSort: Text; Ascending: Boolean)
var
    OrderString: Text;
begin
    if Ascending then
        OrderString := 'order(ascending)'
    else
        OrderString := 'order(descending)';

    RecRef.SetView(StrSubstNo('SORTING(%1) %2', CommaSeparatedFieldsToSort, OrderString));
    if RecRef.FindSet() then;
end;
```

### Parameters Explained

| Parameter | Type | Purpose |
|-----------|------|---------|
| `RecRef` | `RecordRef` (var) | The record reference to sort (modified in place) |
| `CommaSeparatedFieldsToSort` | `Text` | Field names or numbers separated by commas (e.g., `"Name,City"` or `"2,3"`) |
| `Ascending` | `Boolean` | `true` = ascending order; `false` = descending order |

## How SetView Works

The **SetView** method constructs a view string that combines **sorting, ordering, and filters** in a single operation.

### View String Syntax

```
SORTING(Field1,Field2,...) Order(Ascending|Descending) Where(Filters...)
```

**Example**:
```
SORTING(Name) order(ascending)
SORTING("Customer No.",City) order(descending)
SORTING("Document Date") order(ascending) Where("Status"=const(Open))
```

### Effects of SetView

- **Sets the sort key** to the specified fields
- **Sets the sort order** (ascending or descending)
- **Applies filters** (optional, via Where clause)
- **Clears prior filters** (if you use empty string, resets to primary key)
- **Requires FindSet/FindFirst** to actually retrieve sorted records

**Important**: SetView alone does not iterate — it only configures the view. You must call **FindSet()**, **FindFirst()**, or **FindLast()** to populate records.

## Sorting Strategies

### Strategy 1: Using SortRecordRef (Simple & Direct)

Best for: Quick sorting, when field names are known.

```al
procedure ProcessCustomersByName(var RecRef: RecordRef)
var
    TypeHelper: Codeunit "Type Helper";
begin
    RecRef.Open(Database::Customer);
    TypeHelper.SortRecordRef(RecRef, 'Name', true);  // Sort by Name, ascending

    if RecRef.FindSet() then
        repeat
            ProcessRecord(RecRef);
        until RecRef.Next() = 0;
end;
```

**Pros**: Simple, readable, direct.
**Cons**: Only handles single-field or comma-separated field strings; doesn't offer fine-grained key index control.

### Strategy 2: Using CurrentKeyIndex (Advanced & Reliable)

Best for: Production code, multi-language environments, secondary key selection.

```al
procedure ProcessCustomersBySecondaryKey(var RecRef: RecordRef; KeyFieldName: Text)
var
    FieldRef: FieldRef;
    KeyIndex: Integer;
begin
    RecRef.Open(Database::Customer);

    // Find the key index that contains the desired field
    FieldRef := RecRef.Field(RecRef.SystemIdNo());  // Replace with actual field logic
    KeyIndex := GetKeyIndex(RecRef, KeyFieldName);  // Custom helper function

    if KeyIndex > 0 then
        RecRef.CurrentKeyIndex(KeyIndex);

    if RecRef.FindSet() then
        repeat
            ProcessRecord(RecRef);
        until RecRef.Next() = 0;
end;

local procedure GetKeyIndex(RecRef: RecordRef; KeyFieldName: Text): Integer
var
    KeyRef: KeyRef;
    i: Integer;
begin
    for i := 1 to RecRef.KeyCount() do begin
        KeyRef := RecRef.KeyIndex(i);
        if StrPos(Format(KeyRef), KeyFieldName) > 0 then
            exit(i);
    end;
    exit(-1);  // Key not found
end;
```

**Pros**: Language-independent, reliable, supports secondary keys.
**Cons**: More complex, requires helper logic to find keys.

### Strategy 3: Using SetView + Ascending() Method (Flexible)

Best for: Combining sorting with filtering, dynamic specifications.

```al
procedure ProcessCustomersWithFilter(var RecRef: RecordRef; SortField: Text; DescendingOrder: Boolean)
var
    CustomerNo: FieldRef;
begin
    RecRef.Open(Database::Customer);

    // Set sorting and filter in one call
    RecRef.SetView(StrSubstNo('SORTING(%1) Order(%2) Where("Blocked"=const(false))',
        SortField,
        if DescendingOrder then 'descending' else 'ascending'));

    // Verify and optionally adjust order
    if not RecRef.Ascending() = DescendingOrder then
        RecRef.Ascending(DescendingOrder);

    if RecRef.FindSet() then
        repeat
            ProcessRecord(RecRef);
        until RecRef.Next() = 0;
end;
```

**Pros**: Flexible, combines sorting with filtering, supports order verification.
**Cons**: SetView overwrites prior filters; view string syntax requires care.

## Best Practices

### Do: Declare Field Names Explicitly

```al
procedure SortCustomers(var RecRef: RecordRef)
var
    TypeHelper: Codeunit "Type Helper";
begin
    // Good: Clear field name
    TypeHelper.SortRecordRef(RecRef, 'Name', true);
end;
```

### Do: Handle FindSet() Result

```al
procedure IterateSortedRecords(var RecRef: RecordRef)
begin
    if RecRef.FindSet() then
        repeat
            ProcessRecord(RecRef);
        until RecRef.Next() = 0;
end;
```

### Do: Document Table and Field Assumptions

```al
/// <summary>
/// Sorts purchase headers by document date, most recent first.
/// Assumes RecRef is opened to Database::"Purchase Header".
/// </summary>
procedure SortPurchaseHeadersByDate(var RecRef: RecordRef)
var
    TypeHelper: Codeunit "Type Helper";
begin
    TypeHelper.SortRecordRef(RecRef, 'Document Date', false);  // Descending
end;
```

### Don't: Hardcode Field Numbers

```al
// Bad: Field numbers are brittle across versions and extensions
RecRef.SetView('SORTING(2,5) order(ascending)');
```

### Don't: Assume SetView Preserves Existing Filters

```al
// Bad: SetView overwrites all filters
RecRef.SetRange('Active', true);
RecRef.SetView('SORTING(Name)');  // Clears the Active filter!

// Good: Include filters in SetView
RecRef.SetView('SORTING(Name) Where("Active"=const(true))');
```

### Don't: Call SetView Without FindSet/FindFirst

```al
// Bad: View is set but no records are loaded
RecRef.SetView('SORTING(Name) order(ascending)');
Message(RecRef.Field(1).Value);  // May be empty

// Good: Always call Find after SetView
RecRef.SetView('SORTING(Name) order(ascending)');
if RecRef.FindSet() then
    Message(RecRef.Field(1).Value);
```

## Common Scenarios

### Scenario 1: Sort Table by Custom Field, Then Iterate

```al
procedure ListCustomersAlphabetically()
var
    CustomerRecRef: RecordRef;
    TypeHelper: Codeunit "Type Helper";
    NameField: FieldRef;
begin
    CustomerRecRef.Open(Database::Customer);
    TypeHelper.SortRecordRef(CustomerRecRef, 'Name', true);

    if CustomerRecRef.FindSet() then
        repeat
            NameField := CustomerRecRef.Field(2);  // Name field ID
            Message('Customer: %1', NameField.Value);
        until CustomerRecRef.Next() = 0;
end;
```

### Scenario 2: Sort with Filters (Most Recent Open Orders)

```al
procedure ReportOpenSalesOrdersByDate()
var
    SalesRecRef: RecordRef;
begin
    SalesRecRef.Open(Database::"Sales Header");

    // Combine sort, order, and filter
    SalesRecRef.SetView('SORTING("Document Date") Order(descending) Where("Document Type"=const(Order),"Status"=const(Open))');

    if SalesRecRef.FindSet() then
        repeat
            ProcessOrder(SalesRecRef);
        until SalesRecRef.Next() = 0;
end;
```

### Scenario 3: Generic Procedure for Any Table

```al
procedure ExportSortedData(TableID: Integer; SortByField: Text; Desc: Boolean)
var
    RecRef: RecordRef;
    TypeHelper: Codeunit "Type Helper";
begin
    RecRef.Open(TableID);
    TypeHelper.SortRecordRef(RecRef, SortByField, not Desc);  // not Desc because SortRecordRef param is Ascending

    if RecRef.FindSet() then
        repeat
            ExportRecordToCsv(RecRef);
        until RecRef.Next() = 0;
end;
```

## Reference

For detailed code examples, advanced patterns, use cases, and implementation techniques, see **REFERENCE.md** in this skill folder.

Key topics in REFERENCE.md:
- Complete SortRecordRef implementations
- Multi-field sorting patterns
- Combining sorting with FieldRef operations
- Language-independent sorting strategies
- Performance considerations for large datasets
- Integration with Data Type Management codeunit
- Handling edge cases and errors

## Key Concepts to Remember

1. **RecordRef** is a generic table pointer; explicit sorting is required
2. **SortRecordRef** simplifies sorting by building SetView automatically
3. **SetView** overwrites filters — include Where clause to preserve them
4. **Always call FindSet/FindFirst** after SetView to load records
5. **Field names** are preferred over numbers for clarity and stability
6. **Ascending() method** can verify and modify sort order post-SetView
7. **CurrentKeyIndex()** is the production-grade approach for secondary keys

---

**Last Updated**: March 2026
**Skill Version**: 1.0
**Based on**: Type Helper Codeunit 10, Microsoft Learn RecordRef documentation, AL Guidelines best practices

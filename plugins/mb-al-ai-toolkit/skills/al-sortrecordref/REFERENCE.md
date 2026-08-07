# AL RecordRef Sorting & SortRecordRef - Detailed Reference

This document provides comprehensive code examples, implementation patterns, use cases, and advanced techniques for sorting records using RecordRef and the SortRecordRef procedure.

## Table of Contents

1. [Complete SortRecordRef Implementations](#complete-sortrecordref-implementations)
2. [Multi-Field Sorting Patterns](#multi-field-sorting-patterns)
3. [SetView Method Deep Dive](#setview-method-deep-dive)
4. [Ascending/Descending Order Control](#ascendingdescending-order-control)
5. [Generic Sorting Utilities](#generic-sorting-utilities)
6. [Real-World Use Cases](#real-world-use-cases)
7. [Error Handling & Edge Cases](#error-handling--edge-cases)
8. [Performance Considerations](#performance-considerations)
9. [Integration Patterns](#integration-patterns)

---

## Complete SortRecordRef Implementations

### Basic Usage: Single Field

```al
procedure SortCustomersByName()
var
    CustomerRecRef: RecordRef;
    TypeHelper: Codeunit "Type Helper";
begin
    CustomerRecRef.Open(Database::Customer);
    TypeHelper.SortRecordRef(CustomerRecRef, 'Name', true);  // Ascending

    if CustomerRecRef.FindSet() then
        repeat
            ProcessCustomer(CustomerRecRef);
        until CustomerRecRef.Next() = 0;
end;

local procedure ProcessCustomer(RecRef: RecordRef)
var
    NameField: FieldRef;
    NoField: FieldRef;
begin
    NoField := RecRef.Field(1);  // "No." field
    NameField := RecRef.Field(2);  // "Name" field
    Message('No: %1, Name: %2', NoField.Value, NameField.Value);
end;
```

### Custom Sort Procedure

```al
codeunit 50000 "Custom Sorter"
begin
    /// <summary>
    /// Sorts a RecordRef by specified field(s) in ascending or descending order.
    /// </summary>
    /// <param name="RecRef">The RecordRef to sort (modified in place)</param>
    /// <param name="FieldNames">Comma-separated field names (e.g., "Name,City")</param>
    /// <param name="Ascending">true for ascending, false for descending</param>
    procedure Sort(var RecRef: RecordRef; FieldNames: Text; Ascending: Boolean)
    var
        TypeHelper: Codeunit "Type Helper";
    begin
        TypeHelper.SortRecordRef(RecRef, FieldNames, Ascending);
    end;

    /// <summary>
    /// Sorts in ascending order (convenience method)
    /// </summary>
    procedure SortAscending(var RecRef: RecordRef; FieldNames: Text)
    begin
        Sort(RecRef, FieldNames, true);
    end;

    /// <summary>
    /// Sorts in descending order (convenience method)
    /// </summary>
    procedure SortDescending(var RecRef: RecordRef; FieldNames: Text)
    begin
        Sort(RecRef, FieldNames, false);
    end;
end;
```

---

## Multi-Field Sorting Patterns

### Two-Field Sorting (Primary + Secondary)

```al
procedure SortCustomersByStateAndName()
var
    CustomerRecRef: RecordRef;
    TypeHelper: Codeunit "Type Helper";
begin
    CustomerRecRef.Open(Database::Customer);

    // Sort by State, then by Name (both ascending)
    TypeHelper.SortRecordRef(CustomerRecRef, '"State Code","Name"', true);

    if CustomerRecRef.FindSet() then
        repeat
            ProcessCustomer(CustomerRecRef);
        until CustomerRecRef.Next() = 0;
end;
```

### Three-Field Sorting with Mixed Order

For cases requiring different sort orders on different fields, use **SetView** directly:

```al
procedure SortSalesOrdersComplex()
var
    SalesRecRef: RecordRef;
begin
    SalesRecRef.Open(Database::"Sales Header");

    // Sort by Customer (asc), Document Date (desc), Amount (asc)
    // Note: SetView only supports uniform order, so we use multiple calls
    SalesRecRef.SetView('SORTING("Sell-to Customer No.","Document Date") order(ascending)');

    // After FindSet, use SetAscending to adjust individual fields
    if SalesRecRef.FindSet() then begin
        SalesRecRef.SetAscending(SalesRecRef.Field(SalesRecRef.FieldIndex('Document Date')), false);  // Descending
        repeat
            ProcessOrder(SalesRecRef);
        until SalesRecRef.Next() = 0;
    end;
end;
```

---

## SetView Method Deep Dive

### Basic SetView Syntax

```al
procedure DemoSetView()
var
    RecRef: RecordRef;
    ViewString: Text;
begin
    RecRef.Open(Database::Customer);

    // Set view with sorting only
    RecRef.SetView('SORTING(Name) order(ascending)');

    // Retrieve the view that was set
    ViewString := RecRef.GetView(true);  // true = use captions
    Message('Current View: %1', ViewString);

    if RecRef.FindSet() then;
end;
```

### SetView with Filters

```al
procedure SortAndFilterCustomers()
var
    CustomerRecRef: RecordRef;
begin
    CustomerRecRef.Open(Database::Customer);

    // Combine sorting AND filtering in one SetView call
    CustomerRecRef.SetView(
        'SORTING(Name) order(ascending) Where("Country/Region Code"=const(US),"Blocked"=const(false))'
    );

    if CustomerRecRef.FindSet() then
        repeat
            ProcessCustomer(CustomerRecRef);
        until CustomerRecRef.Next() = 0;
end;
```

### Resetting to Primary Key

```al
procedure ResetSortingToPrimaryKey(var RecRef: RecordRef)
begin
    // Empty SetView clears all filters and reverts to primary key
    RecRef.SetView('');
end;
```

### Building Dynamic View Strings

```al
procedure BuildAndApplyView(var RecRef: RecordRef; SortFields: Text; FilterClause: Text)
var
    ViewString: Text;
    OrderString: Text;
begin
    // Build order string
    OrderString := 'order(ascending)';

    // Build complete view
    if FilterClause = '' then
        ViewString := StrSubstNo('SORTING(%1) %2', SortFields, OrderString)
    else
        ViewString := StrSubstNo('SORTING(%1) %2 Where(%3)', SortFields, OrderString, FilterClause);

    RecRef.SetView(ViewString);
    if RecRef.FindSet() then;
end;
```

---

## Ascending/Descending Order Control

### Using the Ascending() Method

```al
procedure CheckAndSetSortOrder(var RecRef: RecordRef; ShouldBeAscending: Boolean)
var
    IsCurrentlyAscending: Boolean;
begin
    // Check current sort order
    IsCurrentlyAscending := RecRef.Ascending();

    if IsCurrentlyAscending <> ShouldBeAscending then begin
        // Change sort order if needed
        RecRef.Ascending(ShouldBeAscending);
        Message('Sort order changed to %1', if ShouldBeAscending then 'Ascending' else 'Descending');
    end;
end;
```

### Complete Order Control Pattern

```al
procedure SortWithOrderVerification(var RecRef: RecordRef; FieldName: Text; Descending: Boolean)
var
    TypeHelper: Codeunit "Type Helper";
begin
    // Apply sorting via SortRecordRef
    TypeHelper.SortRecordRef(RecRef, FieldName, not Descending);  // Negate because param is Ascending

    // Verify and adjust if needed
    if RecRef.Ascending() = Descending then
        RecRef.Ascending(not Descending);

    if RecRef.FindSet() then;
end;
```

### SetAscending for Specific Fields

```al
procedure SortMultipleFieldsWithMixedOrder()
var
    ItemRecRef: RecordRef;
    PostingDateField: FieldRef;
    QuantityField: FieldRef;
begin
    ItemRecRef.Open(Database::Item);

    // Sort by two fields: Posting Date (descending), Quantity (ascending)
    ItemRecRef.SetView('SORTING("Posting Date","Quantity") order(ascending)');

    if ItemRecRef.FindSet() then begin
        // Adjust Posting Date to descending while keeping Quantity ascending
        PostingDateField := ItemRecRef.Field(ItemRecRef.FieldIndex('Posting Date'));
        ItemRecRef.SetAscending(PostingDateField, false);

        repeat
            ProcessItem(ItemRecRef);
        until ItemRecRef.Next() = 0;
    end;
end;
```

---

## Generic Sorting Utilities

### Generic Sort Wrapper

```al
codeunit 50001 "Generic Sorter"
begin
    /// <summary>
    /// Opens a table by ID and sorts it by specified fields.
    /// Returns the sorted RecordRef for iteration.
    /// </summary>
    procedure OpenAndSort(TableID: Integer; SortFields: Text; Ascending: Boolean): RecordRef
    var
        RecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
    begin
        RecRef.Open(TableID);
        TypeHelper.SortRecordRef(RecRef, SortFields, Ascending);
        exit(RecRef);
    end;

    /// <summary>
    /// Counts records after applying a sort (for reporting)
    /// </summary>
    procedure CountSortedRecords(TableID: Integer; SortFields: Text): Integer
    var
        RecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
    begin
        RecRef := OpenAndSort(TableID, SortFields, true);
        exit(RecRef.Count());
    end;

    /// <summary>
    /// Applies sorting AND filtering with one operation
    /// </summary>
    procedure SortAndFilter(var RecRef: RecordRef; SortFields: Text; FilterText: Text; Ascending: Boolean)
    var
        ViewString: Text;
    begin
        if FilterText = '' then
            ViewString := StrSubstNo('SORTING(%1) order(%2)', SortFields, if Ascending then 'ascending' else 'descending')
        else
            ViewString := StrSubstNo('SORTING(%1) order(%2) Where(%3)', SortFields,
                if Ascending then 'ascending' else 'descending', FilterText);

        RecRef.SetView(ViewString);
    end;
end;
```

### Reusable Sort Library

```al
codeunit 50002 "Sort Helpers"
begin
    /// <summary>
    /// Sorts a RecordRef by multiple fields with uniform order
    /// </summary>
    procedure SortByFields(var RecRef: RecordRef; FieldList: List of [Text]; Ascending: Boolean)
    var
        FieldNames: Text;
        Field: Text;
    begin
        foreach Field in FieldList do begin
            if FieldNames = '' then
                FieldNames := '"' + Field + '"'
            else
                FieldNames += ',"' + Field + '"';
        end;

        var TypeHelper: Codeunit "Type Helper";
        TypeHelper.SortRecordRef(RecRef, FieldNames, Ascending);
    end;

    /// <summary>
    /// Finds the last record in a sorted set (useful for descending sorts)
    /// </summary>
    procedure FindLastInSort(var RecRef: RecordRef): Boolean
    begin
        exit(RecRef.FindLast());
    end;

    /// <summary>
    /// Iterates through sorted records in a safe, controlled manner
    /// </summary>
    procedure IterateSortedRecords(var RecRef: RecordRef; ProcessProc: Text)
    begin
        if RecRef.FindSet() then
            repeat
                // ProcessProc would be invoked here in a real scenario
            until RecRef.Next() = 0;
    end;
end;
```

---

## Real-World Use Cases

### Use Case 1: Generate Sorted Report Data

```al
codeunit 50010 "Sales Report Generator"
begin
    procedure GenerateSalesOrderReport()
    var
        SalesRecRef: RecordRef;
    begin
        SalesRecRef.Open(Database::"Sales Header");

        // Sort by customer, then document date (most recent first)
        SalesRecRef.SetView('SORTING("Sell-to Customer No.","Document Date") order(ascending)');
        SalesRecRef.SetAscending(SalesRecRef.Field(SalesRecRef.FieldIndex('Document Date')), false);

        if SalesRecRef.FindSet() then
            repeat
                OutputReportLine(SalesRecRef);
            until SalesRecRef.Next() = 0;
    end;

    local procedure OutputReportLine(RecRef: RecordRef)
    var
        CustomerNo: FieldRef;
        DocumentNo: FieldRef;
        DocumentDate: FieldRef;
    begin
        CustomerNo := RecRef.Field(RecRef.FieldIndex('Sell-to Customer No.'));
        DocumentNo := RecRef.Field(RecRef.FieldIndex('No.'));
        DocumentDate := RecRef.Field(RecRef.FieldIndex('Document Date'));

        Message('Customer: %1 | Order: %2 | Date: %3', CustomerNo.Value, DocumentNo.Value, DocumentDate.Value);
    end;
end;
```

### Use Case 2: Export Data in Sorted Order

```al
codeunit 50011 "Data Exporter"
begin
    procedure ExportCustomersToCSV(Filename: Text)
    var
        CustomerRecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
        FileHandle: File;
        OutStream: OutStream;
    begin
        CustomerRecRef.Open(Database::Customer);
        TypeHelper.SortRecordRef(CustomerRecRef, 'Name', true);

        FileHandle.Create(Filename);
        FileHandle.CreateOutStream(OutStream);

        if CustomerRecRef.FindSet() then
            repeat
                WriteCustomerLine(OutStream, CustomerRecRef);
            until CustomerRecRef.Next() = 0;

        FileHandle.Close();
    end;

    local procedure WriteCustomerLine(OutStream: OutStream; RecRef: RecordRef)
    var
        NoField: FieldRef;
        NameField: FieldRef;
        CityField: FieldRef;
    begin
        NoField := RecRef.Field(RecRef.FieldIndex('No.'));
        NameField := RecRef.Field(RecRef.FieldIndex('Name'));
        CityField := RecRef.Field(RecRef.FieldIndex('City'));

        OutStream.WriteText(StrSubstNo('%1,%2,%3', NoField.Value, NameField.Value, CityField.Value));
        OutStream.WriteText(OutStream.NewLine());
    end;
end;
```

### Use Case 3: Archive Data by Date (Descending)

```al
codeunit 50012 "Archive Manager"
begin
    procedure ArchiveOldOrders(CutoffDate: Date)
    var
        SalesRecRef: RecordRef;
    begin
        SalesRecRef.Open(Database::"Sales Header");

        // Sort by date, most recent first (to skip recent orders)
        SalesRecRef.SetView('SORTING("Document Date") order(descending) Where("Document Type"=const(Order),"Status"=const(Released))');

        if SalesRecRef.FindSet() then
            repeat
                if SalesRecRef.Field(SalesRecRef.FieldIndex('Document Date')).Value < CutoffDate then
                    ArchiveRecord(SalesRecRef);
            until SalesRecRef.Next() = 0;
    end;

    local procedure ArchiveRecord(RecRef: RecordRef)
    begin
        // Archive logic here
        Message('Archived order: %1', RecRef.Field(RecRef.FieldIndex('No.')).Value);
    end;
end;
```

### Use Case 4: Data Validation with Sorted Inspection

```al
codeunit 50013 "Data Validator"
begin
    procedure ValidateItemsInStockOrder()
    var
        ItemRecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
        ErrorCount: Integer;
    begin
        ItemRecRef.Open(Database::Item);

        // Sort by stock level (ascending) to see low-stock items first
        TypeHelper.SortRecordRef(ItemRecRef, 'Inventory', true);

        if ItemRecRef.FindSet() then
            repeat
                if not ValidateItem(ItemRecRef) then
                    ErrorCount += 1;
            until ItemRecRef.Next() = 0;

        Message('Validation complete. %1 errors found.', ErrorCount);
    end;

    local procedure ValidateItem(RecRef: RecordRef): Boolean
    var
        InventoryField: FieldRef;
    begin
        InventoryField := RecRef.Field(RecRef.FieldIndex('Inventory'));
        if InventoryField.Value < 0 then
            exit(false);  // Invalid
        exit(true);
    end;
end;
```

---

## Error Handling & Edge Cases

### Handling Missing Fields

```al
procedure SortWithFieldValidation(var RecRef: RecordRef; FieldName: Text; Ascending: Boolean)
var
    FieldRef: FieldRef;
    ErrorMsg: Text;
begin
    // Verify field exists before sorting
    if RecRef.FieldExists(RecRef.FieldIndex(FieldName)) then begin
        var TypeHelper: Codeunit "Type Helper";
        TypeHelper.SortRecordRef(RecRef, FieldName, Ascending);
    end else begin
        ErrorMsg := StrSubstNo('Field %1 does not exist in table %2', FieldName, RecRef.Name);
        Error(ErrorMsg);
    end;
end;
```

### Handling Empty RecordRef

```al
procedure SafeSort(var RecRef: RecordRef; FieldName: Text)
var
    TypeHelper: Codeunit "Type Helper";
begin
    if RecRef.Number = 0 then
        Error('RecordRef is not open. Call RecordRef.Open() first.');

    TypeHelper.SortRecordRef(RecRef, FieldName, true);
end;
```

### Fallback to Primary Key on Error

```al
procedure SortWithFallback(var RecRef: RecordRef; FieldName: Text)
var
    TypeHelper: Codeunit "Type Helper";
begin
    begin
        TypeHelper.SortRecordRef(RecRef, FieldName, true);
    end catch E: Error do begin
        Message('Failed to sort by %1. Reverting to primary key. Error: %2', FieldName, E.Message);
        RecRef.SetView('');  // Reset to primary key
    end;
end;
```

### Detecting Empty Result Set

```al
procedure SortAndProcessWithCheck(var RecRef: RecordRef; FieldName: Text)
var
    TypeHelper: Codeunit "Type Helper";
    RecordCount: Integer;
begin
    TypeHelper.SortRecordRef(RecRef, FieldName, true);

    RecordCount := RecRef.Count();
    if RecordCount = 0 then begin
        Message('No records found after sorting.');
        exit;
    end;

    if RecRef.FindSet() then
        repeat
            ProcessRecord(RecRef);
        until RecRef.Next() = 0;
end;

local procedure ProcessRecord(RecRef: RecordRef)
begin
    // Process logic
end;
```

---

## Performance Considerations

### Large Dataset Sorting

For large datasets, avoid repeatedly sorting the same table:

```al
codeunit 50020 "Performance Conscious Sorter"
begin
    // ✅ Good: Sort once, iterate multiple times
    procedure Efficiency_SortOnce()
    var
        SalesRecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
    begin
        SalesRecRef.Open(Database::"Sales Header");
        TypeHelper.SortRecordRef(SalesRecRef, 'Document Date', false);  // Sort once

        // First pass: count records
        var Count := SalesRecRef.Count();

        // Second pass: iterate (reuse sorted order)
        if SalesRecRef.FindSet() then
            repeat
                ProcessOrder(SalesRecRef);
            until SalesRecRef.Next() = 0;
    end;

    // ❌ Bad: Re-sorting on each operation
    procedure Inefficiency_ResortMultipleTimes()
    var
        SalesRecRef: RecordRef;
        TypeHelper: Codeunit "Type Helper";
    begin
        SalesRecRef.Open(Database::"Sales Header");

        TypeHelper.SortRecordRef(SalesRecRef, 'Document Date', false);
        if SalesRecRef.FindSet() then
            repeat
                ProcessOrder(SalesRecRef);
            until SalesRecRef.Next() = 0;

        // Another operation requires re-opening and re-sorting (bad!)
        SalesRecRef.Close();
        SalesRecRef.Open(Database::"Sales Header");
        TypeHelper.SortRecordRef(SalesRecRef, 'Document Date', false);
        if SalesRecRef.FindSet() then;
    end;
end;
```

### Using Filters to Reduce Dataset Size

```al
procedure SortFilteredData()
var
    CustomerRecRef: RecordRef;
begin
    CustomerRecRef.Open(Database::Customer);

    // Filter BEFORE sorting to reduce the working set
    CustomerRecRef.SetView('SORTING(Name) order(ascending) Where("Blocked"=const(false),"Country/Region Code"=const(US))');

    if CustomerRecRef.FindSet() then
        repeat
            ProcessCustomer(CustomerRecRef);
        until CustomerRecRef.Next() = 0;
end;
```

---

## Integration Patterns

### Integration with Data TypeManagement

```al
codeunit 50030 "Advanced Record Handling"
begin
    procedure ProcessRecordByVariant(RecVariant: Variant; SortField: Text)
    var
        RecRef: RecordRef;
        DataTypeManagement: Codeunit "Data Type Management";
        TypeHelper: Codeunit "Type Helper";
    begin
        // Convert Variant to RecordRef
        DataTypeManagement.GetRecordRef(RecVariant, RecRef);

        // Sort the RecordRef
        TypeHelper.SortRecordRef(RecRef, SortField, true);

        // Process sorted records
        if RecRef.FindSet() then
            repeat
                ProcessRecord(RecRef);
            until RecRef.Next() = 0;
    end;

    local procedure ProcessRecord(RecRef: RecordRef)
    begin
        // Implementation
    end;
end;
```

### Custom Event Publishing

```al
codeunit 50031 "Event-Driven Sorter"
begin
    [IntegrationEvent(false, false)]
    procedure OnBeforeSort(var RecRef: RecordRef; var SortFields: Text; var Ascending: Boolean)
    begin
    end;

    [IntegrationEvent(false, false)]
    procedure OnAfterSort(var RecRef: RecordRef)
    begin
    end;

    procedure SortWithEvents(var RecRef: RecordRef; SortFields: Text; Ascending: Boolean)
    var
        TypeHelper: Codeunit "Type Helper";
    begin
        OnBeforeSort(RecRef, SortFields, Ascending);
        TypeHelper.SortRecordRef(RecRef, SortFields, Ascending);
        OnAfterSort(RecRef);
    end;
end;
```

---

**Last Updated**: March 2026
**Reference Version**: 1.0

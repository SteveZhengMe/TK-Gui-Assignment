# Program Design Document

## 1. Class Design

- All widgets and windows are inherited from tk.Frame
- I designed 4 widgets, they are:
  - LabelInputCombo: Entry + Label
  - LabelDDCombo: Combo box + Label
  - TreeViewWithScrollBar: Table + Scrollbar
  - LayoutFrame: pack multiple widgets
- I used the widgets to build two windows
  - ActivityDisplayWindow: Display the activities and summaries. This window is a "parent" window. If this window is closed, ActivityEntryWindow will close, and the application exits.
  - ActivityEntryWindow: Transaction insert and search. This window holds a handler of ActivityDisplayWindow because of the two reasons:
    - Close ActivityEntryWindow will trigger ActivityDisplayWindow close as well as the application
    - When a new record is inserted, it will be displayed at the ActivityDisplayWindow automatically

``` mermaid
    classDiagram
        ActivityDisplayWindow o-- LabelInputCombo
        ActivityDisplayWindow o-- TreeViewWithScrollBar
        ActivityDisplayWindow o-- LayoutFrame
        ActivityDisplayWindow o-- LabelDDCombo
        ActivityEntryWindow *-- ActivityDisplayWindow

        ActivityEntryWindow o-- LabelInputCombo
        ActivityEntryWindow o-- TreeViewWithScrollBar
        ActivityEntryWindow o-- LayoutFrame
        ActivityEntryWindow o-- LabelDDCombo

        LabelInputCombo o-- Validator

        ActivityEntryWindow o-- DataController
        ActivityDisplayWindow o-- DataController

        class ActivityEntryWindow {
            -createWidgets()
            -dataInputForm()
            -buttons()
            +updateTransactions()
        }

        class ActivityDisplayWindow {
            -createWidgets()
            -buildSummaryPage()
            -buildActivitiesPage()
            +updateInfo()
        }

        class DataController {
            +getSummaryInfo()
            +listTransactions()
            +addTransaction()
            +initializeDatabase()
        }
```

## 2. Major Sequence Diagram

### A. Application Initializing

``` mermaid
    sequenceDiagram
        Main ->>+ActivityDisplayWindow: Create
        ActivityDisplayWindow->>ActivityDisplayWindow: createWidgets
        ActivityDisplayWindow-->>ActivityDisplayWindow: buildSummaryPage
        ActivityDisplayWindow-->>ActivityDisplayWindow: updateInfo
        ActivityDisplayWindow->>+DataController: getSummaryInfo
        DataController-->>-ActivityDisplayWindow: Data from DB
        ActivityDisplayWindow-->>-Main: activityDisplayWindow instance, loop
        Main->>+ActivityEntryWindow: create(activityDisplayWindow)
        ActivityEntryWindow->>ActivityEntryWindow: createWidgets
        ActivityEntryWindow->>ActivityEntryWindow: updateTransactions
        ActivityEntryWindow->>+DataController: listTransactions
        DataController-->>-ActivityEntryWindow: Data from DB
        ActivityEntryWindow-->>-Main: activityEntryWindow instance, loop
```

- **createWidgets**: Create all the UI elements based on the widget classes
- **buildSummaryPage**: Build the summary information page as the first page of the "Summary Window"
- **updateTransactions**: Fill in the treeview in the "Activities Entry Window"

### B. Click "Search" Button

``` mermaid
    sequenceDiagram
        User->>+ActivityEntryWindow: Click Search Button
        ActivityEntryWindow->>+ActivityEntryWindow: trigger: searchOnClick
        ActivityEntryWindow->>ActivityEntryWindow: Collect the non-empty inputs and generate the query 
        ActivityEntryWindow->>+DataController: listTransactions(query)
        DataController-->>-ActivityEntryWindow: An Array of the query results
        ActivityEntryWindow->>ActivityEntryWindow: setValues to the tree view
        ActivityEntryWindow->>-User: Show successful message
```

### C. Click "Record" Button

``` mermaid
    sequenceDiagram
        User->>+ActivityEntryWindow: Click Record Button
        ActivityEntryWindow->>+ActivityEntryWindow: trigger: recordOnClick
        ActivityEntryWindow->>ActivityEntryWindow: Collect the non-empty inputs
        alt all inputs have the validated value
            ActivityEntryWindow->>+DataController: addTransaction(parameters)
            DataController-->>-ActivityEntryWindow: Success
            ActivityEntryWindow->>ActivityEntryWindow: setValues to the tree view
            ActivityEntryWindow->>+ActivityDisplayWindow: update summary and activities data in Summary Window
            ActivityEntryWindow->>-User: Show successful message
        else one input has invalidated value
            ActivityEntryWindow->>User: Input is not validate error
        else one input is empty
            ActivityEntryWindow->>User: not enough inputs error
        end
```
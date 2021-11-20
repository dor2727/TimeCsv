# TimeCsv

This project is a way for me to track my time, and get statistics about it.
This project sets a syntax and a parser, together with filters and statistics about the data.

## documentation & examples
An example file for the data format is found in the documentation folder

## Sublime Sytax
open sublime -> Preferences -> Browser Packages
Open the `User` folder
Create a new folder named `TimeCsv` (or any other name)
Copy the contents of the `Sublime_Package` folder into the `TimeCsv` folder

## Example code
```python
import TimeCsv
d = TimeCsv.DataFolder()
time_filter = TimeCsv.TimeFilter_ThisWeek()
data = time_filter % d.data
g = TimeCsv.GroupedStats_Group(data, time_filter)
print(g.to_text())
```
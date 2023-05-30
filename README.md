# isv-sync
delta finder between sfdc tech partner tracker &amp; go/isvmatrix

# v0.5
brian.wooden@databricks.com
2023-05-30

## Changelog
 - centralized report separator and added variable length dashes, for output beautification
 - added explicit header check for both input files (to complement the initial check that isv matrix does not have 2 header rows)
 - added check for accounts in go/isvmatrix that are NOT in SFDC report
 - defined a main function to make this haphazard project slightly more pythonic. If only barely. 

### TODO
 - centralize various discrepancy finders (integration status, category names, etc)


# v0.4
brian.wooden@databricks.com
2023-05-17

## Changelog
 - removed "new" from "Adding SFDC Account" sentence in output report, for easier copy pasta
 - udpated SFDC field name "zzz Databricks Parter Name" to "Databricks Parter Name" throughout script based on change in SFDC (and alerted Randy that "Parter" is spelled incorrectly)

### TODO
 - check for go/isvmatrix accounts NOT in SFDC report
 - centralize various discrepancy finders (integration status, category names, etc)

# v0.3
brian.wooden@databricks.com

## Changelog
 - Cleaned up output report to make it more human readable
 - Error handling for splitting names when there is no name to split (can't split an empty string)
 - Check for superflous header row in go/isvmatrix (and remove it if it exists)

### TODO
 - centralize various discrepancy finders (integration status, category names, etc)


# v0.2
brian.wooden@databricks.com

## Changelog
Added two new outputs (delta identification) for:

 - "category"
 - "new" (AKA "stranded") account records

# init v0.1
brian.wooden@databricks.com

**Inputs**: 
This version requires CSV files from 

 - SFDC
 - ISV Matrix

The paths are hardcoded at top of isv-sync.py

**Outputs**: 
 - Delta report of differences between the two for fields "SA", "PDM", and "Integration Validation Status", printed to screen
 - CSV file to be appended to go/isvmatrix (for accounts in SFDC not in go/isvmatrix)


**Usage Instructions**:
 1. Manually pull CSV from SFDC tech tracker report & go/isvmatrix
 2. lop off first row of isvmatrix (it has two header rows)
 3. Update paths in isv-sync.py to reflect above files
 4. run isv-sync.py
 5. View discrepancies
 6. Manually resolve
 7. Rinse & Repeat

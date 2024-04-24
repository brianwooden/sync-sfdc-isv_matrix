# sync-sfdc-isv_matrix
Python to evaluate CSV files from SFDC &amp; go/isvmatrix and report on discrepancies

**Usage Instructions**:
 1. Manually pull CSV from SFDC tech tracker (UTF-8, CSV, Details only) report & go/isvmatrix (CSV)
 2. lop off first row of isvmatrix (it has two header rows)
 3. Update paths in isv-sync.py to reflect above files
 4. run isv-sync.py
 5. View discrepancies
 6. Manually resolve
 7. Rinse & Repeat

# v1.1.5
brian.wooden@databricks.com
2024-04-24 11:26 EST

## Changelog
  - Updated dismissable header row logic to avoid worrying about number of integrations

# v1.1.4
brian.wooden@databricks.com
2024-03-01 18:49 EST

## Changelog
  - Updated to check required SFDC fields are present in the headers but don't worry if there are extra ones (we don't write SFDC report rows)
  - updated NA skip logic (to complement POOLED logic)
  - upddated headers in-code to remove '(Salesforce)' from Partner Category
  - added logic to ignore first name if last name is Zuckerberg (similar to Sepp)

# v1.1.3
brian.wooden@databricks.com
2023-12-04 11:51 EST

## Changelog
  - Updated to change in-memory PDM recommendation for matrix (doesn't write to file at this time)

# v1.1.2
brian.wooden@databricks.com
2023-10-17 09:18 PDT

## Changelog
  - Tuned PDM delta report to 'sfdc wins' for recommendation

# v1.1.1
brian.wooden@databricks.com
2023-10-17 09:18 PDT

 ## Changelog
  - stripped superflous commas from CSV output mode


# v1.1
brian.wooden@databricks.com
2023-10-17 08:13 PDT

 ## Changelog
  - Added CSV mode for outputs
  - Defaults to CSV mode for outputs

# v1.0
brian.wooden@databricks.com
2023-10-16 18:13 PDT

## Changelog
 - Refreshed headers logic, (re-implemented ISV superflous headers cleanup)
 - Further consolidated header check functions (eliminated stand-alone isv matrix header logic)

# v0.9
brian.wooden@databricks.com
2023-10-09 11:53 PDT

## Changelog
 - Refreshed headers based on changes to ISV Matrix
 - Added logic to faciliate "pooled" SA in matrix if unassigned in SFDC

# v0.8
brian.wooden@databricks.com
2023-09-06 14:33 EDT

## Changelog
 - Updated headers check to show differences
 - removed "Leverages UC personal Staging locations" from ISV Matrix headers

# v0.7
brian.wooden@databricks.com
2023-06-14 12:20 EDT

## Changelog
 - Updated headers for ISV Matrix to reflect new "partner integration count" in worksheet
 - Re-worked logic of "found in ISV Matrix but not SFDC" to sort report alphabetically to find like-errors

# v0.6
brian.wooden@databricks.com
2023-05-30 17:25 EDT

## Changelog
 - Updated expected headers in check & code for SFDC file because "Databricks Parter SA" was updated to "Databricks Partner SA".

# v0.5
brian.wooden@databricks.com
2023-05-30

## Changelog
 - centralized report separator and added variable length dashes, for output beautification
 - added explicit header check for both input files (to complement the initial check that isv matrix does not have 2 header rows)
 - added check for accounts in go/isvmatrix that are NOT in SFDC report
 - defined a main function to make this haphazard project slightly more pythonic. If only barely.

# v0.4
brian.wooden@databricks.com
2023-05-17

## Changelog
 - removed "new" from "Adding SFDC Account" sentence in output report, for easier copy pasta
 - udpated SFDC field name "zzz Databricks Parter Name" to "Databricks Parter Name" throughout script based on change in SFDC (and alerted Randy that "Parter" is spelled incorrectly)

### TODO
 - check for go/isvmatrix accounts NOT in SFDC report

# v0.3
brian.wooden@databricks.com

## Changelog
 - Cleaned up output report to make it more human readable
 - Error handling for splitting names when there is no name to split (can't split an empty string)
 - Check for superflous header row in go/isvmatrix (and remove it if it exists)

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

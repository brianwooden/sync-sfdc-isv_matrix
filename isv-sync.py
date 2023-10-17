import csv


def validate_csv_headers(csv_file, expected_headers, dismissable_headers):

    headers_match = False

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the first row (headers) from the CSV


        # Check if expected headers match the actual headers
        if headers == expected_headers:
            print('CSV header validation successful for', csv_file, 'Headers match the expected format.')
            headers_match = True
        # if they don't, report on difference
        else:
            print('CSV header validation failed for', csv_file, 'Headers do not match the expected format.')
            print('Expected headers: ', expected_headers)
            print('Actual headers: ', headers)
            difference = list(set(headers) ^ set(expected_headers))
            if difference:
                print('\n--> The difference between headers and new_headers is:', difference, '\n')
            else:
                print('The lists headers and expected_headers are the same. Hmmm.')
            if headers == dismissable_headers:
                # if headers are diferent than expected, but known pre-header row, lop it off and keep going
                print('Actually, the top of', csv_file, 'file starts with header line 1 of 2, and we only use the 2nd line for downstream field list. Lopping off the top line and overwriting', csv_file, ' and continuing.')
                with open(csv_file, 'r') as fin:
                    data = fin.read().splitlines(True)
                with open(csv_file, 'w') as fout:
                    fout.writelines(data[1:])
                headers_match = True

    return headers_match

def print_section_separator(heading_text):
    num_dashes = len(heading_text)
    print()
    for _ in range(num_dashes):
        print('-', end='')
    print(''.join(['\n', heading_text]))
    for _ in range(num_dashes):
        print('-', end='')
    print()

def report_finding_headers():
    print (','.join(['section', 'sfdc_partner', 'sfdc_person', 'matrix_partner', 'matrix_person', 'recommended_action']))
def report_finding(section, sfdc_partner, sfdc_item, matrix_partner, matrix_item, recommended_action):
    if section is None: section = ''
    if sfdc_partner is None: sfdc_partner = ''
    if sfdc_item is None: sfdc_item = ''
    if matrix_partner is None: matrix_partner = ''
    if matrix_item is None: matrix_item = ''
    if recommended_action is None:
        recommended_action = ''
    else:
        recommended_action = recommended_action.replace(',', '_')
    print (','.join([section, sfdc_partner, sfdc_item, matrix_partner, matrix_item, recommended_action]))


def main(isv_csv_fieldnames, output_mode):
    # open SFDC file as "left table", open ISV file as "right table" ~ish
    with open(sfdc) as sfdc_file:
        reader_left = csv.DictReader(sfdc_file, delimiter=',')
        with open(isv_matrix) as isv_file:
            reader_right = csv.DictReader(isv_file, delimiter=',')

            #if CSV output mode, write headers
            if output_mode.upper() == 'CSV':
                report_finding_headers()

            # look at both files and print accounts where ISV has different SA that SFDC
            if not output_mode.upper() == 'CSV':

                print_section_separator('SA Deltas')

            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        # use upper case evals for SA as they're incosistent across systems
                        if isv_row['Partner SA'].upper() != sfdc_row['Databricks Partner SA'].upper():
                            # unassigned looks differently across systems, and not spelled correctly, but I digress, let's check to make sure both aren't "unassigned" before moving on (if they are both unassigned, they match)
                            if not (len(sfdc_row['Databricks Partner SA'].upper()) == 0 and isv_row['Partner SA'].upper() == 'UNASIGNED'):
                                # replace empty strings (and mispelled UNASIGNEDs) with 'UNASSIGNED', for reporting purposes
                                if len(sfdc_row['Databricks Partner SA']) == 0:
                                    sfdc_row['Databricks Partner SA'] = 'UNASSIGNED'
                                if isv_row['Partner SA'].upper() == 'UNASIGNED' or len(isv_row['Partner SA']) == 0:
                                    isv_row['Partner SA'] = 'UNASSIGNED'
                                try:
                                    # sometimes a Timothy is known as Tim, so ignore first name if last name is Sepp
                                    if isv_row['Partner SA'].upper().split(' ', 1)[1] == 'SEPP' and sfdc_row['Databricks Partner SA'].upper().split(' ', 1)[1] == 'SEPP':
                                        pass
                                    else:
                                        if not output_mode.upper() == 'CSV':
                                            print('SFDC Account', sfdc_row['Account Name'], 'has SA', sfdc_row['Databricks Partner SA'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has SA', isv_row['Partner SA'])
                                        else:
                                            report_finding('SA Delta', sfdc_row['Account Name'], sfdc_row['Databricks Partner SA'], isv_row['Partner'], isv_row['Partner SA'], 'update SA in SFDC to ' + isv_row['Partner SA'])
                                # whenever we do a split, make sure it isn't a dreaded 7-10 split, as it were (bowling joke! But do make sure we didn't reference an index that didn't exist b/c we're trying to split an unsplittable, as it were
                                except IndexError:
                                        # ignore matrix POOLED SA if SFDC is Unassigned (otherwise, there is still a discrepancy that needs to be resolved)
                                        if isv_row['Partner SA'].upper() == 'POOLED' and sfdc_row['Databricks Partner SA'].upper() == 'UNASSIGNED':
                                            pass
                                        else:
                                            if not output_mode.upper() == 'CSV':
                                                print('SFDC Account', sfdc_row['Account Name'], 'has SA', sfdc_row['Databricks Partner SA'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has SA', isv_row['Partner SA'])
                                            else:
                                                report_finding('SA Delta', sfdc_row['Account Name'], sfdc_row['Databricks Partner SA'], isv_row['Partner'], isv_row['Partner SA'], 'update SA in SFDC to ' + isv_row['Partner SA'])

                # rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look at both files and print accounts where ISV has different PDM than SFDC
            if not output_mode.upper() == 'CSV':
                print_section_separator('PDM Deltas')
            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        # use upper case evals for PDM in case they're incosistent across systems
                        if isv_row['Partner Manager'].upper() != sfdc_row['Partner Manager'].upper():
                            # replace empty strings with 'UNASSIGNED', for reporting purposes
                            if len(isv_row['Partner Manager']) == 0:
                                isv_row['Partner Manager'] = 'UNASSIGNED'
                            if len(sfdc_row['Partner Manager']) == 0:
                                sfdc_row['Partner Manager'] = 'UNASSIGNED'
                            if not output_mode.upper() == 'CSV':
                                print('SFDC Account', sfdc_row['Account Name'], 'has PDM', sfdc_row['Partner Manager'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has PDM', isv_row['Partner Manager'])
                            else:
                                report_finding('PDM Delta', sfdc_row['Account Name'], sfdc_row['Partner Manager'], isv_row['Partner'], isv_row['Partner Manager'], 'update PDM in Matrix to ' + isv_row['Partner Manager'])
                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)


            # look at both files and print accounts where ISV says integration is validated but SFDC says it is in development
            # NB: This takes into account other integration status messages that are beyond validated, such as "Partner Connect Tile Published" etc
            if not output_mode.upper() == 'CSV':
                print_section_separator('Integration Status Deltas')
            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        if isv_row['Integration Status'] == 'Integration Validated' and sfdc_row['ISV Onboarding Status'] == 'Integration in Development':
                            if not output_mode.upper() == 'CSV':
                                print('SFDC Account', sfdc_row['Account Name'],'has validation status as', sfdc_row['ISV Onboarding Status'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has validation status as', isv_row['Integration Status'])
                            else:
                                report_finding('Validation Delta', sfdc_row['Account Name'], sfdc_row['ISV Onboarding Status'], isv_row['Partner'], isv_row['Integration Status'], 'updated SFDC validation to ' + isv_row['Integration Status'])

                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look at both files and print accounts where categories are different
            if not output_mode.upper() == 'CSV':
                print_section_separator('Category Deltas')
            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        if isv_row['Partner Category (Salesforce)'] != sfdc_row['ISV Partner Category']:
                            # AI/ML show up differently, check for that
                            if isv_row['Partner Category (Salesforce)'] == 'ML/ AI' and not sfdc_row['ISV Partner Category'] == 'Data Science / Machine Learning':
                                if not output_mode.upper() == 'CSV':
                                    print('SFDC Account', sfdc_row['Account Name'],'has partner category as', sfdc_row['ISV Partner Category'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has partner category as', isv_row['Partner Category (Salesforce)'])
                                else:
                                    report_finding('Category Delta', sfdc_row['Account Name'], sfdc_row['ISV Partner Category'], isv_row['Partner'], isv_row['Partner Category (Salesforce)'], 'updated SFDC Category to ' + isv_row['Partner Category (Salesforce)'])
                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look for accounts that exist in SFDC but not ISV Matrix, print those
            if not output_mode.upper() == 'CSV':
                print_section_separator('Account Deltas (in SFDC, not in ISV Matrix)')
            # open new csv for things in sfdc that aren't in matrix, define & write headers
            with open(new_matrix, 'w', newline='\n') as csvfile:
                # fieldnames expects a list
                writer = csv.DictWriter(csvfile, fieldnames=isv_csv_fieldnames)
                writer.writeheader()
                for sfdc_row in reader_left:
                    sfdc_in_matrix = False
                    for isv_row in reader_right:
                        if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                            sfdc_in_matrix = True
                    if not sfdc_in_matrix and sfdc_row['Account ID'] != 'Account ID':
                        # fix-up a few things for the ISV Matrix, accounting for known discrepancies between SFDC & go/isvmatrix regarding validation status && partner category
                        if sfdc_row['ISV Onboarding Status'] == 'GTM Collateral Published':
                            if not output_mode.upper() == 'CSV':
                                print ('Updating SFDC Account', sfdc_row['Account Name'], 'integration status from', sfdc_row['ISV Onboarding Status'], 'to Integration Validated in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Onboarding Status'] = 'Integration Validated'
                        if sfdc_row['ISV Onboarding Status'] == 'Integration Certified':
                            if not output_mode.upper() == 'CSV':
                                print ('Updating SFDC Account', sfdc_row['Account Name'], 'integration status from', sfdc_row['ISV Onboarding Status'], 'to Integration Validated in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Onboarding Status'] = 'Integration Validated'
                        if sfdc_row['ISV Partner Category'] == 'Data Science / Machine Learning':
                            if not output_mode.upper() == 'CSV':
                                print ('Updating SFDC Account', sfdc_row['Account Name'], 'category from', sfdc_row['ISV Partner Category'], 'to ML/ AI in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Partner Category'] = 'ML/ AI'
                        if not output_mode.upper() == 'CSV':
                            print('Adding SFDC Account', sfdc_row['Account Name'],'with Account ID', sfdc_row['Account ID'], 'to go/isvmatrix update-helper file:', new_matrix)
                        else:
                            report_finding('Account Delta', sfdc_row['Account Name'], sfdc_row['Account ID'], None, None, 'import matrix helpfer file ' + new_matrix)
                        writer.writerow({'Partner': sfdc_row['Account Name'],'Partner Manager': sfdc_row['Partner Manager'],'Partner Category (Salesforce)': sfdc_row['ISV Partner Category'],'Partner SA': sfdc_row['Databricks Partner SA'],'Databricks Salesforce Account Id': sfdc_row['Account ID'],'Integration Status': sfdc_row['ISV Onboarding Status']})
                    # be kind, rewind ISV file
                    isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look for accounts that exist in ISV Matrix but not SFDC, print those
            not_in_sfdc = []
            if not output_mode.upper() == 'CSV':
                print_section_separator('Account Deltas (in ISV Matrix, not in SFDC)')
            for isv_row in reader_right:
                matrix_in_sfdc = False
                for sfdc_row in reader_left:
                    try:
                        if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                            matrix_in_sfdc = True
                    except IndexError:
                        if not output_mode.upper() == 'CSV':
                            print ('index error in isv ghosts part 1\nisv:', isv_row, '\nsfdc: ', sfdc_row)
                    except KeyError:
                        if not output_mode.upper() == 'CSV':
                            print ('key error in isv ghosts part 1\nisv:', isv_row, '\nsfdc: ', sfdc_row)

                try:
                    if not matrix_in_sfdc and sfdc_row['Account ID'] != 'Account ID':
                        row_to_add = (isv_row['Partner'], isv_row['Databricks Salesforce Account Id'])
                        if len(row_to_add) > 0:
                            if not isv_row['Partner'].lower() == 'partner':
                                not_in_sfdc.append(row_to_add)
                except IndexError:
                    if not output_mode.upper() == 'CSV':
                        print ('index error in isv ghosts part 2\nisv:', isv_row, '\nsfdc: ', sfdc_row)
                except KeyError:
                    if not output_mode.upper() == 'CSV':
                        print ('key error in isv ghosts part 2\nisv:', isv_row, '\nsfdc: ', sfdc_row)

                # be kind, rewind SFDC file
                sfdc_file.seek(0)
            # be kind, rewind ISV file
            isv_file.seek(0)

            not_in_sfdc.sort(key=lambda x: x[0])
            for partner, account_id in not_in_sfdc:
                if not output_mode.upper() == 'CSV':
                    print('Not in SFDC: ISV Matrix Account', partner,'with Account ID', account_id)
                else:
                    report_finding('SFDC-less', None, None, partner, account_id, 'Remove from or fix account ID in Matrix')

if __name__ == "__main__":
    """
    SFDC File (source, SFDC export, CSV, details only, UTF-8)
    """
    sfdc = './sfdc.csv'

    """
    ISV Matrix File (source, go/isvmatrix, download as CSV)
    """
    isv_matrix = './matrix.csv'

    # new csv to capture accounts in sfdc that are not in the isv matrix
    new_matrix = 'new_matrix.csv'

    # stash string of expected headers into a string
    isv_expected_headers = 'Tier,Tier Staging Area (WIP for PDM),Partner,Partner Product,Partner Category (Salesforce),Product sub-category,Integration Status,Partner\'s Customer Facing Integration Docs Link,Partner Manager,Partner SA,SaaS,Self-hosted,Cloud Marketplace,On Databricks Partner Connect,Has OSS offering,Has free saas trial,Has on-prem agent,AWS,Azure,GCP,Have Databricks named connector,Delta as source,Delta as target,Library,PAT Tokens,OAuth - Azure AAD,OAuth - AWS,SQL Warehouse,Serverless,Interactive Clusters,Automated Clusters,Delta Live Tables,Support Unity Catalog,Multiple catalog support,Catalog configured at connection in ISV product,Supports Delta Sharing,Execute SQL,Submits Python Jobs,Submits Scala or Java Jobs,REST api,JDBC,Push down DLT,ODBC,Use Databricks Connectors,User Agent string passed,Integration uses a Library,ML flow integration,Strengths,Comments (pricing and misc),Partners documentation link,Automatically create delta tables if the table does not exist,Support external tables,Support partitioning based on certain columns,ISV managed staging location for Ingest,Customer owned staging location for ingest,UC managed personal staging locations for ingest,Support UC external tables,g1,g2,g3,s1,s2,s3,s4,Integrates with mlflow registry,Integrates with mlflow experiments and tracking,Integrates with model serving,Integrates with databricks feature store,Push ML workloads into Databricks,Databricks Salesforce Account Id,Last updated date,Last integration review mm/yyyy,FedRAMP,HIPAA,Built on Databricks'
    # convert string to a list
    isv_expected_headers = isv_expected_headers.split(',')
    # identify false header row & convert string to a list
    isv_false_headers = ',,num_validated_intgrtns,147,,,,,,,Deployment,,,,,,,Clouds Supported for Databricks Integration,,,Databricks Connector,,,,Authentication,,,Databricks features supported,,,,,Unity Catalog,,,,Integration mechanism ,,,,,,,,,,,General,,,Ingest / ETL / Reverse ETL,,,,,,,Governance,,,Security,,,,ML,,,,,ISV Team Metadata,,,(optional) Additional fields,,'
    isv_false_headers = isv_false_headers.split(',')

    if validate_csv_headers(isv_matrix, isv_expected_headers, isv_false_headers):
        # stash string of expected headers into a list
        sfdc_expected_headers = 'Account Name,Partner Manager,ISV Partner Category,Databricks Partner SA,PPA Signed IP Address,New Partner Agreement Signed Date,Created Date,Account ID,ISV Onboarding Status'
        sfdc_expected_headers = sfdc_expected_headers.split(',')
        if validate_csv_headers(sfdc, sfdc_expected_headers, None):
            #output mode can be constrained to 'csv', any other value results in free form text output
            main(isv_expected_headers, 'csv')

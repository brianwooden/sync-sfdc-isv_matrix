import csv


def validate_csv_headers(csv_file, expected_headers):

    headers_match = False

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the first row (headers) from the CSV


        # Check if expected headers match the actual headers
        if headers == expected_headers:
            print('CSV header validation successful for', csv_file, 'Headers match the expected format.')
            headers_match = True
        else:
            print('CSV header validation failed for', csv_file, 'Headers do not match the expected format.')
            print('Expected headers: ', expected_headers)
            print('Actual headers: ', headers)

    return headers_match

def print_section_separator(heading_text):
    num_dashes = len(heading_text)
    print()
    for _ in range(num_dashes):
        print("-", end="")
    print(''.join(['\n', heading_text]))
    for _ in range(num_dashes):
        print("-", end="")
    print()

def main():
    # open SFDC file as "left table", open ISV file as "right table" ~ish
    with open(sfdc) as sfdc_file:
        reader_left = csv.DictReader(sfdc_file, delimiter=',')
        with open(isv_matrix) as isv_file:
            reader_right = csv.DictReader(isv_file, delimiter=',')

            # look at both files and print accounts where ISV has different SA that SFDC
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
                                # sometimes a Timothy is known as Tim, so ignore first name if last name is Sepp
                                try:
                                    if isv_row['Partner SA'].upper().split(' ', 1)[1] == 'SEPP' and sfdc_row['Databricks Partner SA'].upper().split(' ', 1)[1] == 'SEPP':  
                                        pass
                                    else:
                                        print('SFDC Account', sfdc_row['Account Name'], 'has SA', sfdc_row['Databricks Partner SA'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has SA', isv_row['Partner SA'])
                                # whenever we do a split, make sure it isn't a dreaded 7-10 split, as it were (bowling joke! But do make sure we didn't reference an index that didn't exist b/c we're trying to split an unsplittable, as it were
                                except IndexError:
                                        print('SFDC Account', sfdc_row['Account Name'], 'has SA', sfdc_row['Databricks Partner SA'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has SA', isv_row['Partner SA'])

                # rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look at both files and print accounts where ISV has different PDM than SFDC
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
                            print('SFDC Account', sfdc_row['Account Name'], 'has PDM', sfdc_row['Partner Manager'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has PDM', isv_row['Partner Manager'])
                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)


            # look at both files and print accounts where ISV says integration is validated but SFDC says it is in development
            # NB: This takes into account other integration status messages that are beyond validated, such as "Partner Connect Tile Published" etc
            print_section_separator('Integration Status Deltas')        
            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        if isv_row['Integration Status'] == 'Integration Validated' and sfdc_row['ISV Onboarding Status'] == 'Integration in Development':
                            print('SFDC Account', sfdc_row['Account Name'],'has validation status as', sfdc_row['ISV Onboarding Status'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has validation status as', isv_row['Integration Status'])
                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look at both files and print accounts where categories are different
            print_section_separator('Category Deltas')        
            for sfdc_row in reader_left:
                for isv_row in reader_right:
                    if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                        if isv_row['Partner Category (Salesforce)'] != sfdc_row['ISV Partner Category']:
                            # AI/ML show up differently, check for that
                            if isv_row['Partner Category (Salesforce)'] == 'ML/ AI' and not sfdc_row['ISV Partner Category'] == 'Data Science / Machine Learning':
                                print('SFDC Account', sfdc_row['Account Name'],'has partner category as', sfdc_row['ISV Partner Category'], 'whereas go/isvmatrix Account', isv_row['Partner'], 'has partner category as', isv_row['Partner Category (Salesforce)'])
                # be kind, rewind ISV file
                isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look for accounts that exist in SFDC but not ISV Matrix, print those
            print_section_separator('Account Deltas (in SFDC, not in ISV Matrix)')        
            # open new csv for things in sfdc that aren't in matrix, define & write headers
            with open(new_matrix, 'w', newline='\n') as csvfile:
                fieldnames = ['Tier','Partner','Partner Product','Partner Category (Salesforce)','Product sub-category','Integration Status','Partner Manager','Partner SA','SaaS','Self-hosted','Cloud Marketplace','On Databricks Partner Connect','Has OSS offering','Has free saas trial','Has on-prem agent','AWS','Azure','GCP','Have Databricks named connector','Delta as source','Delta as target','Library','SQL Warehouse','Serverless','Interactive Clusters','Automated Clusters','Delta Live Tables','Support Unity Catalog','Multiple catalog support','Catalog configured at connection in ISV product','Leverages UC personal Staging locations','Supports Delta Sharing','Execute SQL','Submits Python Jobs','Submits Scala or Java Jobs','REST api','JDBC','ODBC','Use Databricks Connectors','User Agent string passed','Integration uses a Library','ML flow integration','Strengths','Comments (pricing and misc)','Partners documentation link','Automatically create delta tables if the table does not exist','Support external tables','Support partitioning based on certain columns','ISV managed staging location for Ingest','Customer owned staging location for ingest','UC managed personal staging locations for ingest','Support UC external tables','g1','g2','g3','s1','s2','s3','s4','Integrates with mlflow registry','Integrates with mlflow experiments and tracking','Integrates with model serving','Integrates with databricks feature store','Push ML workloads into Databricks','Databricks Salesforce Account Id','Last updated date','Last integration review mm/yyyy','FedRAMP','HIPPA','Built on Databricks']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for sfdc_row in reader_left:
                    sfdc_in_matrix = False
                    for isv_row in reader_right:
                        if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                            sfdc_in_matrix = True
                    if not sfdc_in_matrix and sfdc_row['Account ID'] != 'Account ID':
                        # fix-up a few things for the ISV Matrix, accounting for known discrepancies between SFDC & go/isvmatrix regarding validation status && partner category
                        if sfdc_row['ISV Onboarding Status'] == 'GTM Collateral Published':
                            print ('Updating SFDC Account', sfdc_row['Account Name'], 'integration status from', sfdc_row['ISV Onboarding Status'], 'to Integration Validated in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Onboarding Status'] = 'Integration Validated'
                        if sfdc_row['ISV Onboarding Status'] == 'Integration Certified':
                            print ('Updating SFDC Account', sfdc_row['Account Name'], 'integration status from', sfdc_row['ISV Onboarding Status'], 'to Integration Validated in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Onboarding Status'] = 'Integration Validated'
                        if sfdc_row['ISV Partner Category'] == 'Data Science / Machine Learning': 
                            print ('Updating SFDC Account', sfdc_row['Account Name'], 'category from', sfdc_row['ISV Partner Category'], 'to ML/ AI in go/isvmatrix update-helper file...')
                            sfdc_row['ISV Partner Category'] = 'ML/ AI'
                        print('Adding SFDC Account', sfdc_row['Account Name'],'with Account ID', sfdc_row['Account ID'], 'to go/isvmatrix update-helper file:', new_matrix)
                        writer.writerow({'Partner': sfdc_row['Account Name'],'Partner Manager': sfdc_row['Partner Manager'],'Partner Category (Salesforce)': sfdc_row['ISV Partner Category'],'Partner SA': sfdc_row['Databricks Partner SA'],'Databricks Salesforce Account Id': sfdc_row['Account ID'],'Integration Status': sfdc_row['ISV Onboarding Status']})
                    # be kind, rewind ISV file
                    isv_file.seek(0)
            # be kind, rewind SFDC file
            sfdc_file.seek(0)

            # look for accounts that exist in ISV Matrix but not SFDC, print those
            not_in_sfdc = []
            print_section_separator('Account Deltas (in ISV Matrix, not in SFDC)')       
            for isv_row in reader_right:
                matrix_in_sfdc = False
                for sfdc_row in reader_left:
                    try:
                        if sfdc_row['Account ID'] == isv_row['Databricks Salesforce Account Id']:
                            matrix_in_sfdc = True
                    except IndexError:
                        print ('index error in isv ghosts part 1\nisv:', isv_row, '\nsfdc: ', sfdc_row)
                    except KeyError:
                        print ('key error in isv ghosts part 1\nisv:', isv_row, '\nsfdc: ', sfdc_row)                   

                try:
                    if not matrix_in_sfdc and sfdc_row['Account ID'] != 'Account ID':
                        row_to_add = (isv_row['Partner'], isv_row['Databricks Salesforce Account Id'])
                        if len(row_to_add) > 0:
                            if not isv_row['Partner'].lower() == 'partner':
                                not_in_sfdc.append(row_to_add)
                except IndexError:
                    print ('index error in isv ghosts part 2\nisv:', isv_row, '\nsfdc: ', sfdc_row)
                except KeyError:
                    print ('key error in isv ghosts part 2\nisv:', isv_row, '\nsfdc: ', sfdc_row)

                # be kind, rewind SFDC file
                sfdc_file.seek(0)
            # be kind, rewind ISV file
            isv_file.seek(0)

            not_in_sfdc.sort(key=lambda x: x[0])
            for partner, account_id in not_in_sfdc:
                print('Not in SFDC: ISV Matrix Account', partner,'with Account ID', account_id)

if __name__ == "__main__": 
    """
    SFDC File (source, SFDC export, details only, UTF-8)
    Expected Headers::
    "Account Name","Partner Manager","ISV Partner Category","Databricks Partner SA","PPA Signed IP Address","New Partner Agreement Signed Date","Created Date","Account ID","ISV Onboarding Status"
    """
    sfdc = './sfdc.csv'

    """
    ISV Matrix File (source, go/isvmatrix, download as CSV)
    Expected Headers::
    Tier,Partner,Partner Product,Partner Category (Salesforce),Product sub-category,Integration Status,Partner Manager,Partner SA,SaaS,Self-hosted,Cloud Marketplace,On Databricks Partner Connect,Has OSS offering,Has free saas trial,Has on-prem agent,AWS,Azure,GCP,Have Databricks named connector,Delta as source,Delta as target,Library,SQL Warehouse,Serverless,Interactive Clusters,Automated Clusters,Delta Live Tables,Support Unity Catalog,Multiple catalog support,Catalog configured at connection in ISV product,Leverages UC personal Staging locations,Supports Delta Sharing,Execute SQL,Submits Python Jobs,Submits Scala or Java Jobs,REST api,JDBC,ODBC,Use Databricks Connectors,User Agent string passed,Integration uses a Library,ML flow integration,Strengths,Comments (pricing and misc),Partners documentation link,Automatically create delta tables if the table does not exist,Support external tables,Support partitioning based on certain columns,ISV managed staging location for Ingest,Customer owned staging location for ingest,UC managed personal staging locations for ingest,Support UC external tables,g1,g2,g3,s1,s2,s3,s4,Integrates with mlflow registry,Integrates with mlflow experiments and tracking,Integrates with model serving,Integrates with databricks feature store,Push ML workloads into Databricks,Databricks Salesforce Account Id,Last updated date,Last integration review mm/yyyy,FedRAMP,HIPPA,Built on Databricks
    """
    isv_matrix = './matrix.csv'

    # new csv to capture accounts in sfdc that are not in the isv matrix
    new_matrix = 'new_matrix.csv'

    with open(isv_matrix, 'r') as f:
        first_line = f.readline()
        if first_line.startswith(',,,,,,,,Deployment') or first_line.startswith(',num_validated_intgrtns'):
            if len(first_line) > 20:
                print('The top of', isv_matrix, 'file starts with\'', first_line[:20], '\'. That is not ideal because that is header line 1 of 2, and we only use the 2nd line for downstream field list. Lopping off the top line and overwriting', isv_matrix, '...')
            else:
                print('The top of', isv_matrix, 'file starts with\'', first_line[:len(first_line)], '\'. That is not ideal because that is header line 1 of 2, and we only use the 2nd line for downstream field list. Lopping off the top line and overwriting', isv_matrix, '...')
                
            with open(isv_matrix, 'r') as fin:
                data = fin.read().splitlines(True)
            with open(isv_matrix, 'w') as fout:
                fout.writelines(data[1:])
        else:
            print('The top of', isv_matrix, 'file looks like it is as expected, moving along ...')

    isv_expected_headers = ['Tier', 'Partner', 'Partner Product', 'Partner Category (Salesforce)', 'Product sub-category', 'Integration Status', 'Partner Manager', 'Partner SA', 'SaaS', 'Self-hosted', 'Cloud Marketplace', 'On Databricks Partner Connect', 'Has OSS offering', 'Has free saas trial', 'Has on-prem agent', 'AWS', 'Azure', 'GCP', 'Have Databricks named connector', 'Delta as source', 'Delta as target', 'Library', 'SQL Warehouse', 'Serverless', 'Interactive Clusters', 'Automated Clusters', 'Delta Live Tables', 'Support Unity Catalog', 'Multiple catalog support', 'Catalog configured at connection in ISV product', 'Leverages UC personal Staging locations', 'Supports Delta Sharing', 'Execute SQL', 'Submits Python Jobs', 'Submits Scala or Java Jobs', 'REST api', 'JDBC', 'ODBC', 'Use Databricks Connectors', 'User Agent string passed', 'Integration uses a Library', 'ML flow integration', 'Strengths', 'Comments (pricing and misc)', 'Partners documentation link', 'Automatically create delta tables if the table does not exist', 'Support external tables', 'Support partitioning based on certain columns', 'ISV managed staging location for Ingest', 'Customer owned staging location for ingest', 'UC managed personal staging locations for ingest', 'Support UC external tables', 'g1', 'g2', 'g3', 's1', 's2', 's3', 's4', 'Integrates with mlflow registry', 'Integrates with mlflow experiments and tracking', 'Integrates with model serving', 'Integrates with databricks feature store', 'Push ML workloads into Databricks', 'Databricks Salesforce Account Id', 'Last updated date', 'Last integration review mm/yyyy', 'FedRAMP', 'HIPPA', 'Built on Databricks']
    if validate_csv_headers(isv_matrix, isv_expected_headers):
        sfdc_expected_headers = ['Account Name', 'Partner Manager', 'ISV Partner Category', 'Databricks Partner SA', 'PPA Signed IP Address', 'New Partner Agreement Signed Date', 'Created Date', 'Account ID', 'ISV Onboarding Status']
        if validate_csv_headers(sfdc, sfdc_expected_headers):
            main()

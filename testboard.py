import re
# 103.247.22.229:234
# yayan
# Yayan@12345
# String input
text = "System Description: C320 Version V2.1.0 Software, Copyright (c) by ZTE Corporation Compiled"

# Regex pattern to match "C320" and "V2.1.0"
pattern = r"System Description:\s(\w+)\sVersion\s([\w.]+)\s"

# Search for the pattern in the text
match = re.search(pattern, text)

# Extract the groups if a match is found
if match:
    c320 = match.group(1)
    version = match.group(2)
    print(f"Version: {c320}, Software: {version}")
else:
    print("No match found")


data = """Rack Shelf Slot CfgType RealType Port  HardVer SoftVer         Status
-------------------------------------------------------------------------------
1    1     1    GTGH    GTGHK    16    V1.0.0  V2.1.0          INSERVICE
1    1     2    GTGO             8                             OFFLINE
1    1     3    SMXA             3                             OFFLINE
1    1     4    SMXA    SMXA     3     V1.0.0  V2.1.0          INSERVICE"""

# Split the data into lines
lines = data.strip().split("\n")

# Extract headers
headers = lines[0].split()

# Initialize an empty list to store the parsed data
parsed_data = []

# Iterate over the lines, starting from the third line (actual data)
for line in lines[2:]:
    # Split each line into fields based on whitespace
    fields = line.split()

    # Create a dictionary for each row
    row = {}

    # Handle the specific structure of this data
    row['Rack'] = fields[0]
    row['Shelf'] = fields[1]
    row['Slot'] = fields[2]
    row['CfgType'] = fields[3]
    row['RealType'] = fields[4] if len(fields) > 4 else ""
    row['Port'] = fields[5] if len(fields) > 5 else ""
    row['HardVer'] = fields[6] if len(fields) > 6 else ""
    row['SoftVer'] = fields[7] if len(fields) > 7 else ""
    row['Status'] = fields[8] if len(fields) > 8 else ""

    # Append the row to the parsed_data list
    parsed_data.append(row)

# Output the parsed data
print(parsed_data)



#show card-temperature
#show processor
#show card slotno 4
#reset-card slotno 4 (reboot card masih di cari lagi)
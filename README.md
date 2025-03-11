# EDI Generator

This project is a simple Electronic Data Interchange (EDI) message generator for healthcare billing. It generates paired 837 (claim) and 835 (payment) messages based on randomized inputs. The generated files are stored in a designated output folder and can be used for testing or educational purposes. 

- Here are links to the official 835/837 formats with descriptions of each field for better understanding:     
  - 835 - https://datainsight.health/edi/payments/comprehensive/
  - 837 - https://datainsight.health/edi/claims/comprehensive/

## Overview

### How It Works

- **Name Loading:**  
  The script reads lists of male, female, and surname names from text files (located in `../names-surnames-list/`) to randomly generate patient names.

- **Random Data Generation:**  
  It selects random insurance information, provider details, service dates, claim amounts, and payment amounts using helper functions.  
  - Insurance and provider data are pulled from dictionaries defined in `constants.py`.  
  - Dates, times, and claim numbers are generated randomly to simulate realistic data.

- **EDI Message Creation:**  
  Two main types of EDI messages are created:
  - **837 Message:** Contains the claim details including patient and provider information.
  - **835 Message:** Contains payment information along with service line details and adjustments.
  
  The generation functions build segments according to a simplified structure of the 837/835 standards. The segments include ISA, GS, ST, and additional segments specific to claim and payment information.

- **Output:**  
  Change the NUM_MESSAGES variable to output the desired amount of 835/837 files. Generated EDI files are saved in the output directory (`../edi_messages`). The script creates this directory if it does not already exist. 

### Main Files

- **edi_generator.py:**  
  The primary script that contains all the logic to generate the 837 and 835 messages. It:
  - Loads names from external text files.
  - Generates random data for claims and payments.
  - Writes the generated EDI messages into separate files in the output directory.

- **constants.py:**  
  Contains dictionaries with pre-defined data:
  - **Insurance Payers:** Expanded details for various insurance companies.
  - **Provider NPIs:** Details of healthcare providers including their NPIs and addresses.
  - **Adjustment Codes:** A list of adjustment groups and their respective reason codes used in EDI adjustments.

## How to Run the Project

### Prerequisites

- **Python:**  
  Ensure that Python (version 3.x) is installed on your computer.
- **Text Files:**  
  Make sure the following files (or similar ones) exist in the expected directories:
  - `../names-surnames-list/male-names-list.txt`
  - `../names-surnames-list/female-names-list.txt`
  - `../names-surnames-list/surnames-list.txt`
  
  These files are used to generate random patient names.

- **edi_messages**
  The edi_messages directory is there for display. Delete this directory before running your code.

### Running the Script

1. **Clone or Download the Project:**  
   Ensure all project files (`edi_generator.py`, `constants.py`, and the required name lists) are in the correct directory structure.

2. **Open a Terminal/Command Prompt:**  
   Navigate to the directory where `edi_generator.py` is located.

3. **Run the Script:**  
   Execute the following command:
   ```bash
   python edi_generator.py

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

- **edi_messages:**  
  The edi_messages directory is included in the repository for display purposes. Delete this directory before running your code.

## Running the Script

This guide explains how to clone or download the EDI Generator project for users of all experience levels.

### For Beginners: Downloading the Project Without Git

If you’re not familiar with Git or prefer not to use it, follow these steps:

1. **Locate the Repository:**
   - Open your web browser and navigate to the project's GitHub page (or the hosting site where the repository is available).

2. **Download as a ZIP:**
   - Look for a button or link labeled “Code” or “Download.”
   - Click on **Download ZIP**. This will download the entire project as a compressed ZIP file.

3. **Extract the Files:**
   - Once downloaded, locate the ZIP file on your computer.
   - Right-click the file and select “Extract All…” (Windows) or use your preferred extraction tool (macOS/Linux).
   - Ensure that the extracted directory retains the correct structure:
     - The main folder should contain `edi_generator.py`, `constants.py`, and a folder (e.g., `names-surnames-list`) with the required text files.

### For Intermediate to Advanced Users: Using Git to Clone the Repository

If you have Git installed, cloning the repository is quick and allows you to easily update your local copy with future changes:

1. **Verify Git Installation:**
   - Open your terminal (Command Prompt, PowerShell, or any shell on Linux/macOS).
   - Run the command:
     ```bash
     git --version
     ```
   - If Git is installed, you should see the version number. If not, download and install Git from [git-scm.com](https://git-scm.com/).

2. **Clone the Repository:**
   - Navigate to the directory where you want to store the project. For example:
     ```bash
     cd ~/projects
     ```
   - Use the `git clone` command along with the repository URL. For example:
     ```bash
     git clone https://github.com/yourusername/edi-generator.git
     ```
   - This command creates a folder named `edi-generator` (or the repository name) containing all project files.

3. **Verify the Directory Structure:**
   - After cloning, change to the project directory:
     ```bash
     cd edi-generator
     ```
   - Ensure that files like `edi_generator.py` and `constants.py` are in the root directory, and that the `names-surnames-list` folder is present with the necessary text files.

### Run the code

Regardless of the cloning method, make sure to:

- **Check the File Structure:**  
  Verify that the expected directories (like `../names-surnames-list` for name files) and output folders (`../edi_messages`) are correctly positioned relative to the main script.  
  > If the output directory exists from a previous run, consider deleting it before running the script to avoid conflicts.

- **Read the Documentation:**  
  Review any README or documentation files included in the repository to understand dependencies, configuration options, or additional setup steps.

- **Run the Project:**  
  Open a terminal in the project directory and execute:
  ```bash
  python edi_generator.py

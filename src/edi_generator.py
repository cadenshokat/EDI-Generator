import random
import os
from datetime import datetime, timedelta
from constants import *


NUM_MESSAGES = 3  # Number of 837/835 pairs to generate

OUTPUT_DIR = "../edi_messages"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_names(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

male_first_names = load_names("../names-surnames-list/male-names-list.txt")
female_first_names = load_names('../names-surnames-list/female-names-list.txt')
last_names = load_names('../names-surnames-list/surnames-list.txt')

def patient_name_random():
    gender = random.choice(['M', 'F'])
    last_name = random.choice(last_names)
    if gender == 'M':
        first_name = random.choice(male_first_names)
    else:
        first_name = random.choice(female_first_names)

    return f"{first_name} {last_name}"


# ---------------------------------------------
# Helper Functions
# ---------------------------------------------
def get_random_insurance():
    ins = []
    insurance = random.choice(list(insurance_payers_expanded.keys()))
    ins.append({
        "name": insurance,
        "ID": insurance_payers_expanded[insurance].get("insurance_id"),
        "streetAddress": insurance_payers_expanded[insurance]["street_address"],
        "cityStZip": insurance_payers_expanded[insurance]["city_st_zip"],
    })

    return ins

def get_random_provider():
    prov = []
    provider = random.choice(list(provider_npis))
    prov.append({
        "name": provider,
        "npi": provider_npis[provider]["npi"],
        "streetAddress": provider_npis[provider]["streetAddress"],
        "cityStZip": provider_npis[provider]["cityStZip"],
    })

    return prov



def random_date(start_year=2022, end_year=2023):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_day = random.randrange(delta.days)
    date = start + timedelta(days=random_day)
    return date.strftime("%Y%m%d"), date


def random_time():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}{minute:02d}"


def generate_claim_number():
    return f"CLM{random.randint(10000, 99999)}"


def count_transaction_segments(segments):
    """Count segments from ST to SE (inclusive)."""
    return len(segments[2:-2])


def generate_ISA_GS(function_id, transaction_date, transaction_time, trans_id="000000002"):
    """Build ISA and GS segments."""
    isa_date = datetime.strptime(transaction_date, "%Y%m%d").strftime("%y%m%d")
    isa = (f"ISA*00*          *00*          *ZZ*SUBMITTER      *ZZ*RECEIVER       *"
           f"{isa_date}*{transaction_time}*^*00501*{trans_id}*0*T*:~")
    gs = f"GS*{function_id}*SUBMITTER*RECEIVER*{transaction_date}*{transaction_time}*1*X*005010X221A1~"
    return isa, gs, trans_id


# ---------------------------------------------
# (Optional) 837 Generator for completeness
# ---------------------------------------------
def generate_837(claim_number, patient, provider, service_date, service_dt_obj, claim_amount):
    trans_time = random_time()
    isa, gs, trans_id = generate_ISA_GS("HC", service_date, trans_time, "000000001")
    bht = f"BHT*0019*00*{claim_number[-4:]}*{service_date}*{trans_time}*CH~"

    segments = [
        isa,
        gs,
        "ST*837*0001~",
        bht,
        "NM1*41*2*ABC BILLING SERVICE*****46*123456789~",
        "NM1*40*2*XYZ INSURANCE*****46*987654321~",
        f"NM1*85*2*{provider[0].get("name")}*****XX*{provider[0].get("npi")}~",
        f"NM1*IL*1*{patient.split()[1]}*{patient.split()[0]}****MI*1234567~",
        f"CLM*{claim_number}*{claim_amount:.2f}***11:B:1*Y*A*Y*Y~",
        f"REF*F8*{random.randint(100000, 999999)}~",
        f"DTP*472*D8*{service_date}~",
        "HI*ABK:I10~",
        "LX*1~",
        f"SV1*HC:99213*{claim_amount:.2f}*UN*1***1~"
    ]
    segment_count = count_transaction_segments(segments)
    se = f"SE*{segment_count}*0001~"
    ge = "GE*1*1~"
    iea = f"IEA*1*{trans_id}~"
    segments.extend([se, ge, iea])
    return "\n".join(segments)


# ---------------------------------------------
# Service Line Logic (Loop 2110)
# ---------------------------------------------

def distribute_payment_across_lines(total_payment, num_lines):
    """
    Randomly split total_payment across num_lines so that
    sum(line_payments) == total_payment.
    """
    if num_lines == 1:
        return [total_payment]

    random_values = [random.random() for _ in range(num_lines)]
    s = sum(random_values)
    line_payments = [(val / s) * total_payment for val in random_values]

    # Round to cents, then adjust for rounding differences
    rounded = [round(lp, 2) for lp in line_payments]
    diff = round(total_payment - sum(rounded), 2)
    rounded[0] = round(rounded[0] + diff, 2)
    return rounded


def generate_line_adjustments():
    """
    Creates 0–4 random adjustments for a single service line,
    grouped by group code (CO, PR, OA, etc.).
    Returns a list of CAS segments (one per group code).
    """
    num_adjustments = random.randint(0, 4)
    if num_adjustments == 0:
        return []

    # Group adjustments by group code
    grouped_adjustments = {}
    for _ in range(num_adjustments):
        group_choice = random.choice(ADJUSTMENT_CODES)
        group_code = group_choice["group"]
        reason_choice = random.choice(group_choice["reason_codes"])
        reason_code = reason_choice["code"]
        adj_amount = round(random.uniform(1.0, 50.0), 2)

        grouped_adjustments.setdefault(group_code, []).append((reason_code, adj_amount))

    # Build CAS segments (one per group code)
    cas_segments = []
    for group_code, reason_pairs in grouped_adjustments.items():
        parts = ["CAS", group_code]
        for (rc, amt) in reason_pairs:
            parts.append(rc)
            parts.append(f"{amt:.2f}")
        cas_segments.append("*".join(parts) + "~")

    return cas_segments


def generate_service_lines_835(service_date, total_payment):
    """
    Creates 1-4 service lines (Loop 2110).
    Each line has SVC, DTM, 0–4 CAS adjustments (grouped),
    and some example REF, AMT, QTY segments.
    """
    num_lines = random.randint(1, 4)
    line_payments = distribute_payment_across_lines(total_payment, num_lines)

    segments = []
    for idx in range(num_lines):
        line_charge = round(line_payments[idx] * random.uniform(1.0, 1.5), 2)
        line_paid = line_payments[idx]
        procedure_code = random.choice(["99213", "D0120", "D0220", "D1110"])

        # SVC: Service Payment Information
        # SVC01: e.g. HC:99213
        # SVC02: line item charge
        # SVC03: line item provider payment
        svc = (f"SVC*HC:{procedure_code}*{line_charge:.2f}*"
               f"{line_paid:.2f}**1~")  # simplified
        segments.append(svc)

        # DTM: Service Date
        segments.append(f"DTM*472*{service_date}~")

        # CAS (line-level) with grouping
        line_cas_segments = generate_line_adjustments()
        segments.extend(line_cas_segments)

        # Example REF, AMT, QTY
        segments.append(f"REF*6R*LineRef{idx + 1}~")
        # Suppose allowed amount is line_paid for demonstration
        segments.append(f"AMT*B6*{line_paid:.2f}~")
        segments.append(f"QTY*QA*1~")

    return segments


# ---------------------------------------------
# Main 835 Generator (Including Service Lines)
# ---------------------------------------------
def generate_835(claim_number, claim_amount, service_date, service_dt_obj, payment_amount, provider, insurance):
    """
    Generates an 835 with:
      - Claim Payment Info (CLP)
      - 0-4 grouped adjustments at the claim level
      - 1-4 service lines in Loop 2110 with SVC, DTM, CAS, etc.
        (each line can have 0-4 random adjustments grouped by group code)
    """
    payment_dt_obj = service_dt_obj + timedelta(days=random.randint(10, 30))
    payment_date = payment_dt_obj.strftime("%Y%m%d")
    trans_time = random_time()

    ins_citystzip = insurance[0].get("cityStZip")  # e.g., "Chicago, IL 60602"
    city, state_zip = [part.strip() for part in ins_citystzip.split(',', 1)]
    state, zip_code = state_zip.split()

    prov_citystzip = provider[0].get("cityStZip")  # e.g., "Chicago, IL 60602"
    p_city, p_state_zip = [part.strip() for part in prov_citystzip.split(',', 1)]
    p_state, p_zip_code = p_state_zip.split()

    # ISA/GS
    isa, gs, trans_id = generate_ISA_GS("HP", payment_date, trans_time)

    st = "ST*835*0001~"
    bpr = f"BPR*I*{payment_amount:.2f}*C*CHK*NON************{payment_date}~"
    trn = f"TRN*1*{random.randint(100000, 999999)}*{insurance[0].get("ID")}~"
    dtm = f"DTM*405*{payment_date}~"


    # Payer loops
    n1_payer = f"N1*PR*{insurance[0].get("name")}~"
    n3_payer = f"N3*{insurance[0].get("streetAddress")}~"
    n4_payer = f"N4*{city}*{state}*{zip_code}~"
    payer_ref1 = "REF*2U*0101~"
    payer_ref2 = "REF*HI*0202~"

    # Payee loops
    n1_payee = f"N1*PE*{provider[0].get("name")} LLC~"
    n3_payee = f"N3*{insurance[0].get("streetAddress")}~"
    n4_payee = f"N4*{p_city}*{p_state}*{p_zip_code}~"
    payee_ref = "REF*PQ*0505~"

    # CLP: claim-level payment info
    clp = f"CLP*{claim_number}*1*{claim_amount:.2f}*{payment_amount:.2f}*0*MC*1234567890*12*1~"

    # -- Claim-level adjustments (CAS) grouped by group code --
    num_adjustments = random.randint(0, 4)
    grouped_adjustments = {}
    for _ in range(num_adjustments):
        group_choice = random.choice(ADJUSTMENT_CODES)
        group_code = group_choice["group"]
        reason_choice = random.choice(group_choice["reason_codes"])
        reason_code = reason_choice["code"]
        adj_amount = round(random.uniform(5.0, 300.0), 2)
        grouped_adjustments.setdefault(group_code, []).append((reason_code, adj_amount))

    cas_segments = []
    for group_code, reason_pairs in grouped_adjustments.items():
        parts = ["CAS", group_code]
        for (rc, amt) in reason_pairs:
            parts.append(rc)
            parts.append(f"{amt:.2f}")
        cas_segments.append("*".join(parts) + "~")

    total_adjustment = sum(amt for rp in grouped_adjustments.values() for (_, amt) in rp)

    # NM1*PE: payee entity
    nm1_payee_entity = f"NM1*PE*2*{provider[0].get("name")}*****XX*{provider[0].get("npi")}~"

    # PLB
    plb_ref = random.randint(100000, 999999)
    plb = f"PLB*{provider[0].get("npi")}*{payment_date}*{plb_ref}*{total_adjustment:.2f}~"

    # ---------------------------------------------
    # Build 835 segments
    # ---------------------------------------------
    segments = [
                   isa,
                   gs,
                   st,
                   bpr,
                   trn,
                   dtm,

                   # Payer
                   n1_payer,
                   n3_payer,
                   n4_payer,
                   payer_ref1,
                   payer_ref2,

                   # Payee
                   n1_payee,
                   n3_payee,
                   n4_payee,
                   payee_ref,

                   # Claim Info
                   clp
               ] + cas_segments  # Insert claim-level CAS (if any)

    # ---------------------------------------------
    # Service Lines (Loop 2110) with line-level CAS
    # ---------------------------------------------
    service_line_segments = generate_service_lines_835(service_date, payment_amount)
    segments.extend(service_line_segments)

    # Wrap up
    segments.extend([
        nm1_payee_entity,
        plb
    ])

    segment_count = count_transaction_segments(segments)
    se = f"SE*{segment_count}*0001~"
    ge = "GE*1*1~"
    iea = f"IEA*1*{trans_id}~"
    segments.extend([se, ge, iea])

    return "\n".join(segments)


# ---------------------------------------------
# Main Script: Generate 837 & 835
# ---------------------------------------------
def main():
    for i in range(NUM_MESSAGES):
        claim_number = generate_claim_number()
        patient = patient_name_random()
        provider = get_random_provider()
        insurance = get_random_insurance()
        service_date, service_dt_obj = random_date(2022, 2023)
        claim_amount = round(random.uniform(100.00, 1000.00), 2)

        # Generate 837
        message_837 = generate_837(claim_number, patient, provider, service_date, service_dt_obj, claim_amount)
        with open(f"{OUTPUT_DIR}/837_{i}.edi", "w") as f:
            f.write(message_837)

        # Payment is typically <= claim_amount
        payment_amount = round(random.uniform(0.5, 1.0) * claim_amount, 2)

        # Generate 835 (now includes service lines with line-level CAS)
        message_835 = generate_835(claim_number, claim_amount, service_date, service_dt_obj, payment_amount, provider, insurance)
        with open(f"{OUTPUT_DIR}/835_{i}.edi", "w") as f:
            f.write(message_835)

    print(f"Generated {NUM_MESSAGES} pairs of 837 & 835 EDI files in '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()

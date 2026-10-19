BLOOD_GROUPS = ("O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+")
DONOR_TO_RECIPIENT = {
    "O-": set(BLOOD_GROUPS), "O+": {"O+", "A+", "B+", "AB+"},
    "A-": {"A-", "A+", "AB-", "AB+"}, "A+": {"A+", "AB+"},
    "B-": {"B-", "B+", "AB-", "AB+"}, "B+": {"B+", "AB+"},
    "AB-": {"AB-", "AB+"}, "AB+": {"AB+"},
}
def is_compatible(donor_group: str, recipient_group: str) -> bool:
    return recipient_group in DONOR_TO_RECIPIENT.get(donor_group, set())

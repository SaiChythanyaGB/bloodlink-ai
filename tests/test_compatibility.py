import pytest
from app.algorithms.compatibility import BLOOD_GROUPS,is_compatible
EXPECTED={'O-':set(BLOOD_GROUPS),'O+':{'O+','A+','B+','AB+'},'A-':{'A-','A+','AB-','AB+'},'A+':{'A+','AB+'},'B-':{'B-','B+','AB-','AB+'},'B+':{'B+','AB+'},'AB-':{'AB-','AB+'},'AB+':{'AB+'}}
@pytest.mark.parametrize('donor',BLOOD_GROUPS)
def test_all_group_pairs(donor):
    for recipient in BLOOD_GROUPS:assert is_compatible(donor,recipient)==(recipient in EXPECTED[donor])
def test_invalid_groups_fail_closed():assert not is_compatible('x','A+') and not is_compatible('O-','x')

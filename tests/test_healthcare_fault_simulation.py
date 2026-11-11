from safeagent.healthcare.fault_simulation import (
    simulate_lost_acknowledgment,
)
from safeagent.healthcare.fault_simulation import (
    simulate_idempotent_lost_acknowledgment,
)

from safeagent.healthcare.fault_simulation import (
    simulate_safeagent_lost_acknowledgment,
)

from safeagent.healthcare.fault_simulation import (
    simulate_safeagent_verification_outage,
)

from safeagent.healthcare.fault_simulation import (
    simulate_safeagent_confirmed_non_execution,
)


def test_naive_retry_creates_duplicate_prior_auth():

    result = simulate_lost_acknowledgment()

    assert result["total_authorizations"] == 2
    assert result["retries"] == 1
    assert result["duplicate_submissions"] == 1



def test_naive_vs_idempotent_recovery():

    naive = simulate_lost_acknowledgment()
    idempotent = simulate_idempotent_lost_acknowledgment()

    assert naive["total_authorizations"] == 2
    assert naive["duplicate_submissions"] == 1

    assert idempotent["total_authorizations"] == 1
    assert idempotent["duplicate_submissions"] == 0

    # Both approaches attempted one recovery retry.
    assert naive["retries"] == 1
    assert idempotent["retries"] == 1






def test_safeagent_verifies_before_retry():

    result = simulate_safeagent_lost_acknowledgment()

    assert result["total_authorizations"] == 1
    assert result["retries"] == 0
    assert result["duplicate_submissions"] == 0

    assert result["verification_status"] == "SUCCESS"
    assert result["recovery_decision"] == "STOP"



    


def test_safeagent_verification_outage():

    result = simulate_safeagent_verification_outage()

    assert result["total_authorizations"] == 1
    assert result["retries"] == 0
    assert result["duplicate_submissions"] == 0

    assert result["verification_status"] == "UNKNOWN"
    assert result["recovery_decision"] == "ESCALATE"




def test_safeagent_retries_confirmed_non_execution():

    result = simulate_safeagent_confirmed_non_execution()

    assert result["verification_status"] == "NOT_EXECUTED"
    assert result["recovery_decision"] == "RETRY"

    assert result["retries"] == 1
    assert result["total_authorizations"] == 1
    assert result["duplicate_submissions"] == 0
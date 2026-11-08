from safeagent.recovery.verification import (
    VerificationRecoveryController,
    VerificationStatus,
)


def run_scenario(name, verification_status):
    controller = VerificationRecoveryController()

    result = controller.decide(
        verify=lambda: verification_status
    )

    print(f"\nScenario: {name}")
    print(f"Verification: {result.verification_status.value}")
    print(f"Decision: {result.decision.value}")
    print(f"Reason: {result.reason}")


if __name__ == "__main__":

    run_scenario(
        "Operation already completed",
        VerificationStatus.SUCCESS,
    )

    run_scenario(
        "Operation definitely not executed",
        VerificationStatus.NOT_EXECUTED,
    )

    run_scenario(
        "Operation outcome unknown",
        VerificationStatus.UNKNOWN,
    )
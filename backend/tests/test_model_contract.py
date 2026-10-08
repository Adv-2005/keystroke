from keystroke.models.base import TypingVerificationModel


def test_model_contract_covers_the_shared_lifecycle() -> None:
    assert TypingVerificationModel.__abstractmethods__ == {
        "fit_background",
        "enroll",
        "score",
        "save",
        "load",
    }

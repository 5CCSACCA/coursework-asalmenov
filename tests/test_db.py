from services.yolo.db import init_db, log_prediction, list_predictions

def test_init_db_and_log_prediction_and_list_predictions():
    init_db()

    log_prediction(
        filename="test_image.jpg",
        label="apple",
        confidence=0.99,
    )

    preds = list_predictions(limit=10)
    assert isinstance(preds, list)
    assert len(preds) >= 1

    first = preds[0]
    assert "filename" in first
    assert "label" in first
    assert "confidence" in first
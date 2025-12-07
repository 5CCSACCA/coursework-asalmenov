from services.yolo import storage

def test_save_output_returns_none_when_firebase_not_initialised():
    storage._db = None  # force uninitialised
    doc_id = storage.save_output({"label": "apple"})
    assert doc_id is None

def test_list_outputs_returns_empty_when_firebase_not_initialised():
    storage._db = None
    docs = storage.list_outputs(limit=10)
    assert isinstance(docs, list)
    assert docs == []

def test_update_output_is_noop_when_firebase_not_initialised():
    storage._db = None
    storage.update_output("some-id", {"label": "changed"})


def test_delete_output_is_noop_when_firebase_not_initialised():
    storage._db = None
    storage.delete_output("some-id")
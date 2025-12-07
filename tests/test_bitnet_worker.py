from services.bitnet.worker import fake_bitnet_postprocess

def test_fake_bitnet_postprocess_no_detections():
    msg = {"detections": []}
    out = fake_bitnet_postprocess(msg)
    assert out["recipe_title"] == "No recipe available"
    assert out["ingredients"] == []
    assert "No food items were detected" in out["steps"][0]

def test_fake_bitnet_postprocess_with_detections():
    msg = {
        "detections": [
            {"label": "apple"},
            {"label": "banana"},
            {"label": "apple"},
        ]
    }
    out = fake_bitnet_postprocess(msg)

    assert "recipe_title" in out
    assert "Quick Apple Dish" in out["recipe_title"]
    assert "apple (as the main ingredient)" in out["ingredients"][0]
    assert "banana" in " ".join(out["ingredients"])
    assert "steps" in out
    assert len(out["steps"]) >= 3
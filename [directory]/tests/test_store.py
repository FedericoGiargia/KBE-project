from ui.store import STORE, DEFAULT_POPULATION_SIZE, DEFAULT_STEP

def test_model_creation():
    STORE.create_models()
    assert len(STORE.models) == DEFAULT_POPULATION_SIZE

def test_store_reset():
    STORE.reset()
    assert STORE.step == DEFAULT_STEP
    assert STORE.selected is None
    assert STORE.final_design is None
    assert len(STORE.models) == 0
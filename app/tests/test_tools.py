@pytest.mark.unit
def test_save_patient_profile_accepts_arbitrary_field(fake_store):
    result = save_patient_profile.invoke({
        "patient_id": "p1", "field": "occupation", "value": "Software Engineer",
        "source_message": "I work as a software engineer",
    })
    assert "occupation = Software Engineer" in result
    saved = fake_store.get(("patient_profile", "p1"), "occupation")
    assert saved.value["value"] == "Software Engineer"


@pytest.mark.unit
def test_save_patient_profile_normalizes_key_but_keeps_label(fake_store):
    save_patient_profile.invoke({
        "patient_id": "p1", "field": "Emergency Contact", "value": "Ali (brother)",
        "source_message": "my emergency contact is my brother Ali",
    })
    saved = fake_store.get(("patient_profile", "p1"), "emergency_contact")
    assert saved.value["label"] == "Emergency Contact"
    assert saved.value["value"] == "Ali (brother)"


@pytest.mark.unit
def test_fetch_patient_profile_returns_all_saved_fields(fake_store):
    fake_store.put(("patient_profile", "p1"), "name", {"value": "Ayan"})
    fake_store.put(("patient_profile", "p1"), "occupation", {"value": "Engineer"})
    fake_store.put(("patient_profile", "p1"), "city", {"value": "Lahore"})
    result = fetch_patient_profile.invoke({"patient_id": "p1"})
    assert "name: Ayan" in result
    assert "occupation: Engineer" in result
    assert "city: Lahore" in result


@pytest.mark.unit
def test_save_patient_profile_rejects_empty_value(fake_store):
    result = save_patient_profile.invoke({
        "patient_id": "p1", "field": "name", "value": "  ",
        "source_message": "x",
    })
    assert "required" in result.lower()
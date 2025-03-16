import pytest
from translator_api import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.mark.parametrize("word,source_lang,target_lang,expected_translation", [
    ("pineapple", "en", "ru", "ананас"),
    ("урод", "ru", "en", "freak"),
    ("аҡса юҡ", "ba", "ja", "お金はありません"),
])
def test_translate_success(client, word, source_lang, target_lang, expected_translation):
    response = client.get(f'/translate?word={word}&source_lang={source_lang}&target_lang={target_lang}')
    assert response.status_code == 200
    data = response.get_json()
    assert data["word"] == word
    assert data["translation"].lower() == expected_translation.lower()

def test_translate_no_word_provided(client):
    response = client.get('/translate')
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "No word provided"

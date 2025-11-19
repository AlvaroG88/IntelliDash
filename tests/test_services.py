
import pytest
import requests
from services import forex, news, weather, wiki

@pytest.fixture
def mock_get_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": "some data"}
    return mocker.patch("requests.get", return_value=mock_response)

@pytest.fixture
def mock_get_fail(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    return mocker.patch("requests.get", return_value=mock_response)

@pytest.fixture
def mock_get_exception(mocker):
    return mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Test timeout"))

def test_forex_convert_currency_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "rates": {"USD": 1.1},
        "base": "EUR",
        "date": "2025-01-01"
    }
    mocker.patch("requests.get", return_value=mock_response)

    result = forex.convert_currency(100, "EUR", "USD")
    assert result["success"] is True
    assert result["result"] == pytest.approx(110.0)

def test_forex_convert_currency_fail(mock_get_fail):
    result = forex.convert_currency(100, "EUR", "USD")
    assert result["success"] is False
    assert "error" in result

def test_news_search_hn_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hits": [{"title": "Test News"}]}
    mocker.patch("requests.get", return_value=mock_response)

    result = news.search_hn("test")
    assert len(result) == 1
    assert result[0]["title"] == "Test News"

def test_news_search_hn_fail(mock_get_fail):
    result = news.search_hn("test")
    assert result == []

def test_weather_geocode_city_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": [{"name": "Chicago"}]}
    mocker.patch("requests.get", return_value=mock_response)

    result = weather.geocode_city("Chicago")
    assert result is not None
    assert result["name"] == "Chicago"

def test_weather_geocode_city_fail(mock_get_fail):
    result = weather.geocode_city("Chicago")
    assert result is None

def test_weather_get_weather_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"current_weather": {"temperature": 10}}
    mocker.patch("requests.get", return_value=mock_response)

    result = weather.get_weather(41.8, -87.6)
    assert result is not None
    assert result["current_weather"]["temperature"] == 10

def test_weather_get_weather_fail(mock_get_fail):
    result = weather.get_weather(41.8, -87.6)
    assert result is None

def test_wiki_search_pages_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"pages": [{"title": "Python (programming language)"}]}
    mocker.patch("requests.get", return_value=mock_response)

    result = wiki.search_pages("Python")
    assert len(result) == 1
    assert result[0]["title"] == "Python (programming language)"

def test_wiki_search_pages_fail(mock_get_fail):
    result = wiki.search_pages("Python")
    assert result == []

def test_wiki_get_summary_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"extract": "A high-level programming language."}
    mocker.patch("requests.get", return_value=mock_response)

    result = wiki.get_summary("Python (programming language)")
    assert result is not None
    assert "high-level" in result["extract"]

def test_wiki_get_summary_fail(mock_get_fail):
    result = wiki.get_summary("Python (programming language)")
    assert result is None

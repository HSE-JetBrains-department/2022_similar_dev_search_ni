from collections import Counter

import pytest

from repo_processing.stargazers.github_api import process_stargazers

result_counter = Counter({"vk-education/android-samples": 8,
                          "pichenettes/eurorack": 1,
                          "sirius-ai/MobileFaceNet_TF": 1,
                          "Whiletruedoend/Vk-to-telegram-transfer-bot": 1,
                          "Nate711/StanfordDoggoProject": 1,
                          "limitedeternity/foxford_courses": 1,
                          "ossu/computer-science": 1,
                          "codecrafters-io/build-your-own-x": 1,
                          "cookiecutter-flask/cookiecutter-flask": 1,
                          "danlkv/tgflow": 1,
                          "Widdershin/flask-desktop": 1,
                          "c0defather/Khameleon": 1,
                          "velmurugan-murugesan/Android-Example": 1,
                          "evvvsss/fractol": 1,
                          "LonamiWebs/Telethon": 1,
                          "vk-education/VoluptuousWaffles": 1,
                          "hukenovs/dsp-theory": 1,
                          "flipperdevices/Flipper-Android-App": 1,
                          "ayles/heart": 1,
                          "raspberrypi/linux": 1,
                          "valiotti/leftjoin": 1,
                          "IntelRealSense/librealsense": 1,
                          "leralerale/CourseProject_2nd_Year": 1,
                          "nosequeldeebee/blockchain-tutorial": 1,
                          "avelino/awesome-go": 1,
                          "rust-unofficial/awesome-rust": 1,
                          "Checkmarx/kics": 1,
                          "corona10/goimagehash": 1,
                          "teh-cmc/go-internals": 1,
                          "matter-labs/awesome-zero-knowledge-proofs": 1,
                          "ADKosm/lsml-2022-public": 1,
                          "loomnetwork/cryptozombies-lesson-code": 1,
                          "Apress/practical-tla-plus": 1,
                          "lucas-clemente/quic-go": 1,
                          "mailcourses/python_backend_autumn_2021": 1,
                          "tarantool/sysprog": 1,
                          "golang/go": 1,
                          "hse-system-design-2021/public": 1,
                          "tarantool/cartridge-cli": 1,
                          "mtrempoltsev/tarantool_highload": 1,
                          "tiangolo/fastapi": 1})

API_KEY = "API_KEY"


@pytest.mark.parametrize("url, apikey, expected_counter",
                         [("https://github.com/vk-education/android-samples", API_KEY, result_counter),
                          ("vk-education/android-samples", API_KEY, result_counter)])
def test_stargazers_returns_right_counter(url: str, apikey: str, expected_counter: Counter) -> None:
    """
    Tests process_stargazers function is returning Counter type and that returns right data for testing repository
    example with different urls.
    """

    parse = process_stargazers(github_token=apikey, current_repo_name=url)
    expected_counter.most_common()
    assert (type(parse) is Counter) and (parse == expected_counter) and (len(parse) == len(expected_counter))
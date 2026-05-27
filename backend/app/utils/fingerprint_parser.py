import re

class FingerprintParser:

    FILENAME_PATTERN = re.compile(
        r"^(\d+)__(M|F)_(Left|Right)_(thumb|index|middle|ring|little)_finger\.BMP$",
        re.IGNORECASE
    )

    def parse_filename(self, filename: str):

        if not self.FILENAME_PATTERN.match(filename):
            return None

        # remove extension
        name = Path(filename).stem

        # split
        parts = name.split("_")

        # 1__M_Left_thumb_finger
        # ['1', '', 'M', 'Left', 'thumb', 'finger']

        external_id = int(parts[0])

        sex = parts[2]

        hand = parts[3].lower()

        finger = parts[4].lower()

        return {
            "external_id": external_id,
            "sex": sex,
            "hand": hand,
            "finger": finger
        }
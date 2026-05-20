import re


class PreprocessingService:

    def clean_text(
            self,
            text: str
    ):

        if not text:
            return ""

        text = text.lower()

        noise_patterns = [

            r"build info:.*",
            r"system info:.*",
            r"driver info:.*",
            r"capabilities \{.*",
            r"session id:.*",
            r"command:.*",
            r"\(session info:.*",

            # remove dynamic angular ids
            r"_ngcontent-[a-z0-9\-]+",

            # remove timestamps
            r"\d{2}:\d{2}:\d{2}",

            # remove memory addresses
            r"0x[a-f0-9]+",
        ]

        for pattern in noise_patterns:

            text = re.sub(
                pattern,
                " ",
                text,
                flags=re.DOTALL
            )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    def build_failure_text(
            self,
            data
    ):

        combined_text = f"""

        Test Name:
        {data.testName}

        Exception:
        {data.exceptionMessage}

        Stack Trace:
        {data.stackTrace}

        Browser Logs:
        {data.browserLogs}

        """

        cleaned_text = self.clean_text(
            combined_text
        )

        print(
            "\n================ CLEANED TEXT ================\n"
        )

        print(cleaned_text)

        print(
            "\n=====================================================\n"
        )

        return cleaned_text
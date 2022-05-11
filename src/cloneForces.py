import os
import config
from datetime import datetime

from bs4 import BeautifulSoup
import requests
from selenium import webdriver 
from webdriver_manager.firefox import GeckoDriverManager

api = "https://codeforces.com/api/user.status"
EXTENSIONS = {
    "C++": "cpp",
    "Bash": "sh",
    "C#": "cs",
    "JavaScript": "js",
    "OpenJDK": "java",
    "Haskell": "hs",
    "OCaml": "ml",
    "Perl": "pl",
    "PHP": "php",
    "Python": "py",
    "PyPy": "py",
    "Pascal": "pas",
    "Perl": "pl",
    "Ruby": "rb",
    "Scala": "scala",
    "Text": "txt",
    "Visual Basic": "vb",
    "Objective-C": "m",
    "Swift": "swift",
    "Rust": "rs",
    "Sed": "sed",
    "Awk": "awk",
    "Brainfuck": "bf",
    "Standard ML": "ml",
    "Crystal": "cr",
    "Julia": "jl",
    "Octave": "m",
    "Nim": "nim",
    "TypeScript": "ts",
    "Perl6": "p6",
    "Kotlin": "kt",
    "COBOL": "cob",
    "C": ".c",
}


class CF(object):

    def __init__(self, time_range):
        self.user_id = config.user_id
        self.time_range = time_range
        self.cur_unix_time = int(datetime.timestamp(datetime.now()))
        self.unix_time  =  int(datetime.timestamp(datetime.now()))

        if self.user_id is None:
            raise Exception("user_id not found. you must configure src/config.py")

    def get_submissions(self) -> None:

        self.unix_time = self.cur_unix_time - self.time_range
        params = {"handle": self.user_id,"from":"1","count":"1000"}
        result = requests.get(url=api, params=params)

        if not result.status_code == 200:
            raise Exception(f"{result.status_code} : Something went wrong")
        self.submissions = result.json()
        listOfSubmissions = self.submissions["result"]
        self.submissions = listOfSubmissions


    def get_and_write_submitted_codes(self) -> None:
    
        for record in self.submissions:
            contest_id = (record["contestId"])
            language = record["programmingLanguage"]
            problem_id = record["problem"]
            problem_name = problem_id["index"]

            submission_id = record["id"]
            result = record["verdict"]
            creationTime = record["creationTimeSeconds"]

            if result == "OK":
                if creationTime >= self.unix_time:
                    code = self.get_code(contest_id, submission_id)
                    self.write_code(code, contest_id, problem_name, language)
                else:
                    break
            else:
                pass

    def __call__(self):
        self.get_submissions()
        self.get_and_write_submitted_codes()

    @staticmethod
    def get_code(contest_id: str, submission_id: int) -> str:

        submission_url = (
            f"https://codeforces.com/contest/{contest_id}/submission/{submission_id}"
        )

        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        # executable_path param is not needed if you updated PATH
        # browser = webdriver.Firefox(options=options, executable_path='./geckodriver.exe')
        browser = webdriver.Firefox(options=options,executable_path=GeckoDriverManager().install())

        browser.get(submission_url)
        html = browser.page_source
        soup = BeautifulSoup(
            requests.get(submission_url).content, "html.parser"
        ).pre.string
        return soup
        # browser.quit()
        


    @staticmethod
    def write_code(code, contest_id, problem_name, language) -> None:

        extension = CF.get_extension(language)
        path = f"{contest_id}/{problem_name}.{extension}"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(code)


    @staticmethod
    def get_extension(language: str) -> str:

        extension = None
        for lang in EXTENSIONS.keys():
            if lang in language:
                extension = EXTENSIONS[lang]
                break
        if extension is None:
            raise Exception(
                f"Extension for {language} did not found. Please contact @uchihadark via GitHub"
            )
        return extension

if __name__ == "__main__":
    pass

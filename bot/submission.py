import attr


# pylint: disable=too-few-public-methods
@attr.s(auto_attribs=True)
class Submission:
    id: int
    cid: int
    rid: int
    login: str
    problem: str
    link: str

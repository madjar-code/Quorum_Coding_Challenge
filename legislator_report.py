from dataclasses import dataclass


class InputFileNotFound(Exception):
    def __init__(self, message):
        self.message = message


class IncorrectVoteCode(Exception):
    def __init__(self, message):
        self.message = message


class Config:
    INPUT_FOLDER = 'new_input'
    OUTPUT_FOLDER = 'new_output'
    VOTE_TYPE_MAPPING = {
        1: 'num_supported_bills',
        2: 'num_opposed_bills',
    }


@dataclass
class BillDTO:
    id: int
    title: str
    sponsor_id: int


@dataclass
class LegislatorDTO:
    id: int
    name: str


@dataclass
class VoteDTO:
    id: int
    bill_id: int


@dataclass
class VoteResultDTO:
    vote_id: int
    legislator_id: int
    vote_type: int

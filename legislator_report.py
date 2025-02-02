import os
import csv
from dataclasses import dataclass
from typing import Protocol, List, Dict


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


class DataReader(Protocol):
    def read_bills(self) -> List[BillDTO]:
        pass

    def read_legislators(self) -> List[LegislatorDTO]:
        pass

    def read_votes(self) -> List[VoteDTO]:
        pass

    def read_vote_results(self) -> List[VoteResultDTO]:
        pass


class CSVReader:
    def __init__(
        self,
        bills_filename: str,
        legislators_filename: str,
        votes_filename: str,
        vote_results_filename: str
    ):
        self.bills_path = os.path.join(Config.INPUT_FOLDER, bills_filename)
        self.legislators_path = os.path.join(Config.INPUT_FOLDER, legislators_filename)
        self.votes_path = os.path.join(Config.INPUT_FOLDER, votes_filename)
        self.vote_results_path = os.path.join(Config.INPUT_FOLDER, vote_results_filename)

    def _read_csv(self, path: str) -> List[Dict[str, str]]:
        try:
            with open(path, newline='', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        except FileNotFoundError:
            raise InputFileNotFound('Please make sure that the file exists in input folder')

    def read_bills(self) -> List[BillDTO]:
        return [
            BillDTO(
                int(row['id']),
                row['title'],
                int(row['sponsor_id'])
            ) for row in self._read_csv(self.bills_path)
        ]

    def read_legislators(self) -> List[LegislatorDTO]:
        return [
            LegislatorDTO(
                int(row['id']),
                row['name']
            ) for row in self._read_csv(self.legislators_path)
        ]

    def read_votes(self) -> List[VoteDTO]:
        return [
            VoteDTO(
                int(row['id']),
                int(row['bill_id'])
            ) for row in self._read_csv(self.votes_path)
        ]

    def read_vote_results(self) -> List[VoteResultDTO]:
        return [
            VoteResultDTO(
                int(row['vote_id']),
                int(row['legislator_id']),
                int(row['vote_type'])
            ) for row in self._read_csv(self.vote_results_path)
        ]


class LegislatorReportGenerator:
    def __init__(
        self,
        votes: List[VoteDTO],
        vote_results: List[VoteResultDTO],
        legislators: List[LegislatorDTO]
    ):
        self.votes = votes
        self.vote_results = vote_results
        self.legislators = {l.id: l.name for l in legislators}

    def generate_report(self) -> List[Dict[str, str]]:
        legislator_counts = dict()

        for vote_result in self.vote_results:  # O(V)
            legislator_id = vote_result.legislator_id
            vote_type = vote_result.vote_type

            if legislator_id not in legislator_counts:
                legislator_counts[legislator_id] = {
                    'num_supported_bills': 0,
                    'num_opposed_bills': 0
                }

            if vote_type in Config.VOTE_TYPE_MAPPING:
                key = Config.VOTE_TYPE_MAPPING[vote_type]
                legislator_counts[legislator_id][key] += 1
            else:
                raise IncorrectVoteCode(
                    f'The voting code `{vote_type}` in your file does not match the settings'
                )

        report = list()
        for legislator_id, counts in legislator_counts.items():  # O(L)
            report.append({
                'id': legislator_id,
                'name': self.legislators.get(legislator_id, 'Unknown'),
                'num_supported_bills': str(counts['num_supported_bills']),
                'num_opposed_bills': str(counts['num_opposed_bills'])
            })
        return report

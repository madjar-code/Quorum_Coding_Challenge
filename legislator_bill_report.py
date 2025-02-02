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
    INPUT_FOLDER = 'input'
    OUTPUT_FOLDER = 'output'
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


class BillReportGenerator:
    def __init__(
        self,
        votes: List[VoteDTO],
        bills: List[BillDTO],
        vote_results: List[VoteResultDTO],
        legislators: List[LegislatorDTO],
    ):
        self.vote_results = vote_results
        self.votes = {vote.id: vote.bill_id for vote in votes}
        self.bills = {b.id: b for b in bills}
        self.legislators = {l.id: l.name for l in legislators}

    def generate_report(self) -> List[Dict[str, str]]:
        bill_counts = dict()

        for vote_result in self.vote_results:
            bill_id = self.votes.get(vote_result.vote_id)
            if bill_id is None:
                continue

            if bill_id not in bill_counts:
                bill_counts[bill_id] = {
                    'supporter_count': 0,
                    'opposer_count': 0
                }

            if vote_result.vote_type == 1:
                bill_counts[bill_id]['supporter_count'] += 1
            elif vote_result.vote_type == 2:
                bill_counts[bill_id]['opposer_count'] += 1
            else:
                raise IncorrectVoteCode(
                    f'The voting code `{vote_result.vote_type}` in your file does not match the settings'
                )

        report = list()
        for bill_id, counts in bill_counts.items():
            bill = self.bills[bill_id]
            primary_sponsor = self.legislators.get(bill.sponsor_id, 'Unknown')

            report.append({
                'id': str(bill.id),
                'title': bill.title,
                'supporter_count': str(counts['supporter_count']),
                'opposer_count': str(counts['opposer_count']),
                'primary_sponsor': primary_sponsor,
            })

        return report            

class ReportWriter:
    @staticmethod
    def save_to_csv(data: List[Dict[str, str]], filename: str) -> None:
        if not data:
            print(f'No data to save in {filename}')
            return

        output_path = os.path.join(Config.OUTPUT_FOLDER, filename)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)


if __name__ == '__main__':
    reader = CSVReader(
        'bills.csv',
        'legislators.csv',
        'votes.csv',
        'vote_results.csv',
    )

    bills = reader.read_bills()
    legislators = reader.read_legislators()
    votes = reader.read_votes()
    vote_results = reader.read_vote_results()

    leg_report_generator = LegislatorReportGenerator(
        votes,
        vote_results,
        legislators,
    )
    legislator_report = leg_report_generator.generate_report()

    ReportWriter.save_to_csv(
        data=legislator_report,
        filename='legislators-support-oppose-count.csv'
    )

    bill_report_generator = BillReportGenerator(
        votes,
        bills,
        vote_results,
        legislators,
    )
    bill_report = bill_report_generator.generate_report()
    ReportWriter.save_to_csv(
        data=bill_report,
        filename='bills.csv'
    )

    print('CSV files generated successfully!')
